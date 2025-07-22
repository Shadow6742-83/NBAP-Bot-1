# Tudo após "#" é um comentário

# Esse código foi desenvolvido para criar itens, no Wikidata, para escolas brasileiras que ainda não existem
# neste projeto. Utiliza, como fonte, o Censo Escolar de 2022. Para isso, segue três etapas:
# 1) A partir de um arquivo contendo dados do Censo, obtém os dados das escolas;
# 2) Realiza uma query (SPARQL) para conferir se a escola já existe no Wikidata;
# 3) Caso não exista, cria o item para a escola, contendo: "rótulo", "descrição", "instância de", "país" e "Código INEP";
# As três fases são realizadas em loop, até finalizar o arquivo fonte.

# Definindo funções

# Função para adicionar declarações
def adicionar_declaracao(item, prop_id, valor, valor_tipo='wikibase-item', qualificadores = None):
    declaracao = pywikibot.Claim(repo, prop_id)
    
    # Define o valor da declaração
    if valor_tipo == 'wikibase-item':
        target = pywikibot.ItemPage(repo, valor)
        declaracao.setTarget(target)
    elif valor_tipo == 'string':
        declaracao.setTarget(str(valor))
    elif valor_tipo == 'coordinate':
        declaracao.setTarget(pywikibot.Coordinate(
            lat=valor['latitude'],
            lon=valor['longitude'],
            precision=0.0001
            )
        )
    elif valor_tipo == 'quantity':
        declaracao.setTarget(pywikibot.WbQuantity(
            amount=valor,
            site=site
            )
        )
    elif valor_tipo == 'time':
        declaracao.setTarget(valor)
    else:
        raise ValueError('Tipo de valor não suportado')
    
    # Adiciona a declaração ao item"
    item.addClaim(declaracao, summary=f'Adicionado {prop_id} -> {valor}')

    # Adiciona os Qualificadores
    if qualificadores:
        for prop_q, val_q, type_q in qualificadores:
            if val_q is None:
                continue #pula se o valor não existir

            qual = pywikibot.Claim(repo, prop_q)

            if type_q == 'wikibase-item':
                target = pywikibot.ItemPage(repo, val_q)
                qual.setTarget(target)
            elif type_q == 'string':
                qual.setTarget(str(val_q))
            elif type_q == 'coordinate':
                qual.setTarget(pywikibot.Coordinate(
                    lat=val_q['latitude'],
                    lon=val_q['longitude'],
                    precision=0.0001
                )
            )
            elif type_q == 'quantity':
                qual.setTarget(pywikibot.WbQuantity(
                    amount=val_q,
                    site=site
                )
            )
            elif type_q == 'time':
                qual.setTarget(val_q)
            else:
                raise ValueError('Tipo de valor não suportado')

            declaracao.addQualifier(qual, summary=f'Adicionando qualificador {prop_q} -> {val_q}')
        
    # Adiciona sempre a mesma referência (Censo Escolar 2023, com a mesma data de acesso)
    # Adiciona referência: P248 (afirmado em) → Q133805362
    ref_fonte = pywikibot.Claim(repo, 'P248')
    item_fonte = pywikibot.ItemPage(repo, 'Q133805362')
    ref_fonte.setTarget(item_fonte)

    # Adiciona referência: P813 (data de consulta) → 10/07/2025
    data_consulta = pywikibot.WbTime(year=2025, month=7, day=10)
    ref_data = pywikibot.Claim(repo, 'P813')
    ref_data.setTarget(data_consulta)
        
    # Anexa as referências na declaração
    declaracao.addSources([ref_fonte, ref_data])


