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


class ClasseAssinaturaRequisicaoTest(unittest.TestCase):

    def test_parse_xml(self):

        from pagseguro_xml.assinatura.v2.classes import ClasseAssinaturaRequisicao

        log = self.logger.getLogger(u'%s.%s' % (__package__, self.__class__.__name__))

        log.debug(u'Criando instancia de "ClasseAssinaturaRequisicao"')
        result = ClasseAssinaturaRequisicao()

        log.debug(u'Gerando PARSE do xml')
        result.xml = self.xml

        log.debug(u'Quantidade de alertas no "parse": %s' % len(result.alertas))

        for a in result.alertas:
            log.debug(u'Alerta: %s' % a)

        data = TagDataHoraUTC()
        # data.valor = u'2011-02-16T20:14:35.000-02:00'

        log.debug(u'Testando valores da "preApprovalRequest"')
        self.assertEqual(result.redirectURL.valor, u'http://www.seusite.com.br/retorno.php')
        self.assertEqual(result.reviewURL.valor, u'http://www.seusite.com.br/revisao.php')
        self.assertEqual(result.reference.valor, u'REF1234')
        self.assertEqual(result.receiver.email.valor, u'nao@sei.com')
        self.assertEqual(result.sender.email.valor, u'cliente@uol.com.br')
        self.assertEqual(result.sender.name.valor, u'Nome do Cliente')
        self.assertEqual(result.sender.phone.areaCode.valor, 11)
        self.assertEqual(result.sender.phone.number.valor, 56273440)
        self.assertEqual(result.sender.address.street.valor, u'Avenida Brigadeiro Faria Lima')
        self.assertEqual(result.sender.address.number.valor, u'1384')
        self.assertEqual(result.sender.address.complement.valor, u'Andar')
        self.assertEqual(result.sender.address.district.valor, u'Jardim Paulistano')
        self.assertEqual(result.sender.address.postalCode.valor, u'01452002')
        self.assertEqual(result.sender.address.city.valor, u'São Paulo')
        self.assertEqual(result.sender.address.state.valor, u'SP')
        self.assertEqual(result.sender.address.country.valor, u'BRA')
        self.assertEqual(result.preApproval.charge.valor, u'auto')
        self.assertEqual(result.preApproval.name.valor, u'Seguro contra roubo do Notebook')
        self.assertEqual(result.preApproval.details.valor, u'Todo dia 28 será cobrado o valor de R$100,00 referente ao seguro contra roubo de Notebook')
        self.assertEqual(result.preApproval.amountPerPayment.valor, Decimal(u'100.00'))
        self.assertEqual(result.preApproval.period.valor, u'MONTHLY')

        data.valor = u'2014-01-21T00:00:000-03:00'
        self.assertEqual(result.preApproval.finalDate.valor, data.valor)
        self.assertEqual(result.preApproval.maxTotalAmount.valor, Decimal(u'2400.00'))

        log.debug(u'Valores da "preApprovalRequest" OK')

    def setUp(self):

        logging.basicConfig(stream=sys.stderr)
        logging.getLogger(u'%s.%s' % (__package__, self.__class__.__name__)).setLevel(logging.DEBUG)

        self.logger = logging

        self.xml = u'''<?xml version="1.0" encoding="ISO-8859-1" standalone="yes"?>
<preApprovalRequest>
    <redirectURL>http://www.seusite.com.br/retorno.php</redirectURL>
    <reviewURL>http://www.seusite.com.br/revisao.php</reviewURL>
    <reference>REF1234</reference>
    <receiver>
        <email>nao@sei.com</email>
    </receiver>
    <sender>
        <name>Nome do Cliente</name>
        <email>cliente@uol.com.br</email>
        <phone>
            <areaCode>11</areaCode>
            <number>56273440</number>
        </phone>
        <address>
            <street>Avenida Brigadeiro Faria Lima</street>
            <number>1384</number>
            <complement>Andar</complement>
            <district>Jardim Paulistano</district>
            <postalCode>01452002</postalCode>
            <city>São Paulo</city>
            <state>SP</state>
            <country>BRA</country>
        </address>
    </sender>
    <preApproval>
        <charge>auto</charge>
        <name>Seguro contra roubo do Notebook</name>
        <details>Todo dia 28 será cobrado o valor de R$100,00 referente ao seguro contra roubo de Notebook</details>
        <amountPerPayment>100.00</amountPerPayment>
        <period>MONTHLY</period>
        <finalDate>2014-01-21T00:00:000-03:00</finalDate>
        <maxTotalAmount>2400.00</maxTotalAmount>
    </preApproval>
</preApprovalRequest>'''


class ClasseAssinaturaRespostaTest(unittest.TestCase):

    def test_parse_xml(self):

        from pagseguro_xml.assinatura.v2.classes import ClasseAssinaturaResposta

        log = self.logger.getLogger(u'%s.%s' % (__package__, self.__class__.__name__))

        log.debug(u'Criando instancia de "ClasseAssinaturaResposta"')
        result = ClasseAssinaturaResposta()

        log.debug(u'Gerando PARSE do xml')
        result.xml = self.xml

        log.debug(u'Quantidade de alertas no "parse": %s' % len(result.alertas))

        for a in result.alertas:
            log.debug(u'Alerta: %s' % a)

        data = TagDataHoraUTC()
        data.valor = u'2014-01-21T00:00:00.000-03:00'

        log.debug(u'Testando valores da "preApprovalRequest"')
        self.assertEqual(result.code.valor, u'DC2DAC98FBFBDD1554493F94E85FAE05')
        self.assertEqual(result.date.valor, data.valor)
        log.debug(u'Valores da "preApprovalRequest" OK')

    def setUp(self):

        logging.basicConfig(stream=sys.stderr)
        logging.getLogger(u'%s.%s' % (__package__, self.__class__.__name__)).setLevel(logging.DEBUG)

        self.logger = logging

        self.xml = u'''<?xml version="1.0" encoding="ISO-8859-1" standalone="yes"?>
<preApprovalRequest>
    <code>DC2DAC98FBFBDD1554493F94E85FAE05</code>
    <date>2014-01-21T00:00:00.000-03:00</date>
</preApprovalRequest>'''
