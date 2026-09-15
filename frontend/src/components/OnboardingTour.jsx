import { useCallback, useEffect, useState } from "react";

const STORAGE_KEY = "educai_tour_seen";

const STEPS = [
  {
    target: '[data-tour="header"]',
    title: "Bem-vindo ao EDUC.AI",
    text: "Esse assistente gera guia de estudos, plano de estudos, mensagem motivacional e vídeos personalizados, usando agentes de IA. Vamos te mostrar como usar em poucos passos.",
  },
  {
    target: '[data-tour="disciplina-assunto"]',
    title: "Disciplina e assunto",
    text: "Diga qual matéria e qual assunto você quer estudar. Quanto mais específico o assunto, melhor o material gerado.",
  },
  {
    target: '[data-tour="topicos"]',
    title: "Tópicos",
    text: "Liste os pontos que o guia e o plano devem cobrir, separados por vírgula.",
  },
  {
    target: '[data-tour="tempo"]',
    title: "Tempo disponível",
    text: "Informe quantas horas por dia e quantos dias você tem para estudar — o plano distribui os blocos de estudo com base nesses números.",
  },
  {
    target: '[data-tour="gerar"]',
    title: "Gerar material",
    text: "Clique aqui para os quatro agentes de IA começarem a trabalhar. Uma barra de progresso mostra cada etapa em tempo real.",
  },
  {
    target: '[data-tour="resultado"]',
    title: "Seu material aparece aqui",
    text: "Motivação, guia, plano e vídeos aparecem nesta área. Quando estiver pronto, use o botão \"Baixar Material Completo (PDF)\" para levar tudo com você.",
  },
];

export default function OnboardingTour({ restartSignal }) {
  const [stepIndex, setStepIndex] = useState(0);
  // Primeira visita: abre sozinho se o aluno ainda não viu o tour.
  const [open, setOpen] = useState(() => {
    try {
      return !localStorage.getItem(STORAGE_KEY);
    } catch {
      // localStorage indisponível (ex: modo privado) — não bloqueia o uso.
      return false;
    }
  });
  const [rect, setRect] = useState(null);

  // Botão "Como usar?": reabre do início sempre que for acionado.
  useEffect(() => {
    if (restartSignal > 0) {
      setStepIndex(0);
      setOpen(true);
    }
  }, [restartSignal]);

  const medirAlvo = useCallback(() => {
    if (!open) return;
    const el = document.querySelector(STEPS[stepIndex].target);
    if (!el) return;
    el.scrollIntoView({ behavior: "smooth", block: "center" });
    const atualizar = () => setRect(el.getBoundingClientRect());
    atualizar();
    const timeout = setTimeout(atualizar, 300);
    return () => clearTimeout(timeout);
  }, [open, stepIndex]);

  useEffect(() => {
    const limpar = medirAlvo();
    window.addEventListener("resize", medirAlvo);
    return () => {
      window.removeEventListener("resize", medirAlvo);
      limpar?.();
    };
  }, [medirAlvo]);

  function finalizar() {
    setOpen(false);
    try {
      localStorage.setItem(STORAGE_KEY, "1");
    } catch {
      // localStorage indisponível — sem problema, só não lembra da próxima vez.
    }
  }

  function avancar() {
    if (stepIndex === STEPS.length - 1) {
      finalizar();
    } else {
      setStepIndex((i) => i + 1);
    }
  }

  if (!open || !rect) return null;

  const step = STEPS[stepIndex];
  const padding = 8;
  const destaque = {
    top: rect.top - padding,
    left: rect.left - padding,
    width: rect.width + padding * 2,
    height: rect.height + padding * 2,
  };

  const larguraTooltip = 320;
  const espacoAbaixo = window.innerHeight - rect.bottom;
  const mostrarAbaixo = espacoAbaixo > 190;
  const tooltipTop = mostrarAbaixo ? destaque.top + destaque.height + 12 : Math.max(16, destaque.top - 172);
  const tooltipLeft = Math.min(Math.max(16, rect.left), window.innerWidth - larguraTooltip - 16);

  return (
    <>
      <div className="fixed inset-0 z-40" aria-hidden="true" />
      <div
        className="fixed z-40 rounded-xl motion-reduce:transition-none transition-all duration-300 pointer-events-none"
        style={{ ...destaque, boxShadow: "0 0 0 9999px rgba(15, 10, 25, 0.65)" }}
      />
      <div
        role="dialog"
        aria-modal="true"
        className="fixed z-50 rounded-xl border border-purple-300 bg-white p-4 shadow-xl dark:border-purple-700 dark:bg-gray-900"
        style={{ top: tooltipTop, left: tooltipLeft, width: larguraTooltip }}
      >
        <p className="text-xs font-medium text-purple-600">
          Passo {stepIndex + 1} de {STEPS.length}
        </p>
        <h3 className="mt-1 text-base font-semibold text-gray-900 dark:text-gray-100">{step.title}</h3>
        <p className="mt-1.5 text-sm text-gray-600 dark:text-gray-400">{step.text}</p>
        <div className="mt-4 flex items-center justify-between">
          <button
            type="button"
            onClick={finalizar}
            className="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            Pular
          </button>
          <button
            type="button"
            onClick={avancar}
            className="rounded-lg bg-purple-600 px-4 py-1.5 text-sm font-medium text-white transition hover:bg-purple-700"
          >
            {stepIndex === STEPS.length - 1 ? "Concluir" : "Próximo"}
          </button>
        </div>
      </div>
    </>
  );
}
