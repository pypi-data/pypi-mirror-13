# coding=utf-8
# ---------------------------------------------------------------
# Desenvolvedor:    Arannã Sousa Santos
# Mês:              12
# Ano:              2015
# Projeto:          pagseguro_xml
# e-mail:           asousas@live.com
# ---------------------------------------------------------------

import logging
import sys
import unittest

from ...core.base_classes import TagDataHoraUTC


class ClasseCancelamentoAssinaturaRetornoTest(unittest.TestCase):

    def test_parse_xml(self):

        from pagseguro_xml.assinatura.v2.classes import ClasseCancelamentoAssinaturaRetorno

        log = self.logger.getLogger(u'%s.%s' % (__package__, self.__class__.__name__))

        log.debug(u'Criando instancia de "ClasseCancelamentoAssinaturaRetorno"')
        result = ClasseCancelamentoAssinaturaRetorno()

        log.debug(u'Gerando PARSE do xml')
        result.xml = self.xml

        log.debug(u'Quantidade de alertas no "parse": %s' % len(result.alertas))

        for a in result.alertas:
            log.debug(u'Alerta: %s' % a)

        log.debug(u'Verificando a list de erros')

        data = TagDataHoraUTC()
        data.valor = u'2011-08-31T13:43:23.000-03:00'
        log.debug(u'Testando valores da "result"')
        self.assertEqual(result.date.valor, data.valor)
        self.assertEqual(result.status.valor, u'OK')


        log.debug(u'Errors OK')

    def setUp(self):

        logging.basicConfig(stream=sys.stderr)
        logging.getLogger(u'%s.%s' % (__package__, self.__class__.__name__)).setLevel(logging.DEBUG)

        self.logger = logging

        self.xml = u'''<?xml version="1.0" encoding="ISO-8859-1" standalone="yes"?>
<result>
    <date>2011-08-31T13:43:23.000-03:00</date>
    <status>OK</status>
</result>'''
