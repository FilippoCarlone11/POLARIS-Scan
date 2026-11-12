# Copyright (C) 2026 Politecnico di Torino
# Dept. of Control and Computer Engineering - CAD Group
#
# Contacts:
# Matteo Sonza Reorda -
# Josie Esteban Rodriguez Condia -
# Filippo Carlone -
# Gabriele Belli - 
#

import logging

def setup_logging(log_path):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_path, mode="w"),
            logging.StreamHandler(),
        ],
    )