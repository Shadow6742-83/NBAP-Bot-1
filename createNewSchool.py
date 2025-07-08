# Tudo após "#" é um comentário

# Esse script foi desenvolvido para criar itens, no Wikidata, para escolas brasileiras que ainda não existem
# neste projeto. Utiliza, como fonte, o Censo Escolar de 2022. Para isso, segue três etapas:
# 1) A partir de um arquivo contendo dados do Censo, obtém o Código INEP de uma escola;
# 2) Realiza uma query (SPARQL) para conferir se a escola já existe no Wikidata;
# 3) Caso não exista, cria o item para a escola, contendo: "rótulo", "descrição", "instância de", "país" e "Código INEP";
# As três fases são realizadas em loop, até finalizar o arquivo fonte.

# Início do script

# Vamos trabalhar com pywikibot que é uma biblioteca, logo, precisamos importá-la
import pywikibot

# Etapa 1: obter o código INEP de um arquivo fonte
# Desenvolver etapa 1 aqui...


# Etapa 2: realizar a consulta para verificar e existência (ou não) de um item
# Desenvolver etapa 2 aqui...


# Etapa 3: caso o item ainda não exista (conforme verificado na etapa 2), criá-lo
# Desenvolver etapa 3 aqui...

