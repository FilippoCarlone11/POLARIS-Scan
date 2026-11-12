# Copyright (C) 2026 Politecnico di Torino
# Dept. of Control and Computer Engineering - CAD Group
#
# Contacts:
# Matteo Sonza Reorda - 
# Josie Esteban Rodriguez Condia - 
# Filippo Carlone -
# Gabriele Belli - 
#
from log import setup_logging
import logging
from constants import polaris_scan_report, version
import argparse
import sys
from pathlib import Path
from parser import parse_tcl

from chain import chain_scan

from profiling import PROFILER


def main():
    parser = argparse.ArgumentParser(
        prog="polaris",
        description="POLARIS (POLito ATPG-Ready Insertion of Scan) is a Design-for-Testability tool developed at Politecnico di Torino that automates scan chain insertion. Like the North Star, it guides designers toward fully testable circuits."
    )

    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {version}")
    parser.add_argument("tcl_file", nargs="?", help="TCL file path")

    args = parser.parse_args()

    if args.tcl_file is None:
        parser.print_help()
        sys.exit(1)

    filename = args.tcl_file
    configuration = None
    log = logging.getLogger("polaris")
    try:
        configuration = parse_tcl(filename)
        work_dir = Path(configuration['work_dir'])
        setup_logging(work_dir / polaris_scan_report)
        log = logging.getLogger("polaris")

        operations = configuration['operations']

        chain_scan(verilog_input = configuration['verilog_file'],
                               clk_name = configuration['clock'],
                               chain_output = configuration['output_name'],
                               liberty_path = configuration['liberty_file'],
                               sin_name = configuration['sin'],
                               sout_name = configuration['sout'],
                               shift_name = configuration['shift'],
                               tck_name = configuration['tck'],
                               test_name = configuration['test'],
                               n_chains = configuration['n_chains'])
        
    except (RuntimeError, FileNotFoundError, ValueError) as e:
        log.error(e)
        sys.exit(1)
    finally:
        PROFILER.report(log=log.info, prefix="")
        if PROFILER.records and configuration is not None:
            PROFILER.dump_json(Path(configuration['work_dir']) / "profile.json")


if __name__ == "__main__":
    main()
