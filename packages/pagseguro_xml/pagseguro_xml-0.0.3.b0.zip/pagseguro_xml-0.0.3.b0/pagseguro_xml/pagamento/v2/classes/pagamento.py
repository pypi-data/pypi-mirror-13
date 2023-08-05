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
    ABERTURA, TagCaracter, TagDataHoraUTC, TagInteiro, TagDecimal, TagData,
    XMLAPI
)


class CONST(object):

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

        self.ID = TagCaracter(nome=u'id', raiz=u'//item', tamanho_max=100)
        self.description = TagCaracter(nome=u'description', raiz=u'//item', tamanho_max=100)

        # valor unitario do item
        self.amount = TagDecimal(nome=u'amount', raiz=u'//item', tamanho_max=10, decimal_digitos=2, valor=0)

        self.quantity = TagInteiro(nome=u'quantity', raiz=u'//item', tamanho_min=1, tamanho_max=999, valor=0)

        # custos de frete dos itens
        self.shippingCost = TagDecimal(nome=u'shippingCost', raiz=u'//item', tamanho_max=10, decimal_digitos=2,
                                       obrigatorio=False)
        # peso - em gramas
        self.weight = TagInteiro(nome=u'weight', raiz=u'//item', tamanho_max=30000, obrigatorio=False)

    def get_xml(self):
        xml = XMLAPI.get_xml(self)
        xml += u'<item>'

        xml += self.ID.xml
        xml += self.description.xml
        xml += self.amount.xml
        xml += self.quantity.xml

        xml += self.shippingCost.xml
        xml += self.weight.xml

        xml += u'</item>'
        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):
            self.ID.xml = arquivo
            self.description.xml = arquivo
            self.amount.xml = arquivo
            self.quantity.xml = arquivo
            self.shippingCost.xml = arquivo
            self.weight.xml = arquivo

    xml = property(get_xml, set_xml)

    def get_alertas(self):
        alertas = []

        alertas.extend(self.ID.alertas)
        alertas.extend(self.description.alertas)
        alertas.extend(self.amount.alertas)
        alertas.extend(self.quantity.alertas)
        alertas.extend(self.shippingCost.alertas)
        alertas.extend(self.weight.alertas)

        return alertas

    alertas = property(get_alertas)


class Document(XMLAPI):
    def __init__(self):
        super(Document, self).__init__()

        self.type = TagInteiro(nome=u'type', raiz=u'/document', opcoes=(u'CPF',), obrigatorio=False)
        self.value = TagInteiro(nome=u'value', raiz=u'/document', obrigatorio=False)

    def get_xml(self):
        if not (self.type.valor or self.value.valor):
            return u''

        xml = XMLAPI.get_xml(self)
        xml += u'<document>'

        xml += self.type.xml
        xml += self.value.xml

        xml += u'</document>'
        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):
            self.type.xml = arquivo
            self.value.xml = arquivo

    xml = property(get_xml, set_xml)

    def get_alertas(self):
        alertas = []

        alertas.extend(self.type.alertas)
        alertas.extend(self.value.alertas)

        return alertas

    alertas = property(get_alertas)


