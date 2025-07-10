# Tudo após "#" é um comentário

# Esse código foi desenvolvido para criar itens, no Wikidata, para escolas brasileiras que ainda não existem
# neste projeto. Utiliza, como fonte, o Censo Escolar de 2022. Para isso, segue três etapas:
# 1) A partir de um arquivo contendo dados do Censo, obtém os dados das escolas;
# 2) Realiza uma query (SPARQL) para conferir se a escola já existe no Wikidata;
# 3) Caso não exista, cria o item para a escola, contendo: "rótulo", "descrição", "instância de", "país" e "Código INEP";
# As três fases são realizadas em loop, até finalizar o arquivo fonte.

# Definindo funções

# Função para adicionar declarações
def adicionar_declaracao(item, prop_id, valor, valor_tipo='wikibase-item'):
    declaracao = pywikibot.Claim(repo, prop_id)

    # Define o valor da declaração
    if valor_tipo == 'wikibase-item':
        target = pywikibot.ItemPage(repo, valor)
        declaracao.setTarget(target)
    elif valor_tipo == 'string':
        declaracao.setTarget(str(valor))
    else:
        raise ValueError('Tipo de valor não suportado')

    # Adiciona a declaração ao item
    item.addClaim(declaracao, summary=f'Adicionando propriedade {prop_id}')

    # Adiciona sempre a mesma referência (Censo Escolar 2023, com a mesma data de acesso)
    # Adiciona referência: P248 (afirmado em) → Q133805362
    ref_fonte = pywikibot.Claim(repo, 'P248')
    item_fonte = pywikibot.ItemPage(repo, 'Q133805362')
    ref_fonte.setTarget(item_fonte)

    # Adiciona referência: P813 (data de consulta) → 10/07/2025
    data_consulta = WbTime(year=2025, month=7, day=10)
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
        
        # Armazenar os valores em uma novas variáveis, para reutilizar depois, nos passos 2 e 3
        nome = formatar_nome(linha['NO_ENTIDADE'])
        codigo_inep = linha['CO_ENTIDADE']
        municipio = linha['NO_MUNICIPIO']
        codigo_municipio = linha['CO_MUNICIPIO']
        estudantes = linha['QT_MAT_BAS']
        professores = linha['QT_DOC_BAS']
        localizacao = linha['TP_LOCALIZACAO']
        localizacao_diferenciada = linha['TP_LOCALIZACAO_DIFERENCIADA']        
        
        # Final da Etapa 1
        
        # Etapa 2: realizar a consulta para verificar e existência (ou não) de um item

        # Nesta variável, vamos armazenar nossa query
        consulta = "SELECT ?item ?itemLabel  WHERE { ?item wdt:P31 wd:Q3914 . ?item wdt:P11704 '" + codigo_inep + "' . }"

        # Definindo o site (wikidata)
        site = pywikibot.Site("wikidata", "wikidata")
        repo = site.data_repository()
        
        # Checando se existe um item ou não
        if any(pagegenerators.WikidataSPARQLPageGenerator(consulta, site=site)):
            print(f"A escola {nome} já existe no Wikidata. Prosseguindo para a próxima.")
        else:
            print(f"A escola {nome} ainda não existe no Wikidata. Prosseguindo para criação do item.")

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
        
            # Criar um novo item vazio
            #item = pywikibot.ItemPage(repo)

            # Criar o item com labels e descrições
            #item.editEntity(dados, summary='Criando item para escola brasileira - Censo Escolar 2023')

            # Adicionar "instância de" (P31) = tipo_escola
            #adicionar_declaracao(item, 'P31', tipo_escola)

            # Adicionar "país" (P17) = Brasil (Q155)
            #adicionar_declaracao(item, 'P17', 'Q155')

            # Adicionar "Código INEP" (P11704) = código da escola (string)
            #adicionar_declaracao(item, 'P11704', codigo_inep, valor_tipo='string')

            print(f'Item criado para a escola {nome} (código INEP: {codigo_inep})')