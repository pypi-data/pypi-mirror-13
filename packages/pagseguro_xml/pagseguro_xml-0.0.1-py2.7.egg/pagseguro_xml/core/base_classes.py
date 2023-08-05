# coding=utf-8
# ---------------------------------------------------------------
# Desenvolvedor:    Arannã Sousa Santos
# Mês:              12
# Ano:              2015
# Projeto:          pagseguro_xml
# e-mail:           asousas@live.com
#
# Baseado no projeto PYSPED
#
# ---------------------------------------------------------------
from __future__ import division, print_function, unicode_literals

import locale
import re
import pytz
import lxml.etree as etree
from datetime import datetime, date
from decimal import Decimal

ABERTURA = '<?xml version="1.0" encoding="utf-8"?>'


try:
    locale.setlocale(locale.LC_ALL, b'pt_BR.UTF-8')
    locale.setlocale(locale.LC_COLLATE, b'pt_BR.UTF-8')
except BaseException as e:
    locale.setlocale(locale.LC_ALL, b'')
    locale.setlocale(locale.LC_COLLATE, b'')


def tirar_acentos(texto):
    if not texto:
        return texto or ''

    texto = texto.replace('&', '&amp;')
    texto = texto.replace('<', '&lt;')
    texto = texto.replace('>', '&gt;')
    texto = texto.replace('"', '&quot;')
    texto = texto.replace("'", '&apos;')

    #
    # Trocar ENTER e TAB
    #
    texto = texto.replace('\t', ' ')
    # texto = texto.replace('\n', '| ')

    # Remove espaços seguidos
    # Nem pergunte...
    while '  ' in texto:
        texto = texto.replace('  ', ' ')

    return texto


def por_acentos(texto):
    if not texto:
        return texto

    texto = texto.replace('&#39;', "'")
    texto = texto.replace('&apos;', "'")
    texto = texto.replace('&quot;', '"')
    texto = texto.replace('&gt;', '>')
    texto = texto.replace('&lt;', '<')
    texto = texto.replace('&amp;', '&')
    texto = texto.replace('&APOS;', "'")
    texto = texto.replace('&QUOT;', '"')
    texto = texto.replace('&GT;', '>')
    texto = texto.replace('&LT;', '<')
    texto = texto.replace('&AMP;', '&')

    return texto


def tira_abertura(texto):
    # aberturas = (
    # '<?xml version="1.0" encoding="utf-8"?>',
    # '<?xml version="1.0" encoding="utf-8" ?>',
    # '<?xml version="1.0" encoding="utf-8" standalone="no"?>',
    # '<?xml version="1.0" encoding="utf-8" standalone="no" ?>',
    # '<?xml version="1.0" encoding="utf-8" standalone="yes"?>',
    # '<?xml version="1.0" encoding="utf-8" standalone="yes" ?>',

    # '<?xml version="1.0" encoding="UTF-8"?>',
    # '<?xml version="1.0" encoding="UTF-8" ?>',
    # '<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
    # '<?xml version="1.0" encoding="UTF-8" standalone="no" ?>',
    # '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
    # '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>',

    # "<?xml version='1.0' encoding='utf-8'?>",
    # "<?xml version='1.0' encoding='utf-8' ?>",
    # "<?xml version='1.0' encoding='utf-8' standalone='no'?>",
    # "<?xml version='1.0' encoding='utf-8' standalone='no' ?>",
    # "<?xml version='1.0' encoding='utf-8' standalone='yes'?>",
    # "<?xml version='1.0' encoding='utf-8' standalone='yes' ?>",

    # "<?xml version='1.0' encoding='UTF-8'?>",
    # "<?xml version='1.0' encoding='UTF-8' ?>",
    # "<?xml version='1.0' encoding='UTF-8' standalone='no'?>",
    # "<?xml version='1.0' encoding='UTF-8' standalone='no' ?>",
    # "<?xml version='1.0' encoding='UTF-8' standalone='yes'?>",
    # "<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>",
    # )

    # for a in aberturas:
    # texto = texto.replace(a,  '')

    if '?>' in texto:
        texto = texto.split('?>')[1:]
        texto = ''.join(texto)

    return texto


