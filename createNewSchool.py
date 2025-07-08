# Tudo após "#" é um comentário

# Esse código foi desenvolvido para criar itens, no Wikidata, para escolas brasileiras que ainda não existem
# neste projeto. Utiliza, como fonte, o Censo Escolar de 2022. Para isso, segue três etapas:
# 1) A partir de um arquivo contendo dados do Censo, obtém o Código INEP de uma escola;
# 2) Realiza uma query (SPARQL) para conferir se a escola já existe no Wikidata;
# 3) Caso não exista, cria o item para a escola, contendo: "rótulo", "descrição", "instância de", "país" e "Código INEP";
# As três fases são realizadas em loop, até finalizar o arquivo fonte.

# Início do script

# Vamos trabalhar com pywikibot que é uma biblioteca, logo, precisamos importá-la
import pywikibot

# Etapa 1: obter os dados da escola de um arquivo fonte






# Etapa 2: realizar a consulta para verificar e existência (ou não) de um item

# Nesta variável, vamos armazenar nossa query
consulta = "desenvolver query aqui..."

# Para realizar a consulta, podemos utilizar essa função
generator = pagegenerators.WikidataSPARQLPageGenerator(sparql_query, site=site)





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

