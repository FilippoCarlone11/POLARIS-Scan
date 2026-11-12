# Copyright (C) 2026 Politecnico di Torino
# Dept. of Control and Computer Engineering - CAD Group
#
# Contacts:
# Matteo Sonza Reorda - 
# Josie Esteban Rodriguez Condia - 
# Filippo Carlone -
# Gabriele Belli - 
#
# For every DFF a library mux is inserted on the D pin:
#   D_ff = shift ? (Q of the previous FF in the chain, or `sin` for the first)
#               : original functional D driver
# plus the clock mux: __clk_source__ = test ? tck : clk, driving the CLK of
# every FF. `sout` = Q of the last FF in the chain.
#
# MULTIPLE CHAINS (n_chains > 1): the FFs are split into n_chains contiguous
# groups, balanced (the first `len(ffs) % n_chains` chains get one FF more), so
# the SHIFT DEPTH -- the length of the longest chain, which sets the test
# application time -- is the minimum possible. Each chain gets its own
# `sin<i>`/`sout<i>` port pair, while `shift`, `test` and `tck` stay SHARED (a
# single scan-enable and a single clock mux for the whole design). With
# n_chains == 1 nothing changes: the ports keep the plain `sin`/`sout` names
# and the emitted netlist/metadata are identical to the single-chain ones.
#
# Key differences with respect to Fault's chain:
# - no boundary scan (we never used it: --no-boundary);
# - REAL library cells are instantiated (MUX2_X1 / sg13g2_mux2_1), so the
#   yosys resynthesis Fault needed (it inserted ternaries and had to re-map
#   them) is not needed -> much faster;
# - no built-in .tb.sv self-verification (the slow part of Fault): the chain
#   is validated downstream by the ATPG-vector scan test (flow step 10) and,
#   optionally, by the quick shift-through check (--verify-chain).
#
# The FAULT METADATA comment is emitted in the same JSON format as Fault's,
# so all the downstream tooling (generate_scan_tb.py, etc.) works unchanged.

import json
import sys
from pyosys import libyosys as ys
from lib2flipflop import dff_families, mux_by_lib
from constants import *
import logging
from profiling import profiled


def _idw(name):
    return ys.IdString(f"\\{name}")


def _add_input(module, name):
    w = module.addWire(_idw(name), 1)
    w.port_input = True
    return w


def _same_wire(sig, wire):
    """True if the SigSpec is exactly that wire (used for the clock warning)."""
    try:
        return sig.is_wire() and sig.as_wire().name.str() == wire.name.str()
    except Exception:
        return False


def split_chains(n_items, n_chains):
    """Balanced contiguous partition: the first (n_items % n_chains) chains get
    one item more, so the difference in length between any two chains is at
    most 1 and the shift depth (the longest chain) is minimal.
    Example: 10 FFs in 3 chains -> [4, 3, 3]."""
    base, rem = divmod(n_items, n_chains)
    return [base + 1 if i < rem else base for i in range(n_chains)]


def _port_names(base, n_chains):
    """Scan port names: a single chain keeps the plain name (`sin`), several
    chains are numbered (`sin0`, `sin1`, ...)."""
    if n_chains == 1:
        return [base]
    return [f"{base}{i}" for i in range(n_chains)]