class NohXML(object):
    def __init__(self, *args, **kwargs):
        self._xml = None

    # self.alertas = []

    def _le_xml(self, arquivo):
        if arquivo is None:
            return False

        parser = etree.XMLParser(strip_cdata=False)

        if not isinstance(arquivo, basestring):
            arquivo = etree.tounicode(arquivo)
            # self._xml = arquivo
            # return True

            # elif arquivo is not None:
        if arquivo is not None:
            if isinstance(arquivo, basestring):
                if isinstance(arquivo, str):
                    arquivo = unicode(arquivo.encode('utf-8'))

                if '<' in arquivo:
                    self._xml = etree.fromstring(tira_abertura(arquivo).encode('utf-8'), parser=parser)
                else:
                    arq = open(arquivo)
                    txt = b''.join(arq.readlines())
                    txt = unicode(txt.decode('utf-8'))
                    txt = tira_abertura(txt)
                    arq.close()
                    self._xml = etree.fromstring(txt, parser=parser)
            else:
                self._xml = etree.parse(arquivo, parser=parser)
            return True

        return False

    def _preenche_namespace(self, tag, sigla_ns):
        if sigla_ns != '':
            sigla_sig = sigla_ns + ':sig'
            sigla_ns = '/' + sigla_ns + ':'
            tag = sigla_ns.join(tag.split('/')).replace(sigla_ns + sigla_ns, '/' + sigla_ns).replace(sigla_sig, 'sig')

        return tag

    def _le_nohs(self, tag, ns=None, sigla_ns=''):
        #
        # Tenta ler a tag sem os namespaces
        # Necessário para ler corretamente as tags de grupo reenraizadas
        #
        try:
            nohs = self._xml.xpath(tag)
            if len(nohs) >= 1:
                return nohs
        except:
            pass

        #
        # Não deu certo, tem que botar mesmo os namespaces
        #
        namespaces = {}

        if ns is not None:
            namespaces['res'] = ns

        if not tag.startswith('//*/res'):
            tag = self._preenche_namespace(tag, sigla_ns)

        nohs = self._xml.xpath(tag, namespaces=namespaces)

        if len(nohs) >= 1:
            return nohs

        return None

    def _le_noh(self, tag, ns=None, ocorrencia=1):
        nohs = self._le_nohs(tag, ns)

        if (nohs is not None) and (len(nohs) >= ocorrencia):
            return nohs[ocorrencia - 1]
        else:
            return None

    def _le_tag(self, tag, propriedade=None, ns=None, ocorrencia=1):
        noh = self._le_noh(tag, ns, ocorrencia)

        if noh is None:
            valor = ''
        else:
            if propriedade is None:
                valor = noh.text
            elif (noh.attrib is not None) and (len(noh.attrib) > 0):
                valor = noh.attrib.get(propriedade, u'')
            else:
                valor = ''

        return valor


class ErroObrigatorio(Exception):
    def __init__(self, raiz, nome, propriedade):
        if propriedade:
            self.value = u'%(raiz)s No campo "%(nome)s", a propriedade "%(propriedade)s" é de envio obrigatório, mas não foi preenchida.' % {
                u'nome': nome,
                u'propriedade': propriedade,
                u'raiz': raiz,
            }
        else:
            self.value = u'%(raiz)s O campo "%(nome)s" é de envio obrigatório, mas não foi preenchido.' % {
                u'nome': nome,
                u'raiz': raiz,
            }

    def __str__(self):
        return repr(self.value)

    def __unicode__(self):
        return self.value


class TamanhoInvalido(Exception):
    def __init__(self, raiz, nome, valor, tam_min=None, tam_max=None, dec_min=None, dec_max=None):
        if tam_min:
            self.value = u'%(raiz)s O campo "%(nome)s", deve ter o tamanho mínimo de %(tam_min)s, mas o tamanho enviado foi %(tam_env)s: %(valor)s' % {
                u'nome': nome,
                u'tam_min': unicode(tam_min),
                u'tam_env': unicode(len(unicode(valor))),
                u'valor': unicode(valor),
                u'raiz': raiz,
            }
        elif tam_max:
            self.value = u'%(raiz)s O campo "%(nome)s", deve ter o tamanho máximo de %(tam_max)s, mas o tamanho enviado foi %(tam_env)s: %(valor)s' % {
                u'nome': nome,
                u'tam_max': unicode(tam_max),
                u'tam_env': unicode(len(unicode(valor))),
                u'valor': unicode(valor),
                u'raiz': raiz,
            }

        if dec_min:
            self.value = u'%(raiz)s O campo "%(nome)s", deve ter o tamanho mínimo de %(dec_min)s casa(s) decimal(is): %(valor)s' % {
                u'nome': nome,
                u'dec_min': unicode(dec_min),
                u'valor': unicode(valor),
                u'raiz': raiz,
            }
        elif dec_max:
            self.value = u'%(raiz)s O campo "%(nome)s", deve ter o tamanho máximo de %(dec_max)s casa(s) decimal(is): %(valor)s' % {
                u'nome': nome,
                u'dec_max': unicode(dec_max),
                u'valor': unicode(valor),
                u'raiz': raiz,
            }

    def __str__(self):
        return repr(self.value)

    def __unicode__(self):
        return self.value


