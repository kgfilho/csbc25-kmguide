import asyncio
import json

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

import agents

app = FastAPI(title="KMGuide API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def sse_event(stage: str, progress: int, message: str = "", content: str | None = None) -> str:
    payload = {"stage": stage, "progress": progress, "message": message}
    if content is not None:
        payload["content"] = content
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


async def gerar_material_stream(disciplina, assunto, topicos_str, horas, dias):
    topicos = agents.processar_topicos(topicos_str)
    solicitacao = f"Disciplina: {disciplina}\nAssunto: {assunto}\nTópicos: {topicos}\n"

    try:
        yield sse_event("motivacao", 10, "Criando mensagem motivacional...")
        saida_motivador = await asyncio.to_thread(agents.gerar_motivacao)

        yield sse_event("guia", 35, "Gerando guia de estudos...")
        saida_guia = await asyncio.to_thread(agents.gerar_guia, disciplina, assunto, topicos)

        yield sse_event("plano", 60, "Criando plano de estudos...")
        saida_plano = await asyncio.to_thread(agents.gerar_plano, disciplina, assunto, topicos, horas, dias)

        yield sse_event("videos", 85, "Buscando e organizando vídeos do YouTube...")
        saida_youtube = await asyncio.to_thread(agents.gerar_videos, assunto, solicitacao)

        saida_completa = f"""# 🎯 Motivação
{saida_motivador}

---

# 📖 Guia de Estudos
{saida_guia}

---

# 📅 Plano de Estudos
{saida_plano}

---

# 🎥 Vídeos Educacionais
{saida_youtube}
"""
        yield sse_event("done", 100, "Processo concluído!", content=saida_completa)
    except Exception as exc:
        yield sse_event("error", 0, f"Erro ao gerar material: {exc}")


@app.get("/api/generate")
async def generate(
    disciplina: str = Query(...),
    assunto: str = Query(...),
    topicos: str = Query(""),
    horas: str = Query(...),
    dias: str = Query(...),
):
    return StreamingResponse(
        gerar_material_stream(disciplina, assunto, topicos, horas, dias),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/api/health")
async def health():
    return {"status": "ok"}
