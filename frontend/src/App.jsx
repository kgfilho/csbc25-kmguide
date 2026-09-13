import { useState } from "react";
import { gerarMaterial } from "./api";
import MaterialResult from "./components/MaterialResult";
import ProgressBar from "./components/ProgressBar";
import StudyForm from "./components/StudyForm";

export default function App() {
  const [status, setStatus] = useState("idle"); // idle | loading | done | error
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState("");
  const [content, setContent] = useState("");
  const [disciplina, setDisciplina] = useState("");
  const [error, setError] = useState("");

  function handleSubmit(form) {
    setStatus("loading");
    setProgress(0);
    setMessage("Iniciando...");
    setContent("");
    setDisciplina(form.disciplina);
    setError("");

    gerarMaterial(
      form,
      (event) => {
        setProgress(event.progress);
        setMessage(event.message);
        if (event.stage === "done") {
          setContent(event.content);
          setStatus("done");
        } else if (event.stage === "error") {
          setError(event.message);
          setStatus("error");
        }
      },
      (err) => {
        setError(err.message);
        setStatus("error");
      },
    );
  }

  return (
    <div className="mx-auto min-h-screen max-w-4xl px-4 py-10">
      <header className="mb-8 text-center">
        <h1 className="text-3xl font-semibold text-gray-900 dark:text-gray-100">
          📚 KMGuide
        </h1>
        <p className="mt-1 text-gray-600 dark:text-gray-400">
          Guia e plano de estudos personalizados, gerados por agentes de IA
        </p>
      </header>

      <div className="grid gap-8 md:grid-cols-2">
        <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-900">
          <StudyForm onSubmit={handleSubmit} disabled={status === "loading"} />

          {status === "loading" && (
            <div className="mt-6">
              <ProgressBar progress={progress} message={message} />
            </div>
          )}

          {status === "error" && (
            <p className="mt-6 rounded-lg bg-red-50 p-3 text-sm text-red-700 dark:bg-red-950 dark:text-red-300">
              {error}
            </p>
          )}
        </section>

        <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-900">
          {status === "done" ? (
            <MaterialResult content={content} disciplina={disciplina} />
          ) : (
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Preencha o formulário e clique em "Gerar Material" para ver aqui o seu
              guia de estudos, plano de estudos, mensagem motivacional e vídeos
              recomendados.
            </p>
          )}
        </section>
      </div>
    </div>
  );
}
