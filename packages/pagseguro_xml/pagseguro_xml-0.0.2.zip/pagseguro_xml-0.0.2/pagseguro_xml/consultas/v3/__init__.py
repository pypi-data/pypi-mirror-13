# coding=utf-8
# ---------------------------------------------------------------
# Desenvolvedor:    Arannã Sousa Santos
# Mês:              12
# Ano:              2015
# Projeto:          pagseguro_xml
# e-mail:           asousas@live.com
# ---------------------------------------------------------------

from .. import v2


class CONST(v2.CONST):

    URL_TRANSACAO_DETALHES_V3 = u'https://ws.{ambiente}pagseguro.uol.com.br/v3/transactions/{chave_transacao}?{parametros}'


class ApiPagSeguroConsulta(v2.ApiPagSeguroConsulta):

    def __init__(self, ambiente=CONST.AMBIENTE.SANDBOX):
        super(ApiPagSeguroConsulta, self).__init__(ambiente=ambiente)
        self.__url_transacao_detalhes_v3 = CONST.URL_TRANSACAO_DETALHES_V3

    def detalhes_v3(self, email, token, chave_transacao):

        from urllib import urlencode
        from classes import ClasseTransacaoDetalhes

        URL = self.__url_transacao_detalhes_v3.format(
            ambiente=CONST.AMBIENTE._resolve_[self.__ambiente],
            chave_transacao=chave_transacao,
            parametros=urlencode(dict(email=email, token=token))
        )

        # resposta pode conter a ClassXML de resposta ou uma mensagem de erro
        return self.__requisicao(URL, ClasseTransacaoDetalhes())
