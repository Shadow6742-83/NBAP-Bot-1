# Tudo após "#" é um comentário

# Esse código foi desenvolvido para criar itens, no Wikidata, para escolas brasileiras que ainda não existem
# neste projeto. Utiliza, como fonte, o Censo Escolar de 2022. Para isso, segue três etapas:
# 1) A partir de um arquivo contendo dados do Censo, obtém os dados das escolas;
# 2) Realiza uma query (SPARQL) para conferir se a escola já existe no Wikidata;
# 3) Caso não exista, cria o item para a escola, contendo: "rótulo", "descrição", "instância de", "país" e "Código INEP";
# As três fases são realizadas em loop, até finalizar o arquivo fonte.

# Início do script

# Vamos trabalhar com pywikibot que é uma biblioteca, logo, precisamos importá-la
import pywikibot

#A função PageGenerator interpreta a consulta SPARQL e retorna objetos pywikibot.
from pywikibot import pagegenerators 

# Vamos utilizar essa biblioteca para ler o arquivo fonte, que está salvo no formato csv
import csv

# Etapa 1: obter os dados da escola de um arquivo fonte

# Definindo qual é o arquivo fonte (com os dados que iremos importar)
arquivoFonte = 'microdados_ed_basica_2023_sc_resumido.csv'

# Precisamos que o programa abra o arquivo fonte, e armazene seu conteúdo em uma variável para que possamos usá-lo
# Nesse caso, a variável será arquivoCsv
with open(arquivoFonte, newline='', encoding='utf-8') as arquivoCsv:

    # Vamos usar a classe DictReader, da biblioteca csv que importamos na linha 16, para processar nosso arquivo fonte,
    # que está no formato .csv. Cada linha de conteúdo será armazenada como um objeto, com cabeçalho
    leitor = csv.DictReader(arquivoCsv, delimiter=';')

    # Cada objeto do arquivo (cada linha), será armazenado na variável 'linha', e para cada linha, faremos o seguinte:
    # Importante: esse é o loop de nosso código, onde para cada linha (cada escola) o programa repetirá todas as
    # instruções abaixo:
    for linha in leitor:

        # Armazenar os valores em uma novas variáveis, para reutilizar depois, nos passos 2 e 3
        nome = linha['NO_ENTIDADE']
        codigoInep = linha['CO_ENTIDADE']
        municipio = linha['NO_MUNICIPIO']
        codigoMunicipio = linha['CO_MUNICIPIO']
        estudantes = linha['QT_MAT_BAS']
        professores = linha['QT_DOC_BAS']
        localizacao = linha['TP_LOCALIZACAO']
        localizacaoDiferenciada = linha['TP_LOCALIZACAO_DIFERENCIADA']        

        # Final da Etapa 1

        # Etapa 2: realizar a consulta para verificar e existência (ou não) de um item

        # Nesta variável, vamos armazenar nossa query
        consulta = "SELECT ?item ?itemLabel  WHERE { ?item wdt:P31 wd:Q3914 . ?item wdt:P11704 '42021960' . }"


        # Definindo o site (wikidata)
        site = pywikibot.Site("wikidata", "wikidata")
        repo = site.data_repository()

        
        # Para realizar a consulta, podemos utilizar essa função
        generator = pagegenerators.WikidataSPARQLPageGenerator(sparql_query, site=site)

        # Iterando sobre os itens retornados
        for item in generator:
            print(f"{item.title()} - {item.get()['labels'].get('pt', 'Sem rótulo em pt')}")



        # Etapa 3: caso o item ainda não exista (conforme verificado na etapa 2), criá-lo

        # Nesta variável (array), vamos armazenar as informações que gostaríamos de adicionar em nosso item
        dados = {
            'labels': {
                'en': 'Exemplo de rótulo em inglês',
                'pt': 'Exemplo de rótulo em português',
            },
            'descriptions': {
                'en': 'Exemplo de descrição em inglês',
                'pt': 'Exemplo de descrição em português',
            }
        }