@profiled("chain")
def chain_scan(verilog_input, clk_name, chain_output, liberty_path=None,
               sin_name="sin", sout_name="sout", shift_name="shift",
               tck_name="tck", test_name="test", n_chains=1):
    """Inserts the internal scan chain(s) into the synthesized netlist.

    n_chains: how many parallel scan chains to build (default 1). The FFs are
    split into balanced contiguous groups; every chain gets its own sin/sout
    while shift/test/tck are shared.
    The reset is not touched (the internal chain does not use it).
    liberty_path is only needed if the synth contains leftover generic cells.
    """
    log = logging.getLogger(__name__)
    log.info(f"start scan chain")
    if liberty_path is None:
        raise FileNotFoundError("The liberty path is none")

    DFF_FAMILIES = dff_families(liberty_path)
    MUX_BY_LIB = mux_by_lib(liberty_path)

    if n_chains < 1:
        raise ValueError(f"n_chains must be >= 1 (got {n_chains})")
    design = ys.Design()
    ys.run_pass(f"read_verilog {verilog_input}", design)
    ys.run_pass("proc", design)
    module = design.top_module()

    # A netlist written by our synth already carries the `top` attribute set by
    # the `hierarchy -top` in the .ys script, so top_module() resolves and we do
    # nothing. It is None when the input never went through hierarchy (e.g. raw
    # multi-module RTL passed straight to `polaris chain`): try to elect the top
    # ourselves before giving up.
    if module is None:
        log.info("[POLARIS_Scan] No top module marked in the input: trying hierarchy -auto-top...")
        try:
            ys.run_pass("hierarchy -auto-top", design)
        except Exception as e:
            raise RuntimeError(
                f"Top module not found in the input netlist and hierarchy -auto-top failed ({e}). "
                f"'{verilog_input}' does not look like a synthesized netlist: run synthesis first."
            )
        module = design.top_module()
        if module is None:
            raise RuntimeError(
                f"Top module not found in the input netlist: '{verilog_input}' does not look like "
                f"a synthesized netlist. Run synthesis first."
            )
        top_name = module.name.str().lstrip("\\")
        log.info(f"Top module elected: {top_name}")

    
        subs = [c for c in module.cells_.values()
                if design.module(c.type) is not None]
        if subs:
            log.info(f"{len(subs)} instances of sub modules: trying flatten...")
            ys.run_pass("flatten", design)
            module = design.top_module()
            n = len(module.cells_)
            log.info(f"[POLARIS-Scan] Post-flatten: {n} cells in the main module")


    
    # On some circuits (b11, b15, b17, b18, b19...) synthesis leaves unmapped
    # generic cells ($_MUX_ etc.) which write_verilog emits as behavioral
    # ternaries -> OpenSTA (and any "clean netlist" consumer) rejects them.
    # Fault did not show the problem only because it always resynthesized.
    # Here we map them with abc ONLY if present (clean circuits pay nothing).
    leftover = any(c.type.str().startswith("$") and c.type.str() != "$scopeinfo"
                   for c in module.cells_.values())
    if leftover:
        if not liberty_path:
            raise RuntimeError("Leftover generic cells in the synth but no liberty provided")
        log.info("Leftover generic cells in the synth: mapping with abc...")
        ys.run_pass("techmap", design)
        ys.run_pass(f"abc -liberty {liberty_path}", design)
        ys.run_pass("opt_clean -purge", design)
        module = design.top_module()

    # 1. find the FFs (same families as the cut) and detect the library
    ffs = []
    lib = None
    for cell in list(module.cells_.values()):
        cell_type = cell.type.str().lstrip("\\")
        for fam, clk_pin, d_pin, q_pin, fam_lib in DFF_FAMILIES:
            if fam in cell_type:
                ffs.append((cell, clk_pin, d_pin, q_pin))
                if lib is None:
                    lib = fam_lib
                elif lib != fam_lib:
                    log.warning(f"mixed FF libraries in the netlist: {lib} vs {fam_lib}")
                break

    if not ffs:
        from collections import Counter
        hist = Counter(c.type.str().lstrip("\\") for c in module.cells_.values())
        log.info(f"Nessuna FF riconosciuta. {len(module.cells_)} celle nel top:")
        for t, n in hist.most_common(25):
            known = "" if design.module(_idw(t)) is None else "  <- sub-module!"
            print(f"   {n:7d}  {t}{known}")
        raise RuntimeError(
            "No flip-flop found: try to flatten your circuit, or check the technology"
        )

    # more chains than FFs makes no sense (empty chains): clamp
    if n_chains > len(ffs):
        log.warning(f"{n_chains} chains requested but only {len(ffs)} FFs available: "
              f"using {len(ffs)} chains")
        n_chains = len(ffs)

    mux_cell_name, mux_i0, mux_i1, mux_s, mux_z = MUX_BY_LIB[lib]

    # 2. existing clock port + new scan ports (one sin/sout pair per chain,
    #    shift/test/tck shared)
    clk_wire = module.wire(_idw(clk_name))
    if clk_wire is None:
        raise RuntimeError(f"Clock port '{clk_name}' not found")

    sin_names  = _port_names(sin_name, n_chains)
    sout_names = _port_names(sout_name, n_chains)
    sin_ws  = [_add_input(module, n) for n in sin_names]
    shift_w = _add_input(module, shift_name)
    tck_w   = _add_input(module, tck_name)
    test_w  = _add_input(module, test_name)
    sout_ws = []
    for n in sout_names:
        w = module.addWire(_idw(n), 1)
        w.port_output = True
        sout_ws.append(w)

    # 3. clock mux: __clk_source__ = test ? tck : clk 
    clk_src = module.addWire(_idw("__clk_source__"), 1)
    cmux = module.addCell(_idw("__clk_mux__"), _idw(mux_cell_name))
    cmux.setPort(_idw(mux_i0), ys.SigSpec(clk_wire))
    cmux.setPort(_idw(mux_i1), ys.SigSpec(tck_w))
    cmux.setPort(_idw(mux_s),  ys.SigSpec(test_w))
    cmux.setPort(_idw(mux_z),  ys.SigSpec(clk_src))

    # 4. the chains: a mux on every FF's D, CLK rewired to __clk_source__.
    #    The FFs are taken in netlist order and split into balanced contiguous
    #    groups; the cell/wire indices stay GLOBAL so the names are unique.
    sizes = split_chains(len(ffs), n_chains)
    chains_meta = []
    i = 0
    for c, size in enumerate(sizes):
        prev = ys.SigSpec(sin_ws[c])   # scan-in of the first FF of this chain
        order = []
        for _ in range(size):
            ff, clk_pin, d_pin, q_pin = ffs[i]
            ff_name = ff.name.str().lstrip("\\")

            # D and CK must be connected; Q can be legitimately unconnected in a
            # DC netlist (FF used only through QN): getPort on a missing pin
            # throws dict::at(), so check first
            if not ff.hasPort(_idw(d_pin)) or not ff.hasPort(_idw(clk_pin)):
                raise RuntimeError(f"{ff_name}: pin {d_pin} or {clk_pin} not connected")
            if not ff.hasPort(_idw(q_pin)):
                # the chain needs Q as the scan path: attach a fresh wire
                qw = module.addWire(_idw(f"__scan_q_{i}__"), 1)
                ff.setPort(_idw(q_pin), ys.SigSpec(qw))

            d_sig = ff.getPort(_idw(d_pin))
            mux_out = module.addWire(_idw(f"__scan_mux_{i}__"), 1)
            mux = module.addCell(_idw(f"__scan_mux_cell_{i}__"), _idw(mux_cell_name))
            mux.setPort(_idw(mux_i0), d_sig)               # shift=0: functional D
            mux.setPort(_idw(mux_i1), prev)                # shift=1: scan path
            mux.setPort(_idw(mux_s),  ys.SigSpec(shift_w))
            mux.setPort(_idw(mux_z),  ys.SigSpec(mux_out))
            ff.setPort(_idw(d_pin), ys.SigSpec(mux_out))

            cur_clk = ff.getPort(_idw(clk_pin))
            if not _same_wire(cur_clk, clk_wire):
                log.warning(f"{ff_name}: clock different from '{clk_name}', rewired to __clk_source__ anyway")
            ff.setPort(_idw(clk_pin), ys.SigSpec(clk_src))

            prev = ff.getPort(_idw(q_pin))                 # Q -> scan-in of the next FF
            order.append({"name": ff_name, "width": 1, "kind": "dff", "ordinal": 0})
            log.info(f"Chained (chain {c}, {i}): {ff_name}")
            i += 1

        # 5. sout of this chain = Q of its last FF
        module.connect(ys.SigSpec(sout_ws[c]), prev)
        chains_meta.append({"sin": sin_names[c], "sout": sout_names[c], "order": order})

    module.fixup_ports()

    # 6. write the netlist + metadata in Fault's format
    ys.run_pass(f"write_verilog {chain_output}", design)

    # metadata: the historical fields keep their meaning (order = all the FFs
    # in chain order, sin/sout = those of the FIRST chain) so anything reading
    # Fault's format still works; 'chains' is added ONLY with several chains
    # and carries the per-chain ports and order (used by the TB generators).
    metadata = {
        "sin": sin_names[0], "shift": shift_name, "sout": sout_names[0],
        "boundaryCount": 0, "internalCount": len(ffs),
        "order": [e for ch in chains_meta for e in ch["order"]],
    }
    if n_chains > 1:
        metadata["chains"] = chains_meta
    content = open(chain_output).read()
    header = f"/* POLARIS-Scan METADATA: '{json.dumps(metadata)}' END POLARIS-Scan METADATA */\n"
    with open(chain_output, "w") as f:
        f.write(header + content)

    depth = max(sizes)
    log.info(f"Internal scan chain inserted: {len(ffs)} FFs in {n_chains} chain(s) "
          f"(sizes {'/'.join(str(s) for s in sizes)}, shift depth {depth}), "
          f"mux {mux_cell_name}, clock mux __clk_source__")
    if n_chains > 1:
        log.info(f"[POLARIS-Scan] Shift cost per vector: {2 * depth + 2} ticks vs "
              f"{2 * len(ffs) + 2} with a single chain")
    log.info(f"The scan chain generation is completed")
    log.info(f"the scan chain file name is {chain_output}")
    return len(ffs)

