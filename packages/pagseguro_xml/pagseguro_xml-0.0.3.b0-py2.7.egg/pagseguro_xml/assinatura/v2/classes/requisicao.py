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
    class PREAPPROVAL(object):
        class CHARGE(object):
            AUTO = u'auto'
            MANUAL = u'manual'
            opcoes = {
                AUTO: u'Automático (PagSeguro gerencia)',
                MANUAL: u'Manual (Vendedor gerencia)',
            }

        class PERIOD(object):
            WEEKLY = u'WEEKLY'
            MONTHLY = u'MONTHLY'
            BIMONTHLY = u'BIMONTHLY'
            TRIMONTHLY = u'TRIMONTHLY'
            SEMIANNUALLY = u'SEMIANNUALLY'
            YEARLY = u'YEARLY'
            opcoes = {
                WEEKLY: u'Semanal',
                MONTHLY: u'Mensal',
                BIMONTHLY: u'Bimestral',
                TRIMONTHLY: u'Trimestral',
                SEMIANNUALLY: u'Semestral',
                YEARLY: u'Anual',
            }


class Address(XMLAPI):
    def __init__(self):
        super(Address, self).__init__()

        self.country = TagCaracter(nome=u'country', raiz=u'//preApprovalRequest/sender/address', opcoes=(u'BRA',),
                                   valor=u'BRA', obrigatorio=False)
        # UF - somente duas letras
        self.state = TagCaracter(nome=u'state', raiz=u'//preApprovalRequest/sender/address', tamanho_min=2, tamanho_max=2,
                                 obrigatorio=False)
        self.city = TagCaracter(nome=u'city', raiz=u'//preApprovalRequest/sender/address', obrigatorio=False,
                                tamanho_min=2, tamanho_max=60)
        self.postalCode = TagCaracter(nome=u'postalCode', raiz=u'//preApprovalRequest/sender/address', tamanho_min=8,
                                     tamanho_max=8, obrigatorio=False)
        # endereco do envio
        self.district = TagCaracter(nome=u'district', raiz=u'//preApprovalRequest/sender/address', obrigatorio=False,
                                    tamanho_max=60)
        self.street = TagCaracter(nome=u'street', raiz=u'//preApprovalRequest/sender/address', obrigatorio=False,
                                  tamanho_max=80)
        self.number = TagCaracter(nome=u'number', raiz=u'//preApprovalRequest/sender/address', obrigatorio=False,
                                  tamanho_max=20)
        self.complement = TagCaracter(nome=u'complement', raiz=u'//preApprovalRequest/sender/address',
                                      obrigatorio=False, tamanho_max=40)

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


class Phone(XMLAPI):
    def __init__(self):
        super(Phone, self).__init__()

        self.areaCode = TagInteiro(nome=u'areaCode', raiz=u'//preApprovalRequest/sender/phone', tamanho_min=2, tamanho_max=2,
                                   obrigatorio=False)
        self.number = TagInteiro(nome=u'number', raiz=u'//preApprovalRequest/sender/phone', tamanho_min=7, tamanho_max=9,
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

        self.name = TagCaracter(nome=u'name', raiz=u'//preApprovalRequest/sender', tamanho_max=50, obrigatorio=False)
        self.email = TagCaracter(nome=u'email', raiz=u'//preApprovalRequest/sender', tamanho_max=60, obrigatorio=False)
        self.phone = Phone()
        self.address = Address()

    def get_xml(self):
        xml = XMLAPI.get_xml(self)
        xml += u'<sender>'

        xml += self.email.xml
        xml += self.name.xml
        xml += self.phone.xml
        xml += self.address.xml

        xml += u'</sender>'
        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):
            self.email.xml = arquivo
            self.name.xml = arquivo
            self.phone.xml = arquivo
            self.address.xml = arquivo

    xml = property(get_xml, set_xml)

    def get_alertas(self):
        alertas = []

        alertas.extend(self.email.alertas)
        alertas.extend(self.name.alertas)
        alertas.extend(self.phone.alertas)
        alertas.extend(self.address.alertas)

        return alertas

    alertas = property(get_alertas)


