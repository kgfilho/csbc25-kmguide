import requests

WIKIPEDIA_API_URL = "https://pt.wikipedia.org/w/api.php"

# A Wikimedia bloqueia com 403 Forbidden requisições sem um User-Agent que
# identifique a aplicação (política deles: https://meta.wikimedia.org/wiki/User-Agent_policy).
# O User-Agent padrão do `requests` ("python-requests/x.x") cai nesse bloqueio.
HEADERS = {"User-Agent": "EDUC.AI/1.0 (https://github.com/kgfilho/csbc25-kmguide)"}


def pesquisar_wikipedia(topicos, num_resultados=2):
    """
    Pesquisa artigos na Wikipedia em português para uma lista de tópicos,
    garantindo pelo menos um resultado por tópico quando possível.

    Args:
        topicos (list[str] | str): um tópico ou lista de tópicos de pesquisa.
        num_resultados (int, opcional): número máximo de artigos por tópico. Padrão: 2.

    Returns:
        list: lista de dicionários com Tópico, Título, URL e Trecho de cada artigo.
    """
    if isinstance(topicos, str):
        topicos = [topicos]

    artigos = []
    for topico in topicos:
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": topico,
            "srlimit": num_resultados,
            "utf8": 1,
        }
        try:
            resposta = requests.get(WIKIPEDIA_API_URL, params=params, headers=HEADERS, timeout=10)
            resposta.raise_for_status()
            resultados = resposta.json().get("query", {}).get("search", [])
        except Exception as e:
            print(f"Erro ao buscar '{topico}' na Wikipedia: {e}")
            continue

        for item in resultados:
            titulo = item["title"]
            trecho = item["snippet"].replace('<span class="searchmatch">', "").replace("</span>", "")
            artigos.append(
                {
                    "Tópico": topico,
                    "Título": titulo,
                    "URL": f"https://pt.wikipedia.org/wiki/{titulo.replace(' ', '_')}",
                    "Trecho": trecho,
                }
            )

    return artigos
