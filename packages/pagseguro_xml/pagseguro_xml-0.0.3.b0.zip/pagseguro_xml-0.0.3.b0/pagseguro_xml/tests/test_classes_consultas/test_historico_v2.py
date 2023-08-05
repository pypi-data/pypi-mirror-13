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


class ClasseTransacaoHistoricoTest(unittest.TestCase):
    def setUp(self):

        logging.basicConfig(stream=sys.stderr)
        logging.getLogger(u'%s.%s' % (__package__, self.__class__.__name__)).setLevel(logging.DEBUG)

        self.logger = logging

        self.xml = u'''<?xml version="1.0" encoding="ISO-8859-1" standalone="yes"?>
<transactionSearchResult>
    <date>2011-02-16T20:14:35.000-02:00</date>
    <currentPage>1</currentPage>
    <resultsInThisPage>10</resultsInThisPage>
    <totalPages>1</totalPages>
    <transactions>
        <transaction>
            <date>2011-02-05T15:46:12.000-02:00</date>
            <lastEventDate>2011-02-15T17:39:14.000-03:00</lastEventDate>
            <code>9E884542-81B3-4419-9A75-BCC6FB495EF1</code>
            <reference>REF1234</reference>
            <type>1</type>
            <status>3</status>
            <paymentMethod>
                <type>1</type>
            </paymentMethod>
            <grossAmount>49900.00</grossAmount>
            <discountAmount>0.00</discountAmount>
            <feeAmount>0.00</feeAmount>
            <netAmount>49900.00</netAmount>
            <extraAmount>0.00</extraAmount>
        </transaction>
        <transaction>
            <date>2011-02-07T18:57:52.000-02:00</date>
            <lastEventDate>2011-02-14T21:37:24.000-03:00</lastEventDate>
            <code>2FB07A22-68FF-4F83-A356-24153A0C05E1</code>
            <reference>REF5678</reference>
            <type>3</type>
            <status>4</status>
            <paymentMethod>
                <type>3</type>
            </paymentMethod>
            <grossAmount>26900.00</grossAmount>
            <discountAmount>0.00</discountAmount>
            <feeAmount>0.00</feeAmount>
            <netAmount>26900.00</netAmount>
            <extraAmount>0.00</extraAmount>
        </transaction>
    </transactions>
</transactionSearchResult>'''

    def test_parse_xml(self):

        from pagseguro_xml.consultas.v2.classes import ClasseTransacaoHistorico

        log = self.logger.getLogger(u'%s.%s' % (__package__, self.__class__.__name__))

        log.debug(u'Criando instancia de "ClasseTransacaoHistorico"')
        result = ClasseTransacaoHistorico()

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
        self.assertEqual(result.resultsInThisPage.valor, 10)
        self.assertEqual(result.totalPages.valor, 1)
        self.assertEqual(len(result.transactions), 2)
        log.debug(u'Valores da "transactionSearchResult" OK')

        transactionsFilhos = [
            {
                u'date': u'2011-02-05T15:46:12.000-02:00',
                u'lastEventDate': u'2011-02-15T17:39:14.000-03:00',
                u'code': u'9E884542-81B3-4419-9A75-BCC6FB495EF1',
                u'reference': u'REF1234',
                u'type': 1,
                u'status': 3,
                u'paymentMethod.type': 1,
                u'grossAmount': Decimal(u'49900.00'),
                u'discountAmount': Decimal(u'0.00'),
                u'feeAmount': Decimal(u'0.00'),
                u'netAmount': Decimal(u'49900.00'),
                u'extraAmount': Decimal(u'0.00'),
            },
            {
                u'date': u'2011-02-07T18:57:52.000-02:00',
                u'lastEventDate': u'2011-02-14T21:37:24.000-03:00',
                u'code': u'2FB07A22-68FF-4F83-A356-24153A0C05E1',
                u'reference': u'REF5678',
                u'type': 3,
                u'status': 4,
                u'paymentMethod.type': 3,
                u'grossAmount': Decimal(u'26900.00'),
                u'discountAmount': Decimal(u'0.00'),
                u'feeAmount': Decimal(u'0.00'),
                u'netAmount': Decimal(u'26900.00'),
                u'extraAmount': Decimal(u'0.00'),
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
            self.assertEqual(transaction.status.valor, transactionsFilhos[i][u'status'])
            self.assertEqual(transaction.paymentMethod.type.valor, transactionsFilhos[i][u'paymentMethod.type'])
            self.assertEqual(transaction.grossAmount.valor, transactionsFilhos[i][u'grossAmount'])
            self.assertEqual(transaction.discountAmount.valor, transactionsFilhos[i][u'discountAmount'])
            self.assertEqual(transaction.feeAmount.valor, transactionsFilhos[i][u'feeAmount'])
            self.assertEqual(transaction.netAmount.valor, transactionsFilhos[i][u'netAmount'])
            self.assertEqual(transaction.extraAmount.valor, transactionsFilhos[i][u'extraAmount'])
