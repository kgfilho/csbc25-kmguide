import os

import crewai.llms.cache as _crewai_cache
from crewai import Agent, LLM, Task

from youtube import pesquisar_videos_youtube

# CrewAI injects a `cache_breakpoint` field into every message, but only Anthropic's
# API accepts it — Groq (and other OpenAI-compatible providers) reject the request.
# strip_cache_breakpoint() exists in crewai but is never called for non-Anthropic
# providers, so we no-op the marker instead. See https://github.com/crewAIInc/crewAI/issues/5886
_crewai_cache.mark_cache_breakpoint = lambda message: message

GROQ_API_KEY_01 = os.getenv("GROQ_API_KEY_01")
# GROQ_API_KEY_02 é opcional: as duas chaves só existem para distribuir as
# chamadas entre agentes e reduzir o risco de esbarrar no limite de requisições
# de uma única conta Groq. Se não for definida, reaproveita a primeira chave.
GROQ_API_KEY_02 = os.getenv("GROQ_API_KEY_02") or GROQ_API_KEY_01

if not GROQ_API_KEY_01:
    raise RuntimeError(
        "Defina GROQ_API_KEY_01 nas variáveis de ambiente (veja .env.example)."
    )

# llama-3.3-70b-versatile foi descontinuado pela Groq em 16/08/2026;
# openai/gpt-oss-120b é o substituto recomendado.
# https://console.groq.com/docs/deprecations
GROQ_MODEL = "groq/openai/gpt-oss-120b"

groqllm = LLM(model=GROQ_MODEL, api_key=GROQ_API_KEY_01)
groqllm2 = LLM(model=GROQ_MODEL, api_key=GROQ_API_KEY_02)


def processar_topicos(topicos_str):
    """Converte uma string de tópicos separada por vírgulas em uma lista tratada."""
    return [t.strip() for t in topicos_str.split(",") if t.strip()]


def gerar_motivacao():
    agent = Agent(
        role="Motivador",
        goal="Escrever uma mensagem motivacional para o estudante.",
        backstory="Você é um coach motivacional com experiência em ajudar estudantes a manterem o foco.",
        llm=groqllm,
        verbose=True,
    )
    task = Task(
        description=(
            "Escreva uma mensagem motivacional para o estudante, formatada em Markdown.\n\n"
            "A mensagem deve conter:\n"
            "## Mensagem Motivacional 🎯\n\n"
            "- Um parágrafo inicial incentivando o estudante a seguir seus estudos.\n"
            "- Frases inspiradoras para manter o foco e a disciplina.\n"
            "- Um fechamento encorajador, reforçando a importância do esforço e da dedicação.\n\n"
            "O texto deve ser positivo, motivador e adequado para estudantes de ensino médio. "
            "O texto completo deve ter entre 150 e 200 palavras — nem mais curto, nem mais longo."
        ),
        agent=agent,
        expected_output="Mensagem motivacional em markdown, entre 150 e 200 palavras.",
    )
    return agent.execute_task(task)


def gerar_guia(disciplina, assunto, topicos):
    agent = Agent(
        role="Especialista em Guia de Estudos",
        goal="Criar um guia de estudos estruturado, explicativo e didático sobre um determinado assunto.",
        backstory="Você é um especialista em educação, com experiência na criação de guias de estudo detalhados.",
        llm=groqllm,
        verbose=True,
    )
    task = Task(
        description=(
            f"Crie um Guia de Estudos para {disciplina}, abordando {assunto} e os tópicos {topicos}. "
            "O guia deve seguir a seguinte estrutura e formatação:\n\n"
            f"## Guia de Estudos: {disciplina}\n\n"
            "### Introdução (80 a 120 palavras)\n"
            "- Texto introdutório justificado sobre o tema, destacando sua importância e contexto.\n\n"
            "### Conceitos Fundamentais\n"
            "- Explicação dos principais conceitos abordados, com exemplos práticos.\n"
            "- Utilize listas não ordenadas para estruturar os conceitos, com no máximo 3 a 5 bullets por conceito.\n\n"
            "### Aplicações Práticas\n"
            "- Explique como o tema se aplica no mundo real, com 2 a 3 exemplos concretos por conceito.\n"
            "- Utilize listas para organizar as aplicações.\n\n"
            "### Técnicas de Aprendizado e Dificuldades Comuns\n"
            "- Apresente métodos eficazes para aprender o tema (3 a 5 bullets).\n"
            "- Liste dificuldades comuns dos alunos e estratégias para superá-las (3 a 5 bullets).\n\n"
            "### Indicação de Materiais Gratuitos\n"
            "- Forneça de 3 a 5 sugestões de livros, vídeos e artigos gratuitos sobre o tema.\n"
            "- Apresente os materiais em formato de lista com títulos e links quando possível.\n\n"
            "O conteúdo deve ser didático, acessível para alunos do ensino médio e utilizar texto justificado sempre "
            "que possível. O guia completo (todas as seções somadas) deve ter entre 800 e 1200 palavras — respeite "
            "esse limite para manter o material objetivo."
        ),
        agent=agent,
        expected_output="Guia de estudos em markdown, entre 800 e 1200 palavras no total.",
    )
    return agent.execute_task(task)


