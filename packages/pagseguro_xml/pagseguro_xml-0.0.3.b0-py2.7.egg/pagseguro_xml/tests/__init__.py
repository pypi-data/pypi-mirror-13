# coding=utf-8
# ---------------------------------------------------------------
# Desenvolvedor:    Arannã Sousa Santos
# Mês:              12
# Ano:              2015
# Projeto:          pagseguro_xml
# e-mail:           asousas@live.com
# ---------------------------------------------------------------

import logging
import unittest
logger = logging.basicConfig(level=logging.DEBUG)

from .test_classes_assinatura import *
from .test_classes_consultas import *
from .test_classes_notificacao import *
from .test_classes_pagamento import *


if __name__ == '__main__':
    unittest.main()