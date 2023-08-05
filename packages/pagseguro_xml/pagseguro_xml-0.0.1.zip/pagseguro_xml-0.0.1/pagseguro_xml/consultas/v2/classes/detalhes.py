# coding=utf-8
# ---------------------------------------------------------------
# Desenvolvedor:    Arannã Sousa Santos
# Mês:              12
# Ano:              2015
# Projeto:          pagseguro_xml
# e-mail:           asousas@live.com
# ---------------------------------------------------------------

from __future__ import division, print_function, unicode_literals
from ....core.base_classes import (
    ABERTURA, TagCaracter, TagInteiro, TagDataHoraUTC, TagDecimal,
    XMLAPI
)


class CONST(object):
    class TYPE(object):
        PAGAMENTO = 1

        opcoes = {
            PAGAMENTO: u'A transação foi criada por um comprador fazendo um pagamento.',
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

        class CODE(object):
            opcoes = {
                101: u'Cartão de cédito VISA',
                102: u'Cartão de cédito MasterCard',
                103: u'Cartão de cédito American Express',
                104: u'Cartão de cédito Diners',
                105: u'Cartão de cédito Hipercard',
                106: u'Cartão de cédito Aura',
                107: u'Cartão de cédito Elo',
                108: u'Cartão de cédito PLENOCard',  # *
                109: u'Cartão de cédito PersonalCard',
                110: u'Cartão de cédito JCB',
                111: u'Cartão de cédito Discover',
                112: u'Cartão de cédito BrasilCard',
                113: u'Cartão de cédito FORTBRASIL',
                114: u'Cartão de cédito CARDBAN',
                115: u'Cartão de cédito VALECARD',
                116: u'Cartão de cédito Cabal',
                117: u'Cartão de cédito Mais!',
                118: u'Cartão de cédito Avista',
                119: u'Cartão de cédito GRANDCARD',
                120: u'Cartão de cédito Sorocred',
                201: u'Boleto Bradesco',
                202: u'Boleto Santander',
                301: u'Débito online Bradesco',
                302: u'Débito online Itaú',
                303: u'Débito online Unibanco',
                304: u'Débito online Banco do Brasil',
                305: u'Débito online Banco Real',
                306: u'Débito online Barisul',
                307: u'Débito online HSBC',
                401: u'Saldo PagSeguro',
                501: u'OI Paggo',
                701: u'Depósito em conta - Banco do Brasil',
                702: u'Depósito em conta - HSBC',
            }

    class SHIPPING(object):
        class TYPE(object):
            NORMAL_PAC = 1
            SEDEX = 2
            NAO_ESPECIFICADO = 3

            opcoes = {
                NORMAL_PAC: u'Encomenda normal PAC',
                SEDEX: u'SEDEX',
                NAO_ESPECIFICADO: u'Sem frete',
            }


class Item(XMLAPI):
    def __init__(self):
        super(Item, self).__init__()

        self.ID = TagCaracter(nome=u'id', raiz=u'//item')
        self.description = TagCaracter(nome=u'description', raiz=u'//item')

        # valor unitario do item
        self.amount = TagDecimal(nome=u'amount', raiz=u'//item', tamanho_max=10, decimal_digitos=2, valor=0)
        self.quantity = TagDecimal(nome=u'quantity', raiz=u'//item', tamanho_max=10, decimal_digitos=2, valor=0)

    def get_xml(self):
        xml = XMLAPI.get_xml(self)
        xml += u'<item>'

        xml += self.ID.xml
        xml += self.description.xml
        xml += self.amount.xml
        xml += self.quantity.xml

        xml += u'</item>'
        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):
            self.ID.xml = arquivo
            self.description.xml = arquivo
            self.amount.xml = arquivo
            self.quantity.xml = arquivo

    xml = property(get_xml, set_xml)

    def get_alertas(self):
        alertas = []

        alertas.extend(self.ID.alertas)
        alertas.extend(self.description.alertas)
        alertas.extend(self.amount.alertas)
        alertas.extend(self.quantity.alertas)

        return alertas

    alertas = property(get_alertas)


