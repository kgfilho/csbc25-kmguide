const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

/**
 * Abre uma conexão SSE com o backend para gerar o material de estudos.
 * onEvent é chamado a cada etapa com { stage, progress, message, content? }.
 * Retorna uma função para cancelar a conexão.
 */
export function gerarMaterial({ disciplina, assunto, topicos, horas, dias }, onEvent, onError) {
  const params = new URLSearchParams({ disciplina, assunto, topicos, horas, dias });
  const eventSource = new EventSource(`${API_BASE_URL}/api/generate?${params.toString()}`);

  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onEvent(data);
    if (data.stage === "done" || data.stage === "error") {
      eventSource.close();
    }
  };

  eventSource.onerror = () => {
    eventSource.close();
    onError?.(new Error("Conexão com o servidor perdida."));
  };

  return () => eventSource.close();
}

/**
 * Pede ao backend um PDF do conteúdo em Markdown informado e dispara o
 * download no navegador.
 */
export async function baixarPdf(content, title = "Plano de Estudos") {
  const response = await fetch(`${API_BASE_URL}/api/export-pdf`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content, title }),
  });

  if (!response.ok) {
    throw new Error("Não foi possível gerar o PDF.");
  }

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${title}.pdf`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
