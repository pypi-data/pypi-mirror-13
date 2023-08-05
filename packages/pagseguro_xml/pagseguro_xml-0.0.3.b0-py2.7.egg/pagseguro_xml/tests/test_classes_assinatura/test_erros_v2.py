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


class ClasseAssinaturaErrosTest(unittest.TestCase):

    def test_parse_xml(self):

        from pagseguro_xml.assinatura.v2.classes.erros import ClasseAssinaturaErros

        log = self.logger.getLogger(u'%s.%s' % (__package__, self.__class__.__name__))

        log.debug(u'Criando instancia de "ClasseAssinaturaErros"')
        result = ClasseAssinaturaErros()

        log.debug(u'Gerando PARSE do xml')
        result.xml = self.xml

        log.debug(u'Quantidade de alertas no "parse": %s' % len(result.alertas))

        for a in result.alertas:
            log.debug(u'Alerta: %s' % a)

        itens = [
            {
                u'code': u'11072',
                u'message': u'preApprovalFinalDate invalid value.',
            },
            {
                u'code': u'17022',
                u'message': u'invalid pre-approval status to execute the requested operation. Pre-approval status is CANCELLED_BY_RECEIVER.',
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
        <code>11072</code>
        <message>preApprovalFinalDate invalid value.</message>
    </error>
    <error>
        <code>17022</code>
        <message>invalid pre-approval status to execute the requested operation. Pre-approval status is CANCELLED_BY_RECEIVER.</message>
    </error>
</errors>'''