class OpcaoInvalida(Exception):
    def __init__(self, raiz, nome, propriedade, opcoes, valor):

        opcoes = [unicode(o) for o in opcoes]

        opcoes = u', '.join(opcoes)

        if propriedade:
            self.value = u'%(raiz)s No campo "%(nome)s", a propriedade "%(propriedade)s" possui valor inválido "%(valor)s", as opções sao: "%(opcoes)s".' % {
                u'nome': nome,
                u'propriedade': propriedade,
                u'raiz': raiz,
                u'opcoes': opcoes,
                u'valor': valor,
            }
        else:
            self.value = u'%(raiz)s O campo "%(nome)s" possui valor inválido "%(valor)s", as opções sao: "%(opcoes)s".' % {
                u'nome': nome,
                u'raiz': raiz,
                u'opcoes': opcoes,
                u'valor': valor,
            }

    def __str__(self):
        return repr(self.value)

    def __unicode__(self):
        return self.value


class TagCaracter(NohXML):
    def __init__(self, nome=u'', valor=None, tamanho_min=None, tamanho_max=None, placehold=None,
                 opcoes=None,
                 propriedade=None, namespace=None, namespace_obrigatorio=True, alertas=[],
                 raiz=None, obrigatorio=True, *args, **kwargs):
        super(TagCaracter, self).__init__(*args, **kwargs)

        self.nome = nome
        self._valor_string = ''
        self.obrigatorio = obrigatorio
        self.tamanho_min = tamanho_min
        self.tamanho_max = tamanho_max
        self.placehold = placehold
        self.opcoes = opcoes
        self.propriedade = propriedade
        self.namespace = namespace
        self.namespace_obrigatorio = namespace_obrigatorio
        self.alertas = alertas
        self.raiz = raiz
        self.valor = valor

        # Codigo para dinamizar a criacao de instancias de entidade,
        # aplicando os valores dos atributos na instanciacao
        for k, v in kwargs.items():
            setattr(self, k, v)

        if kwargs.has_key('valor'):
            self.valor = kwargs['valor']

    def _testa_opcoes(self, valor):
        if (valor or self.obrigatorio) and self.opcoes and not valor in self.opcoes:
            return OpcaoInvalida(self.raiz, self.nome, self.propriedade, self.opcoes, valor)

    def _testa_obrigatorio(self, valor):
        if self.obrigatorio and (not valor):
            return ErroObrigatorio(self.raiz, self.nome, self.propriedade)

    def _testa_tamanho_minimo(self, valor):
        if self.tamanho_min and (len(unicode(valor)) < self.tamanho_min) and self.obrigatorio:
            return TamanhoInvalido(self.raiz, self.nome, valor, tam_min=self.tamanho_min)

    def _testa_tamanho_maximo(self, valor):
        if self.tamanho_max and len(unicode(valor)) > self.tamanho_max:
            return TamanhoInvalido(self.raiz, self.nome, valor, tam_max=self.tamanho_max)

    def _valida(self, valor):
        self.alertas = []

        if self._testa_obrigatorio(valor):
            self.alertas.append(self._testa_obrigatorio(valor))

        if self._testa_tamanho_minimo(valor):
            self.alertas.append(self._testa_tamanho_minimo(valor))

        if self._testa_tamanho_maximo(valor):
            self.alertas.append(self._testa_tamanho_maximo(valor))

        if self._testa_opcoes(valor):
            self.alertas.append(self._testa_opcoes(valor))

        return self.alertas == []

    def set_valor(self, novo_valor):
        if novo_valor is not None:
            #
            # É obrigatório remover os espaços no início e no final do valor
            #
            novo_valor = novo_valor.strip()

        if self._valida(novo_valor):
            self._valor_string = unicode(tirar_acentos(novo_valor))
        else:
            self._valor_string = ''

    def get_valor(self):
        return unicode(por_acentos(self._valor_string))

    valor = property(get_valor, set_valor)

    def __unicode__(self):
        texto = u''
        if (not self.obrigatorio) and (not self.valor):
            return texto
        else:
            if self.propriedade:
                return u' %s="%s"' % (self.propriedade, self._valor_string)

            texto = u'<%s' % self.nome

            if self.valor or (self.placehold and self.tamanho_max):
                texto += u'>%s</%s>' % (self._valor_string, self.nome)
            else:
                texto += u' />'
        return texto

    def __repr__(self):
        return self.__unicode__()

    def get_xml(self):
        return self.__unicode__()

    def set_xml(self, arquivo, ocorrencia=1):
        if self._le_xml(arquivo):
            self._alertas = []
            self.valor = self._le_tag(self.raiz + '/' + self.nome, propriedade=self.propriedade, ns=self.namespace,
                                      ocorrencia=ocorrencia)

    xml = property(get_xml, set_xml)

    def get_text(self):
        if self.propriedade:
            return '%s_%s=%s' % (self.nome, self.propriedade, self._valor_string)
        else:
            return '%s=%s' % (self.nome, self._valor_string)

    text = property(get_text)

    def get_txt(self):
        if self.obrigatorio:
            return self._valor_string

        if self.valor:
            return self._valor_string

        return ''

    txt = property(get_txt)


