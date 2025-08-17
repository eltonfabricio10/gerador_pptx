# -*- coding: utf-8 -*-
import requests
import sys
import os

# Substitua pela sua chave de API obtida no Google Cloud
API_KEY = os.getenv("GOOGLE_API_KEY")  # Sua chave de API

# ID do motor de busca (CX) gerado na configuração do seu CSE
CX = os.getenv("GOOGLE_ID_CX")  # Seu ID de motor de busca


# Função para buscar no Google Custom Search
def search_google(query):
    url = f'https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={CX}&num=7'
    response = requests.get(url)

    if response.status_code == 200:
        results = response.json()
        search_results = []

        # Extrai título, link, descrição e outros detalhes dos resultados
        for item in results.get('items', []):
            result = {
                'title': item.get('title'),
                'link': item.get('link')
            }
            search_results.append(result)

        return search_results
    else:
        return []


if __name__ == '__main__':
    # Exemplo de busca
    query = sys.argv[1]
    search_results = search_google(query)
    # Exibe os resultados com título, link, descrição e URL formatada
    for s in search_results:
        print(s)
