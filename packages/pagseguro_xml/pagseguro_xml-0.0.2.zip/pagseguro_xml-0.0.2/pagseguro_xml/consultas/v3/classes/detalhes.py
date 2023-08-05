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

from ...v2.classes import detalhes as classe_v2


class CONST(object):
    class TYPE(classe_v2.CONST.TYPE):
        pass

    class STATUS(classe_v2.CONST.STATUS):
        pass

    class CANCELLATIONSOURCE(classe_v2.CONST.CANCELLATIONSOURCE):
        pass

    class PAYMENTMETHOD(classe_v2.CONST.PAYMENTMETHOD):
        pass

    class SHIPPING(classe_v2.CONST.SHIPPING):
        pass


class Item(classe_v2.Item):
    pass


class Address(classe_v2.Address):
    pass


class Shipping(classe_v2.Shipping):
    pass


class Phone(classe_v2.Phone):
    pass


class Sender(classe_v2.Sender):
    pass


class CreditorFees(XMLAPI):
    def __init__(self):
        super(CreditorFees, self).__init__()

        # taxa de parcelamento
        self.installmentFeeAmount = TagDecimal(nome=u'installmentFeeAmount', raiz=u'//transaction/creditorFees',
                                               tamanho_max=10, decimal_digitos=2, obrigatorio=False)
        # taxa de operacao
        self.operationalFeeAmount = TagDecimal(nome=u'operationalFeeAmount', raiz=u'//transaction/creditorFees',
                                               tamanho_max=10, decimal_digitos=2, obrigatorio=False)
        # tarifa de intermediacao
        self.intermediationRateAmount = TagDecimal(nome=u'intermediationRateAmount', raiz=u'//transaction/creditorFees',
                                                   tamanho_max=10, decimal_digitos=2, obrigatorio=False)
        # tarifa de intermediacao
        self.intermediationFeeAmount = TagDecimal(nome=u'intermediationFeeAmount', raiz=u'//transaction/creditorFees',
                                                  tamanho_max=10, decimal_digitos=2, obrigatorio=False)

    def get_xml(self):
        xml = XMLAPI.get_xml(self)
        xml += u'<creditorFees>'

        xml += self.installmentFeeAmount.xml
        xml += self.operationalFeeAmount.xml
        xml += self.intermediationRateAmount.xml
        xml += self.intermediationFeeAmount.xml

        xml += u'</creditorFees>'

        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):
            self.installmentFeeAmount.xml = arquivo
            self.operationalFeeAmount.xml = arquivo
            self.intermediationRateAmount.xml = arquivo
            self.intermediationFeeAmount.xml = arquivo

    xml = property(get_xml, set_xml)

    def get_alertas(self):
        alertas = []

        alertas.extend(self.installmentFeeAmount.alertas)
        alertas.extend(self.operationalFeeAmount.alertas)
        alertas.extend(self.intermediationRateAmount.alertas)
        alertas.extend(self.intermediationFeeAmount.alertas)

        return alertas

    alertas = property(get_alertas)


class PaymentMethod(classe_v2.PaymentMethod):
    pass


class ClasseTransacaoDetalhes(classe_v2.ClasseTransacaoDetalhes):
    def __init__(self):
        super(ClasseTransacaoDetalhes, self).__init__()

        # campo 'feeAmount' deixou de existir

        # dados dos custos cobrados (nao tenho ideia de como eh isso)
        self.creditorFees = CreditorFees()

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