class Address(XMLAPI):
    def __init__(self):
        super(Address, self).__init__()

        self.country = TagCaracter(nome=u'country', raiz=u'//transaction/shipping/address', opcoes=(u'BRA',),
                                   valor=u'BRA', obrigatorio=False)
        # UF - somente duas letras
        self.state = TagCaracter(nome=u'state', raiz=u'//transaction/shipping/address', tamanho_min=2, tamanho_max=2,
                                 obrigatorio=False)
        self.city = TagCaracter(nome=u'city', raiz=u'//transaction/shipping/address', obrigatorio=False)
        self.postalCode = TagCaracter(nome=u'postalCode', raiz=u'//transaction/shipping/address', tamanho_min=8,
                                      tamanho_max=8, obrigatorio=False)
        # endereco do envio
        self.district = TagCaracter(nome=u'district', raiz=u'//transaction/shipping/address', obrigatorio=False)
        self.street = TagCaracter(nome=u'street', raiz=u'//transaction/shipping/address', obrigatorio=False)
        self.number = TagCaracter(nome=u'number', raiz=u'//transaction/shipping/address', obrigatorio=False)
        self.complement = TagCaracter(nome=u'complement', raiz=u'//transaction/shipping/address', obrigatorio=False)

    def get_xml(self):
        if not (
                                            self.country.valor or
                                            self.state.valor or
                                        self.city.valor or
                                    self.postalCode.valor or
                                self.district.valor or
                            self.street.valor or
                        self.number.valor or
                    self.complement.valor
        ):
            return u''

        xml = XMLAPI.get_xml(self)
        xml += u'<address>'

        xml += self.country.xml
        xml += self.state.xml
        xml += self.city.xml
        xml += self.postalCode.xml
        xml += self.district.xml
        xml += self.street.xml
        xml += self.number.xml
        xml += self.complement.xml

        xml += u'</address>'
        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):
            self.country.xml = arquivo
            self.state.xml = arquivo
            self.city.xml = arquivo
            self.postalCode.xml = arquivo
            self.district.xml = arquivo
            self.street.xml = arquivo
            self.number.xml = arquivo
            self.complement.xml = arquivo

    xml = property(get_xml, set_xml)

    def get_alertas(self):
        alertas = []

        alertas.extend(self.country.alertas)
        alertas.extend(self.state.alertas)
        alertas.extend(self.city.alertas)
        alertas.extend(self.postalCode.alertas)
        alertas.extend(self.district.alertas)
        alertas.extend(self.street.alertas)
        alertas.extend(self.number.alertas)
        alertas.extend(self.complement.alertas)

        return alertas

    alertas = property(get_alertas)


class Shipping(XMLAPI):
    def __init__(self):
        super(Shipping, self).__init__()

        # por mais estranho, na documentacao diz que é obrigatorio MAS no xml retornado nao veio
        self.cost = TagDecimal(nome=u'cost', raiz=u'//transaction/shipping', tamanho_max=10, decimal_digitos=2, valor=0,
                               obrigatorio=False)

        self.type = TagInteiro(nome=u'type', raiz=u'//transaction/shipping', opcoes=CONST.SHIPPING.TYPE.opcoes.keys())

        self.address = Address()

    def get_xml(self):
        xml = XMLAPI.get_xml(self)
        xml += u'<shipping>'

        xml += self.cost.xml
        xml += self.type.xml
        xml += self.address.xml

        xml += u'</shipping>'
        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):
            self.cost.xml = arquivo
            self.type.xml = arquivo
            self.address.xml = arquivo

    xml = property(get_xml, set_xml)

    def get_alertas(self):
        alertas = []

        alertas.extend(self.cost.alertas)
        alertas.extend(self.type.alertas)
        alertas.extend(self.address.alertas)

        return alertas

    alertas = property(get_alertas)


