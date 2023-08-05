# coding=utf-8
# ---------------------------------------------------------------
# Desenvolvedor:    Arannã Sousa Santos
# Mês:              12
# Ano:              2015
# Projeto:          pagseguro_xml
# e-mail:           asousas@live.com
# ---------------------------------------------------------------

import unittest
import logging
import sys
from ...core.base_classes import TagDataHoraUTC
from decimal import Decimal


class ClasseNotificacaoTransacaoTest(unittest.TestCase):
    def setUp(self):

        logging.basicConfig(stream=sys.stderr)
        logging.getLogger(u'%s.%s' % (__package__, self.__class__.__name__)).setLevel(logging.DEBUG)

        self.logger = logging

        self.xml = u'''<?xml version="1.0" encoding="ISO-8859-1" standalone="yes"?>
<transaction>
        <date>2011-02-10T16:13:41.000-03:00</date>
        <code>9E884542-81B3-4419-9A75-BCC6FB495EF1</code>
        <reference>REF1234</reference>
        <type>1</type>
        <status>3</status>
        <paymentMethod>
            <type>1</type>
            <code>101</code>
        </paymentMethod>
        <grossAmount>49900.00</grossAmount>
        <discountAmount>0.00</discountAmount>
        <creditorFees>
            <intermediationRateAmount>0.40</intermediationRateAmount>
            <intermediationFeeAmount>1644.80</intermediationFeeAmount>
        </creditorFees>
        <netAmount>49900.00</netAmount>
        <extraAmount>0.00</extraAmount>
        <installmentCount>1</installmentCount>
        <itemCount>2</itemCount>
        <items>
            <item>
                <id>0001</id>
                <description>Notebook Prata</description>
                <quantity>1</quantity>
                <amount>24300.00</amount>
            </item>
            <item>
                <id>0002</id>
                <description>Notebook Rosa</description>
                <quantity>1</quantity>
                <amount>25600.00</amount>
            </item>
        </items>
        <sender>
            <name>José Comprador</name>
            <email>comprador@uol.com.br</email>
            <phone>
                <areaCode>11</areaCode>
                <number>56273440</number>
            </phone>
        </sender>
        <shipping>
            <address>
                <street>Av. Brig. Faria Lima</street>
                <number>1384</number>
                <complement>5o andar</complement>
                <district>Jardim Paulistano</district>
                <postalCode>01452002</postalCode>
                <city>Sao Paulo</city>
                <state>SP</state>
                <country>BRA</country>
            </address>
            <type>1</type>
            <cost>21.50</cost>
        </shipping>
</transaction>'''

    def test_parse_xml(self):

        from ...notificacao.v3.classes import ClasseNotificacaoTransacao

        log = self.logger.getLogger(u'%s.%s' % (__package__, self.__class__.__name__))

        log.debug(u'Criando instancia de "ClasseNotificacaoTransacao_v3"')
        result = ClasseNotificacaoTransacao()

        log.debug(u'Gerando PARSE do xml')
        result.xml = self.xml
        log.debug(u'Quantidade de alertas no "parse": %s' % len(result.alertas))

        log.debug(u'Testando valores da "transaction"')

        data = TagDataHoraUTC()
        data.valor = u'2011-02-10T16:13:41.000-03:00'

        self.assertEqual(result.date.valor, data.valor)

        self.assertEqual(result.code.valor, u'9E884542-81B3-4419-9A75-BCC6FB495EF1')
        self.assertEqual(result.reference.valor, u'REF1234')
        self.assertEqual(result.type.valor, 1)
        self.assertEqual(result.status.valor, 3)

        self.assertEqual(result.paymentMethod.type.valor, 1)
        self.assertEqual(result.paymentMethod.code.valor, 101)

        self.assertEqual(result.grossAmount.valor, Decimal(u'49900.00'))
        self.assertEqual(result.discountAmount.valor, Decimal(u'0.00'))

        self.assertEqual(result.creditorFees.intermediationRateAmount.valor, Decimal(u'0.40'))
        self.assertEqual(result.creditorFees.intermediationFeeAmount.valor, Decimal(u'1644.80'))

        self.assertEqual(result.netAmount.valor, Decimal(u'49900.00'))
        self.assertEqual(result.extraAmount.valor, Decimal(u'0.00'))
        self.assertEqual(result.installmentCount.valor, 1)
        self.assertEqual(result.itemCount.valor, 2)

        self.assertEqual(len(result.items), 2)

        log.debug(u'Valores da "transacao" OK')

        items = [
            {
                u'id': u'0001',
                u'description': u'Notebook Prata',
                u'quantity': Decimal(u'1.00'),
                u'amount': Decimal(u'24300.00'),
            },
            {
                u'id': u'0002',
                u'description': u'Notebook Rosa',
                u'quantity': Decimal(u'1.00'),
                u'amount': Decimal(u'25600.00'),
            },
        ]
        log.debug(u'Testando valores dos "itens"')
        for i, item in enumerate(result.items):

            log.debug(u'Item No: %s' % (i + 1))

            self.assertEqual(item.ID.valor, items[i][u'id'])
            self.assertEqual(item.description.valor, items[i][u'description'])
            self.assertEqual(item.quantity.valor, items[i][u'quantity'])
            self.assertEqual(item.amount.valor, items[i][u'amount'])

        log.debug(u'Testando dados do "comprador"')
        self.assertEqual(result.sender.name.valor, u'José Comprador')
        self.assertEqual(result.sender.email.valor, u'comprador@uol.com.br')
        self.assertEqual(result.sender.phone.areaCode.valor, 11)
        self.assertEqual(result.sender.phone.number.valor, 56273440)

        log.debug(u'Testando dados do "endereco" do comprador')
        self.assertEqual(result.shipping.address.street.valor, u'Av. Brig. Faria Lima')
        self.assertEqual(result.shipping.address.number.valor, u'1384')
        self.assertEqual(result.shipping.address.complement.valor, u'5o andar')
        self.assertEqual(result.shipping.address.district.valor, u'Jardim Paulistano')
        self.assertEqual(result.shipping.address.city.valor, u'Sao Paulo')
        self.assertEqual(result.shipping.address.state.valor, u'SP')
        self.assertEqual(result.shipping.address.country.valor, u'BRA')
        self.assertEqual(result.shipping.address.postalCode.valor, u'01452002')
        self.assertEqual(result.shipping.type.valor, 1)
        self.assertEqual(result.shipping.cost.valor, Decimal(u'21.50'))