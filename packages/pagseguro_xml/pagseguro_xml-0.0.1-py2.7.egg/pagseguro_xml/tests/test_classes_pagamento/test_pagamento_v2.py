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
from decimal import Decimal


class ClassePagamentoCheckoutV2Test(unittest.TestCase):
    def setUp(self):

        logging.basicConfig(stream=sys.stderr)
        logging.getLogger(u'%s.%s' % (__package__, self.__class__.__name__)).setLevel(logging.DEBUG)

        self.logger = logging

        self.xml = u'''<?xml version="1.0" encoding="ISO-8859-1" standalone="yes"?>
<checkout>
    <reference>REF1234</reference>
    <currency>BRL</currency>
    <items>
        <item>
            <id>0001</id>
            <description>Notebook Prata</description>
            <amount>24300.00</amount>
            <quantity>1</quantity>
            <weight>1000</weight>
        </item>
        <item>
            <id>0002</id>
            <description>Notebook Rosa</description>
            <amount>25600.00</amount>
            <quantity>2</quantity>
            <weight>750</weight>
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
        <type>1</type>
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
    </shipping>
</checkout>'''

    def test_parse_xml(self):

        from ...pagamento.v2.classes import ClassePagamentoCheckout

        log = self.logger.getLogger(u'%s.%s' % (__package__, self.__class__.__name__))

        log.debug(u'Criando instancia de "ClassePagamentoCheckout_v2"')
        result = ClassePagamentoCheckout()

        log.debug(u'Gerando PARSE do xml')
        result.xml = self.xml
        log.debug(u'Quantidade de alertas no "parse": %s' % len(result.alertas))

        log.debug(u'Testando valores da "checkout"')

        self.assertEqual(result.reference.valor, u'REF1234')
        self.assertEqual(result.currency.valor, u'BRL')

        self.assertEqual(len(result.items), 2)

        log.debug(u'Valores da "checkout" OK')

        items = [
            {
                u'id': u'0001',
                u'description': u'Notebook Prata',
                u'amount': Decimal(u'24300.00'),
                u'quantity': 1,
                u'weight': 1000,
            },
            {
                u'id': u'0002',
                u'description': u'Notebook Rosa',
                u'amount': Decimal(u'25600.00'),
                u'quantity': 2,
                u'weight': 750,
            },
        ]
        log.debug(u'Testando valores dos "itens"')
        for i, item in enumerate(result.items):

            log.debug(u'Item No: %s' % (i + 1))

            self.assertEqual(item.ID.valor, items[i][u'id'])
            self.assertEqual(item.description.valor, items[i][u'description'])
            self.assertEqual(item.amount.valor, items[i][u'amount'])
            self.assertEqual(item.quantity.valor, items[i][u'quantity'])
            self.assertEqual(item.weight.valor, items[i][u'weight'])

        log.debug(u'Testando dados do "comprador"')
        self.assertEqual(result.sender.name.valor, u'José Comprador')
        self.assertEqual(result.sender.email.valor, u'comprador@uol.com.br')
        self.assertEqual(result.sender.phone.areaCode.valor, 11)
        self.assertEqual(result.sender.phone.number.valor, 56273440)

        log.debug(u'Testando dados do "endereco" do comprador')
        self.assertEqual(result.shipping.type.valor, 1)
        self.assertEqual(result.shipping.address.street.valor, u'Av. Brig. Faria Lima')
        self.assertEqual(result.shipping.address.number.valor, u'1384')
        self.assertEqual(result.shipping.address.complement.valor, u'5o andar')
        self.assertEqual(result.shipping.address.district.valor, u'Jardim Paulistano')
        self.assertEqual(result.shipping.address.city.valor, u'Sao Paulo')
        self.assertEqual(result.shipping.address.state.valor, u'SP')
        self.assertEqual(result.shipping.address.country.valor, u'BRA')


class ClassePagamentoRetornoCheckoutV2Test(unittest.TestCase):
    def setUp(self):

        logging.basicConfig(stream=sys.stderr)
        logging.getLogger(u'%s.%s' % (__package__, self.__class__.__name__)).setLevel(logging.DEBUG)

        self.logger = logging

        self.xml = u'''<?xml version="1.0" encoding="ISO-8859-1" standalone="yes"?>
<checkout>
    <code>8CF4BE7DCECEF0F004A6DFA0A8243412</code>
    <date>2010-12-02T10:11:28.000-02:00</date>
</checkout>  '''

    def test_parse_xml(self):

        from ...pagamento.v2.classes import ClassePagamentoRetornoCheckout

        log = self.logger.getLogger(u'%s.%s' % (__package__, self.__class__.__name__))

        log.debug(u'Criando instancia de "ClassePagamentoRetornoCheckout_v2"')
        result = ClassePagamentoRetornoCheckout()

        log.debug(u'Gerando PARSE do xml')
        result.xml = self.xml
        log.debug(u'Quantidade de alertas no "parse": %s' % len(result.alertas))

        log.debug(u'Testando valores da "checkout"')

        from ...core.base_classes import TagDataHoraUTC

        date = TagDataHoraUTC()
        date.valor = u'2010-12-02T10:11:28.000-02:00'

        self.assertEqual(result.code.valor, u'8CF4BE7DCECEF0F004A6DFA0A8243412')
        self.assertEqual(result.date.valor, date.valor)
