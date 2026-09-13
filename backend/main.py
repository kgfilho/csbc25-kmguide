import asyncio
import io
import json

from dotenv import load_dotenv

load_dotenv()

import markdown as markdown_lib
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel
from xhtml2pdf import pisa

import agents

app = FastAPI(title="KMGuide API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def sse_event(stage: str, progress: int, message: str = "", **extra) -> str:
    payload = {"stage": stage, "progress": progress, "message": message, **extra}
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
        yield sse_event("done", 100, "Processo concluído!", content=saida_completa, plano=saida_plano)
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


class ExportPdfRequest(BaseModel):
    title: str = "Plano de Estudos"
    content: str


PDF_STYLE = """
<style>
  @page { size: A4; margin: 2cm; }
  body { font-family: Helvetica, sans-serif; font-size: 11pt; color: #1f2933; }
  h1 { color: #6d28d9; font-size: 20pt; }
  h2 { color: #6d28d9; font-size: 15pt; margin-top: 16pt; }
  h3 { font-size: 12.5pt; margin-top: 12pt; }
  table { border-collapse: collapse; width: 100%; margin: 8pt 0; }
  th, td { border: 1px solid #999; padding: 4px 8px; font-size: 9.5pt; text-align: left; }
  th { background-color: #f3e8ff; }
  code { background-color: #f4f3ec; padding: 1px 4px; }
</style>
"""


@app.post("/api/export-pdf")
async def export_pdf(payload: ExportPdfRequest):
    html_body = markdown_lib.markdown(payload.content, extensions=["tables"])
    html = f"<html><head><meta charset='utf-8'>{PDF_STYLE}</head><body>{html_body}</body></html>"

    pdf_buffer = io.BytesIO()
    pisa.CreatePDF(html, dest=pdf_buffer, encoding="utf-8")

    safe_filename = "".join(c if c.isalnum() or c in " -_" else "" for c in payload.title).strip() or "documento"
    return Response(
        content=pdf_buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{safe_filename}.pdf"'},
    )


@app.get("/api/health")
async def health():
    return {"status": "ok"}
