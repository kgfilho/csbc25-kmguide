import { useState } from "react";
import ReactMarkdown from "react-markdown";
import rehypeRaw from "rehype-raw";
import remarkGfm from "remark-gfm";
import { baixarMarkdown, baixarPdf } from "../api";

export default function MaterialResult({ content, disciplina }) {
  const [baixando, setBaixando] = useState(false);
  const [erroDownload, setErroDownload] = useState("");

  async function handleBaixarPdf() {
    setBaixando(true);
    setErroDownload("");
    try {
      await baixarPdf(content, `Material de Estudos - ${disciplina}`);
    } catch (err) {
      setErroDownload(err.message);
    } finally {
      setBaixando(false);
    }
  }

  function handleBaixarMarkdown() {
    setErroDownload("");
    try {
      baixarMarkdown(content, `Material de Estudos - ${disciplina}`);
    } catch (err) {
      setErroDownload(err.message);
    }
  }

  return (
    <div>
      {content && (
        <div className="mb-4 flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={handleBaixarPdf}
            disabled={baixando}
            className="rounded-lg border border-purple-600 px-3 py-1.5 text-sm font-medium text-purple-600 transition hover:bg-purple-50 disabled:cursor-not-allowed disabled:opacity-50 dark:hover:bg-purple-950"
          >
            {baixando ? "Gerando PDF..." : "⬇ Baixar Material Completo (PDF)"}
          </button>
          <button
            type="button"
            onClick={handleBaixarMarkdown}
            className="rounded-lg border border-purple-600 px-3 py-1.5 text-sm font-medium text-purple-600 transition hover:bg-purple-50 dark:hover:bg-purple-950"
          >
            ⬇ Baixar Material Completo (Markdown)
          </button>
          {erroDownload && <span className="text-sm text-red-600">{erroDownload}</span>}
        </div>
      )}

      <article className="prose prose-sm sm:prose-base max-w-none dark:prose-invert prose-a:text-purple-600">
        <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeRaw]}>
          {content}
        </ReactMarkdown>
      </article>
    </div>
  );
}
