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


class ClasseTransacaoDetalhesTest(unittest.TestCase):
    def setUp(self):

        logging.basicConfig(stream=sys.stderr)
        logging.getLogger(u'%s.%s' % (__package__, self.__class__.__name__)).setLevel(logging.DEBUG)

        self.logger = logging

        self.xml = u'''<?xml version="1.0" encoding="ISO-8859-1" standalone="yes"?>
<transaction>
    <date>2015-12-10T14:32:54.000-02:00</date>
    <code>B8CFB1D5-7E2E-4775-B747-6CD9B927738D</code>
    <reference>REF0001</reference>
    <type>11</type>
    <status>1</status>
    <lastEventDate>2015-12-10T14:32:54.000-02:00</lastEventDate>
    <paymentMethod>
        <type>1</type>
        <code>101</code>
    </paymentMethod>
    <grossAmount>1.00</grossAmount>
    <discountAmount>0.00</discountAmount>
    <creditorFees>
        <installmentFeeAmount>0.00</installmentFeeAmount>
        <intermediationRateAmount>0.40</intermediationRateAmount>
        <intermediationFeeAmount>0.04</intermediationFeeAmount>
    </creditorFees>
    <netAmount>0.56</netAmount>
    <installmentCount>1</installmentCount>
    <itemCount>1</itemCount>
    <items>
        <item>
            <id>001</id>
            <description>Plano simples de 6 meses por R$ 1,00</description>
            <quantity>1</quantity>
            <amount>1.00</amount>
        </item>
    </items>
    <sender>
        <name>ALGUEM DA CUNHA</name>
        <email>teste1234@sandbox.pagseguro.com.br</email>
        <phone>
            <areaCode>63</areaCode>
            <number>92111111</number>
        </phone>
    </sender>
    <shipping>
        <address>
            <street>RUA</street>
            <number>1</number>
            <complement></complement>
            <district>Centro</district>
            <city>PALMAS</city>
            <state>TO</state>
            <country>BRA</country>
            <postalCode>77000000</postalCode>
        </address>
        <type>3</type>
        <cost>0.00</cost>
    </shipping>
</transaction>'''

    def test_parse_xml(self):

        from ...consultas.v3.classes import ClasseTransacaoDetalhes

        log = self.logger.getLogger(u'%s.%s' % (__package__, self.__class__.__name__))

        log.debug(u'Criando instancia de "ClasseTransacaoDetalhes"')
        result = ClasseTransacaoDetalhes()

        log.debug(u'Gerando PARSE do xml')
        result.xml = self.xml
        log.debug(u'Quantidade de alertas no "parse": %s' % len(result.alertas))

        log.debug(u'Testando valores da "transaction"')

        data = TagDataHoraUTC()
        data.valor = u'2015-12-10T14:32:54.000-02:00'

        self.assertEqual(result.date.valor, data.valor)

        self.assertEqual(result.code.valor, u'B8CFB1D5-7E2E-4775-B747-6CD9B927738D')
        self.assertEqual(result.reference.valor, u'REF0001')
        self.assertEqual(result.type.valor, 11)
        self.assertEqual(result.status.valor, 1)

        data.valor = u'2015-12-10T14:32:54.000-02:00'
        self.assertEqual(result.lastEventDate.valor, data.valor)

        self.assertEqual(result.paymentMethod.type.valor, 1)
        self.assertEqual(result.paymentMethod.code.valor, 101)

        self.assertEqual(result.grossAmount.valor, Decimal(u'1.00'))
        self.assertEqual(result.discountAmount.valor, Decimal(u'0.00'))

        self.assertEqual(result.creditorFees.installmentFeeAmount.valor, Decimal(u'0.00'))
        self.assertEqual(result.creditorFees.intermediationRateAmount.valor, Decimal(u'0.40'))
        self.assertEqual(result.creditorFees.intermediationFeeAmount.valor, Decimal(u'0.04'))

        self.assertEqual(result.netAmount.valor, Decimal(u'0.56'))
        self.assertEqual(result.installmentCount.valor, 1)
        self.assertEqual(result.itemCount.valor, 1)

        self.assertEqual(len(result.items), 1)

        log.debug(u'Valores da "transacao" OK')

        items = [
            {
                u'id': u'001',
                u'description': u'Plano simples de 6 meses por R$ 1,00',
                u'quantity': Decimal(u'1.00'),
                u'amount': Decimal(u'1.00'),
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
        self.assertEqual(result.sender.name.valor, u'ALGUEM DA CUNHA')
        self.assertEqual(result.sender.email.valor, u'teste1234@sandbox.pagseguro.com.br')
        self.assertEqual(result.sender.phone.areaCode.valor, 63)
        self.assertEqual(result.sender.phone.number.valor, 92111111)

        log.debug(u'Testando dados do "endereco" do comprador')
        self.assertEqual(result.shipping.address.street.valor, u'RUA')
        self.assertEqual(result.shipping.address.number.valor, u'1')
        self.assertEqual(result.shipping.address.complement.valor, u'')
        self.assertEqual(result.shipping.address.district.valor, u'Centro')
        self.assertEqual(result.shipping.address.city.valor, u'PALMAS')
        self.assertEqual(result.shipping.address.state.valor, u'TO')
        self.assertEqual(result.shipping.address.country.valor, u'BRA')
        self.assertEqual(result.shipping.address.postalCode.valor, u'77000000')
        self.assertEqual(result.shipping.type.valor, 3)
        self.assertEqual(result.shipping.cost.valor, Decimal(u'0.00'))