class Address(XMLAPI):
    def __init__(self):
        super(Address, self).__init__()

        self.country = TagCaracter(nome=u'country', raiz=u'//checkout/shipping/address', opcoes=(u'BRA',),
                                   valor=u'BRA', obrigatorio=False)
        # UF - somente duas letras
        self.state = TagCaracter(nome=u'state', raiz=u'//checkout/shipping/address', tamanho_min=2, tamanho_max=2,
                                 obrigatorio=False, valor=u'')
        self.city = TagCaracter(nome=u'city', raiz=u'//checkout/shipping/address', obrigatorio=False)
        self.postalCode = TagCaracter(nome=u'postalCode', raiz=u'//checkout/shipping/address', tamanho_min=8,
                                      tamanho_max=8, obrigatorio=False)
        # endereco do envio
        self.district = TagCaracter(nome=u'district', raiz=u'//checkout/shipping/address', tamanho_max=60,
                                    obrigatorio=False)
        self.street = TagCaracter(nome=u'street', raiz=u'//checkout/shipping/address', tamanho_max=80, obrigatorio=False)
        self.number = TagCaracter(nome=u'number', raiz=u'//checkout/shipping/address', tamanho_max=20, obrigatorio=False)
        self.complement = TagCaracter(nome=u'complement', raiz=u'//checkout/shipping/address', tamanho_max=40,
                                      obrigatorio=False)

    def get_xml(self):
        if not (self.country.valor or self.state.valor or self.city.valor or self.postalCode.valor or
                self.district.valor or self.street.valor or self.number.valor or self.complement.valor):
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
        self.cost = TagDecimal(nome=u'cost', raiz=u'//checkout/shipping', tamanho_max=10, decimal_digitos=2, valor=0,
                               obrigatorio=False)

        self.type = TagInteiro(nome=u'type', raiz=u'//checkout/shipping', opcoes=CONST.SHIPPING.TYPE.opcoes.keys(),
                               obrigatorio=False)

        self.address = Address()

    def get_xml(self):

        if not (self.cost.valor or self.type.valor or self.address.xml):
            return u''

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

        self.areaCode = TagInteiro(nome=u'areaCode', raiz=u'//checkout/sender/phone', tamanho_min=2, tamanho_max=2,
                                   obrigatorio=False)
        self.number = TagInteiro(nome=u'number', raiz=u'//checkout/sender/phone', tamanho_min=7, tamanho_max=9,
                                 obrigatorio=False)

    def get_xml(self):
        if not (self.areaCode.valor or self.number.valor):
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

        self.email = TagCaracter(nome=u'email', raiz=u'//checkout/sender', tamanho_max=60, obrigatorio=False)
        self.name = TagCaracter(nome=u'name', raiz=u'//checkout/sender', tamanho_max=50, obrigatorio=False)
        self.phone = Phone()

        self.documents = []

        self.bornDate = TagData(nome=u'bornDate', raiz=u'//checkout/sender', obrigatorio=False)

    def get_xml(self):
        xml = XMLAPI.get_xml(self)

        if not (self.email.valor or self.name.valor or self.phone.xml or self.documents or self.bornDate.valor):
            return u''

        xml += u'<sender>'

        xml += self.email.xml
        xml += self.name.xml
        xml += self.phone.xml

        if self.documents:
            xml += u'<documents>'
            for doc in self.documents:
                xml += doc.xml
            xml += u'<documents>'

        xml += self.bornDate.xml

        xml += u'</sender>'
        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):
            self.email.xml = arquivo
            self.name.xml = arquivo
            self.phone.xml = arquivo

            self.documents = self.le_grupo(u'//checkout/sender/documents/document', Document)

            self.bornDate.xml = arquivo

    xml = property(get_xml, set_xml)

    def get_alertas(self):
        alertas = []

        alertas.extend(self.email.alertas)
        alertas.extend(self.name.alertas)
        alertas.extend(self.phone.alertas)

        for doc in self.documents:
            alertas.extend(doc.alertas)

        alertas.extend(self.bornDate.alertas)

        return alertas

    alertas = property(get_alertas)


class Receiver(XMLAPI):
    def __init__(self):
        super(Receiver, self).__init__()

        self.email = TagCaracter(nome=u'email', raiz=u'//checkout/receiver', tamanho_max=60, obrigatorio=False)

    def get_xml(self):
        xml = XMLAPI.get_xml(self)

        if not self.email.valor:
            return u''

        xml += u'<receiver>'

        xml += self.email.xml

        xml += u'</receiver>'
        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):
            self.email.xml = arquivo

    xml = property(get_xml, set_xml)

    def get_alertas(self):
        alertas = []

        alertas.extend(self.email.alertas)

        return alertas

    alertas = property(get_alertas)