class TagBoolean(TagCaracter):
    def __init__(self, **kwargs):

        if not kwargs.has_key(u'opcoes'):
            kwargs[u'opcoes'] = (True, False)

        super(TagBoolean, self).__init__(**kwargs)
        self._valor_boolean = None
        # Codigo para dinamizar a criacao de instancias de entidade,
        # aplicando os valores dos atributos na instanciacao
        for k, v in kwargs.items():
            setattr(self, k, v)

        if kwargs.has_key('valor'):
            self.valor = kwargs['valor']

    def _testa_obrigatorio(self, valor):
        # No caso da tag booleana, False deve ser tratado como preenchido
        if self.obrigatorio and (valor not in self.opcoes):
            return ErroObrigatorio(self.raiz, self.nome, self.propriedade)

    def _valida(self, valor):
        self.alertas = []

        if self._testa_obrigatorio(valor):
            self.alertas.append(self._testa_obrigatorio(valor))

        if self._testa_opcoes(valor):
            self.alertas.append(self._testa_opcoes(valor))

        return self.alertas == []

    def set_valor(self, novo_valor):
        if isinstance(novo_valor, basestring):
            if novo_valor.lower() == 'true':
                novo_valor = True
            elif novo_valor.lower() == 'false':
                novo_valor = False

        if self._valida(novo_valor) and isinstance(novo_valor, bool):
            self._valor_boolean = novo_valor

            if novo_valor == None:
                self._valor_string = ''
            elif novo_valor:
                self._valor_string = 'true'
            else:
                self._valor_string = 'false'
        else:
            self._valor_boolean = None
            self._valor_string = ''

    def get_valor(self):
        return self._valor_boolean

    valor = property(get_valor, set_valor)

    def __unicode__(self):
        if (not self.obrigatorio) and (self.valor == None):
            texto = ''
        else:
            if self.propriedade:
                return u' %s="%s"' % (self.propriedade, self._valor_string)

            texto = '<%s' % self.nome

            if self.namespace:
                texto += ' xmlns="%s"' % self.namespace

            elif not self.valor == None:
                texto += '>%s</%s>' % (self._valor_string, self.nome)
            else:
                texto += ' />'

        return texto