class PreApproval(XMLAPI):
    def __init__(self):
        super(PreApproval, self).__init__()

        self.charge = TagCaracter(nome=u'charge', raiz=u'//preApprovalRequest/preApproval', obrigatorio=False,
                                  opcoes=CONST.PREAPPROVAL.CHARGE.opcoes.keys(), valor=CONST.PREAPPROVAL.CHARGE.AUTO)
        self.name = TagCaracter(nome=u'name', raiz=u'//preApprovalRequest/preApproval', tamanho_max=100)
        self.details = TagCaracter(nome=u'details', raiz=u'//preApprovalRequest/preApproval', obrigatorio=False,
                                                   tamanho_max=255)
        # valor exato por cada cobrança (obrigatorio para charge == auto)
        self.amountPerPayment = TagDecimal(nome=u'amountPerPayment', raiz=u'//preApprovalRequest/preApproval',
                                           tamanho_max=6, decimal_digitos=2, valor=0)
        # valor maximo de cada cobranca (somente sera usado se a tag anterior nao for usada)
        self.maxAmountPerPayment = TagDecimal(nome=u'maxAmountPerPayment', raiz=u'//preApprovalRequest/preApproval',
                                           tamanho_max=6, decimal_digitos=2, valor=0, obrigatorio=False)

        self.period = TagCaracter(nome=u'period', raiz=u'//preApprovalRequest/preApproval',
                                  opcoes=CONST.PREAPPROVAL.PERIOD.opcoes.keys())
        self.finalDate = TagDataHoraUTC(nome=u'finalDate', raiz=u'//preApprovalRequest/preApproval')

        # varlo maximo que pode ser cobrado durante a vigência da assinatura
        self.maxTotalAmount = TagDecimal(nome=u'maxTotalAmount', raiz=u'//preApprovalRequest/preApproval',
                                           tamanho_max=7, decimal_digitos=2)

    def get_xml(self):
        xml = XMLAPI.get_xml(self)
        xml += u'<preApproval>'

        xml += self.charge.xml
        xml += self.name.xml
        xml += self.details.xml

        # obrigatorio se CHARGE == auto
        if self.charge.valor == CONST.PREAPPROVAL.CHARGE.AUTO:
            xml += self.amountPerPayment.xml
        # nao podem ser usados em conjunto, ou 1 ou o outro
        elif not self.amountPerPayment.valor:
            xml += self.maxAmountPerPayment.xml

        xml += self.period.xml
        xml += self.finalDate.xml
        xml += self.maxTotalAmount.xml

        xml += u'</preApproval>'

        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):
            self.charge.xml = arquivo
            self.name.xml = arquivo
            self.details.xml = arquivo

            self.amountPerPayment.xml = arquivo
            self.maxAmountPerPayment.xml = arquivo

            self.period.xml = arquivo
            self.finalDate.xml = arquivo
            self.maxTotalAmount.xml = arquivo

    xml = property(get_xml, set_xml)

    def get_alertas(self):
        alertas = []

        alertas.extend(self.charge.alertas)
        alertas.extend(self.name.alertas)
        alertas.extend(self.details.alertas)

        # obrigatorio se CHARGE == auto
        if self.charge.valor == CONST.PREAPPROVAL.CHARGE.AUTO:
            alertas.extend(self.amountPerPayment.alertas)

        # nao podem ser usados em conjunto, ou 1 ou o outro
        elif not self.amountPerPayment.valor:
            alertas.extend(self.maxAmountPerPayment.alertas)

        alertas.extend(self.period.alertas)
        alertas.extend(self.finalDate.alertas)
        alertas.extend(self.maxTotalAmount.alertas)

        return alertas

    alertas = property(get_alertas)


class Receiver(XMLAPI):
    def __init__(self):
        super(Receiver, self).__init__()

        self.email = TagCaracter(nome=u'email', raiz=u'//preApprovalRequest/receiver', tamanho_max=60, obrigatorio=False)

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


class ClasseAssinaturaRequisicao(XMLAPI):
    def __init__(self):
        super(ClasseAssinaturaRequisicao, self).__init__()

        self.reviewURL = TagCaracter(nome=u'reviewURL', raiz=u'//preApprovalRequest', tamanho_max=255, obrigatorio=False)
        self.redirectURL = TagCaracter(nome=u'redirectURL', raiz=u'//preApprovalRequest', tamanho_max=255, obrigatorio=False)
        self.reference = TagCaracter(nome=u'reference', raiz=u'//preApprovalRequest', tamanho_max=200, obrigatorio=False)

        self.sender = Sender()
        self.preApproval = PreApproval()
        self.receiver = Receiver()

    def get_xml(self):
        xml = XMLAPI.get_xml(self)
        xml += ABERTURA
        xml += u'<preApprovalRequest>'

        xml += self.reviewURL.xml
        xml += self.redirectURL.xml
        xml += self.reference.xml
        xml += self.sender.xml
        xml += self.preApproval.xml
        xml += self.receiver.xml

        xml += u'</preApprovalRequest>'
        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):
            self.reviewURL.xml = arquivo
            self.redirectURL.xml = arquivo
            self.reference.xml = arquivo
            self.sender.xml = arquivo
            self.preApproval.xml = arquivo
            self.receiver.xml = arquivo

    xml = property(get_xml, set_xml)

    def get_alertas(self):
        alertas = []

        alertas.extend(self.reviewURL.alertas)
        alertas.extend(self.redirectURL.alertas)
        alertas.extend(self.reference.alertas)
        alertas.extend(self.sender.alertas)
        alertas.extend(self.preApproval.alertas)
        alertas.extend(self.receiver.alertas)

        return alertas

    alertas = property(get_alertas)


class ClasseAssinaturaResposta(XMLAPI):
    def __init__(self):
        super(ClasseAssinaturaResposta, self).__init__()

        self.code = TagCaracter(nome=u'code', raiz=u'//preApprovalRequest', tamanho_min=32, tamanho_max=32)
        self.date = TagDataHoraUTC(nome=u'date', raiz=u'//preApprovalRequest')

    def get_xml(self):
        xml = XMLAPI.get_xml(self)
        xml += ABERTURA
        xml += u'<preApprovalRequest>'

        xml += self.code.xml
        xml += self.date.xml

        xml += u'</preApprovalRequest>'
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

