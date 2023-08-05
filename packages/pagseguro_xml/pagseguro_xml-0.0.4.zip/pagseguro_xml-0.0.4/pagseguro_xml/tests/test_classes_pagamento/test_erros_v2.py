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


class ClassePagamentoErrosV2Test(unittest.TestCase):

    def test_parse_xml(self):

        from pagseguro_xml.pagamento.v2.classes import ClassePagamentoErros

        log = self.logger.getLogger(u'%s.%s' % (__package__, self.__class__.__name__))

        log.debug(u'Criando instancia de "ClassePagamentoErros_v2"')
        result = ClassePagamentoErros()

        log.debug(u'Gerando PARSE do xml')
        result.xml = self.xml

        log.debug(u'Quantidade de alertas no "parse": %s' % len(result.alertas))

        for a in result.alertas:
            log.debug(u'Alerta: %s' % a)

        itens = [
            {
                u'code': u'11004',
                u'message': u'Currency is required.',
            },
            {
                u'code': u'11005',
                u'message': u'Currency invalid value: 100',
            },
        ]

        log.debug(u'Verificando a list de erros')
        for i, error in enumerate(result.errors):
            log.debug(u'Testando valores do error No "%s"' % (i + 1))
            self.assertEqual(error.code.valor, itens[i][u'code'])
            self.assertEqual(error.message.valor, itens[i][u'message'])

        log.debug(u'Errors OK')

    def setUp(self):

        logging.basicConfig(stream=sys.stderr)
        logging.getLogger(u'%s.%s' % (__package__, self.__class__.__name__)).setLevel(logging.DEBUG)

        self.logger = logging

        self.xml = u'''<?xml version="1.0" encoding="ISO-8859-1" standalone="yes"?>
<errors>
    <error>
        <code>11004</code>
        <message>Currency is required.</message>
    </error>
    <error>
        <code>11005</code>
        <message>Currency invalid value: 100</message>
    </error>
</errors> '''