class Phone(XMLAPI):
    def __init__(self):
        super(Phone, self).__init__()

        self.areaCode = TagInteiro(nome=u'areaCode', raiz=u'//transaction/sender/phone', tamanho_min=2, tamanho_max=2,
                                   obrigatorio=False)
        self.number = TagInteiro(nome=u'number', raiz=u'//transaction/sender/phone', tamanho_min=7, tamanho_max=9,
                                 obrigatorio=False)

    def get_xml(self):
        if not self.areaCode.valor and not self.number.valor:
            return u''

        xml = XMLAPI.get_xml(self)
        xml += u'<phone>'

        if self.areaCode.valor:
            xml += self.areaCode.xml

        if self.number.valor:
            xml += self.number.xml

        xml += u'</phone>'
        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):
            self.areaCode.xml = arquivo
            self.number.xml = arquivo

    xml = property(get_xml, set_xml)

    def get_alertas(self):
        alertas = []

        alertas.extend(self.areaCode.alertas)
        alertas.extend(self.number.alertas)

        return alertas

    alertas = property(get_alertas)


class Sender(XMLAPI):
    def __init__(self):
        super(Sender, self).__init__()

        self.email = TagCaracter(nome=u'email', raiz=u'//transaction/sender', tamanho_max=60)
        self.name = TagCaracter(nome=u'name', raiz=u'//transaction/sender', tamanho_max=50, obrigatorio=False)
        self.phone = Phone()

    def get_xml(self):
        xml = XMLAPI.get_xml(self)
        xml += u'<sender>'

        xml += self.email.xml
        xml += self.name.xml
        xml += self.phone.xml

        xml += u'</sender>'
        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):
            self.email.xml = arquivo
            self.name.xml = arquivo
            self.phone.xml = arquivo

    xml = property(get_xml, set_xml)

    def get_alertas(self):
        alertas = []

        alertas.extend(self.email.alertas)
        alertas.extend(self.name.alertas)
        alertas.extend(self.phone.alertas)

        return alertas

    alertas = property(get_alertas)


class PaymentMethod(XMLAPI):
    def __init__(self):
        super(PaymentMethod, self).__init__()

        self.type = TagInteiro(nome=u'type', raiz=u'//transaction/paymentMethod',
                               opcoes=CONST.PAYMENTMETHOD.TYPE.opcoes)
        self.code = TagInteiro(nome=u'code', raiz=u'//transaction/paymentMethod',
                               opcoes=CONST.PAYMENTMETHOD.CODE.opcoes)

    def get_xml(self):
        xml = XMLAPI.get_xml(self)
        xml += u'<paymentMethod>'

        xml += self.type.xml
        xml += self.code.xml

        xml += u'</paymentMethod>'
        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):
            self.type.xml = arquivo
            self.code.xml = arquivo

    xml = property(get_xml, set_xml)

    def get_alertas(self):
        alertas = []

        alertas.extend(self.type.alertas)
        alertas.extend(self.code.alertas)

        return alertas

    alertas = property(get_alertas)


