# coding=utf-8
# ---------------------------------------------------------------
# Desenvolvedor:    Arannã Sousa Santos
# Mês:              12
# Ano:              2015
# Projeto:          pagseguro_xml
# e-mail:           asousas@live.com
# ---------------------------------------------------------------

import requests
# from urllib import urlencode # somente se o XML de envio for via 'GET'


def api_pagseguro_request(url, class_xml_receber, class_xml_enviar=None, erro={}):
    assert hasattr(class_xml_receber, u'xml'), u'"class_xml_receber" deve possui o atributo "xml".'

    import logging
    # urllib3
    logging.captureWarnings(True)

    logger = logging.getLogger(u'%s.%s' % (__package__, u'api_pagseguro_request'))

    logger.info(u'URL: %s' % url)

    content_type = u'application/x-www-form-urlencoded; charset=UTF-8'
    xml = None

    if hasattr(class_xml_enviar, u'xml'):
        xml = class_xml_enviar.xml.encode(u'utf-8')
        content_type = u'application/xml; charset=UTF-8;'

        logger.info(
            u'Classe XML para "enviar" encontrada. Mudando o "content_type" da requisicao para: "%s"' % content_type)
        logger.info(
            u'Classe XML para "enviar" encontrada. "%s"' % xml)

    not xml and logger.info(u'"content_type" definido: %s' % content_type)

    headers = {u'content-type': content_type}

    # nao sei ainda se houver o XML para enviar, se deve ir via POST ou GET mesmo
    # se for via GET, terei que usar o URL encode

    try:
        logger.debug(u'Iniciando requisicao...')

        if xml:
            resposta = requests.post(url, xml, headers=headers)

        else:
            resposta = requests.get(url, headers=headers)

        logger.debug(u'Requisicao completa com STATUS: %s' % resposta.status_code)

        # checa status
        if resposta.status_code == 200:
            logger.debug(u'Guardando reposta na classe XML: %s' % resposta.text)

            class_xml_receber.xml = resposta.text

            return True, class_xml_receber

        # no caso da API de ASSINATURA, o erro 400 pode ser tratado num XML
        if resposta.status_code == 400 and 400 in erro.keys():
            classe_xml_erro = erro[400]()
            classe_xml_erro.xml = resposta.text

            return False, classe_xml_erro

        return False, u'Erro na requisicao, STATUS recebido %s: %s' % (resposta.status_code, resposta.text)

    except requests.ConnectionError, e:
        logger.error(u'ConnectionError= %s' % e.message)

        return False, u'Erro na conexao: %s' % e.message

    except requests.HTTPError, e:
        logger.error(u'HTTPError = %s' % e.message)

        return False, u'Erro na requisicao: %s' % e.message

    except requests.Timeout, e:
        logger.error(u'Timeout = %s' % e.message)

        return False, u'Erro te tempo maximio: %s' % e.message

    except Exception, e:
        import traceback
        logger.error(u'generic exception: ' + traceback.format_exc())

        return False, u'Erro desconhecido:\n%s' % traceback.format_exc()