#Essa função é utilizada para formatar o nome das escolas,
#Existe função nativa, porém tem efeito estranho em "da", "de", "do", "das", "dos", "e".
def formatar_nome(nome):
    minusculas = ['da', 'de', 'do', 'das', 'dos', 'e']
    correcoes = {
        'educacao': 'Educação',
        'sao': 'São',  
        'colegio': 'Colégio',
        'tecnico': 'Técnico',
        'tecnologico': 'Tecnológico',
        'basico': 'Básico',
        'cei': 'CEI',
        'cmei': 'CMEI',
        'pre': 'Pré',
        'nucleo': 'Núcleo',
        ' iv': ' IV',
        'iii': 'III',
        'ii': 'II',
        'basica': 'Básica',
        'instituicao': 'Instituição',
        'fundacao': 'Fundação',
        'associacao': 'Associação',
        'acao': 'Ação',
        'servico': 'Serviço',
        'esperanca': 'Esperança',
        'lapis': 'Lápis',
        'espaco': 'Espaço',
        'crianca': 'Criança',
        'ceu': 'Céu',
        'pe': 'Pé',
        'valorizacao': 'Valorização',
        'comunitario': 'Comunitário'
    }

    palavras = nome.lower().split()
    resultado = []
    ultima_palavra = None

    for i, palavra in enumerate(palavras):
        if palavra in correcoes:
            palavra_corrigida = correcoes[palavra]
        elif palavra in minusculas and i != 0:
            palavra_corrigida = palavra
        else:
            palavra_corrigida = palavra.capitalize()

        # Evitar repetição da mesma palavra consecutiva (inclusive preposições)
        if palavra_corrigida != ultima_palavra:
            resultado.append(palavra_corrigida)
            ultima_palavra = palavra_corrigida
    
    return ' '.join(resultado)


# Início do script

# Vamos trabalhar com pywikibot que é uma biblioteca, logo, precisamos importá-la
import pywikibot

# A função PageGenerator interpreta a consulta SPARQL e retorna objetos pywikibot; WbTime é necessário
# para processar datas no formato do Wikidata
from pywikibot import pagegenerators, WbTime

# Vamos utilizar essa biblioteca para ler o arquivo fonte, que está salvo no formato csv
import csv

# Etapa 1: obter os dados da escola de um arquivo fonte

# Definindo qual é o arquivo fonte (com os dados que iremos importar)
arquivo_fonte = 'microdados_ed_basica_2023_sc_resumido.csv'