class TagInteiro(TagCaracter):
    def __init__(self, **kwargs):
        super(TagInteiro, self).__init__(**kwargs)
        self._valor_inteiro = 0
        self._valor_string = '0'

        # Codigo para dinamizar a criacao de instancias de entidade,
        # aplicando os valores dos atributos na instanciacao
        for k, v in kwargs.items():
            setattr(self, k, v)

        if kwargs.has_key('valor'):
            self.valor = kwargs['valor']

    def set_valor(self, novo_valor):
        if isinstance(novo_valor, basestring):
            if novo_valor:
                novo_valor = int(novo_valor)
            else:
                novo_valor = 0

        if isinstance(novo_valor, (int, long)) and self._valida(novo_valor):
            self._valor_inteiro = novo_valor
            self._valor_string = unicode(self._valor_inteiro)

            if self.placehold and self.tamanho_max and (len(self._valor_string) < self.tamanho_max):
                self._valor_string = self._valor_string.rjust(self.tamanho_max, '0')

        else:
            self._valor_inteiro = 0
            self._valor_string = '0'

    def get_valor(self):
        return self._valor_inteiro

    valor = property(get_valor, set_valor)

    def _valida(self, valor):
        """
        É separado pois o intero só nao tem valor se for '' ou None
        :param valor:
        :return:
        """
        self.alertas = []

        # converte para string antes de passar nos validador

        if self._testa_obrigatorio(unicode(valor)):
            self.alertas.append(self._testa_obrigatorio(unicode(valor)))

        if self._testa_tamanho_minimo(valor):
            self.alertas.append(self._testa_tamanho_minimo(valor))

        if self._testa_tamanho_maximo(valor):
            self.alertas.append(self._testa_tamanho_maximo(valor))

        if self._testa_opcoes(valor):
            self.alertas.append(self._testa_opcoes(valor))

        return self.alertas == []

    def __unicode__(self):
        texto = u''
        if (not self.obrigatorio) and (not self.valor):
            return texto
        else:
            if self.propriedade:
                return u' %s="%s"' % (self.propriedade, self._valor_string)

            texto = u'<%s' % self.nome

            if unicode(self.valor).isdigit() or (self.placehold and self.tamanho_max):
                texto += u'>%s</%s>' % (self._valor_string, self.nome)
            else:
                texto += u' />'
        return texto


class TagDecimal(TagCaracter):
    def __init__(self, *args, **kwargs):

        self.decimal_digitos = kwargs.pop(u'decimal_digitos', 0)

        super(TagDecimal, self).__init__(*args, **kwargs)

        self._valor_decimal = Decimal('0.0')
        self._valor_string = self._formata(self._valor_decimal)

        # Codigo para dinamizar a criacao de instancias de entidade,
        # aplicando os valores dos atributos na instanciacao
        for k, v in kwargs.items():
            setattr(self, k, v)

    def _parte_inteira(self, valor=None):
        if valor is None:
            valor = self._valor_decimal

        valor = unicode(valor).strip()

        if '.' in valor:
            valor = valor.split('.')[0]

        return valor

    def _parte_decimal(self, valor=None):
        if valor is None:
            valor = self._valor_decimal

        valor = unicode(valor).strip()

        if '.' in valor:
            valor = valor.split('.')[1]
        else:
            valor = ''

        return valor

    def _formata(self, valor):
        texto = self._parte_inteira(valor)

        dec = self._parte_decimal(valor)
        if not dec:
            dec = '0'

        # Tamanho mínimo das casas decimais
        if self.decimal_digitos and (len(dec) < self.decimal_digitos):
            dec = dec.ljust(self.decimal_digitos, '0')

        texto += '.' + dec
        return texto

    # def _testa_decimais_minimo(self, decimal):
    #     if self.tamanho_min:
    #         raise TamanhoInvalido(self.raiz, self.nome, decimal, dec_min=self.tamanho_min)

    def _testa_decimais_maximo(self, decimal):
        if self.decimal_digitos and (len(unicode(decimal)) > self.decimal_digitos):
            raise TamanhoInvalido(self.raiz, self.nome, decimal, dec_max=self.tamanho_max)

    def _testa_obrigatorio(self, valor):
        # valor 0.0 é preenchido mas no 'char' diz que nao é nenhum valor
        if self.obrigatorio and (not valor and valor != Decimal(u'0.0')):
            return ErroObrigatorio(self.raiz, self.nome, self.propriedade)

    def _valida(self, valor):
        self.alertas = []

        if self._testa_obrigatorio(valor):
            self.alertas.append(self._testa_obrigatorio(valor))

        inteiro = self._parte_inteira(valor)
        decimal = self._parte_decimal(valor)

        if self._testa_tamanho_minimo(inteiro):
            self.alertas.append(self._testa_tamanho_minimo(inteiro))

        if self._testa_tamanho_maximo(inteiro):
            self.alertas.append(self._testa_tamanho_maximo(inteiro))

        #
        # Analisando as exp.reg. de validação das tags com decimais,
        # parece haver um número máximo de casas decimais, mas as tags
        # podem ser enviadas sem nenhuma casa decimal, então, não
        # há um mínimo de casas decimais
        #
        # if self._testa_decimais_minimo(decimal):
        #    self.alertas.append(self._testa_decimais_minimo(decimal))

        if self._testa_decimais_maximo(decimal):
            self.alertas.append(self._testa_decimais_maximo(decimal))

        return self.alertas == []

    def set_valor(self, novo_valor):

        if isinstance(novo_valor, basestring):
            if novo_valor:
                novo_valor = Decimal(novo_valor)
            else:
                novo_valor = Decimal('0.0')

        if isinstance(novo_valor, (int, long, Decimal)) and self._valida(novo_valor):
            self._valor_decimal = Decimal(novo_valor)
            self._valor_string = self._formata(self._valor_decimal)
        else:
            self._valor_decimal = Decimal('0.0')
            self._valor_string = self._formata(self._valor_decimal)

    def get_valor(self):
        return self._valor_decimal

    valor = property(get_valor, set_valor)


