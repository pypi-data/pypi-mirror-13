# coding=utf-8
# ---------------------------------------------------------------
# Desenvolvedor:    Arannã Sousa Santos
# Mês:              12
# Ano:              2015
# Projeto:          pagseguro_xml
# e-mail:           asousas@live.com
# ---------------------------------------------------------------

from __future__ import division, print_function, unicode_literals
from ....core.base_classes import ABERTURA, TagCaracter, XMLAPI
from ....core import CONST


class Error(XMLAPI):
    def __init__(self):
        super(Error, self).__init__()

        self.code = TagCaracter(nome=u'code', raiz=u'//error', opcoes=CONST.CODE.opcoes.keys())
        self.message = TagCaracter(nome=u'message', raiz=u'//error')

    def get_xml(self):
        xml = XMLAPI.get_xml(self)
        xml += u'<error>'

        xml += self.code.xml
        xml += self.message.xml

        xml += u'</error>'
        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):
            self.code.xml = arquivo
            self.message.xml = arquivo

    xml = property(get_xml, set_xml)

    def get_alertas(self):
        alertas = []

        alertas.extend(self.code.alertas)
        alertas.extend(self.message.alertas)

        return alertas

    alertas = property(get_alertas)


class ClasseAssinaturaErros(XMLAPI):
    def __init__(self):
        super(ClasseAssinaturaErros, self).__init__()

        self.errors = []

    def get_xml(self):
        xml = XMLAPI.get_xml(self)
        xml += ABERTURA
        xml += u'<errors>'

        for erro in self.errors:
            xml += erro.xml

        xml += u'</errors>'
        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):
            self.errors = self.le_grupo(u'//errors/error', Error)

    xml = property(get_xml, set_xml)

    def get_alertas(self):
        alertas = []

        for error in self.errors:
            alertas.extend(error.alertas)

        return alertas

    alertas = property(get_alertas)