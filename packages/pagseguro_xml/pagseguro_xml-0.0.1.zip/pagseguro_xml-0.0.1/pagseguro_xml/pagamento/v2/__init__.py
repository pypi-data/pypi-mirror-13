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

    URL_PAGAMENTO_CHECKOUT_V2 = u'https://ws.{ambiente}pagseguro.uol.com.br/v2/checkout/?{parametros}'
    URL_PAGAMENTO_FLUXO_V2 = u'https://{ambiente}pagseguro.uol.com.br/v2/checkout/payment.html?code={codigo_pagamento}'


class ApiPagSeguroPagamento(object):
    def __init__(self, ambiente=CONST.AMBIENTE.SANDBOX):
        assert ambiente in CONST.AMBIENTE._resolve_.keys(), \
            u'parametro "ambiente" deve conter um dos seguintes valores: [%s]' % u', '.join(
            CONST.AMBIENTE._resolve_.keys()
        )

        super(ApiPagSeguroPagamento, self).__init__()

        from ...core import api_pagseguro_request

        self.__requisicao = api_pagseguro_request

        self.__ambiente = ambiente

        self.__url_pagamento_checkout_v2 = CONST.URL_PAGAMENTO_CHECKOUT_V2
        self.__url_pagamento_fluxo_v2 = CONST.URL_PAGAMENTO_FLUXO_V2


    def checkout_v2(self, email, token, checkout_class_xml):
        from .classes import ClassePagamentoErros, ClassePagamentoRetornoCheckout, ClassePagamentoCheckout
        from urllib import urlencode

        assert isinstance(checkout_class_xml, ClassePagamentoCheckout), \
            u'Necessário informar uma instância, de ClassePagamentoCheckout, para fazer checkout'

        URL = self.__url_pagamento_checkout_v2.format(
            ambiente=CONST.AMBIENTE._resolve_[self.__ambiente],
            parametros=urlencode(dict(email=email, token=token))
        )

        # resposta pode conter a ClassXML de resposta ou uma mensagem de erro
        return self.__requisicao(URL, ClassePagamentoRetornoCheckout(), class_xml_enviar=checkout_class_xml,
                                erro={400: ClassePagamentoErros})

    def gera_url_fluxo_v2(self, codigo_pagamento):

        return self.__url_pagamento_fluxo_v2.format(
            ambiente=CONST.AMBIENTE._resolve_[self.__ambiente],
            codigo_pagamento=codigo_pagamento
        )
