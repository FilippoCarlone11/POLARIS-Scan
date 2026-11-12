# Copyright (C) 2026 Politecnico di Torino
# Dept. of Control and Computer Engineering - CAD Group
#
# Contacts:
# Matteo Sonza Reorda - 
# Josie Esteban Rodriguez Condia - 
# Filippo Carlone -
# Gabriele Belli - 
#


import shlex
import logging
import sys
#from constants import TECH_MAP


STAGES = ["chain"]

def parse_tcl(filename):
    log = logging.getLogger("parser")
    configuration = {
        'verilog_file': None,
        'clock': 'clk',
        'operations': [],
        'liberty_file' : None,
        #'tech' : None,
        'output_name' : None,
        'work_dir' : '.',
        'sin' : 'sin',
        'sout' : 'sout',
        'shift' : 'shift',
        'tck' : 'tck',
        'test' : 'test',
        'n_chains' : 1,
    }

    def handle_read_verilog(args):
        if args: configuration['verilog_file'] = args[0]

    def handle_set_clock(args):
        if args: configuration['clock'] = args[0]

    def handle_set_operation(args):
        if args: configuration['operations'] = list(args)

    def handle_set_liberty_file(args):
        if args: configuration['liberty_file'] = args[0]

    #def handle_set_tech(args):
    #    if args: configuration['tech'] = args[0]

    def handle_set_output_name(args):
        if args: configuration['output_name'] = args[0]

    def handle_set_work_dir(args):
        if args: configuration['work_dir'] = args[0]

    def handle_set_sin(args):
        if args: configuration['sin'] = args[0]

    def handle_set_sout(args):
        if args: configuration['sout'] = args[0]

    def handle_set_shift(args):
        if args: configuration['shift'] = args[0]

    def handle_set_tck(args):
        if args: configuration['tck'] = args[0]

    def handle_set_test(args):
        if args: configuration['test'] = args[0]

    def handle_set_n_chains(args):
        if args:
            try:
                configuration['n_chains'] = int(args[0])
            except ValueError:
                raise ValueError(f"set_n_chains needs an integer, got {args[0]}")

    dispatch_table = {
        'read_verilog': handle_read_verilog,
        'set_clock': handle_set_clock,
        'set_operation': handle_set_operation,
        'set_liberty' : handle_set_liberty_file,
#        'set_tech' : handle_set_tech,
        'set_output_name' : handle_set_output_name,
        'set_work_dir' : handle_set_work_dir,
        'set_sin' : handle_set_sin,
        'set_sout' : handle_set_sout,
        'set_shift' : handle_set_shift,
        'set_tck' : handle_set_tck,
        'set_test' : handle_set_test,
        'set_n_chains' : handle_set_n_chains,
    }

    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith('#'):
                continue

            try:
                tokens = shlex.split(line)
            except ValueError:
                log.error("There is a problem with the value in the TCL file.")
                continue

            if not tokens:
                continue

            cmd = tokens[0]
            args = tokens[1:]

            if cmd in dispatch_table:
                dispatch_table[cmd](args)
            else:
                log.warning(f"the command {cmd} is not recognized")

    # Verifica operazioni
    operations = configuration['operations']
    if not operations:
        log.error("you need to use the set_operation command in the TCL file")
        sys.exit(1)

    for op in operations:
        if op not in STAGES:
            log.error(f"This operation {op} is not supported. Only 'chain' is allowed.")
            sys.exit(1)

    # Controlli specifici ed esclusivi per la fase 'chain'
    if configuration['verilog_file'] is None:
        log.error("when the operation is CHAIN you should provide a verilog file through read_verilog")
        sys.exit(1)
    if configuration['clock'] is None:
        log.error("when the operation is CHAIN you should provide a clock name that is not None through set_clock (without using set_clock, 'clk' is the standard name)")
        sys.exit(1)
    if configuration['sin'] is None:
        log.error("when the operation is CHAIN you should provide a sin name that is not None through set_sin (without using set_sin, 'sin' is the standard name)")
        sys.exit(1)
    if configuration['sout'] is None:
        log.error("when the operation is CHAIN you should provide a sout name that is not None through set_sout (without using set_sout, 'sout' is the standard name)")
        sys.exit(1)
    if configuration['shift'] is None:
        log.error("when the operation is CHAIN you should provide a shift name that is not None through set_shift (without using set_shift, 'shift' is the standard name)")
        sys.exit(1)
    if configuration['tck'] is None:
        log.error("when the operation is CHAIN you should provide a tck name that is not None through set_tck (without using set_tck, 'tck' is the standard name)")
        sys.exit(1)
    if configuration['test'] is None:
        log.error("when the operation is CHAIN you should provide a test name that is not None through set_test (without using set_test, 'test' is the standard name)")
        sys.exit(1)
    if configuration['n_chains'] is None:
        log.error("when the operation is CHAIN you should provide a n_chains name that is not None through set_n_chains (without using set_n_chains, the chain will be one)")
        sys.exit(1)
    if configuration['output_name'] is None:
        log.error("when the operation is CHAIN you should provide an output name that is not None through set_output_name")
        sys.exit(1)
    if configuration['liberty_file'] is None:
        log.error("when the operation is CHAIN you should provide the liberty_file")
        sys.exit(1)

    if configuration['n_chains'] < 1:
        raise ValueError("set_n_chains must be >= 1")

    
    #if configuration['tech'] and not configuration['liberty_file']:
    #    if configuration['tech'] not in TECH_MAP:
    #        raise ValueError(f"the tech {configuration['tech']} is not supported, choose one of: {', '.join(TECH_MAP)}")
    #    configuration['liberty_file'] = TECH_MAP[configuration['tech']]['liberty']

    return configuration