# Definindo o site (wikidata)
site = pywikibot.Site("wikidata", "wikidata")
repo = site.data_repository()
site.user_agent = "NBAP 0.8"
# Precisamos que o programa abra o arquivo fonte, e armazene seu conteúdo em uma variável para que possamos usá-lo
# Nesse caso, a variável será arquivoCsv
with open(arquivo_fonte, newline='', encoding='utf-8') as arquivo_csv:

    # Vamos usar a classe DictReader, da biblioteca csv que importamos na linha 16, para processar nosso arquivo fonte,
    # que está no formato .csv. Cada linha de conteúdo será armazenada como um objeto, com cabeçalho
    leitor = csv.DictReader(arquivo_csv, delimiter=';')
    
    # Cada objeto do arquivo (cada linha), será armazenado na variável 'linha', e para cada linha, faremos o seguinte:
    # Importante: esse é o loop de nosso código, onde para cada linha (cada escola) o programa repetirá todas as
    # instruções abaixo:
    for linha in leitor:
        
        # Armazenar os valores em novas variáveis, para reutilizar depois, nos passos 2 e 3
        nome = formatar_nome(linha['NO_ENTIDADE'])
        codigo_inep = linha['CO_ENTIDADE']
        municipio = linha['NO_MUNICIPIO']
        codigo_municipio = linha['CO_MUNICIPIO']
        estudantes = linha['QT_MAT_BAS']
        professores = linha['QT_DOC_BAS']
        localizacao = linha['TP_LOCALIZACAO']
        localizacao_diferenciada = linha['TP_LOCALIZACAO_DIFERENCIADA']        
        queima_lixo = linha['IN_LIXO_QUEIMA']
        separa_lixo = linha['IN_TRATAMENTO_LIXO_SEPARACAO']
        esgoto_inexistente = linha['IN_ESGOTO_INEXISTENTE']
        esgoto_fossa_comum = linha['IN_ESGOTO_FOSSA_COMUM']
        esgoto_fossa_septica = linha['IN_ESGOTO_FOSSA_SEPTICA']
        esgoto_rede = linha['IN_ESGOTO_REDE_PUBLICA']
        energia_inexistente = linha['IN_ENERGIA_INEXISTENTE']
        energia_publica = linha['IN_ENERGIA_REDE_PUBLICA']
        energia_gerador = linha['IN_ENERGIA_GERADOR_FOSSIL']
        energia_renovavel = linha['IN_ENERGIA_RENOVAVEL']
        coordenadas_latitude = linha['COORDENADAS_LAT']
        coordenadas_longitude = linha['COORDENADAS_LON']
        # Final da Etapa 1
        
        # Etapa 2: realizar a consulta para verificar e existência (ou não) de um item

        # Nesta variável, vamos armazenar nossa query
        consulta = "SELECT ?item ?itemLabel  WHERE { ?item wdt:P31 wd:Q3914 . ?item wdt:P11704 '" + codigo_inep + "' . }"
        
        # Checando se existe um item ou não
        
        if any(pagegenerators.WikidataSPARQLPageGenerator(query=consulta, site=site)):
            print(f"A escola {nome} já existe no Wikidata. Prosseguindo para a próxima.")
        else:
            print(f"A escola {nome} ainda não existe no Wikidata. Prosseguindo para criação do item.")
            
            consulta_municipio = "select ?item where{ ?item wdt:P1585 '"+ codigo_municipio +"'  . }"

            municipio_item = pagegenerators.WikidataSPARQLPageGenerator(query=consulta_municipio,site=site)
        
            municipio_ID = str(next(iter(municipio_item), None)).replace("[[wikidata:", "")

            municipio_ID = str(municipio_ID).replace("]]", "")

            # Etapa 3: caso o item ainda não exista (conforme verificado na etapa 2), criá-lo        
                
            # Nesta variável (array), vamos armazenar as informações que gostaríamos de adicionar em nosso item
            dados = {
                'labels': {
                'en':  nome,
                'pt':  nome ,
            },
                'descriptions': {
                'en': 'school located in ' + municipio,
                'pt': 'escola localizada em ' + municipio,
                }
            }
    
            #Essa variavel vai nos ajudar a corrigir o bug do valor "Escola"        
            mapa_tipo_escola = {
                '1': "Q134739441",
                '2': "Q134739026",
                '3': "Q133804953",
                '0-1': "Q3914",        # localizacaoDiferenciada=0 e localizacao=1
                '0-2': "Q19855165",    # localizacaoDiferenciada=0 e localizacao=2
            }
    
            # Gera chave combinada para os casos especiais
            chave = (
                f"{localizacao_diferenciada}-{localizacao}"
                if localizacao_diferenciada == '0'
                else localizacao_diferenciada
            )
    
            # Busca no dicionário, ou retorna None se não existir
            tipo_escola = mapa_tipo_escola.get(chave)
                
            #Verifica se queima ou separa o lixo
            if queima_lixo == '1':
                queima_lixo_ID = 'Q133235'
            else:
                queima_lixo_ID = None
    
            if separa_lixo == '0':
                separa_lixo_ID = 'Q135276205'
            elif separa_lixo == '1':
                separa_lixo_ID = 'Q931389'
            else:
                separa_lixo_ID = None
    
            esgoto_fossa_comum_ID = None
            esgoto_fossa_septica_ID = None
            esgoto_rede_ID = None    
                
            if esgoto_inexistente == '1':
                esgoto_prop = 'P6477'
    
            elif esgoto_inexistente == '0':
                esgoto_prop = 'P912'
                
                if esgoto_fossa_comum == '1':
                    esgoto_fossa_comum_ID = 'Q135336657'
    
                if esgoto_fossa_septica== '1':
                    esgoto_fossa_septica_ID = 'Q386300'
    
                if esgoto_rede == '1':
                    esgoto_rede_ID = 'Q156849'      
    
            energia_publica_ID = None
            energia_gerador_ID = None
            energia_renovavel_ID = None
                
            if energia_inexistente == '1':
                energia_prop = 'P6477'
    
            elif energia_inexistente == '0':
                energia_prop = 'P912'
    
                if energia_publica == '1':
                    energia_publica_ID = 'Q1096907'
                    
                if energia_gerador == '1':
                    energia_gerador_ID = 'Q135343942'
    
                if energia_renovavel == '1':
                    energia_renovavel_ID = 'Q12705'    
            
            # Criar um novo item vazio
            #item = pywikibot.ItemPage(repo)

            # Criar o item com labels e descrições
            #item.editEntity(dados, summary='Criando item para escola brasileira - Censo Escolar 2023')

            # Adicionar "instância de" (P31) = tipo_escola
            #adicionar_declaracao(item, 'P31', tipo_escola)

            # Adicionar "país" (P17) = Brasil (Q155)
            #adicionar_declaracao(item, 'P17', 'Q155')

            # Adicionar município (P131)
            #adicionar_declaracao(item, 'P131', municipio_ID)

            # Adicionar "Código INEP" (P11704) = código da escola (string)
            #adicionar_declaracao(item, 'P11704', codigo_inep, valor_tipo='string')

            # Adiciona as informações de tratamento de lixo
            #adicionar_declaracao(
            #    item = item,
            #    prop_id='P912',      #Instalações
            #    valor='Q180388',     #Gestão de resíduos sólidos
            #    qualificadores=[
            #        ('P1552', queima_lixo_ID, 'wikibase-item'),
            #        ('P1552', separa_lixo_ID, 'wikibase-item')           
            #    ]
            #)

            # Adiciona as informações de Esgoto
            #adicionar_declaracao(
            #    item = item,
            #    prop_id = esgoto_prop,
            #    valor = 'Q20127660',
            #    qualificadores=[
            #        ('P1552', esgoto_fossa_comum_ID, 'wikibase-item'),
            #        ('P1552', esgoto_fossa_septica_ID, 'wikibase-item'),
            #        ('P1552', esgoto_rede_ID, 'wikibase-item')
            #    ]
            #)

            # Adicionando as informações de Energia Elétrica
            #adicionar_declaracao(
            #    item = item,
            #    prop_id = energia_prop,
            #    valor = 'Q206799',
            #    qualificadores=[
            #        ('P1552', energia_publica_ID, 'wikibase-item'),
            #        ('P1552', energia_gerador_ID, 'wikibase-item'),
            #        ('P1552', energia_renovavel_ID, 'wikibase-item')
            #    ]
            #)

            # Adicionando quantidade de estudantes
            #adicionar_declaracao(
            #    item = item,
            #    prop_id = 'P2196',       # propriedade "número de alunos" no Wikidata
            #    valor = int(estudantes),
            #    valor_tipo = 'quantity',
            #    qualificadores=[
            #        ('P585', pywikibot.WbTime(year=2023, precision=9), 'time')
            #    ]
            #)

            # Adicionando quantidade de professores
            #adicionar_declaracao(
            #    item = item,
            #    prop_id = 'P10610',       # propriedade "número de professores" no Wikidata
            #    valor = int(professores),
            #    valor_tipo = 'quantity',
            #    qualificadores=[
            #        ('P585', pywikibot.WbTime(year=2023, precision=9), 'time')
            #    ]
            #)

            # Adicionando dados sobre coordenadas
            #if coordenadas_latitude and coordenadas_longitude:
            #    adicionar_declaracao(
            #        item = item,
            #        prop_id = 'P625',
            #        valor = {
            #            'latitude': coordenadas_latitude,
            #            'longitude': coordenadas_longitude
            #        },
            #        valor_tipo = 'coordinate'
            #    )

            #print(f'Item criado para a escola {nome} (código INEP: {codigo_inep})')
