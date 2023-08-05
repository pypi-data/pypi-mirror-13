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
    class STATUS(object):
        INITIATED = u'INITIATED'
        PENDING = u'PENDING'
        ACTIVE = u'ACTIVE'
        CANCELLED = u'CANCELLED'
        CANCELLED_BY_RECEIVER = u'CANCELLED_BY_RECEIVER'
        CANCELLED_BY_SENDER = u'CANCELLED_BY_SENDER'
        EXPIRED = u'EXPIRED'
        opcoes = {
            INITIATED: u'Processo de assinatura iniciada',
            PENDING: u'Assinatura pendente. Aguardando confimação pela operadora',
            ACTIVE: u'Assinatura paga e confirmada pela operadora',
            CANCELLED: u'Assinatura cancelada por não aprovação da PagSeguro u pela operadora',
            CANCELLED_BY_RECEIVER: u'Assinatura cancelada por solicitação do vendedor',
            CANCELLED_BY_SENDER: u'Assinatura cancelada por solicitação do comprador',
            EXPIRED: u'Assinatura expirou',
        }

    class CHARGE(object):
        AUTO = u'auto'
        MANUAL = u'manual'
        opcoes = {
            AUTO: u'Cobrado automaticamente pela PagSeguro',
            MANUAL: u'Cobrado manualmente pele vendedor',
            u'AUTO': u'Cobrado automaticamente pela PagSeguro',
            u'MANUAL': u'Cobrado manualmente pele vendedor',
        }


class Address(XMLAPI):
    def __init__(self):
        super(Address, self).__init__()

        self.country = TagCaracter(nome=u'country', raiz=u'//preApproval/sender/address', opcoes=(u'BRA',),
                                   valor=u'BRA', obrigatorio=False)
        # UF - somente duas letras
        self.state = TagCaracter(nome=u'state', raiz=u'//preApproval/sender/address', tamanho_min=2, tamanho_max=2,
                                 obrigatorio=False)
        self.city = TagCaracter(nome=u'city', raiz=u'//preApproval/sender/address', obrigatorio=False,
                                tamanho_min=2, tamanho_max=60)
        self.postalCode = TagCaracter(nome=u'postalCode', raiz=u'//preApproval/sender/address', tamanho_min=8,
                                     tamanho_max=8, obrigatorio=False)
        # endereco do envio
        self.district = TagCaracter(nome=u'district', raiz=u'//preApproval/sender/address', obrigatorio=False,
                                    tamanho_max=60)
        self.street = TagCaracter(nome=u'street', raiz=u'//preApproval/sender/address', obrigatorio=False,
                                  tamanho_max=80)
        self.number = TagCaracter(nome=u'number', raiz=u'//preApproval/sender/address', obrigatorio=False,
                                  tamanho_max=20)
        self.complement = TagCaracter(nome=u'complement', raiz=u'//preApproval/sender/address',
                                      obrigatorio=False, tamanho_max=40)

    def get_xml(self):
        # como ao gerar a assinatura nao é obrigado a informar, entao tbm nao irei
        # retornar os dados se todos eles nao forem preenchidos
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

        self.areaCode = TagInteiro(nome=u'areaCode', raiz=u'//preApproval/sender/phone', tamanho_min=2, tamanho_max=2,
                                   obrigatorio=False)
        self.number = TagInteiro(nome=u'number', raiz=u'//preApproval/sender/phone', tamanho_min=7, tamanho_max=9,
                                 obrigatorio=False)

    def get_xml(self):
        if not self.areaCode.valor and not self.number.valor:
            return u''

        xml = XMLAPI.get_xml(self)
        xml += u'<phone>'

        xml += self.areaCode.xml
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

        self.name = TagCaracter(nome=u'name', raiz=u'//preApproval/sender', tamanho_max=50, obrigatorio=False)
        self.email = TagCaracter(nome=u'email', raiz=u'//preApproval/sender', tamanho_max=60, obrigatorio=False)
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


