pagseguro_xml
==========================

API do PagSeguro, em python, através de XML gerado por classes. Esquema baseado no projeto [PySPED](https://github.com/aricaldeira/PySPED).

#Instalando

```bash
pip install pagseguro_xml
```

ou

```bash
pip install -e git+https://github.com/arannasousa/pagseguro_xml#egg=pagseguro_xml
```

ou

```
git clone https://github.com/arannasousa/pagseguro_xml
cd pagseguro_xml
pip install -r dependencias.txt
python setup.py install
```

## Se houver problemas com o lxml

Caso encontre problemas na instalação do **lxml** pelo `pip`, tente usar o `easy_install`.

```
easy_install lxml
```

#Como usar

### Exemplos

No diretório [**exemplos**](https://github.com/arannasousa/pagseguro_xml/tree/master/exemplos) possui arquivos com os testes para cada API (pagamento, assinatura, consultas, notificacao) com suas opções de requisição.

# Índice

APIs disponíveis:

#####1. [API Pagamento / Checkout](https://github.com/arannasousa/pagseguro_xml#pagamento--checkout)
#####2. [API Notificações](https://github.com/arannasousa/pagseguro_xml#notifica%C3%A7%C3%B5es)
#####3. [API Consultas](https://github.com/arannasousa/pagseguro_xml#consultas)
#####4. [API Assinaturas](https://github.com/arannasousa/pagseguro_xml#assinaturas)

#####5. [Implementações pendentes](https://github.com/arannasousa/pagseguro_xml#implementa%C3%A7%C3%B5es-pendentes)


## Pagamento / Checkout

Para gerar uma solicitação de pagamento/checkout:

```python 

# criando a classe xml para efetuar o Checkout 
from pagseguro_xml.pagamento.v2.classes.pagamento import CONST as CONST_PAGAMENTO, ClassePagamentoCheckout, Item

checkout = ClassePagamentoCheckout()

# ao final do pagamento, o PagSeguro irá redirecionar para...
checkout.redirectURL.valor = u'http://seusite.com.br'
checkout.reference.valor = u'REF0001'

# prazo maximo de validade do CODIGO_PAGAMENTO que será criado pela PagSeguro (5 minutos)
checkout.maxAge.valor = 5 * 60

checkout.sender.name.valor = u'Cliente de teste'
checkout.sender.email.valor = u'as1234231234e@sandbox.pagseguro.com.br'

checkout.sender.phone.areaCode.valor = u'63'
checkout.sender.phone.number.valor = u'92111111'

checkout.shipping.type.valor = CONST_PAGAMENTO.SHIPPING.TYPE.NAO_ESPECIFICADO
checkout.shipping.address.city.valor = u'Palmas'
checkout.shipping.address.state.valor = u'TO'
checkout.shipping.address.country.valor = u'BRA'     # valor default

# criando o item para o Checkout, quantos desejar    
item1 = Item()
item1.ID.valor = u'ITEM0001'
item1.description.valor = u'Notebook Preto'
item1.amount.valor = u'2345.67'
item1.quantity.valor = 1
item1.weight.valor = 1000       # peso em gramas

# adicionando o Item ao Checkout
checkout.items.append(item1)

# apos preencher o Checkout, vamos verificar se houve algum erro 
# como: campos obrigatorios, passaram do limite, opcao nao disponivel, valores incorretos
    
if checkout.alertas:

    print u'-' * 45, u'ALERTAS', u'-' * 46

    for a in checkout.alertas:
        print a

    print u'-' * 100
    
    
if not checkout.alertas:

    # variaveis
    
    TOKEN_API = u''
    EMAIL_API = u''
        
    # importando a Classe que irá gerar a requisição e retonar o CODIGO para a url de pagamento (se tudo ok)
    from pagseguro_xml.pagamento import ApiPagSeguroConsulta_v2, CONST_v2
    
    # se nao informado, por padrão, o ambiente é SANDBOX
    api = ApiPagSeguroPagamento_v2(ambiente=CONST_v2.AMBIENTE.SANDBOX)
    
    # iniciando processo de ENVIO e RETORNO à PagSeguro
    ok, retorno = api.checkout_v2(EMAIL_API, TOKEN_API, checkout)
    #
    # podera acontecer os seguintes retorno:
    #   
    # sucesso -> (True, instância da classe ClassePagamentoRetornoCheckout)
    #
    # falha   -> (False, instância da classe ClassePagamentoErros (quando o status da requisicao for 400))
    # falha   -> (False, texto (unicode) contendo o motivo do erro)
    #
    
    if ok:
    
        print u'-' * 45, u'RESPOSTA', u'-' * 45
        # visualizando o XML retornado
        print retorno.xml
        print u'-' * 100
    
        # checando erros no XML retornado
        if retorno.alertas:
    
            print u'-' * 45, u'ALERTAS', u'-' * 46
    
            for a in retorno.alertas:
                print a
    
            print u'-' * 100
    
        # pegando o CODIGO retornado no XML (ClassePagamentoRetornoCheckout)
        #   Exemplo da PagSeguro:
        #
        #   <?xml version="1.0" encoding="ISO-8859-1"?>  
        #    <checkout>  
        #        <code>8CF4BE7DCECEF0F004A6DFA0A8243412</code>     <- este codigo  
        #        <date>2010-12-02T10:11:28.000-02:00</date>  
        #    </checkout>
        #
        CODIGO_REQUISICAO = retorno.code.valor
    
        # gerando a URL para REDIRECIONAMENTO do CLIENTE para efetuar o PAGAMENTO na PagSeguro
        url_fluxo = api.gera_url_fluxo_v2(CODIGO_REQUISICAO)    
        # >> u'https://[sandbox.]pagseguro.uol.com.br/v2/pre-approvals/request.html?code=CODIGO_REQUISICAO'
    
        print u'URL para o fluxo:', url_fluxo
    
        # no final do pagamento a PagSeguro vai gerar a URL como a de baixo, 
        # conforme informado na tag 'checkout.redirectURL.valor'
        # 
        # u'http://seusite.com.br/?code=CODIGO_NOTIFICACAO'
    
    else:
    
        # https://pagseguro.uol.com.br/v2/guia-de-integracao/api-de-pagamentos.html#v2-item-api-de-pagamentos-resposta
        
        # exibindo o erro 
        #
        # exibindo o erro 
        #
        #   caso seja um XML - retorna codigos de erros nos dados enviados
        #
        # Existe uma lista de erros na CONST dentro de:
        #
        #   pagseguro_xml.pagamento.v2.classes.erros.CONST.CODE
        #   pagseguro_xml.pagamento.v2.classes.erros.CONST.opcoes [dict contendo os CODIGOS e o TEXTO do erro]
        #
        if hasattr(retorno, u'xml'):
            print u'Motivo do erro:', retorno.xml
        else:
            print u'Motivo do erro:', retorno

```


## Notificações

Consultando uma notificação de transação:

> https://pagseguro.uol.com.br/v3/guia-de-integracao/api-de-notificacoes.html

```python 


from pagseguro_xml.notificacao import ApiPagSeguroNotificacao_v3, CONST_v3

# variaveis
TOKEN_API = u''
EMAIL_API = u''

CHAVE_NOTIFICACAO = u''

# se nao informado, por padrão, o ambiente é SANDBOX
api = ApiPagSeguroNotificacao_v3(ambiente=CONST_v3.AMBIENTE.SANDBOX)

# consultando a TRANSACAO através da chave_de_notificacao
ok, retorno = api.consulta_notificacao_transacao_v3(EMAIL_API, TOKEN_API, CHAVE_NOTIFICACAO)

# podera acontecer os seguintes retorno:
#   
# sucesso -> (True, instância da classe ClasseNotificacaoTransacao)
# falha   -> (False, texto (unicode) contendo o motivo do erro)
#

if ok:
    
    print u'-' * 45, u'RESPOSTA', u'-' * 45
    # visualizando o XML retornado
    print retorno.xml
    print u'-' * 100

    # checando erros no XML retornado
    if retorno.alertas:

        print u'-' * 45, u'ALERTAS', u'-' * 46

        for a in retorno.alertas:
            print a

        print u'-' * 100

else:
    print u'Motivo do erro:', retorno

```


## Consultas

Conforme o [guia da PagSeguro](https://pagseguro.uol.com.br/v2/guia-de-integracao/consultas.html), existem 3 formas de fazer consulta de transação financeira:

### 1. DETALHES da transação (versão 3)

> https://pagseguro.uol.com.br/v3/guia-de-integracao/consulta-de-transacoes-por-codigo.html

```python

# variaveis
TOKEN_API = u''
EMAIL_API = u'seu@email.com'

# codigo da transação que deseja consultar
CODIGO_TRANSACAO = u''

from pagseguro_xml.consultas import ApiPagSeguroConsulta_v3, CONST_v3

# se nao informado, por padrão, o ambiente é SANDBOX
api = ApiPagSeguroConsulta_v3(ambiente=CONST_v3.AMBIENTE.SANDBOX)

# realiza a consulta do CODIGO da TRANSACAO, se sucesso, retorna uma CLASSE que representa o XML
ok, retorno = api.detalhes_v3(EMAIL_API, TOKEN_API, CODIGO_TRANSACAO)

#
# podera acontecer os seguintes retorno:
#   
# sucesso -> (True, instância da classe ClasseTransacaoDetalhes)
# falha   -> (False, texto (unicode) contendo o motivo do erro)
#

if ok:

    print u'-' * 45, u'RESPOSTA', u'-' * 45
    
    # visualizando o XML retornado
    print retorno.xml
    
    print u'-' * 100

    # acessando o STATUS da transacao
    print u'Status da TRANSACAO', retorno.status.valor

    # checando erros no XML retornado
    if retorno.alertas:

        print u'-' * 45, u'ALERTAS', u'-' * 46

        for a in retorno.alertas:
            print a

        print u'-' * 100

else:
    print u'Motivo do erro:', retorno

```

### 2. CONSULTA de transações por INTERVALO DE DATAS (versão 2)

> https://pagseguro.uol.com.br/v2/guia-de-integracao/consulta-de-transacoes-por-intervalo-de-datas.html

```python

# variaveis
TOKEN_API = u''
EMAIL_API = u'seu@email.com'

# codigo da transação que deseja consultar
CODIGO_TRANSACAO = u''

from pagseguro_xml.consultas import ApiPagSeguroConsulta_v3, CONST_v3

# se nao informado, por padrão, o ambiente é SANDBOX
api = ApiPagSeguroConsulta_v3(ambiente=CONST_v3.AMBIENTE.SANDBOX)

from datetime import datetime

# Gera um periodo para consulta
#
# Obs.: Cuidado com as limitações da PAGSEGURO
#
# 1. 'data_inicial' NÃO pode ser maior que 6 meses, contados de HOJE
# 2. 'data_final - data_inicial' NÃO pode ser maior que 30 dias
#
data_inicial = datetime(2015, 12, 9)
data_final = datetime(2015, 12, 12)

# realiza a consulta das TRANSACOES no período especificado acima
# se sucesso, retorna uma CLASSE que representa o XML
ok, retorno = api.historico_v2(EMAIL_API, TOKEN_API, data_inicia, data_final)

#
# podera acontecer os seguintes retorno:
#   
# sucesso -> (True, instância da classe ClasseTransacaoHistorico)
# falha   -> (False, texto (unicode) contendo o motivo do erro)
#

if ok:

    print u'-' * 45, u'RESPOSTA', u'-' * 45
    
    # visualizando o XML retornado
    print retorno.xml
    
    print u'-' * 100

    print u'Total de transações localizadas:', retorno.resultsInThisPage.valor, len(retorno.transactions) 
    
    # acessando o STATUS de cada transacao
    for i, transacao in enumerate(retorno.transactions, start=1):
            print u' - Transacao No "%s", STATUS: %s ' % (i, transacao.status.valor)

    # checando erros no XML retornado
    if retorno.alertas:

        print u'-' * 45, u'ALERTAS', u'-' * 46

        for a in retorno.alertas:
            print a

        print u'-' * 100

else:
    print u'Motivo do erro:', retorno

```

### 3. CONSULTA de transações ABANDONADAS (versão 2)

> https://pagseguro.uol.com.br/v2/guia-de-integracao/consulta-de-transacoes-abandonadas.html

```python

# variaveis
TOKEN_API = u''
EMAIL_API = u'seu@email.com'

# codigo da transação que deseja consultar
CODIGO_TRANSACAO = u''

from pagseguro_xml.consultas import ApiPagSeguroConsulta_v3, CONST_v3

# se nao informado, por padrão, o ambiente é SANDBOX
api = ApiPagSeguroConsulta_v3(ambiente=CONST_v3.AMBIENTE.SANDBOX)

from datetime import datetime

# Gera um periodo para consulta
#
# Obs.: Cuidado com as limitações da PAGSEGURO
#
# 1. 'data_inicial' NÃO pode ser maior que 6 meses, contados de HOJE
# 2. 'data_final - data_inicial' NÃO pode ser maior que 30 dias
#
data_inicial = datetime(2015, 12, 9)
data_final = datetime(2015, 12, 12)

# realiza a consulta das TRANSACOES no período especificado acima
# se sucesso, retorna uma CLASSE que representa o XML
ok, retorno = api.abandonadas_v2(EMAIL_API, TOKEN_API, data_inicia, data_final)

#
# podera acontecer os seguintes retorno:
#   
# sucesso -> (True, instância da classe ClasseTransacaoAbandonadas)
# falha   -> (False, texto (unicode) contendo o motivo do erro)
#

if ok:

    print u'-' * 45, u'RESPOSTA', u'-' * 45
    
    # visualizando o XML retornado
    print retorno.xml
    
    print u'-' * 100

    print u'Total de transações localizadas:', retorno.resultsInThisPage.valor, len(retorno.transactions) 
    
    # acessando a REFERENCIA de cada transacao
    for i, transacao in enumerate(retorno.transactions, start=1):
            print u' - Transacao No "%s", REFERENCIA: %s ' % (i, transacao.reference.valor)

    # checando erros no XML retornado
    if retorno.alertas:

        print u'-' * 45, u'ALERTAS', u'-' * 46

        for a in retorno.alertas:
            print a

        print u'-' * 100

else:
    print u'Motivo do erro:', retorno

```

## Assinaturas

Essa API é composta por 6 chamadas:

> http://download.uol.com.br/pagseguro/docs/pagseguro-assinatura-automatica.pdf

1. **[Requisitando uma assinatura](https://github.com/arannasousa/pagseguro_xml#1-requisitando-uma-assinatura):** processo em que será gerado um código para o cliente ser redirecionado para a PagSeguro e finalizar a compra. No final da compra, a PagSeguro irá notificar o seu sistema enviando um CODIGO de ASSINATURA (semelhante ao CODIGO de TRANSACAO - API de Pagamentos).

2. **[Consultando uma assinatura através do código de *notificação*](https://github.com/arannasousa/pagseguro_xml#2-consultando-uma-assinatura-atrav%C3%A9s-do-c%C3%B3digo-de-notifica%C3%A7%C3%A3o):** Esta consulta deve ser utilizada para consultar uma notificação recebida a fim de obter os dados da assinatura (de forma resumida).
3. **[Consultando uma assinatura através do código de *assinatura*](https://github.com/arannasousa/pagseguro_xml#3-consultando-uma-assinatura-atrav%C3%A9s-do-c%C3%B3digo-de-assinatura):** Esta consulta possibilita o acesso a todos os dados de uma assinatura a partir de seu código identificador.

4. **[Consultando todas as assinaturas, *por dias*, que geraram alguma *notificação*](https://github.com/arannasousa/pagseguro_xml#4-consultando-todas-as-assinaturas-por-dias-que-geraram-alguma-notifica%C3%A7%C3%A3o-assinatura-resumida):** Permite o acesso aos dados de todas as assinaturas que tiveram algum tipo de notificação dentro de um intervalo de tempo (em dias) definido.
5. **[Consultando todas as assinaturas, por intervalo de *datas*](https://github.com/arannasousa/pagseguro_xml#5-consultando-todas-as-assinaturas-por-intervalo-de-datas-assinatura-resumida):** Obtém os dados das assinaturas dado um **intervalo de datas**.

6. **[Cancelando uma assinatura](https://github.com/arannasousa/pagseguro_xml#6-cancelando-uma-assinatura):** processo em que uma assinatura será cancelada.

### 1. Requisitando uma assinatura

Chamada de **autorização**, é o processo onde o cliente, após escolher o serviço no site, é redirecionado para o PagSeguro para efetuar a autorização do débito recorrente em seu cartão de crédito.

```python

# variaveis
TOKEN_API = u''
EMAIL_API = u'seu@email.com'

from pagseguro_xml.assinatura.v2.classes.requisicao import ClasseAssinaturaRequisicao, CONST as CONST_REQUISICAO

# montando o XML para a requisição de pagamento na PagSeguro

xmlRequisicao = ClasseAssinaturaRequisicao()

# url para redirecionamento, ao final do pagamento, na pagSeguro
# através dela, será recebido o CODIGO_DE_ASSINATURA
xmlRequisicao.redirectURL.valor = u'http://seusite.com.br'

xmlRequisicao.reference.valor = u'REF0002'

xmlRequisicao.sender.name.valor = u'Cliente de teste'
xmlRequisicao.sender.email.valor = u'as1234231234e@sandbox.pagseguro.com.br'

xmlRequisicao.sender.address.state.valor = u'TO'

# cobrança [auto|manual] 
xmlRequisicao.preApproval.charge.valor = CONST_REQUISICAO.PREAPPROVAL.CHARGE.AUTO
xmlRequisicao.preApproval.name.valor = u'Assinatura de 1 mes'
xmlRequisicao.preApproval.amountPerPayment.valor = u'10.00'
xmlRequisicao.preApproval.period.valor = CONST_REQUISICAO.PREAPPROVAL.PERIOD.MONTHLY

from datetime import datetime

# data final da cobrança 
xmlRequisicao.preApproval.finalDate.valor = datetime(2016, 01, 23)

# valor total das cobranças até a data de término
xmlRequisicao.preApproval.maxTotalAmount.valor = u'10.00'

# checa se houve algum erro de informação, se existe campos obrigatórios não preenchidos
# antes de enviar à WebService da PagSeguro
if xmlRequisicao.alertas:

    print u'-' * 45, u'ALERTAS', u'-' * 46

    for a in checkout.alertas:
        print a

    print u'-' * 100

    return u'Falha no esquema'

from pagseguro_xml.assinatura import ApiPagSeguroAssinatura_v2, CONST_v2

# se nao informado, por padrão, o ambiente é SANDBOX
api = ApiPagSeguroAssinatura_v2(ambiente=CONST_v2.AMBIENTE.SANDBOX)

# gera a solicitacao de pagamento para a assinatura
ok, retorno = api.requisicao_assinatura_v2(EMAIL_API, TOKEN_API, xmlRequisicao)

#
# podera acontecer os seguintes retorno:
#   
# sucesso -> (True , instância da classe ClasseAssinaturaResposta)
#
# falha   -> (False, instância da classe ClasseAssinaturaErros (quando o status da requisicao for 400))
# falha   -> (False, texto (unicode) contendo o motivo do erro)
#

if ok:
    
    print u'-' * 45, u'RESPOSTA', u'-' * 45
    # visualizando o XML retornado
    print retorno.xml
    print u'-' * 100

    # checando erros no XML retornado
    if retorno.alertas:

        print u'-' * 45, u'ALERTAS', u'-' * 46

        for a in retorno.alertas:
            print a

        print u'-' * 100

    # pegando o CODIGO retornado no XML (ClassePagamentoRetornoCheckout)
    #   Exemplo da PagSeguro:
    #
    #   <?xml version="1.0" encoding="ISO-8859-1"?>  
    #    <preApprovalRequest>  
    #        <code>8CF4BE7DCECEF0F004A6DFA0A8243412</code>     <- este codigo  
    #        <date>2010-12-02T10:11:28.000-02:00</date>  
    #    </preApprovalRequest>
    #
    
    CODIGO_REQUISICAO_PAGAMENTO = retorno.code.valor

    url_fluxo = api.gera_url_fluxo_v2(CODIGO_REQUISICAO_PAGAMENTO)
    # >> u'https://[sandbox.]pagseguro.uol.com.br/v2/pre-approvals/request.html?code=CODIGO-RETORNADO'

    print u'URL para o fluxo:', url_fluxo

    return redirect(url_fluxo)
    
    # --------------------------------------------------------------------------------
    # no final do pagamento, a PagSeguro vai gerar a URL como a de baixo
    #
    # u'http://seusite.com.br/?code=CODIGO-NOTIFICACAO'
    # --------------------------------------------------------------------------------

else:
    #
    # exibindo o erro 
    #
    #   caso seja um XML - retorna codigos de erros nos dados enviados
    #
    # Existe uma lista de erros na CONST dentro de:
    #
    #   pagseguro_xml.assinatura.v2.classes.erros.CONST.CODE
    #   pagseguro_xml.assinatura.v2.classes.erros.CONST.opcoes [dict contendo os CODIGOS e o TEXTO do erro]
    #
    
    if hasattr(retorno, u'xml'):
        print u'Motivo do erro:', retorno.xml
        
        return u'Motivo do erro: %s' % retorno.xml
            
    else:
        print u'Motivo do erro:', retorno
        
        return u'Motivo do erro: %s' % retorno
    
```

### 2. Consultando uma assinatura através do código de *notificação*

Esta consulta deve ser utilizada para consultar uma notificação recebida a fim de obter os dados da assinatura.

```python

# variaveis
TOKEN_API = u''
EMAIL_API = u'seu@email.com'

# codigo da notificacao recebida pela PagSeguro
# Ex.:
# http://seusite.com.br/?code=CODIGO-NOTIFICACAO&notificationType=preApproval
CODIGO_NOTIFICACAO = u''

from pagseguro_xml.assinatura import ApiPagSeguroAssinatura_v2, CONST_v2

# se nao informado, por padrão, o ambiente é SANDBOX
api = ApiPagSeguroAssinatura_v2(ambiente=CONST_v2.AMBIENTE.SANDBOX)

# realiza a consulta da ASSINATURA através do codigo de notificacao
# se sucesso, retorna uma CLASSE que representa o XML
ok, retorno = api.consulta_assinatura_notificacao_v2(EMAIL_API, TOKEN_API, CODIGO_NOTIFICACAO)

#
# podera acontecer os seguintes retorno:
#   
# sucesso -> (True, instância da classe ClasseConsultaAssinaturaResposta)
# falha   -> (False, texto (unicode) contendo o motivo do erro)
#

if ok:

    print u'-' * 45, u'RESPOSTA', u'-' * 45
    
    # visualizando o XML retornado
    print retorno.xml
    
    print u'-' * 100

    print u'Status da Assinatura', retorno.status.valor 
    
    # checando erros no XML retornado
    if retorno.alertas:

        print u'-' * 45, u'ALERTAS', u'-' * 46

        for a in retorno.alertas:
            print a

        print u'-' * 100

else:
    print u'Motivo do erro:', retorno

```

### 3. Consultando uma assinatura através do código de *assinatura*

Esta consulta possibilita o acesso a todos os dados de uma assinatura a partir de seu código identificador.

```python

# variaveis
TOKEN_API = u''
EMAIL_API = u'seu@email.com'

# codigo da assinatura
CODIGO_ASSINATURA = u''

from pagseguro_xml.assinatura import ApiPagSeguroAssinatura_v2, CONST_v2

# se nao informado, por padrão, o ambiente é SANDBOX
api = ApiPagSeguroAssinatura_v2(ambiente=CONST_v2.AMBIENTE.SANDBOX)

# realiza a consulta da ASSINATURA através do codigo
# se sucesso, retorna uma CLASSE que representa o XML
ok, retorno = api.consulta_assinatura_v2(EMAIL_API, TOKEN_API, CODIGO_NOTIFICACAO)

#
# podera acontecer os seguintes retorno:
#   
# sucesso -> (True, instância da classe ClasseConsultaAssinaturaResposta)
# falha   -> (False, texto (unicode) contendo o motivo do erro)
#

if ok:

    print u'-' * 45, u'RESPOSTA', u'-' * 45
    
    # visualizando o XML retornado
    print retorno.xml
    
    print u'-' * 100

    print u'Status da Assinatura', retorno.status.valor 
    
    # checando erros no XML retornado
    if retorno.alertas:

        print u'-' * 45, u'ALERTAS', u'-' * 46

        for a in retorno.alertas:
            print a

        print u'-' * 100

else:
    print u'Motivo do erro:', retorno

```

### 4. Consultando todas as assinaturas, *por dias*, que geraram alguma *notificação* (assinatura resumida)

Permite o acesso aos dados de todas as assinaturas que tiveram algum tipo de notificação dentro de um intervalo de tempo (em dias) definido.

```python

# variaveis
TOKEN_API = u''
EMAIL_API = u'seu@email.com'

# de acordo com a documentacao, o limite maximo é de 30 dias, o mínimo é 1
DIAS = 30

from pagseguro_xml.assinatura import ApiPagSeguroAssinatura_v2, CONST_v2

# se nao informado, por padrão, o ambiente é SANDBOX
api = ApiPagSeguroAssinatura_v2(ambiente=CONST_v2.AMBIENTE.SANDBOX)

# checa se houve assinaturas que geraram notificação dentro de X dias
ok, retorno = api.consulta_notificacao_por_dias_v2(EMAIL_API, TOKEN_API, DIAS)

#
# podera acontecer os seguintes retorno:
#   
# sucesso -> (True , instância da classe ClasseConsultaAssinaturasResposta)
#
# falha   -> (False, instância da classe ClasseAssinaturaErros (quando o status da requisicao for 400))
# falha   -> (False, texto (unicode) contendo o motivo do erro)
#

if ok:
    
    print u'-' * 45, u'RESPOSTA', u'-' * 45
    # visualizando o XML retornado
    print retorno.xml
    print u'-' * 100

    # checando erros no XML retornado
    if retorno.alertas:

        print u'-' * 45, u'ALERTAS', u'-' * 46

        for a in retorno.alertas:
            print a

        print u'-' * 100

    print u'Total de ASSINATURAS localizadas:', retorno.resultsInThisPage.valor, len(retorno.preApprovals) 
    
    # acessando o STATUS de cada transacao
    for i, assinatura in enumerate(retorno.preApprovals, start=1):
            print u' - Assinatura No "%s", STATUS: %s ' % (i, assinatura.status.valor)

    # checando erros no XML retornado
    if retorno.alertas:

        print u'-' * 45, u'ALERTAS', u'-' * 46

        for a in retorno.alertas:
            print a

        print u'-' * 100

else:
    #
    # exibindo o erro 
    #
    #   caso seja um XML - retorna codigos de erros nos dados enviados
    #
    # Existe uma lista de erros na CONST dentro de:
    #
    #   pagseguro_xml.assinatura.v2.classes.erros.CONST.CODE
    #   pagseguro_xml.assinatura.v2.classes.erros.CONST.opcoes [dict contendo os CODIGOS e o TEXTO do erro]
    #
    
    if hasattr(retorno, u'xml'):
        print u'Motivo do erro:', retorno.xml
        
        return u'Motivo do erro: %s' % retorno.xml
            
    else:
        print u'Motivo do erro:', retorno
        
        return u'Motivo do erro: %s' % retorno
    
```

### 5. Consultando todas as assinaturas, por intervalo de *datas* (assinatura resumida)

Obtém os dados das assinaturas dado um intervalo de datas.

```python

# variaveis
TOKEN_API = u''
EMAIL_API = u'seu@email.com'

from datetime import datetime

# Gera um periodo para consulta
#
# Obs.: Cuidado com as limitações da PAGSEGURO
#
# 1. 'data_inicial' NÃO pode ser maior que 6 meses, contados de HOJE
#
data_inicial = datetime(2015, 12, 9)
data_final = datetime(2015, 12, 12)

from pagseguro_xml.assinatura import ApiPagSeguroAssinatura_v2, CONST_v2

# se nao informado, por padrão, o ambiente é SANDBOX
api = ApiPagSeguroAssinatura_v2(ambiente=CONST_v2.AMBIENTE.SANDBOX)

# consulta assinaturas no periodo especificado
ok, retorno = api.consulta_por_data_v2(EMAIL_API, TOKEN_API, data_inicial, data_final)

#
# podera acontecer os seguintes retorno:
#   
# sucesso -> (True , instância da classe ClasseConsultaAssinaturasResposta)
#
# falha   -> (False, instância da classe ClasseAssinaturaErros (quando o status da requisicao for 400))
# falha   -> (False, texto (unicode) contendo o motivo do erro)
#

if ok:
    
    print u'-' * 45, u'RESPOSTA', u'-' * 45
    # visualizando o XML retornado
    print retorno.xml
    print u'-' * 100

    # checando erros no XML retornado
    if retorno.alertas:

        print u'-' * 45, u'ALERTAS', u'-' * 46

        for a in retorno.alertas:
            print a

        print u'-' * 100

    print u'Total de ASSINATURAS localizadas:', retorno.resultsInThisPage.valor, len(retorno.preApprovals) 
    
    # acessando o STATUS de cada transacao
    for i, assinatura in enumerate(retorno.preApprovals, start=1):
            print u' - Assinatura No "%s", STATUS: %s ' % (i, assinatura.status.valor)

    # checando erros no XML retornado
    if retorno.alertas:

        print u'-' * 45, u'ALERTAS', u'-' * 46

        for a in retorno.alertas:
            print a

        print u'-' * 100

else:
    #
    # exibindo o erro 
    #
    #   caso seja um XML - retorna codigos de erros nos dados enviados
    #
    # Existe uma lista de erros na CONST dentro de:
    #
    #   pagseguro_xml.assinatura.v2.classes.erros.CONST.CODE
    #   pagseguro_xml.assinatura.v2.classes.erros.CONST.opcoes [dict contendo os CODIGOS e o TEXTO do erro]
    #
    
    if hasattr(retorno, u'xml'):
        print u'Motivo do erro:', retorno.xml
        
        return u'Motivo do erro: %s' % retorno.xml
            
    else:
        print u'Motivo do erro:', retorno
        
        return u'Motivo do erro: %s' % retorno
    
```

### 6. Cancelando uma assinatura

É possível solicitar o cancelamento de uma assinatura fazendo uma chamada ao serviço de Cancelamento. 
Para tanto, basta que a assinatura esteja com o status ATIVO.

```python

# variaveis
TOKEN_API = u''
EMAIL_API = u'seu@email.com'

CODIGO_ASSINATURA = u''

from pagseguro_xml.assinatura import ApiPagSeguroAssinatura_v2, CONST_v2

# se nao informado, por padrão, o ambiente é SANDBOX
api = ApiPagSeguroAssinatura_v2(ambiente=CONST_v2.AMBIENTE.SANDBOX)

# efetua o cancelamento da ASSINATURA
ok, retorno = api.cancela_v2(EMAIL_API, TOKEN_API, CODIGO_ASSINATURA)

#
# podera acontecer os seguintes retorno:
#   
# sucesso -> (True , instância da classe ClasseCancelamentoAssinaturaRetorno)
#
# falha   -> (False, instância da classe ClasseAssinaturaErros (quando o status da requisicao for 400))
# falha   -> (False, texto (unicode) contendo o motivo do erro)
#

if ok:
    
    print u'-' * 45, u'RESPOSTA', u'-' * 45
    # visualizando o XML retornado
    print retorno.xml
    print u'-' * 100

    # checando erros no XML retornado
    if retorno.alertas:

        print u'-' * 45, u'ALERTAS', u'-' * 46

        for a in retorno.alertas:
            print a

        print u'-' * 100

    #
    # possivel opcoes de status
    #
    # PENDING: u'Assinatura pendente. Aguardando confimação pela operadora',
    # ACTIVE: u'Assinatura paga e confirmada pela operadora',
    # CANCELLED: u'Assinatura cancelada por não aprovação da PagSeguro u pela operadora',
    # CANCELLED_BY_RECEIVER: u'Assinatura cancelada por solicitação do vendedor',
    # CANCELLED_BY_SENDER: u'Assinatura cancelada por solicitação do comprador',
    # EXPIRED: u'Assinatura expirou',
    # OK: u'Assinatura cancelada',
    #
    
    from pagseguro_xml.assinatura.v2.classes.cancelamento import CONST as CONST_CANCELAMENTO
    
    print u'STATUS do cancelamento:', retorno.status.valor
    print u'STATUS do cancelamento:', CONST_CANCELAMENTO.STATUS.opcoes.get(retorno.status.valor, u'----')
    
    # checando erros no XML retornado
    if retorno.alertas:

        print u'-' * 45, u'ALERTAS', u'-' * 46

        for a in retorno.alertas:
            print a

        print u'-' * 100

else:
    #
    # exibindo o erro 
    #
    #   caso seja um XML - retorna codigos de erros nos dados enviados
    #
    # Existe uma lista de erros na CONST dentro de:
    #
    #   pagseguro_xml.assinatura.v2.classes.erros.CONST.CODE
    #   pagseguro_xml.assinatura.v2.classes.erros.CONST.opcoes [dict contendo os CODIGOS e o TEXTO do erro]
    #
    
    if hasattr(retorno, u'xml'):
        print u'Motivo do erro:', retorno.xml
        
        return u'Motivo do erro: %s' % retorno.xml
            
    else:
        print u'Motivo do erro:', retorno
        
        return u'Motivo do erro: %s' % retorno
    
```

## Implementações pendentes

Apesar de todas as funcionalidades, ainda restam algumas pendências:

a) implementar a tag [METADATA](https://pagseguro.uol.com.br/v2/guia-de-integracao/api-de-pagamentos.html#v2-item-api-de-pagamentos-parametros-api) no xml de pagamento.

b) implementar a requisição dos detalhes da transação para a [versão 2](https://pagseguro.uol.com.br/v2/guia-de-integracao/consulta-de-transacoes-por-codigo.html).