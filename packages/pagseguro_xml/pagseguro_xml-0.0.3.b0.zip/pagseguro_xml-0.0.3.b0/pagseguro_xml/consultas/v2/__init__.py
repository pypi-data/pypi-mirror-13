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

    URL_TRANSACAO_DETALHES_V2 = u'https://ws.{ambiente}pagseguro.uol.com.br/v2/transactions/{chave_transacao}?{parametros}'
    URL_TRANSACAO_HISTORICO_V2 = u'https://ws.{ambiente}pagseguro.uol.com.br/v2/transactions?{parametros}'
    URL_TRANSACAO_ABANDONADAS_V2 = u'https://ws.{ambiente}pagseguro.uol.com.br/v2/transactions/abandoned?{parametros}'


class ApiPagSeguroConsulta(object):

    def __init__(self, ambiente=CONST.AMBIENTE.SANDBOX):
        assert ambiente in CONST.AMBIENTE._resolve_.keys(), \
            u'parametro "ambiente" deve conter um dos seguintes valores: [%s]' % u', '.join(
            CONST.AMBIENTE._resolve_.keys()
        )

        super(ApiPagSeguroConsulta, self).__init__()

        from ...core import api_pagseguro_request

        self.__requisicao = api_pagseguro_request

        self.__ambiente = ambiente

        self.__url_transacao_detalhes_v2 = CONST.URL_TRANSACAO_DETALHES_V2
        self.__url_transacao_historico_v2 = CONST.URL_TRANSACAO_HISTORICO_V2
        self.__url_transacao_abandonadas_v2 = CONST.URL_TRANSACAO_ABANDONADAS_V2


    def detalhes_v2(self, email, token, chave_transacao):

        from .classes import ClasseTransacaoDetalhes

        raise NotImplementedError(u'Implementado apenas a versao 3')
    

    def historico_v2(self, email, token, initialDate, finalDate, page=None, maxPageResults=None):
        """

        :rtype: bool, ClasClasseTransacaoHistorico_v2
        """
        from datetime import datetime, timedelta

        assert hasattr(initialDate, u'strftime'), u'Parametro "initialDate" ' \
                                                  u'deve ser do tipo "datetime" ou possui um metodo chamado "strftime"!'

        assert hasattr(finalDate, u'strftime'), u'Parametro "finalDate" deve ser do tipo "datetime"!'

        # --------------------------------------------------------------------------------------------------------------
        # regra numero 1    -   diferença inicial e a data de hoje nao pode ser maior que 6 meses
        #   (now() - initialDate) > 6 meses
        # --------------------------------------------------------------------------------------------------------------
        if (datetime.now() - initialDate) > timedelta(days=30 * 6):
            raise ValueError(u'Valor do "initialDate" > 6 meses')

        # --------------------------------------------------------------------------------------------------------------
        # regra numero 2    -    diferença nao pode ser maior que 30 dias
        #   (finalDate - initialDate) > 30 dias
        # --------------------------------------------------------------------------------------------------------------
        if (finalDate - initialDate) > timedelta(days=30):
            raise ValueError(u'Valor de "finalDate - initialDate" > 30 dias')

        parametros = {
            u'initialDate': initialDate.strftime(u'%Y-%m-%dT%H:%M'),    # 2011-01-28T00:00
            u'finalDate': finalDate.strftime(u'%Y-%m-%dT%H:%M'),
            u'email': email,
            u'token': token,
        }

        if unicode(page).isdigit():
            parametros[u'page'] = page

        if unicode(maxPageResults).isdigit():
            parametros[u'maxPageResults'] = maxPageResults

        from urllib import urlencode
        from .classes import ClasseTransacaoHistorico

        URL = self.__url_transacao_historico_v2.format(ambiente=CONST.AMBIENTE._resolve_[self.__ambiente], parametros=urlencode(parametros))

        # resposta pode conter a ClassXML de resposta ou uma mensagem de erro
        return self.__requisicao(URL, ClasseTransacaoHistorico())

    def abandonadas_v2(self, email, token, initialDate, finalDate, page=None, maxPageResults=None):
        from datetime import datetime, timedelta

        assert hasattr(initialDate, u'strftime'), u'Parametro "initialDate" ' \
                                                  u'deve ser do tipo "datetime" ou possui um metodo chamado "strftime"!'

        assert hasattr(finalDate, u'strftime'), u'Parametro "finalDate" deve ser do tipo "datetime"!'

        # --------------------------------------------------------------------------------------------------------------
        # regra numero 1    -   diferença inicial e a data de hoje nao pode ser maior que 6 meses
        #   (now() - initialDate) > 6 meses
        # --------------------------------------------------------------------------------------------------------------
        if (datetime.now() - initialDate) > timedelta(days=30 * 6):
            raise ValueError(u'Valor do "initialDate" > 6 meses')

        # --------------------------------------------------------------------------------------------------------------
        # regra numero 2    -    diferença nao pode ser maior que 30 dias
        #   (finalDate - initialDate) > 30 dias
        # --------------------------------------------------------------------------------------------------------------
        if (finalDate - initialDate) > timedelta(days=30):
            raise ValueError(u'Valor de "finalDate - initialDate" > 30 dias')

        parametros = {
            u'initialDate': initialDate.strftime(u'%Y-%m-%dT%H:%M'),    # 2011-01-28T00:00
            u'finalDate': finalDate.strftime(u'%Y-%m-%dT%H:%M'),
            u'email': email,
            u'token': token,
        }

        if unicode(page).isdigit():
            parametros[u'page'] = page

        if unicode(maxPageResults).isdigit():
            parametros[u'maxPageResults'] = maxPageResults

        from .classes import ClasseTransacaoAbandonadas
        from urllib import urlencode

        URL = self.__url_transacao_abandonadas_v2.format(ambiente=CONST.AMBIENTE._resolve_[self.__ambiente], parametros=urlencode(parametros))

        # resposta pode conter a ClassXML de resposta ou uma mensagem de erro
        return self.__requisicao(URL, ClasseTransacaoAbandonadas())