def gerar_plano(disciplina, assunto, topicos, horas, dias):
    agent = Agent(
        role="Especialista em Plano de Estudos",
        goal="Criar um plano de estudos eficiente para que o aluno aprenda de maneira organizada.",
        backstory="Você é um planejador educacional especialista em cronogramas de estudo eficientes.",
        llm=groqllm2,
        verbose=True,
    )
    task = Task(
        description=(
            f"Crie um Plano de Estudos para {disciplina}, cobrindo {assunto} e os tópicos {topicos}. "
            f"O aluno tem {horas} horas por dia e {dias} dias para estudar.\n\n"
            "O plano deve seguir esta estrutura e formatação:\n\n"
            f"## Plano de Estudos: {disciplina}\n\n"
            "### Introdução (60 a 80 palavras)\n"
            "- Apresentação do objetivo do plano de estudos.\n"
            "- Importância da organização para otimizar o aprendizado.\n\n"
            "### Distribuição Equilibrada dos Tópicos\n"
            "- Divisão dos conteúdos de forma proporcional ao tempo disponível, em uma tabela com no máximo "
            "4 blocos de atividade por dia (agrupe atividades curtas em vez de listar cada minuto separadamente).\n"
            "- Sugerir uma agenda diária/semanal equilibrada.\n\n"
            "### Técnicas Ativas de Aprendizado\n"
            "- Explicação breve de estratégias eficazes para o estudo, incluindo:\n"
            "  - Resumos\n"
            "  - Flashcards\n"
            "  - Mapas mentais\n"
            "  - Resolução de exercícios\n\n"
            "### Revisões Programadas\n"
            "- Definir períodos estratégicos para revisão de conteúdos (3 a 5 bullets).\n"
            "- Sugestão de técnicas como repetição espaçada e autoavaliação.\n\n"
            "### Monitoramento do Progresso\n"
            "- Métodos para acompanhar a evolução do estudo (3 a 5 bullets).\n"
            "- Uso de checklists ou aplicativos para organização.\n\n"
            "### Sugestões para Pausas e Evitar Sobrecarga Mental\n"
            "- Importância das pausas regulares para manter a produtividade (3 a 5 bullets).\n"
            "- Sugestão de técnicas como a Técnica Pomodoro.\n\n"
            "O plano deve ser didático, bem estruturado e adaptável para alunos do ensino médio. O texto fora da "
            "tabela (todas as seções somadas) deve ter entre 400 e 600 palavras — respeite esse limite."
        ),
        agent=agent,
        expected_output=(
            "Plano de estudos estruturado em markdown, com tabela de no máximo 4 blocos por dia e "
            "texto de apoio entre 400 e 600 palavras."
        ),
    )
    return agent.execute_task(task)


def _padronizar_video(video):
    """Normaliza a caixa do título (maiúsculas) e da descrição (só a
    primeira letra maiúscula) antes de mandar para o agente, para que a
    formatação fique consistente independente do que o LLM decidir fazer."""
    titulo = video.get("Título", "").upper()
    descricao = video.get("Descrição", "").strip()
    if descricao:
        descricao = descricao[:1].upper() + descricao[1:]
    return {**video, "Título": titulo, "Descrição": descricao}


def gerar_videos(assunto, solicitacao):
    entrada_youtube = [_padronizar_video(v) for v in pesquisar_videos_youtube(solicitacao)]

    agent = Agent(
        role="Especialista em Curadoria de Vídeos Educacionais",
        goal="Organizar e formatar vídeos educacionais encontrados no YouTube para aprendizado eficiente.",
        backstory="Você é um especialista em curadoria de materiais educacionais, com experiência na seleção de vídeos para ensino.",
        llm=groqllm2,
        verbose=True,
    )
    task = Task(
        description=(
            f"Lista do Youtube: {entrada_youtube} "
            "Você receberá uma lista de vídeos extraída da API do YouTube. Sua tarefa é classificar e organizar os vídeos "
            "por categorias, formatando-os em Markdown. As categorias devem ser baseadas no título do vídeo.\n\n"
            f"## Vídeos sobre {assunto}\n\n"
            "### Formato de saída\n"
            "- Para cada vídeo, a saída deve seguir EXATAMENTE este formato, com o título e a descrição em "
            "linhas separadas (nunca na mesma linha):\n\n"
            "  **[TÍTULO DO VÍDEO](URL)**\n"
            "  Descrição do vídeo aqui.\n\n"
            "- Exemplo concreto:\n\n"
            "  **[COMO RESOLVER EQUAÇÕES DO 2º GRAU](https://www.youtube.com/watch?v=exemplo)**\n"
            "  Aprenda o passo a passo da fórmula de Bhaskara com exemplos práticos.\n\n"
            "- NÃO altere a caixa (maiúsculas/minúsculas) do título nem da descrição — eles já vêm formatados "
            "corretamente (título em maiúsculas, descrição com a primeira letra maiúscula) e devem ser reproduzidos "
            "exatamente como recebidos.\n"
            "- Se um vídeo não tiver descrição, substituir por '(Sem descrição disponível)'.\n"
            "- Se houver mais de um vídeo, repetir a estrutura para cada um, com uma linha em branco entre eles.\n"
            "- Certifique-se de que a formatação Markdown esteja correta e bem organizada."
            "Caso um dos videos seja esse: https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            "a saida deverá ser:"
            "- Caso a lista de vídeos não contenha resultados relevantes,"
            "pode haver a inserção automática de um vídeo genérico (exemplo:"
            "\\url{https://www.youtube.com/watch?v=dQw4w9WgXcQ}), utilizado"
            "como marcador de ausência de vídeos sobre o tema buscado."
            " Nesses casos, a saída deve ser:"
            "##Não foram encontrados vídeos sobre o assunto"
        ),
        agent=agent,
        expected_output="Lista de vídeos organizados em Markdown.",
    )
    return agent.execute_task(task)
