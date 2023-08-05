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

    URL_ASSINATURA_REQUISICAO_V2 = u'https://ws.{ambiente}pagseguro.uol.com.br/v2/pre-approvals/' \
                                   u'request?{parametros}'
    URL_ASSINATURA_FLUXO_V2 = u'https://{ambiente}pagseguro.uol.com.br/v2/pre-approvals/' \
                              u'request.html?code={codigo_pagamento}'
    # SIMPLES
    URL_ASSINATURA_CONSULTA_NOTIFICACAO_V2 = u'https://ws.{ambiente}pagseguro.uol.com.br/v2/pre-approvals/' \
                                             u'notifications/{codigo_notificacao}?{parametros}'
    URL_ASSINATURA_CONSULTA_V2 = u'https://ws.{ambiente}pagseguro.uol.com.br/v2/pre-approvals/' \
                                 u'{codigo_assinatura}?{parametros}'
    # LISTA
    URL_ASSINATURA_CONSULTA_NOTIFICACAO_POR_DIAS_V2 = u'https://ws.{ambiente}pagseguro.uol.com.br/v2/pre-approvals/' \
                                                      u'notifications?{parametros}'
    URL_ASSINATURA_CONSULTA_POR_DATA_V2 = u'https://ws.{ambiente}pagseguro.uol.com.br/v2/pre-approvals?{parametros}'

    URL_ASSINATURA_CANCELA_V2 = u'https://ws.{ambiente}pagseguro.uol.com.br/v2/pre-approvals/cancel/' \
                                u'{codigo_assinatura}?{parametros}'