def fuso_horario_sistema():
    # no windows, a linha abaixo da problema
    # diferenca = int(strftime('%z')) // 100
    from time import timezone

    diferenca = timezone // 3600

    if diferenca < 0:
        return pytz.timezone('Etc/GMT+' + str(diferenca * -1))

    if diferenca > 0:
        return pytz.timezone('Etc/GMT-' + str(diferenca))

    return pytz.UTC


class TagData(TagCaracter):
    def __init__(self, **kwargs):
        super(TagData, self).__init__(**kwargs)
        self._valor_data = None
        # Codigo para dinamizar a criacao de instancias de entidade,
        # aplicando os valores dos atributos na instanciacao
        for k, v in kwargs.items():
            setattr(self, k, v)

        if kwargs.has_key('valor'):
            self.valor = kwargs['valor']

    def _valida(self, valor):
        self.alertas = []

        if self._testa_obrigatorio(valor):
            self.alertas.append(self._testa_obrigatorio(valor))

        return self.alertas == []

    def set_valor(self, novo_valor):
        if isinstance(novo_valor, basestring):
            if novo_valor:
                novo_valor = datetime.strptime(novo_valor, '%Y-%m-%d')
            else:
                novo_valor = None

        if isinstance(novo_valor, (datetime, date,)) and self._valida(novo_valor):
            self._valor_data = novo_valor
            # Cuidado!!!
            # Aqui não dá pra usar a função strftime pois em alguns
            # casos a data retornada é 01/01/0001 00:00:00
            # e a função strftime só aceita data com anos a partir de 1900
            self._valor_string = '%04d-%02d-%02d' % (
                self._valor_data.year, self._valor_data.month, self._valor_data.day)
        else:
            self._valor_data = None
            self._valor_string = ''

    def get_valor(self):
        return self._valor_data

    valor = property(get_valor, set_valor)

    def formato_danfe(self):
        if self._valor_data is None:
            return ''
        else:
            return self._valor_data.strftime('%d/%m/%Y')


