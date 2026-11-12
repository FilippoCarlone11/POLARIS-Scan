# Copyright (C) 2026 Politecnico di Torino
# Dept. of Control and Computer Engineering - CAD Group
#
# Contacts:
# Matteo Sonza Reorda - 
# Josie Esteban Rodriguez Condia -  
# Filippo Carlone -
# Gabriele Belli - 
#

"""Profilazione per fase di Polaris: tempo (wall/CPU) e memoria (RSS).

Misura sia il processo Python (che include Yosys, dato che pyosys gira
in-process) sia i processi figli (Atalanta, yosys-abc, ...), senza dover
modificare le chiamate a subprocess esistenti.

Uso:
    from polaris.profiling import profiled, PROFILER

    @profiled("chain")
    def chain_scan(...): ...

    # a fine main():
    PROFILER.report()
    PROFILER.dump_json(work_dir / "profile.json")
"""
import functools
import json
import resource
import threading
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path

import psutil

_MB = 1024 * 1024


@dataclass
class PhaseRecord:
    name: str
    depth: int                  # livello di annidamento (flow -> 0, sue fasi -> 1)
    status: str = "ok"
    wall_s: float = 0.0         # tempo reale
    cpu_s: float = 0.0          # CPU del processo Polaris (tutti i thread, Yosys incluso)
    child_cpu_s: float = 0.0    # CPU dei figli terminati nella fase (Atalanta, abc, ...)
    rss_start_mb: float = 0.0
    rss_end_mb: float = 0.0
    rss_peak_mb: float = 0.0    # picco RSS del processo durante la fase
    child_peak_mb: float = 0.0  # picco della somma RSS dei figli vivi durante la fase

    @property
    def rss_growth_mb(self):
        """Quanto la fase ha fatto salire la memoria rispetto a come l'ha trovata."""
        return self.rss_peak_mb - self.rss_start_mb


def _children_cpu():
    ru = resource.getrusage(resource.RUSAGE_CHILDREN)
    return ru.ru_utime + ru.ru_stime


class Profiler:
    def __init__(self, interval_s=0.01):
        self._proc = psutil.Process()
        self._interval = interval_s
        self._stack = []            # fasi attive (annidate)
        self._lock = threading.Lock()
        self._thread = None
        self.records = []           # in ordine di inizio

    # ---------- campionamento in background ----------
    def _ensure_sampler(self):
        if self._thread is None:
            self._thread = threading.Thread(target=self._sample, daemon=True,
                                            name="polaris-profiler")
            self._thread.start()

    def _sample(self):
        while True:
            time.sleep(self._interval)
            try:
                own = self._proc.memory_info().rss
                kids = 0
                for c in self._proc.children(recursive=True):
                    try:
                        kids += c.memory_info().rss
                    except psutil.Error:      # figlio appena terminato
                        pass
            except psutil.Error:
                continue
            with self._lock:
                for r in self._stack:         # aggiorna tutte le fasi annidate
                    r.rss_peak_mb = max(r.rss_peak_mb, own / _MB)
                    r.child_peak_mb = max(r.child_peak_mb, kids / _MB)

    # ---------- API ----------
    @contextmanager
    def phase(self, name):
        rss0 = self._proc.memory_info().rss / _MB
        with self._lock:
            rec = PhaseRecord(name, depth=len(self._stack),
                              rss_start_mb=rss0, rss_end_mb=rss0, rss_peak_mb=rss0)
            self.records.append(rec)
            self._stack.append(rec)
        self._ensure_sampler()

        t0, c0, k0 = time.perf_counter(), time.process_time(), _children_cpu()
        try:
            yield rec
        except KeyboardInterrupt:
            rec.status = "interrotta"
            raise
        except BaseException:
            rec.status = "errore"
            raise
        finally:
            rec.wall_s = time.perf_counter() - t0
            rec.cpu_s = time.process_time() - c0
            rec.child_cpu_s = _children_cpu() - k0
            rss1 = self._proc.memory_info().rss / _MB
            with self._lock:
                rec.rss_end_mb = rss1
                rec.rss_peak_mb = max(rec.rss_peak_mb, rss1)
                self._stack.remove(rec)

    def report(self, log=print, prefix="[POLARIS]"):
        if not self.records:
            return

        # Definizione delle larghezze per ogni colonna (aumentate per dare più respiro)
        w_phase = 26
        w_wall = 12
        w_cpu = 12
        w_ccpu = 16
        w_rss = 16
        w_growth = 14
        w_crss = 13

        # Header con spaziatura aumentata
        cols = (f"{'phase':<{w_phase}}{'wall[s]':>{w_wall}}{'CPU[s]':>{w_cpu}}"
                f"{'childs CPU[s]':>{w_ccpu}}{'RSSpeak[MB]':>{w_rss}}"
                f"{'+peak[MB]':>{w_growth}}{'childs[MB]':>{w_crss}}")

        log(f"{prefix} ===== Resources per phase =====")
        log(f"{prefix} {cols}")
        log(f"{prefix} {'-' * len(cols)}")

        for r in self.records:
            label = "  " * r.depth + r.name + ("" if r.status == "ok" else f" [{r.status}]")
            log(f"{prefix} {label:<{w_phase}}{r.wall_s:>{w_wall}.2f}{r.cpu_s:>{w_cpu}.2f}"
                f"{r.child_cpu_s:>{w_ccpu}.2f}{r.rss_peak_mb:>{w_rss}.1f}"
                f"{r.rss_growth_mb:>{w_growth}.1f}{r.child_peak_mb:>{w_crss}.1f}")

        top = [r for r in self.records if r.depth == 0]
        if len(top) > 1:
            log(f"{prefix} {'-' * len(cols)}")
            log(f"{prefix} {'TOTAL':<{w_phase}}{sum(r.wall_s for r in top):>{w_wall}.2f}"
                f"{sum(r.cpu_s for r in top):>{w_cpu}.2f}{sum(r.child_cpu_s for r in top):>{w_ccpu}.2f}"
                f"{max(r.rss_peak_mb for r in top):>{w_rss}.1f}{'':>{w_growth}}"
                f"{max(r.child_peak_mb for r in top):>{w_crss}.1f}")

        self_peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
        log(f"{prefix} RSS peak of Polaris on the entire run: {self_peak:.1f} MB")

    def dump_json(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = [dict(asdict(r), rss_growth_mb=r.rss_growth_mb) for r in self.records]
        path.write_text(json.dumps(data, indent=2))


PROFILER = Profiler()


def profiled(name=None):
    """Decoratore: registra la funzione come fase con il nome dato."""
    def deco(fn):
        label = name or fn.__name__

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            with PROFILER.phase(label):
                return fn(*args, **kwargs)
        return wrapper
    return deco