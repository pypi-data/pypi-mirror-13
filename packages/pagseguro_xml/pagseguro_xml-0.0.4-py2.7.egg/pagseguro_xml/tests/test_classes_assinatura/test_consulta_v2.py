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


class ClasseConsultaAssinaturaRespostaTest(unittest.TestCase):

    def test_parse_xml(self):

        from pagseguro_xml.assinatura.v2.classes import ClasseConsultaAssinaturaResposta

        log = self.logger.getLogger(u'%s.%s' % (__package__, self.__class__.__name__))

        log.debug(u'Criando instancia de "ClasseConsultaAssinaturaResposta"')
        result = ClasseConsultaAssinaturaResposta()

        log.debug(u'Gerando PARSE do xml')
        result.xml = self.xml

        log.debug(u'Quantidade de alertas no "parse": %s' % len(result.alertas))

        for a in result.alertas:
            log.debug(u'Alerta: %s' % a)

        data = TagDataHoraUTC()

        log.debug(u'Verificando os dados de "preApproval"')
        self.assertEqual(result.name.valor, u'Seguro contra roubo do Notebook Prata')
        self.assertEqual(result.code.valor, u'C08984179E9EDF3DD4023F87B71DE349')
        data.valor = u'2011-11-23T13:40:23.000-02:00'
        self.assertEqual(result.date.valor, data.valor)
        self.assertEqual(result.tracker.valor, u'538C53')
        self.assertEqual(result.status.valor, u'CANCELLED')
        self.assertEqual(result.reference.valor, u'REF1234')
        data.valor = u'2011-11-25T20:04:23.000-02:00'
        self.assertEqual(result.lastEventDate.valor, data.valor)
        self.assertEqual(result.charge.valor, u'auto')

        log.debug(u'Verificando os dados de "sender" (comprador)')
        self.assertEqual(result.sender.name.valor, u'Nome Comprador')
        self.assertEqual(result.sender.email.valor, u'comprador@uol.com')
        self.assertEqual(result.sender.phone.areaCode.valor, 11)
        self.assertEqual(result.sender.phone.number.valor, 30389678)
        self.assertEqual(result.sender.address.street.valor, u'ALAMEDA ITU')
        self.assertEqual(result.sender.address.number.valor, u'78')
        self.assertEqual(result.sender.address.complement.valor, u'ap. 2601')
        self.assertEqual(result.sender.address.district.valor, u'Jardim Paulista')
        self.assertEqual(result.sender.address.city.valor, u'SAO PAULO')
        self.assertEqual(result.sender.address.country.valor, u'BRA')
        self.assertEqual(result.sender.address.postalCode.valor, u'01421000')

        log.debug(u'Dados OK')

    def setUp(self):

        logging.basicConfig(stream=sys.stderr)
        logging.getLogger(u'%s.%s' % (__package__, self.__class__.__name__)).setLevel(logging.DEBUG)

        self.logger = logging

        self.xml = u'''<?xml version="1.0" encoding="ISO-8859-1" standalone="yes"?>
<preApproval>
    <name>Seguro contra roubo do Notebook Prata</name>
    <code>C08984179E9EDF3DD4023F87B71DE349</code>
    <date>2011-11-23T13:40:23.000-02:00</date>
    <tracker>538C53</tracker>
    <status>CANCELLED</status>
    <reference>REF1234</reference>
    <lastEventDate>2011-11-25T20:04:23.000-02:00</lastEventDate>
    <charge>auto</charge>
    <sender>
        <name>Nome Comprador</name>
        <email>comprador@uol.com</email>
        <phone>
            <areaCode>11</areaCode>
            <number>30389678</number>
        </phone>
        <address>
            <street>ALAMEDA ITU</street>
            <number>78</number>
            <complement>ap. 2601</complement>
            <district>Jardim Paulista</district>
            <city>SAO PAULO</city>
            <state>SP</state>
            <country>BRA</country>
            <postalCode>01421000</postalCode>
        </address>
    </sender>
</preApproval>'''


class ClasseConsultaAssinaturasRespostaTest(unittest.TestCase):

    def test_parse_xml(self):

        from pagseguro_xml.assinatura.v2.classes import ClasseConsultaAssinaturasResposta

        log = self.logger.getLogger(u'%s.%s' % (__package__, self.__class__.__name__))

        log.debug(u'Criando instancia de "ClasseConsultaAssinaturasResposta"')
        result = ClasseConsultaAssinaturasResposta()

        log.debug(u'Gerando PARSE do xml')
        result.xml = self.xml

        log.debug(u'Quantidade de alertas no "parse": %s' % len(result.alertas))

        for a in result.alertas:
            log.debug(u'Alerta: %s' % a)

        data = TagDataHoraUTC()

        log.debug(u'Verificando os dados de "preApprovalSearchResult"')
        self.assertEqual(result.resultsInThisPage.valor, 1)
        self.assertEqual(result.currentPage.valor, 1)
        self.assertEqual(result.totalPages.valor, 1)
        data.valor = u'2011-08-08T16:16:23.000-03:00'
        self.assertEqual(result.date.valor, data.valor)

        itens = [
            {
                u'name': u'PagSeguro Pre Approval',
                u'code': u'12E10BEF5E5EF94004313FB891C8E4CF',
                u'date': u'2011-08-15T11:06:44.000-03:00',
                u'tracker': u'624C17',
                u'status': u'INITIATED',
                u'reference': u'R123456',
                u'lastEventDate': u'2011-08-08T15:37:30.000-03:00',
                u'charge': u'auto',
            },
        ]

        log.debug(u'Verificando a list de "preAproval"')
        for i, preApproval in enumerate(result.preApprovals):
            log.debug(u'Testando valores do preApproval No "%s"' % (i + 1))
            self.assertEqual(preApproval.name.valor, itens[i][u'name'])
            self.assertEqual(preApproval.code.valor, itens[i][u'code'])
            data.valor = itens[i][u'date']
            self.assertEqual(preApproval.date.valor, data.valor)
            self.assertEqual(preApproval.tracker.valor, itens[i][u'tracker'])
            self.assertEqual(preApproval.status.valor, itens[i][u'status'])
            self.assertEqual(preApproval.reference.valor, itens[i][u'reference'])
            data.valor = itens[i][u'lastEventDate']
            self.assertEqual(preApproval.lastEventDate.valor, data.valor)
            self.assertEqual(preApproval.charge.valor, itens[i][u'charge'])

        log.debug(u'Dados OK')

    def setUp(self):

        logging.basicConfig(stream=sys.stderr)
        logging.getLogger(u'%s.%s' % (__package__, self.__class__.__name__)).setLevel(logging.DEBUG)

        self.logger = logging

        self.xml = u'''<?xml version="1.0" encoding="ISO-8859-1" standalone="yes"?>
<preApprovalSearchResult>
    <resultsInThisPage>1</resultsInThisPage>
    <currentPage>1</currentPage>
    <totalPages>1</totalPages>
    <date>2011-08-08T16:16:23.000-03:00</date>
    <preApprovals>
        <preApproval>
            <name>PagSeguro Pre Approval</name>
            <code>12E10BEF5E5EF94004313FB891C8E4CF</code>
            <date>2011-08-15T11:06:44.000-03:00</date>
            <tracker>624C17</tracker>
            <status>INITIATED</status>
            <reference>R123456</reference>
            <lastEventDate>2011-08-08T15:37:30.000-03:00</lastEventDate>
            <charge>auto</charge>
        </preApproval>
    </preApprovals>
</preApprovalSearchResult>
'''