class ClassePagamentoCheckout(XMLAPI):
    def __init__(self):
        super(ClassePagamentoCheckout, self).__init__()
        
        self.receiver = Receiver()

        self.currency = TagCaracter(nome=u'currency', raiz=u'//checkout', valor=u'BRL')
        self.reference = TagCaracter(nome=u'reference', raiz=u'//checkout', tamanho_max=200, obrigatorio=False)

        self.extraAmount = TagDecimal(nome=u'extraAmount', raiz=u'//checkout', decimal_digitos=2, obrigatorio=False)
        self.redirectURL = TagCaracter(nome=u'redirectURL', raiz=u'//checkout', obrigatorio=False, tamanho_max=255)
        self.notificationURL = TagCaracter(nome=u'notificationURL', raiz=u'//checkout', obrigatorio=False,
                                           tamanho_max=255)

        # numero maximo de usos para o codigo
        self.maxUses = TagInteiro(nome=u'maxUses', raiz=u'//checkout', tamanho_max=999, obrigatorio=False)

        # prazo, em segundos, de validade do código de pagamento
        self.maxAge = TagInteiro(nome=u'maxAge', raiz=u'//checkout', tamanho_min=30, tamanho_max=999999999, obrigatorio=False)

        self.items = []

        self.sender = Sender()
        self.shipping = Shipping()

        # self.metadata = []

    def get_xml(self):
        xml = XMLAPI.get_xml(self)
        xml += ABERTURA
        xml += u'<checkout>'

        xml += self.receiver.xml

        xml += self.currency.xml
        xml += self.reference.xml
        xml += self.extraAmount.xml
        xml += self.redirectURL.xml
        xml += self.notificationURL.xml
        xml += self.maxUses.xml
        xml += self.maxAge.xml

        xml += u'<items>'
        for item in self.items:
            xml += item.xml
        xml += u'</items>'

        xml += self.sender.xml
        xml += self.shipping.xml

        # if self.metadata:
        #     xml += u'<metadata>'
        #     for metadata in self.metadata:
        #         xml += metadata.xml
        #     xml += u'</metadata>'

        xml += u'</checkout>'
        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):

            self.receiver.xml = arquivo

            self.currency.xml = arquivo
            self.reference.xml = arquivo
            self.extraAmount.xml = arquivo
            self.redirectURL.xml = arquivo
            self.notificationURL.xml = arquivo
            self.maxUses.xml = arquivo
            self.maxAge.xml = arquivo

            self.items = self.le_grupo(u'//checkout/items/item', Item)

            self.sender.xml = arquivo
            self.shipping.xml = arquivo

            # self.metadata = self.le_grupo(u'//checkout/metadata', Metadata)

    xml = property(get_xml, set_xml)

    def get_alertas(self):
        alertas = []

        alertas.extend(self.receiver.alertas)
        alertas.extend(self.currency.alertas)
        alertas.extend(self.reference.alertas)
        alertas.extend(self.extraAmount.alertas)
        alertas.extend(self.redirectURL.alertas)
        alertas.extend(self.notificationURL.alertas)
        alertas.extend(self.maxUses.alertas)
        alertas.extend(self.maxAge.alertas)

        for item in self.items:
            alertas.extend(item.alertas)

        alertas.extend(self.sender.alertas)
        alertas.extend(self.shipping.alertas)

        return alertas

    alertas = property(get_alertas)


class ClassePagamentoRetornoCheckout(XMLAPI):
    def __init__(self):
        super(ClassePagamentoRetornoCheckout, self).__init__()

        self.code = TagCaracter(nome=u'code', raiz=u'//checkout', tamanho_min=32, tamanho_max=32)
        self.date = TagDataHoraUTC(nome=u'date', raiz=u'//checkout')

    def get_xml(self):
        xml = XMLAPI.get_xml(self)
        xml += ABERTURA
        xml += u'<checkout>'

        xml += self.code.xml
        xml += self.date.xml

        xml += u'</checkout>'
        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):
            self.code.xml = arquivo
            self.date.xml = arquivo

    xml = property(get_xml, set_xml)

    def get_alertas(self):
        alertas = []

        alertas.extend(self.code.alertas)
        alertas.extend(self.date.alertas)

        return alertas

    alertas = property(get_alertas)
