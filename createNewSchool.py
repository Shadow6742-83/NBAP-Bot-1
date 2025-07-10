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
        consulta = "SELECT ?item ?itemLabel  WHERE { ?item wdt:P31 wd:Q3914 . ?item wdt:P11704 '" + codigoInep + "' . }"


        # Definindo o site (wikidata)
        site = pywikibot.Site("wikidata", "wikidata")
        repo = site.data_repository()

        
        # Checando se existe um item ou não
        if any(pagegenerators.WikidataSPARQLPageGenerator(consulta, site=site)):
           print("A consulta retornou resultados.")
        else:
            print("A consulta não retornou nenhum resultado.")

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
    
            # Criar um novo item vazio
            item = pywikibot.ItemPage(repo)

            # Criar o item com labels e descrições
            item.editEntity(dados, summary='Criando item para escola brasileira - Censo Escolar 2023')

            # Função auxiliar para adicionar declarações (claims)
            def adicionar_claim(item, prop_id, valor, valor_tipo='wikibase-item'):
                claim = pywikibot.Claim(repo, prop_id)
                if valor_tipo == 'wikibase-item':
                    target = pywikibot.ItemPage(repo, valor)
                    claim.setTarget(target)
                elif valor_tipo == 'string':
                    claim.setTarget(str(valor))
                else:
                    raise ValueError('Tipo de valor não suportado')
                item.addClaim(claim, summary=f'Adicionando propriedade {prop_id}')

            # Adicionar "instância de" (P31) = escola (Q3914)
            adicionar_claim(item, 'P31', 'Q3914')

            # Adicionar "país" (P17) = Brasil (Q155)
            adicionar_claim(item, 'P17', 'Q155')

            # Adicionar "Código INEP" (P11704) = código da escola (string)
            adicionar_claim(item, 'P11704', codigoInep, valor_tipo='string')

            print(f'Item criado para a escola "{nome}" (Código INEP {codigoInep})')
