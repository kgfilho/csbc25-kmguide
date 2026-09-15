# EDUC.AI — Guia de estudo personalizado com LLM e arquitetura multi-agente

Sistema de recomendação educacional que gera guias e planos de estudo personalizados
usando LLMs (via [Groq](https://groq.com/)) orquestrados com [CrewAI](https://www.crewai.com/),
além de curadoria de vídeos do YouTube. O projeto foi avaliado com alunos de um curso
técnico em Informática (modelo TAM) e publicado no CSBC 2025.

O sistema é dividido em dois projetos independentes:

- **[`backend/`](backend)** — API em **FastAPI** que orquestra os agentes CrewAI e expõe
  o progresso da geração via **Server-Sent Events (SSE)**.
- **[`frontend/`](frontend)** — interface em **React (Vite + Tailwind)** para os alunos
  preencherem o formulário e acompanharem a geração do material em tempo real.

A interface original do protótipo usava [Gradio](https://www.gradio.app/); ela foi
substituída por essa arquitetura cliente/servidor para permitir disponibilizar a
ferramenta de forma mais robusta aos alunos.

> **Nota sobre o nome**: o link do código-fonte citado no artigo do CSBC 2025 continua no
> ar, mas o projeto mudou de nome desde então — era **KMGuide** no artigo, e hoje se
> chama **EDUC.AI**. É o mesmo projeto, apenas renomeado.

## ✨ Funcionalidades

- Geração de material personalizado com progresso em tempo real (SSE).
- Conteúdo com tamanho e estrutura padronizados (veja a seção "Padrão de conteúdo" abaixo).
- Download do material completo em **PDF** (motivação, guia, plano e vídeos), com fonte
  com suporte a acentos, travessões e aspas tipográficas.
- Curadoria de vídeos do YouTube com título e descrição em formatação padronizada.

## 🧠 Agentes Inteligentes

1. **Motivador** — escreve uma mensagem motivacional para o estudante.
2. **Especialista em Guia de Estudos** — cria um guia estruturado sobre a disciplina/assunto.
3. **Especialista em Plano de Estudos** — cria um cronograma de estudos considerando tempo disponível.
4. **Especialista em Curadoria de Vídeos** — busca e organiza vídeos do YouTube sobre o tema.

## 📏 Padrão de conteúdo

Para manter o material consistente entre gerações, os prompts dos agentes seguem limites
explícitos de tamanho e estrutura:

| Seção | Limite |
|---|---|
| Motivação | 150–200 palavras |
| Guia de Estudos | 800–1200 palavras no total, 3–5 bullets por conceito |
| Plano de Estudos | Tabela com no máximo 4 blocos de atividade por dia, texto de apoio de 400–600 palavras |
| Vídeos | Até 5 vídeos, título em maiúsculas e descrição com a primeira letra maiúscula |

## 🛠️ Tecnologias

- **Backend**: Python 3.11+, FastAPI, Uvicorn, CrewAI, Groq, YouTube Data API v3, xhtml2pdf (exportação em PDF)
- **Frontend**: React 19, Vite, Tailwind CSS v4, react-markdown

> A exportação em PDF usa a fonte [Bitstream Vera](https://www.gnome.org/fonts/) (licença
> livre, distribuída junto com o `reportlab`), embutida em `backend/assets/fonts/`, para
> suportar acentos, travessões e aspas tipográficas corretamente.

## 🚀 Como rodar localmente

### 1. Backend

```sh
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate   # Linux/macOS

pip install -r requirements.txt
cp .env.example .env
```

Preencha o `.env` com suas chaves:

- `GROQ_API_KEY_01`: chave da [Groq](https://console.groq.com/) (obrigatória).
- `GROQ_API_KEY_02`: segunda chave da Groq (opcional). Se deixada em branco, os agentes
  reaproveitam `GROQ_API_KEY_01`. As duas existem só para distribuir a carga entre contas
  e reduzir o risco de esbarrar no limite de requisições.
- `YOUTUBE_API_KEY`: chave da [YouTube Data API v3](https://console.cloud.google.com/apis/library/youtube.googleapis.com).

Suba a API:

```sh
uvicorn main:app --reload --port 8000
```

A documentação interativa fica disponível em `http://localhost:8000/docs`.

### 2. Frontend

Em outro terminal:

```sh
cd frontend
npm install
npm run dev
```

Acesse `http://localhost:5173`. Por padrão o frontend aponta para a API em
`http://localhost:8000`; para apontar para outro endereço, crie um `frontend/.env.local`
com `VITE_API_BASE_URL=http://seu-backend:porta`.

## 📖 Como Funciona

1. O aluno preenche o formulário (disciplina, assunto, tópicos, tempo diário e dias disponíveis).
2. O frontend abre uma conexão SSE com `GET /api/generate` no backend.
3. Os agentes são executados em sequência (motivação → guia → plano → vídeos), e cada
   etapa concluída atualiza a barra de progresso em tempo real.
4. Ao final, o aluno recebe o material completo renderizado em Markdown na tela, com a
   opção de baixar tudo em PDF (`POST /api/export-pdf`).

## 📌 Como Contribuir

1. **Fork** o repositório.
2. Crie uma **branch** para a sua funcionalidade (`git checkout -b minha-feature`).
3. Faça o **commit** das suas alterações (`git commit -m 'Adiciona nova feature'`).
4. Faça o **push** para a branch (`git push origin minha-feature`).
5. Abra um **Pull Request**.