class ClasseTransacaoDetalhes(XMLAPI):
    def __init__(self):
        super(ClasseTransacaoDetalhes, self).__init__()

        self.date = TagDataHoraUTC(nome=u'date', raiz=u'//transaction')
        self.lastEventDate = TagDataHoraUTC(nome=u'lastEventDate', raiz=u'//transaction')

        self.code = TagCaracter(nome=u'code', raiz=u'//transaction', tamanho_min=36, tamanho_max=36)
        self.reference = TagCaracter(nome=u'reference', raiz=u'//transaction', tamanho_max=200)
        self.type = TagInteiro(nome=u'type', raiz=u'//transaction', tamanho_max=2, opcoes=CONST.TYPE.opcoes.keys(),
                               valor=CONST.TYPE.PAGAMENTO)
        self.status = TagInteiro(nome=u'status', raiz=u'//transaction', tamanho_max=1,
                                 opcoes=CONST.STATUS.opcoes.keys())

        self.cancellationSource = TagCaracter(nome=u'cancellationSource', raiz=u'//transaction',
                                              opcoes=CONST.CANCELLATIONSOURCE.opcoes.keys(), obrigatorio=False)

        self.paymentMethod = PaymentMethod()

        # valor bruto
        self.grossAmount = TagDecimal(nome=u'grossAmount', raiz=u'//transaction', tamanho_max=10, decimal_digitos=2,
                                      valor=0)

        # valor do desconto dado
        self.discountAmount = TagDecimal(nome=u'discountAmount', raiz=u'//transaction', tamanho_max=10,
                                         decimal_digitos=2, valor=0)

        # valor total das Taxas Cobradas
        self.feeAmount = TagDecimal(nome=u'feeAmount', raiz=u'//transaction', tamanho_max=10, decimal_digitos=2,
                                    valor=0)

        # valor liquido da transacao
        self.netAmount = TagDecimal(nome=u'netAmount', raiz=u'//transaction', tamanho_max=10, decimal_digitos=2,
                                    valor=0)

        self.escrowEndDate = TagDataHoraUTC(nome=u'escrowEndDate', raiz=u'//transaction', obrigatorio=False)

        # valor extra - documentacao diz que é obrigatorio, mas no xml retornado nao veio
        self.extraAmount = TagDecimal(nome=u'extraAmount', raiz=u'//transaction', tamanho_max=10, decimal_digitos=2,
                                      valor=0, obrigatorio=False)

        # numero de parcelas
        self.installmentCount = TagInteiro(nome=u'installmentCount', raiz=u'//transaction')

        # numero de itens da transacao
        self.itemCount = TagInteiro(nome=u'itemCount', raiz=u'//transaction')

        self.items = []

        self.sender = Sender()
        self.shipping = Shipping()

    def get_xml(self):
        xml = XMLAPI.get_xml(self)
        xml += ABERTURA
        xml += u'<transaction>'

        xml += self.date.xml
        xml += self.lastEventDate.xml
        xml += self.code.xml
        xml += self.reference.xml
        xml += self.type.xml
        xml += self.status.xml

        if self.status.valor == CONST.STATUS.CANCELADA:
            xml += self.cancellationSource.xml

        xml += self.paymentMethod.xml
        xml += self.grossAmount.xml
        xml += self.discountAmount.xml
        xml += self.feeAmount.xml
        xml += self.netAmount.xml

        if self.status.valor in (
                CONST.STATUS.PAGA,
                CONST.STATUS.DISPONIVEL,
                CONST.STATUS.EM_DISPUTA,
                CONST.STATUS.DEVOLVIDA,
        ):
            xml += self.escrowEndDate.xml

        xml += self.extraAmount.xml
        xml += self.installmentCount.xml
        xml += self.creditorFees.xml
        xml += self.itemCount.xml

        xml += u'<items>'
        for item in self.items:
            xml += item.xml
        xml += u'</items>'

        xml += self.sender.xml
        xml += self.shipping.xml

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

            self.escrowEndDate.xml = arquivo

            self.extraAmount.xml = arquivo
            self.installmentCount.xml = arquivo
            self.creditorFees.xml = arquivo
            self.itemCount.xml = arquivo

            self.items = self.le_grupo(u'/transaction/items/item', Item)

            self.sender.xml = arquivo
            self.shipping.xml = arquivo

    xml = property(get_xml, set_xml)

    def get_alertas(self):
        alertas = []

        alertas.extend(self.date.alertas)
        alertas.extend(self.lastEventDate.alertas)
        alertas.extend(self.code.alertas)
        alertas.extend(self.reference.alertas)
        alertas.extend(self.type.alertas)
        alertas.extend(self.status.alertas)

        if self.status.valor == CONST.STATUS.CANCELADA:
            alertas.extend(self.cancellationSource.alertas)

        alertas.extend(self.paymentMethod.alertas)
        alertas.extend(self.grossAmount.alertas)
        alertas.extend(self.discountAmount.alertas)
        alertas.extend(self.feeAmount.alertas)
        alertas.extend(self.netAmount.alertas)

        if self.status.valor in (
                CONST.STATUS.PAGA,
                CONST.STATUS.DISPONIVEL,
                CONST.STATUS.EM_DISPUTA,
                CONST.STATUS.DEVOLVIDA,
        ):
            alertas.extend(self.escrowEndDate.alertas)

        alertas.extend(self.extraAmount.alertas)
        alertas.extend(self.installmentCount.alertas)
        alertas.extend(self.creditorFees.alertas)
        alertas.extend(self.itemCount.alertas)

        for item in self.items:
            alertas.extend(item.alertas)

        alertas.extend(self.sender.alertas)
        alertas.extend(self.shipping.alertas)

        return alertas

    alertas = property(get_alertas)
