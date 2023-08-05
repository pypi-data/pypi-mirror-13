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

        class STATUS(object):
            AGUARDANDO_PAGAMENTO = 1
            EM_ANALISE = 2
            PAGA = 3
            DISPONIVEL = 4
            EM_DISPUTA = 5
            DEVOLVIDA = 6
            CANCELADA = 7
            CHARGEBACK_DEBITADO = 8
            EM_CONTENTACAO = 9

            opcoes = {
                AGUARDANDO_PAGAMENTO: u'Aguardando pagamento',
                EM_ANALISE: u'Em análise',
                PAGA: u'Paga',
                DISPONIVEL: u'Disponível',
                EM_DISPUTA: u'Em disputa',
                DEVOLVIDA: u'Devolvida',
                CANCELADA: u'Cancelada',
                CHARGEBACK_DEBITADO: u'Chargeback debitado',
                EM_CONTENTACAO: u'Em contestação',
            }

            desc = {
                AGUARDANDO_PAGAMENTO: u'o comprador iniciou a transação, mas até o momento o PagSeguro não recebeu nenhuma informação sobre o pagamento',
                EM_ANALISE: u'o comprador optou por pagar com um cartão de crédito e o PagSeguro está analisando o risco da transação',
                PAGA: u'a transação foi paga pelo comprador e o PagSeguro já recebeu uma confirmação da instituição financeira responsável pelo processamento',
                DISPONIVEL: u'a transação foi paga e chegou ao final de seu prazo de liberação sem ter sido retornada e sem que haja nenhuma disputa aberta',
                EM_DISPUTA: u'o comprador, dentro do prazo de liberação da transação, abriu uma disputa',
                DEVOLVIDA: u'o valor da transação foi devolvido para o comprador',
                CANCELADA: u'a transação foi cancelada sem ter sido finalizada',
                CHARGEBACK_DEBITADO: u'o valor da transação foi devolvido para o comprador',
                EM_CONTENTACAO: u'o comprador abriu uma solicitação de chargeback junto à operadora do cartão de crédito',
            }

        class CANCELLATIONSOURCE(object):
            INTERNAL = u'INTERNAL'
            EXTERNAL = u'EXTERNAL'

            opcoes = {
                INTERNAL: u'PagSeguro',
                EXTERNAL: u'Intituições Financeiras',
            }

        class PAYMENTMETHOD(object):
            class TYPE(object):
                CARTAO_CREDITO = 1
                BOLETO = 2
                DEBITO_ONLINE = 3
                SALDO_PAGSEGURO = 4
                OI_PAGGO = 5
                DEPOSITO_CONTA = 7

                opcoes = {
                    CARTAO_CREDITO: u'Cartão de crédito',
                    BOLETO: u'Boleto',
                    DEBITO_ONLINE: u'Débito online (TEF)',
                    SALDO_PAGSEGURO: u'Saldo PagSeguro',
                    OI_PAGGO: u'OI Paggo',  # nao disponivel para utilizacao =/
                    DEPOSITO_CONTA: u'Depósito em conta',
                }


class PaymentMethod(XMLAPI):
    def __init__(self):
        super(PaymentMethod, self).__init__()

        self.type = TagInteiro(nome=u'type', raiz=u'//transaction/paymentMethod',
                               opcoes=CONST.TRANSACTION.PAYMENTMETHOD.TYPE.opcoes)

    def get_xml(self):
        xml = XMLAPI.get_xml(self)
        xml += u'<paymentMethod>'

        xml += self.type.xml

        xml += u'</paymentMethod>'
        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):
            self.type.xml = arquivo

    xml = property(get_xml, set_xml)

    def get_alertas(self):
        alertas = []

        alertas.extend(self.type.alertas)

        return alertas

    alertas = property(get_alertas)