class ClasseConsultaAssinaturaResposta(XMLAPI):
    def __init__(self):
        super(ClasseConsultaAssinaturaResposta, self).__init__()

        self.name = TagCaracter(nome=u'name', raiz=u'//preApproval')
        self.code = TagCaracter(nome=u'code', raiz=u'//preApproval')
        self.date = TagDataHoraUTC(nome=u'date', raiz=u'//preApproval')
        self.tracker = TagCaracter(nome=u'tracker', raiz=u'//preApproval')
        self.status = TagCaracter(nome=u'status', raiz=u'//preApproval', opcoes=CONST.STATUS.opcoes.keys())
        self.reference = TagCaracter(nome=u'reference', raiz=u'//preApproval')
        self.lastEventDate = TagDataHoraUTC(nome=u'lastEventDate', raiz=u'//preApproval')
        self.charge = TagCaracter(nome=u'charge', raiz=u'//preApproval', opcoes=CONST.CHARGE.opcoes.keys())
        self.sender = Sender()

    def get_xml(self):
        xml = XMLAPI.get_xml(self)
        xml += ABERTURA
        xml += u'<preApproval>'

        xml += self.name.xml
        xml += self.code.xml
        xml += self.date.xml
        xml += self.tracker.xml
        xml += self.status.xml
        xml += self.reference.xml
        xml += self.lastEventDate.xml
        xml += self.charge.xml
        xml += self.sender.xml

        xml += u'</preApproval>'
        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):
            self.name.xml = arquivo
            self.code.xml = arquivo
            self.date.xml = arquivo
            self.tracker.xml = arquivo
            self.status.xml = arquivo
            self.reference.xml = arquivo
            self.lastEventDate.xml = arquivo
            self.charge.xml = arquivo
            self.sender.xml = arquivo

    xml = property(get_xml, set_xml)

    def get_alertas(self):
        alertas = []

        alertas.extend(self.name.alertas)
        alertas.extend(self.code.alertas)
        alertas.extend(self.date.alertas)
        alertas.extend(self.tracker.alertas)
        alertas.extend(self.status.alertas)
        alertas.extend(self.reference.alertas)
        alertas.extend(self.lastEventDate.alertas)
        alertas.extend(self.charge.alertas)
        alertas.extend(self.sender.alertas)

        return alertas

    alertas = property(get_alertas)


# ------------------------------------------------------------------------------------------------------


class PreApproval(XMLAPI):
    def __init__(self):
        super(PreApproval, self).__init__()

        self.name = TagCaracter(nome=u'name', raiz=u'//preApproval')
        self.code = TagCaracter(nome=u'code', raiz=u'//preApproval')
        self.date = TagDataHoraUTC(nome=u'date', raiz=u'//preApproval')
        self.tracker = TagCaracter(nome=u'tracker', raiz=u'//preApproval')
        self.status = TagCaracter(nome=u'status', raiz=u'//preApproval', opcoes=CONST.STATUS.opcoes.keys())
        self.reference = TagCaracter(nome=u'reference', raiz=u'//preApproval')
        self.lastEventDate = TagDataHoraUTC(nome=u'lastEventDate', raiz=u'//preApproval')
        self.charge = TagCaracter(nome=u'charge', raiz=u'//preApproval', opcoes=CONST.CHARGE.opcoes.keys())

    def get_xml(self):
        xml = XMLAPI.get_xml(self)
        xml += u'<preApproval>'

        xml += self.name.xml
        xml += self.code.xml
        xml += self.date.xml
        xml += self.tracker.xml
        xml += self.status.xml
        xml += self.reference.xml
        xml += self.lastEventDate.xml
        xml += self.charge.xml

        xml += u'</phone>'
        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):

            self.name.xml = arquivo
            self.code.xml = arquivo
            self.date.xml = arquivo
            self.tracker.xml = arquivo
            self.status.xml = arquivo
            self.reference.xml = arquivo
            self.lastEventDate.xml = arquivo
            self.charge.xml = arquivo

    xml = property(get_xml, set_xml)

    def get_alertas(self):
        alertas = []

        alertas.extend(self.name.alertas)
        alertas.extend(self.code.alertas)
        alertas.extend(self.date.alertas)
        alertas.extend(self.tracker.alertas)
        alertas.extend(self.status.alertas)
        alertas.extend(self.reference.alertas)
        alertas.extend(self.lastEventDate.alertas)
        alertas.extend(self.charge.alertas)

        return alertas

    alertas = property(get_alertas)


class ClasseConsultaAssinaturasResposta(XMLAPI):
    def __init__(self):
        super(ClasseConsultaAssinaturasResposta, self).__init__()

        self.resultsInThisPage = TagInteiro(nome=u'resultsInThisPage', raiz=u'//preApprovalSearchResult')
        self.currentPage = TagInteiro(nome=u'currentPage', raiz=u'//preApprovalSearchResult')
        self.totalPages = TagInteiro(nome=u'totalPages', raiz=u'//preApprovalSearchResult')
        self.date = TagDataHoraUTC(nome=u'date', raiz=u'//preApprovalSearchResult')
        self.preApprovals = []

    def get_xml(self):
        xml = XMLAPI.get_xml(self)
        xml += ABERTURA
        xml += u'<preApprovalSearchResult>'

        xml += self.resultsInThisPage.xml
        xml += self.currentPage.xml
        xml += self.totalPages.xml
        xml += self.date.xml

        for preApproval in self.preApprovals:
            xml += preApproval.xml

        xml += u'</preApprovalSearchResult>'
        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):
            self.resultsInThisPage.xml = arquivo
            self.currentPage.xml = arquivo
            self.totalPages.xml = arquivo
            self.date.xml = arquivo

            self.preApprovals = self.le_grupo(u'//preApprovalSearchResult/preApprovals/preApproval', PreApproval)

    xml = property(get_xml, set_xml)

    def get_alertas(self):
        alertas = []

        alertas.extend(self.resultsInThisPage.alertas)
        alertas.extend(self.currentPage.alertas)
        alertas.extend(self.totalPages.alertas)
        alertas.extend(self.date.alertas)

        for alerta in self.preApprovals:
            alertas.extend(alerta.alertas)

        return alertas

    alertas = property(get_alertas)