class TagDataHoraUTC(TagData):
    def __init__(self, **kwargs):
        super(TagDataHoraUTC, self).__init__(**kwargs)
        #
        # Expressão de validação do formato (vinda do arquivo leiauteSRE_V1.00.xsd
        # Alterada para tornar a informação do fuso horário opcional
        #
        self._validacao = re.compile(
            r'((20(([02468][048])|([13579][26]))-02-29)|(20[0-9][0-9])-((((0[1-9])|(1[0-2]))-((0[1-9])|(1\d)|(2[0-8])))|((((0[13578])|(1[02]))-31)|(((0[1,3-9])|(1[0-2]))-(29|30)))))T(20|21|22|23|[0-1]\d):[0-5]\d:[0-5]\d(-0[1-4]:00)?')
        self._valida_fuso = re.compile(r'.*[-+]0[0-9]:00$')
        self._brasilia = pytz.timezone('America/Sao_Paulo')
        self.fuso_horario = 'America/Sao_Paulo'

    def set_valor(self, novo_valor):
        if isinstance(novo_valor, basestring):
            if self._validacao.match(novo_valor):
                if self._valida_fuso.match(novo_valor):
                    #
                    # Extrai e determina qual o fuso horário informado
                    #
                    self.fuso_horario = novo_valor[19:]
                    novo_valor = novo_valor[:19]

                #
                # Converte a data sem fuso horário para o fuso horário atual
                # Isso é necessário pois a função strptime ignora a informação
                # do fuso horário na string de entrada
                #
                novo_valor = self.fuso_horario.localize(datetime.strptime(novo_valor, '%Y-%m-%dT%H:%M:%S'))
            else:
                novo_valor = None

        if isinstance(novo_valor, datetime) and self._valida(novo_valor):

            if not novo_valor.tzinfo:
                novo_valor = fuso_horario_sistema().localize(novo_valor)
                novo_valor = pytz.UTC.normalize(novo_valor)
                novo_valor = self._brasilia.normalize(novo_valor)

            self._valor_data = novo_valor
            self._valor_data = self._valor_data.replace(microsecond=0)
            try:
                self._valor_data = self.fuso_horario.localize(self._valor_data)
            except:
                pass
            # Cuidado!!!
            # Aqui não dá pra usar a função strftime pois em alguns
            # casos a data retornada é 01/01/0001 00:00:00
            # e a função strftime só aceita data com anos a partir de 1900
            # self._valor_string = '%04d-%02d-%02dT%02d:%02d:%02d' % (self._valor_data.year, self._valor_data.month, self._valor_data.day,
            #    self._valor_data.hour, self._valor_data.minute, self._valor_data.second)

            self._valor_string = self._valor_data.isoformat()
        else:
            self._valor_data = None
            self._valor_string = ''

    def get_valor(self):
        return self._valor_data

    valor = property(get_valor, set_valor)

    def set_fuso_horaro(self, novo_valor):
        if novo_valor in pytz.country_timezones['br']:
            self._fuso_horario = pytz.timezone(novo_valor)

        #
        # Nos valores abaixo, não entendi ainda até agora, mas para o resultado
        # correto é preciso usar GMT+ (mais), não (menos) como seria de se
        # esperar...
        #
        elif novo_valor == '-04:00' or novo_valor == '-0400':
            self._fuso_horario = pytz.timezone('Etc/GMT+4')
        elif novo_valor == '-03:00' or novo_valor == '-0300':
            self._fuso_horario = pytz.timezone('Etc/GMT+3')
        elif novo_valor == '-02:00' or novo_valor == '-0200':
            self._fuso_horario = pytz.timezone('Etc/GMT+2')
        elif novo_valor == '-01:00' or novo_valor == '-0100':
            self._fuso_horario = pytz.timezone('Etc/GMT+1')

    def get_fuso_horario(self):
        return self._fuso_horario

    fuso_horario = property(get_fuso_horario, set_fuso_horaro)
    #
    # def formato_danfe(self):
    #     if self._valor_data is None:
    #         return ''
    #     else:
    #         valor = self._brasilia.normalize(self._valor_data).strftime('%d/%m/%Y %H:%M:%S %Z (%z)')
    #         #
    #         # Troca as siglas:
    #         # BRT - Brasília Time -> HOB - Horário Oficial de Brasília
    #         # BRST - Brasília Summer Time -> HVOB - Horário de Verão Oficial de Brasília
    #         # AMT - Amazon Time -> HOA - Horário Oficial da Amazônia
    #         # AMST - Amazon Summer Time -> HVOA - Horário de Verão Oficial da Amazônia
    #         # FNT - Fernando de Noronha Time -> HOFN - Horário Oficial de Fernando de Noronha
    #         #
    #         valor = valor.replace('(-0100)', '(-01:00)')
    #         valor = valor.replace('(-0200)', '(-02:00)')
    #         valor = valor.replace('(-0300)', '(-03:00)')
    #         valor = valor.replace('(-0400)', '(-04:00)')
    #         valor = valor.replace('BRT', 'HOB')
    #         valor = valor.replace('BRST', 'HVOB')
    #         valor = valor.replace('AMT', 'HOA')
    #         valor = valor.replace('AMST', 'HVOA')
    #         valor = valor.replace('FNT', 'HOFN')
    #         return valor


class XMLAPI(NohXML):
    def __init__(self, *args, **kwargs):
        super(XMLAPI, self).__init__(*args, **kwargs)
        self._xml = None

    def get_xml(self):
        return u''

    def valido(self):

        # deve ser sobrescrito
        # buscando os ALERTAS

        return False

    def le_grupo(self, raiz_grupo, classe_grupo, sigla_ns=''):
        tags = []

        grupos = self._le_nohs(raiz_grupo, sigla_ns=sigla_ns)

        if grupos is not None:
            tags = [classe_grupo() for g in grupos]
            for i in range(len(grupos)):
                tags[i].xml = grupos[i]

        return tags