class Transaction(XMLAPI):
    def __init__(self):
        super(Transaction, self).__init__()

        self.date = TagDataHoraUTC(nome=u'date', raiz=u'//transaction')
        self.lastEventDate = TagDataHoraUTC(nome=u'lastEventDate', raiz=u'//transaction')
        self.code = TagCaracter(nome=u'code', raiz=u'//transaction', tamanho_min=36, tamanho_max=36)
        self.reference = TagCaracter(nome=u'reference', raiz=u'//transaction', tamanho_max=200, obrigatorio=False)

        self.type = TagInteiro(nome=u'type', raiz=u'//transaction', opcoes=CONST.TRANSACTION.TYPE.opcoes.keys())
        self.status = TagInteiro(nome=u'status', raiz=u'//transaction', opcoes=CONST.TRANSACTION.STATUS.opcoes.keys())
        self.cancellationSource = TagCaracter(nome=u'cancellationSource', raiz=u'//transaction',
                                              opcoes=CONST.TRANSACTION.CANCELLATIONSOURCE.opcoes.keys(), obrigatorio=False)

        self.paymentMethod = PaymentMethod()

        # valor bruto
        self.grossAmount = TagDecimal(nome=u'grossAmount', raiz=u'//transaction', tamanho_max=10, decimal_digitos=2,
                                      valor=0)

        # valor do desconto dado
        self.discountAmount = TagDecimal(nome=u'discountAmount', raiz=u'//transaction', tamanho_max=10,
                                         decimal_digitos=2, valor=0)

        # valor total das taxas cobradas
        self.feeAmount = TagDecimal(nome=u'feeAmount', raiz=u'//transaction', tamanho_max=10, decimal_digitos=2,
                                    valor=0)

        # valor liquido da transacao
        self.netAmount = TagDecimal(nome=u'netAmount', raiz=u'//transaction', tamanho_max=10, decimal_digitos=2,
                                    valor=0)

        # valor extra
        #
        #   Informa um valor extra que foi somado ou subtraído do valor pago pelo comprador.
        #   Este valor é especificado por você no pagamento e pode representar um valor que
        #   você quer cobrar separadamente do comprador ou um desconto que quer dar a ele
        #
        # Documentacao diz que é obrigatorio, mas no xml retornado nao veio
        self.extraAmount = TagDecimal(nome=u'extraAmount', raiz=u'//transactionSearchResult', tamanho_max=10, decimal_digitos=2,
                                      valor=0, obrigatorio=False)


    def get_xml(self):
        xml = XMLAPI.get_xml(self)
        xml += u'<transaction>'

        xml += self.date.xml
        xml += self.lastEventDate.xml
        xml += self.code.xml
        xml += self.reference.xml
        xml += self.type.xml
        xml += self.status.xml
        xml += self.cancellationSource.xml
        xml += self.paymentMethod.xml
        xml += self.grossAmount.xml
        xml += self.discountAmount.xml
        xml += self.feeAmount.xml
        xml += self.netAmount.xml
        xml += self.extraAmount.xml

        xml += u'</transaction>'
        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):
            self.date.xml = arquivo
            self.lastEventDate.xml = arquivo
            self.code.xml = arquivo
            self.reference.xml = arquivo
            self.type.xml = arquivo
            self.status.xml = arquivo

            self.cancellationSource.xml = arquivo

            self.paymentMethod.xml = arquivo
            self.grossAmount.xml = arquivo
            self.discountAmount.xml = arquivo
            self.feeAmount.xml = arquivo
            self.netAmount.xml = arquivo
            self.extraAmount.xml = arquivo

    xml = property(get_xml, set_xml)

    def get_alertas(self):
        alertas = []

        alertas.extend(self.date.alertas)
        alertas.extend(self.lastEventDate.alertas)
        alertas.extend(self.code.alertas)
        alertas.extend(self.reference.alertas)
        alertas.extend(self.type.alertas)
        alertas.extend(self.status.alertas)
        alertas.extend(self.cancellationSource.alertas)
        alertas.extend(self.paymentMethod.alertas)
        alertas.extend(self.grossAmount.alertas)
        alertas.extend(self.discountAmount.alertas)
        alertas.extend(self.feeAmount.alertas)
        alertas.extend(self.netAmount.alertas)
        alertas.extend(self.extraAmount.alertas)

        return alertas

    alertas = property(get_alertas)


class ClasseTransacaoHistorico(XMLAPI):
    def __init__(self):
        super(ClasseTransacaoHistorico, self).__init__()

        self.date = TagDataHoraUTC(nome=u'date', raiz=u'//transactionSearchResult')
        self.currentPage = TagInteiro(nome=u'currentPage', raiz=u'//transactionSearchResult', valor=1)
        self.resultsInThisPage = TagInteiro(nome=u'resultsInThisPage', raiz=u'//transactionSearchResult')
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
