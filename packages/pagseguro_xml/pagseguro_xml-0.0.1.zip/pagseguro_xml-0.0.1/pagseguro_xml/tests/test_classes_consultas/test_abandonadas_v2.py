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
from decimal import Decimal

from ...core.base_classes import TagDataHoraUTC


class ClasseTransacaoAbandonadasTest(unittest.TestCase):
    def setUp(self):

        logging.basicConfig(stream=sys.stderr)
        logging.getLogger(u'%s.%s' % (__package__, self.__class__.__name__)).setLevel(logging.DEBUG)

        self.logger = logging

        self.xml = u'''<?xml version="1.0" encoding="ISO-8859-1" standalone="yes"?>
<transactionSearchResult>
    <date>2011-02-16T20:14:35.000-02:00</date>
    <currentPage>1</currentPage>
    <resultsInThisPage>2</resultsInThisPage>
    <totalPages>1</totalPages>
    <transactions>
        <transaction>
            <date>2011-02-05T15:46:12.000-02:00</date>
            <lastEventDate>2011-02-15T17:39:14.000-03:00</lastEventDate>
            <code>EDDDC505-8A26-494E-96C2-53D285A470C2</code>
            <type>1</type>
            <grossAmount>6.00</grossAmount>
        </transaction>
        <transaction>
            <date>2011-02-07T18:57:52.000-02:00</date>
            <lastEventDate>2011-02-14T21:37:24.000-03:00</lastEventDate>
            <reference>REFCODE2</reference>
            <code>97B1F57E-0EC0-4D03-BF7E-C4694CF6062E</code>
            <type>1</type>
            <grossAmount>6.00</grossAmount>
        </transaction>
    </transactions>
</transactionSearchResult> '''

    def test_parse_xml(self):

        from pagseguro_xml.consultas.v2.classes import ClasseTransacaoAbandonadas

        log = self.logger.getLogger(u'%s.%s' % (__package__, self.__class__.__name__))

        log.debug(u'Criando instancia de "ClasseTransacaoAbandonadas"')
        result = ClasseTransacaoAbandonadas()

        log.debug(u'Gerando PARSE do xml')
        result.xml = self.xml

        log.debug(u'Quantidade de alertas no "parse": %s' % len(result.alertas))

        for a in result.alertas:
            log.debug(u'Alerta: %s' % a)

        data = TagDataHoraUTC()
        data.valor = u'2011-02-16T20:14:35.000-02:00'

        log.debug(u'Testando valores da "transactionSearchResult"')
        self.assertEqual(result.date.valor, data.valor)
        self.assertEqual(result.currentPage.valor, 1)
        self.assertEqual(result.resultsInThisPage.valor, 2)
        self.assertEqual(result.totalPages.valor, 1)
        self.assertEqual(len(result.transactions), 2)
        log.debug(u'Valores da "transactionSearchResult" OK')

        transactionsFilhos = [
            {
                u'date': u'2011-02-05T15:46:12.000-02:00',
                u'lastEventDate': u'2011-02-15T17:39:14.000-03:00',
                u'code': u'EDDDC505-8A26-494E-96C2-53D285A470C2',
                u'reference': u'',
                u'type': 1,
                u'grossAmount': Decimal(u'6.00'),
            },
            {
                u'date': u'2011-02-07T18:57:52.000-02:00',
                u'lastEventDate': u'2011-02-14T21:37:24.000-03:00',
                u'code': u'97B1F57E-0EC0-4D03-BF7E-C4694CF6062E',
                u'reference': u'REFCODE2',
                u'type': 1,
                u'grossAmount': Decimal(u'6.00'),
            },
        ]
        log.debug(u'Testando valores das "transactions"')
        for i, transaction in enumerate(result.transactions):

            log.debug(u'Transactions No: %s' % (i + 1))

            data.valor = transactionsFilhos[i][u'date']
            self.assertEqual(transaction.date.valor, data.valor)

            data.valor = transactionsFilhos[i][u'lastEventDate']
            self.assertEqual(transaction.lastEventDate.valor, data.valor)

            self.assertEqual(transaction.reference.valor, transactionsFilhos[i][u'reference'])
            self.assertEqual(transaction.type.valor, transactionsFilhos[i][u'type'])
            self.assertEqual(transaction.grossAmount.valor, transactionsFilhos[i][u'grossAmount'])
