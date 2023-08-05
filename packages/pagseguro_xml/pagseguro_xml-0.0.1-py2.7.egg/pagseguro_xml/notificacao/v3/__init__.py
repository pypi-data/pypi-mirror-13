# coding=utf-8
# ---------------------------------------------------------------
# Desenvolvedor:    Arannã Sousa Santos
# Mês:              12
# Ano:              2015
# Projeto:          pagseguro_xml
# e-mail:           asousas@live.com
# ---------------------------------------------------------------


class CONST(object):
    class AMBIENTE(object):
        SANDBOX = u'sandbox'
        PRODUCAO = u'producao'

        _resolve_ = {
            SANDBOX: u'sandbox.',
            PRODUCAO: u'',
        }

    URL_NOTIFICACAO_TRANSACAO_V3 = u'https://ws.{ambiente}pagseguro.uol.com.br/v3/transactions/notifications/' \
                                   u'{chave_notificacao}?{parametros}'


class ApiPagSeguroNotificacao(object):
    def __init__(self, ambiente=CONST.AMBIENTE.SANDBOX):
        assert ambiente in CONST.AMBIENTE._resolve_.keys(), \
            u'parametro "ambiente" deve conter um dos seguintes valores: [%s]' % u', '.join(
            CONST.AMBIENTE._resolve_.keys()
        )

        super(ApiPagSeguroNotificacao, self).__init__()

        from ...core import api_pagseguro_request

        self.__requisicao = api_pagseguro_request

        self.__ambiente = ambiente

        self.__url_transacao_notificacao_v3 = CONST.URL_NOTIFICACAO_TRANSACAO_V3

    def consulta_notificacao_transacao_v3(self, email, token, chave_notificacao):

        from .classes import ClasseNotificacaoTransacao
        from urllib import urlencode

        URL = self.__url_transacao_notificacao_v3.format(
            ambiente=CONST.AMBIENTE._resolve_[self.__ambiente],
            chave_notificacao=chave_notificacao,
            parametros=urlencode(dict(email=email, token=token)),
        )

        # resposta pode conter a ClassXML de resposta ou uma mensagem de erro
        return self.__requisicao(URL, ClasseNotificacaoTransacao())
