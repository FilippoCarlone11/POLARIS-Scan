# Copyright (c) 2026 CAD & Reliability Group, DAUIN, Polytechnic of Turin
#
# Authors:
# - Gabriele Belli  - gabriele.belli [at] studenti.polito.it or gb210403 [at] gmail.com
# - Filippo Carlone  - nome.cognome [at] studenti.polito.it or carlonefilippomm [at] gmail.com
# - Josie Esteban Rodriguez Condia  - josie.rodriguez [at] polito.it
# - Riccardo Cantoro  - riccardo.cantoro [at] polito.it
# - Matteo Sonza Reorda  - matteo.sonzareorda [at] polito.it
#
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
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