class CONST(object):
    class CODE(object):
        # erros gerais
        e10001 = u'10001'
        e10002 = u'10002'
        e10003 = u'10003'
        # especificos
        e11001 = u'11001'
        e11002 = u'11002'
        e11003 = u'11003'
        e11004 = u'11004'
        e11005 = u'11005'
        e11006 = u'11006'
        e11007 = u'11007'
        e11008 = u'11008'
        e11009 = u'11009'
        e11010 = u'11010'
        e11011 = u'11011'
        e11012 = u'11012'
        e11013 = u'11013'
        e11014 = u'11014'
        e11015 = u'11015'
        e11016 = u'11016'
        e11017 = u'11017'
        e11018 = u'11018'
        e11019 = u'11019'
        e11020 = u'11020'
        e11021 = u'11021'
        e11022 = u'11022'
        e11023 = u'11023'
        e11024 = u'11024'
        e11025 = u'11025'
        e11026 = u'11026'
        e11027 = u'11027'
        e11028 = u'11028'
        e11029 = u'11029'
        e11030 = u'11030'
        e11031 = u'11031'
        e11032 = u'11032'
        e11033 = u'11033'
        e11034 = u'11034'
        e11035 = u'11035'
        e11036 = u'11036'
        e11037 = u'11037'
        e11038 = u'11038'
        e11039 = u'11039'
        e11040 = u'11040'
        e11041 = u'11041'
        e11042 = u'11042'
        e11043 = u'11043'
        e11044 = u'11044'
        e11045 = u'11044'
        e11046 = u'11046'
        e11047 = u'11047'
        e11048 = u'11048'
        e11049 = u'11049'
        e11050 = u'11050'
        e11051 = u'11051'
        e11052 = u'11052'
        e11053 = u'11053'
        e11054 = u'11054'
        e11055 = u'11055'
        e11056 = u'11056'
        e11057 = u'11057'
        e11058 = u'11058'
        e11059 = u'11059'
        e11060 = u'11060'
        e11061 = u'11061'
        e11062 = u'11062'
        e11063 = u'11063'
        e11064 = u'11064'
        e11065 = u'11065'
        e11066 = u'11066'
        e11067 = u'11067'
        e11068 = u'11068'
        e11069 = u'11069'
        e11070 = u'11070'
        e11071 = u'11071'
        e11072 = u'11072'
        e11073 = u'11073'
        e11074 = u'11074'
        e11075 = u'11075'
        e11076 = u'11076'
        e11077 = u'11077'
        e11078 = u'11078'
        e11079 = u'11079'
        e11080 = u'11080'
        e11081 = u'11081'
        e11082 = u'11082'
        e11083 = u'11083'
        e11084 = u'11084'
        e11085 = u'11085'

        e11088 = u'11088'
        e11089 = u'11089'
        e11090 = u'11090'
        e11091 = u'11091'
        e11092 = u'11092'
        e11093 = u'11093'
        e11094 = u'11094'
        e11095 = u'11095'
        e11096 = u'11096'
        e11097 = u'11097'
        e11098 = u'11098'
        e11099 = u'11099'
        e11100 = u'11100'
        e11101 = u'11101'
        e11102 = u'11102'
        e11103 = u'11103'
        e11104 = u'11104'
        e11105 = u'11105'
        e11106 = u'11106'
        e11107 = u'11107'
        e11108 = u'11108'
        e11109 = u'11109'
        e11110 = u'11110'
        e11111 = u'11111'
        e11112 = u'11112'
        e11113 = u'11113'
        e11114 = u'11114'

        e11157 = u'11157'

        e13001 = u'13001'
        e13002 = u'13002'
        e13003 = u'13003'
        e13004 = u'13004'
        e13005 = u'13005'
        e13006 = u'13006'
        e13007 = u'13007'
        e13008 = u'13008'
        e13009 = u'13009'
        e13010 = u'13010'
        e13011 = u'13011'
        e13012 = u'13012'
        e13013 = u'13013'
        e13014 = u'13014'
        e13015 = u'13015'
        e13016 = u'13016'
        e13017 = u'13017'
        e13018 = u'13018'
        e13019 = u'13019'
        e13020 = u'13020'
        e13021 = u'13021'

        e17001 = u'17001'
        e17002 = u'17002'
        e17003 = u'17003'
        e17004 = u'17004'
        e17005 = u'17005'
        e17006 = u'17006'
        e17007 = u'17007'
        e17008 = u'17008'
        e17009 = u'17009'
        e17010 = u'17010'
        e17011 = u'17011'
        e17012 = u'17012'
        e17013 = u'17013'
        e17014 = u'17014'
        e17015 = u'17015'
        e17016 = u'17016'
        e17017 = u'17017'
        e17018 = u'17018'
        e17019 = u'17019'
        e17020 = u'17020'
        e17021 = u'17021'
        e17022 = u'17022'
        e17023 = u'17023'
        e17024 = u'17024'
        e17025 = u'17025'
        e17026 = u'17026'
        e17027 = u'17027'
        e17028 = u'17028'
        e17029 = u'17029'
        e17030 = u'17030'
        e17031 = u'17031'

        opcoes = {
            # gerais
            e10001: u'<email>O "e-mail" é obrigatório',
            e10002: u'<email>O "token" é obrigatório',
            e10003: u'<email>O "e-mail" é inválido',
            # especificos
            e11001: u'<receiverEmail>Campo "e-mail do recebedor" é obrigatório',
            e11002: u'<receiverEmail>Campo "e-mail do recebedor" possui tamanho inválido',
            e11003: u'<receiverEmail>Campo "e-mail do recebedor" possui valor inválido',
            e11004: u'<currency>Campo "moeda" é obrigatória',
            e11005: u'<currency>Campo "moeda" possui valor inválido',
            e11006: u'<redirectURL>Campo "redirectURL" possui tamanho inválido',
            e11007: u'<redirectURL>Campo "redirectURL" possui valor inválido',
            e11008: u'<reference>Campo "Referência" possui tamanho inválido',
            e11009: u'<senderEmail>Campo "e-mail do comprador" possui tamanho inválido',
            e11010: u'<senderEmail>Campo "e-mail do comprador" possui valor inválido',
            e11011: u'<senderName>Campo "nome do comprador" possui tamanho inválido',
            e11012: u'<senderName>Campo "nome do comprador" possui valor inválido',
            e11013: u'<senderAreaCode>Campo "o código de área do comprador" possui valor inválido',
            e11014: u'<senderPhone>Campo "telefone do comprador" possui tamanho inválido',
            e11015: u'<shippingType>Campo "tipo de remessa" é obrigatório',
            e11016: u'<shippingType>Campo "tipo de remessa" é inválido',
            e11017: u'<shippingPostalCode>Campo "código postal de remessa" possui valor inválido',
            e11018: u'<shippingAddressStreet>Campo "endereço da rua de remessa" possui tamanho inválido',
            e11019: u'<shippingAddressNumber>Campo "número do endereço de remessa" possui tamanho inválido',
            e11020: u'<shippingAddressComplement>Campo "complemento do endereço de remessa" possui tamanho inválido',
            e11021: u'<shippingAddressDistrict>Campo "distrito do endereço de remessa" possui tamanho inválido',
            e11022: u'<shippingAddressCity>Campo "cidade do endereço de remessa" possui tamanho inválido',
            e11023: u'<shippingAddressState>Campo "estado do endereço de remessa" possui tamanho inválido. Ex.: SP, TO',
            e11024: u'<items>Quantidade inválida de ítens',
            e11025: u'<item.ID>Campo "código ID do item" é obrigatório',
            e11026: u'<item.quantity>Campo "quantidade do item" é obrigatório',
            e11027: u'<item.quantity>Campo "quantidade do item" está fora dos limites',
            e11028: u'<item.amount>Campo "valor do item" é obrigatório',
            e11029: u'<item.amount>Campo "valor do item" está fora dos limites',
            e11030: u'<item.amount>Campo "valor do item" possui valor inválido',
            e11031: u'<item.shippingCost>Campo "custo de remessa do item" possui valor inválido',
            e11032: u'<item.shippingCost>Campo "custo de remessa do item" está fora dos limites',
            e11033: u'<item.description>Campo "descrição do item" é obrigatório',
            e11034: u'<item.description>Campo "descrição do item" possui tamanho inválido',
            e11035: u'<item.weight>Campo "peso do item" possui valor inválido',
            e11036: u'<item.extraAmount>Campo "valores extras do item" possui valor inválido',
            e11037: u'<item.extraAmount>Campo "valores extras do item" está fora dos limites',
            e11038: u'<receiver.email>Campo "email do recebedor" é inválido para checkout. Verifique o STATUS da conta do recebedor e se o mesmo é uma conta do tipo VENDEDOR',
            e11039: u'XML de requisição mal formado',
            e11040: u'<maxAge>Campo "prazo de validade" possui formato inválido',
            e11041: u'<maxAge>Campo "prazo de validade" está fora dos limites',
            e11042: u'<maxUses>Campo "número máximo de usos do código de pagamento" possui formato inválido',
            e11043: u'<maxUses>Campo "número máximo de usos do código de pagamento" está fora dos limites',

            e11044: u'<initialDate>Campo "data inicial" é obrigatório',
            e11045: u'<initialDate>Campo "data inicial" está abaixo do permitido',
            e11046: u'<initialDate>Campo "data inicial" não pode ser maior que 6 meses',
            e11047: u'<initialDate>Campo "data inicial" deve ser menor ou igual ao campo "data final"',
            e11048: u'<interval>Campo "intervalo de busca" está fora dos limites',
            e11049: u'<finalDate>Campo "data final" está fora dos limites',
            e11050: u'<initialDate>Campo "data inicial" possui formato inválido. Deve ser "AAAA-mm-ddTHH:MM" (exemplo 2010-01-31T17:25)',
            e11051: u'<finalDate>Campo "data final" possui formato inválido. Deve ser "AAAA-mm-ddTHH:MM" (exemplo 2010-01-31T17:25)',
            e11052: u'<page>Campo "página" possui valor inválido',
            e11053: u'<maxPageResults>Campo "resultados máximos por página" possui valor inválido. Deve ser entre 1 e 1000',
            e11054: u'<reviewURL>Campo "url de revisão" possui tamanho inválido',
            e11055: u'<reviewURL>Campo "url de revisão" possi valor inválido',
            e11056: u'',
            e11057: u'',
            e11058: u'',
            e11059: u'',
            e11060: u'',
            e11061: u'',
            e11062: u'',
            e11063: u'',
            e11064: u'',
            e11065: u'',
            e11066: u'',
            e11067: u'',
            e11068: u'',
            e11069: u'',
            e11070: u'',
            e11071: u'',
            e11072: u'',
            e11073: u'',
            e11074: u'',
            e11075: u'',
            e11076: u'',
            e11077: u'',
            e11078: u'',
            e11079: u'',
            e11080: u'',
            e11081: u'',
            e11082: u'',
            e11083: u'',
            e11084: u'',
            e11085: u'',
            e11088: u'',
            e11089: u'',
            e11090: u'',
            e11091: u'',
            e11092: u'',
            e11093: u'',
            e11094: u'',
            e11095: u'',
            e11096: u'',
            e11097: u'',
            e11098: u'',
            e11099: u'',
            e11100: u'',
            e11101: u'',
            e11102: u'',
            e11103: u'',
            e11104: u'',
            e11105: u'',
            e11106: u'',
            e11107: u'',
            e11108: u'',
            e11109: u'',
            e11110: u'',
            e11111: u'',
            e11112: u'',
            e11113: u'',
            e11114: u'',

            e11157: u'<senderCPF>O campo "CPF do remetente" é inválido',

            e13001: u'',
            e13002: u'',
            e13003: u'',
            e13004: u'',
            e13005: u'',
            e13006: u'',
            e13007: u'',
            e13008: u'',
            e13009: u'',
            e13010: u'',
            e13011: u'',
            e13012: u'',
            e13013: u'',
            e13014: u'',
            e13015: u'',
            e13016: u'',
            e13017: u'',
            e13018: u'',
            e13019: u'',
            e13020: u'',
            e13021: u'',

            e17001: u'',
            e17002: u'',
            e17003: u'',
            e17004: u'',
            e17005: u'',
            e17006: u'',
            e17007: u'',
            e17008: u'',
            e17009: u'',
            e17010: u'',
            e17011: u'',
            e17012: u'',
            e17013: u'',
            e17014: u'',
            e17015: u'',
            e17016: u'',
            e17017: u'',
            e17018: u'',
            e17019: u'',
            e17020: u'',
            e17021: u'',
            e17022: u'Status da pre-aprovação é inválido para executar a operação requisitada. Status atual é {1}',
            e17023: u'',
            e17024: u'',
            e17025: u'',
            e17026: u'',
            e17027: u'',
            e17028: u'',
            e17029: u'',
            e17030: u'',
            e17031: u'',
        }