class ApiPagSeguroAssinatura(object):

    def __init__(self, ambiente=CONST.AMBIENTE.SANDBOX):
        assert ambiente in CONST.AMBIENTE._resolve_.keys(), \
            u'parametro "ambiente" deve conter um dos seguintes valores: [%s]' % u', '.join(
            CONST.AMBIENTE._resolve_.keys()
        )

        super(ApiPagSeguroAssinatura, self).__init__()

        from ...core import api_pagseguro_request

        self.__requisicao = api_pagseguro_request

        self.__ambiente = ambiente

        self.__url_assinatura_requisicao_v2 = CONST.URL_ASSINATURA_REQUISICAO_V2
        self.__url_assinatura_consulta_notificacao_v2 = CONST.URL_ASSINATURA_CONSULTA_NOTIFICACAO_V2
        self.__url_assinatura_consulta_v2 = CONST.URL_ASSINATURA_CONSULTA_V2
        self.__url_assinatura_consulta_notificacao_por_dias_v2 = CONST.URL_ASSINATURA_CONSULTA_NOTIFICACAO_POR_DIAS_V2
        self.__url_assinatura_consulta_por_data_v2 = CONST.URL_ASSINATURA_CONSULTA_POR_DATA_V2
        self.__url_assinatura_cancela_v2 = CONST.URL_ASSINATURA_CANCELA_V2

        self.__url_assinatura_fluxo_v2 = CONST.URL_ASSINATURA_FLUXO_V2

    def requisicao_assinatura_v2(self, email, token, xml_requisicao):

        from .classes import ClasseAssinaturaRequisicao, ClasseAssinaturaResposta, ClasseAssinaturaErros

        assert type(xml_requisicao) is ClasseAssinaturaRequisicao, u'O parâmetro "xml_requisicao" dese ser uma classe' \
                                                                   u' "ClasseAssinaturaRequisicao_v2"'

        from urllib import urlencode

        URL = self.__url_assinatura_requisicao_v2.format(
            ambiente=CONST.AMBIENTE._resolve_[self.__ambiente],
            parametros=urlencode(dict(email=email, token=token))
        )

        # resposta pode conter a ClassXML de resposta ou uma mensagem de erro
        return self.__requisicao(URL, ClasseAssinaturaResposta(), class_xml_enviar=xml_requisicao,
                                erro={400: ClasseAssinaturaErros})

    def consulta_assinatura_notificacao_v2(self, email, token, codigo_notificacao):

        from .classes import ClasseConsultaAssinaturaResposta
        from urllib import urlencode

        URL = self.__url_assinatura_consulta_notificacao_v2.format(
            ambiente=CONST.AMBIENTE._resolve_[self.__ambiente],
            codigo_notificacao=codigo_notificacao,
            parametros=urlencode(dict(email=email, token=token))
        )

        # resposta pode conter a ClassXML de resposta ou uma mensagem de erro
        return self.__requisicao(URL, ClasseConsultaAssinaturaResposta())

    def consulta_assinatura_v2(self, email, token, codigo_assinatura):

        from .classes import ClasseConsultaAssinaturaResposta
        from urllib import urlencode

        URL = self.__url_assinatura_consulta_v2.format(
            ambiente=CONST.AMBIENTE._resolve_[self.__ambiente],
            codigo_assinatura=codigo_assinatura,
            parametros=urlencode(dict(email=email, token=token))
        )

        # resposta pode conter a ClassXML de resposta ou uma mensagem de erro
        return self.__requisicao(URL, ClasseConsultaAssinaturaResposta())

    def consulta_notificacao_por_dias_v2(self, email, token, dias=30):

        parametros = {
            u'email': email,
            u'token': token,
            u'interval': dias,
        }

        from .classes import ClasseConsultaAssinaturasResposta, ClasseAssinaturaErros
        from urllib import urlencode

        URL = self.__url_assinatura_consulta_notificacao_por_dias_v2.format(
            ambiente=CONST.AMBIENTE._resolve_[self.__ambiente],
            parametros=urlencode(parametros)
        )

        # resposta pode conter a ClassXML de resposta ou uma mensagem de erro
        return self.__requisicao(URL, ClasseConsultaAssinaturasResposta(), erro={400: ClasseAssinaturaErros})

    def consulta_por_data_v2(self, email, token, initialDate, finalDate, pagina=1, resultadoMaximoPorPagina=5):

        assert hasattr(initialDate, u'strftime'), u'Parametro "initialDate" ' \
                                                  u'deve ser do tipo "datetime" ou possui um metodo chamado "strftime"!'

        assert hasattr(finalDate, u'strftime'), u'Parametro "finalDate" deve ser do tipo "datetime"!'

        from datetime import datetime, timedelta
        # --------------------------------------------------------------------------------------------------------------
        # regra numero 1    -   diferença inicial e a data de hoje nao pode ser maior que 6 meses
        #   (now() - initialDate) > 6 meses
        # --------------------------------------------------------------------------------------------------------------
        if (datetime.now() - initialDate) > timedelta(days=30 * 6):
            raise ValueError(u'Valor do "initialDate" > 6 meses')

        parametros = {
            u'initialDate': initialDate.strftime(u'%Y-%m-%dT00:00'),    # 2011-01-28T00:00
            u'finalDate': finalDate.strftime(u'%Y-%m-%dT00:00'),
            u'email': email,
            u'token': token,
            u'page': pagina,
            u'maxPageResults': resultadoMaximoPorPagina,
        }

        from .classes import ClasseConsultaAssinaturasResposta, ClasseAssinaturaErros
        from urllib import urlencode

        URL = self.__url_assinatura_consulta_por_data_v2.format(
            ambiente=CONST.AMBIENTE._resolve_[self.__ambiente],
            parametros=urlencode(parametros)
        )

        # resposta pode conter a ClassXML de resposta ou uma mensagem de erro
        return self.__requisicao(URL, ClasseConsultaAssinaturasResposta(), erro={400: ClasseAssinaturaErros})

    def cancela_v2(self, email, token, codigo_assinatura):

        parametros = {
            u'email': email,
            u'token': token,
        }

        from .classes import ClasseCancelamentoAssinaturaRetorno, ClasseAssinaturaErros
        from urllib import urlencode

        URL = self.__url_assinatura_cancela_v2.format(
            ambiente=CONST.AMBIENTE._resolve_[self.__ambiente],
            codigo_assinatura=codigo_assinatura,
            parametros=urlencode(parametros)
        )

        # resposta pode conter a ClassXML de resposta ou uma mensagem de erro
        return self.__requisicao(URL, ClasseCancelamentoAssinaturaRetorno(), erro={400: ClasseAssinaturaErros})

    def gera_url_fluxo_v2(self, codigo_pagamento):

        return self.__url_assinatura_fluxo_v2.format(
            ambiente=CONST.AMBIENTE._resolve_[self.__ambiente],
            codigo_pagamento=codigo_pagamento
        )