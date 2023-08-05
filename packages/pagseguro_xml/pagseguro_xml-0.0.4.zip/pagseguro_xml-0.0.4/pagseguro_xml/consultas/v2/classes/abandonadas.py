# coding=utf-8
# ---------------------------------------------------------------
# Desenvolvedor:    Arannã Sousa Santos
# Mês:              12
# Ano:              2015
# Projeto:          pagseguro_xml
# e-mail:           asousas@live.com
# ---------------------------------------------------------------

from __future__ import division, print_function, unicode_literals
from pagseguro_xml.core.base_classes import (
    ABERTURA, TagCaracter, TagInteiro, TagDataHoraUTC, TagDecimal,
    XMLAPI
)


class CONST(object):
    class TRANSACTION(object):

        class TYPE(object):
            PAGAMENTO = 1

            opcoes = {
                PAGAMENTO: u'A transação foi criada por um comprador fazendo um pagamento.',
                2: u'Testes',
                3: u'Testes',
                4: u'Testes',
                5: u'Testes',
                6: u'Testes',
                7: u'Testes',
                8: u'Testes',
                9: u'Testes',
                10: u'Testes',
                11: u'Testes',
            }


class Transaction(XMLAPI):
    def __init__(self):
        super(Transaction, self).__init__()

        self.date = TagDataHoraUTC(nome=u'date', raiz=u'//transaction')
        self.lastEventDate = TagDataHoraUTC(nome=u'lastEventDate', raiz=u'//transaction')
        self.code = TagCaracter(nome=u'code', raiz=u'//transaction', tamanho_min=36, tamanho_max=36)
        self.reference = TagCaracter(nome=u'reference', raiz=u'//transaction', tamanho_max=200, obrigatorio=False)

        self.type = TagInteiro(nome=u'type', raiz=u'//transaction', opcoes=CONST.TRANSACTION.TYPE.opcoes.keys())

        # valor bruto
        self.grossAmount = TagDecimal(nome=u'grossAmount', raiz=u'//transaction', tamanho_max=10, decimal_digitos=2,
                                      valor=0)

    def get_xml(self):
        xml = XMLAPI.get_xml(self)
        xml += u'<transaction>'

        xml += self.date.xml
        xml += self.lastEventDate.xml
        xml += self.code.xml
        xml += self.reference.xml
        xml += self.type.xml
        xml += self.grossAmount.xml

        xml += u'</transaction>'
        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):
            self.date.xml = arquivo
            self.lastEventDate.xml = arquivo
            self.code.xml = arquivo
            self.reference.xml = arquivo
            self.type.xml = arquivo
            self.grossAmount.xml = arquivo

    xml = property(get_xml, set_xml)

    def get_alertas(self):
        alertas = []

        alertas.extend(self.date.alertas)
        alertas.extend(self.lastEventDate.alertas)
        alertas.extend(self.code.alertas)
        alertas.extend(self.reference.alertas)
        alertas.extend(self.type.alertas)
        alertas.extend(self.grossAmount.alertas)

        return alertas

    alertas = property(get_alertas)


class ClasseTransacaoAbandonadas(XMLAPI):
    def __init__(self):
        super(ClasseTransacaoAbandonadas, self).__init__()

        self.date = TagDataHoraUTC(nome=u'date', raiz=u'//transactionSearchResult')
        self.currentPage = TagInteiro(nome=u'currentPage', raiz=u'//transactionSearchResult', valor=1)
        self.resultsInThisPage = TagInteiro(nome=u'resultsInThisPage', raiz=u'//transactionSearchResult', valor=50)
        self.totalPages = TagInteiro(nome=u'totalPages', raiz=u'//transactionSearchResult')

        self.transactions = []

    def get_xml(self):
        xml = XMLAPI.get_xml(self)
        xml += ABERTURA
        xml += u'<transactionSearchResult>'

        xml += self.date.xml
        xml += self.currentPage.xml
        xml += self.resultsInThisPage.xml
        xml += self.totalPages.xml

        xml += u'<transactions>'
        for transacao in self.transactions:
            xml += transacao.xml
        xml += u'</transactions>'

        xml += u'</transactionSearchResult>'
        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):
            self.date.xml = arquivo
            self.currentPage.xml = arquivo
            self.resultsInThisPage.xml = arquivo
            self.totalPages.xml = arquivo

            self.transactions = self.le_grupo(u'//transactionSearchResult/transactions/transaction', Transaction)

    xml = property(get_xml, set_xml)

    def get_alertas(self):
        alertas = []

        alertas.extend(self.date.alertas)
        alertas.extend(self.currentPage.alertas)
        alertas.extend(self.resultsInThisPage.alertas)
        alertas.extend(self.totalPages.alertas)

        for transaction in self.transactions:
            alertas.extend(transaction.alertas)

        return alertas

    alertas = property(get_alertas)
