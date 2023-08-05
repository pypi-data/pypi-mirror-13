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
    ABERTURA, TagCaracter, TagDataHoraUTC, XMLAPI
)
from ....core import CONST as CONST_BASE


class CONST(CONST_BASE):
    class STATUS(object):
        """
        Usado nas mensagens de RETORNO, vem embutido na tag 'status' com outros textos
        """
        PENDING = u'PENDING'
        ACTIVE = u'ACTIVE'
        CANCELLED = u'CANCELLED'
        CANCELLED_BY_RECEIVER = u'CANCELLED_BY_RECEIVER'
        CANCELLED_BY_SENDER = u'CANCELLED_BY_SENDER'
        EXPIRED = u'EXPIRED'
        OK = u'OK'
        opcoes = {
            PENDING: u'Assinatura pendente. Aguardando confimação pela operadora',
            ACTIVE: u'Assinatura paga e confirmada pela operadora',
            CANCELLED: u'Assinatura cancelada por não aprovação da PagSeguro u pela operadora',
            CANCELLED_BY_RECEIVER: u'Assinatura cancelada por solicitação do vendedor',
            CANCELLED_BY_SENDER: u'Assinatura cancelada por solicitação do comprador',
            EXPIRED: u'Assinatura expirou',
            OK: u'Assinatura cancelada',
        }


class ClasseCancelamentoAssinaturaRetorno(XMLAPI):
    def __init__(self):
        super(ClasseCancelamentoAssinaturaRetorno, self).__init__()

        self.date = TagDataHoraUTC(nome=u'date', raiz=u'//result')
        self.status = TagCaracter(nome=u'status', raiz=u'//result')

    def get_xml(self):
        xml = XMLAPI.get_xml(self)
        xml += ABERTURA
        xml += u'<result>'

        xml += self.date.xml
        xml += self.status.xml

        xml += u'</result>'
        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):
            self.date.xml = arquivo
            self.status.xml = arquivo

    xml = property(get_xml, set_xml)

    def get_alertas(self):
        alertas = []

        alertas.extend(self.date.alertas)
        alertas.extend(self.status.alertas)

        return alertas

    alertas = property(get_alertas)
