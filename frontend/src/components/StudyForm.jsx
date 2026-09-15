import { useState } from "react";

const initialState = {
  disciplina: "Matemática",
  assunto: "Funções",
  topicos: "Função quadrática, Função exponencial, Função logarítmica",
  horas: "2",
  dias: "5",
};

export default function StudyForm({ onSubmit, disabled }) {
  const [form, setForm] = useState(initialState);

  function handleChange(field) {
    return (event) => setForm((prev) => ({ ...prev, [field]: event.target.value }));
  }

  function handleSubmit(event) {
    event.preventDefault();
    onSubmit(form);
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <div data-tour="disciplina-assunto" className="grid gap-4 sm:grid-cols-2">
        <Field label="Disciplina" value={form.disciplina} onChange={handleChange("disciplina")} disabled={disabled} />
        <Field label="Assunto" value={form.assunto} onChange={handleChange("assunto")} disabled={disabled} />
      </div>
      <div data-tour="topicos">
        <Field
          label="Tópicos (separados por vírgula)"
          value={form.topicos}
          onChange={handleChange("topicos")}
          disabled={disabled}
        />
      </div>
      <div data-tour="tempo" className="grid grid-cols-2 gap-4 sm:max-w-xs">
        <Field
          label="Tempo diário (horas)"
          type="number"
          min="1"
          max="24"
          value={form.horas}
          onChange={handleChange("horas")}
          disabled={disabled}
        />
        <Field
          label="Quantos dias"
          type="number"
          min="1"
          max="90"
          value={form.dias}
          onChange={handleChange("dias")}
          disabled={disabled}
        />
      </div>
      <button
        type="submit"
        data-tour="gerar"
        disabled={disabled}
        className="mt-2 rounded-lg bg-purple-600 px-4 py-2.5 font-medium text-white transition hover:bg-purple-700 disabled:cursor-not-allowed disabled:opacity-50 sm:self-start sm:px-8"
      >
        {disabled ? "Gerando..." : "Gerar Material"}
      </button>
    </form>
  );
}

function Field({ label, value, onChange, disabled, type = "text", min, max }) {
  return (
    <label className="flex flex-col gap-1 text-sm font-medium text-gray-700 dark:text-gray-300">
      {label}
      <input
        type={type}
        min={min}
        max={max}
        value={value}
        onChange={onChange}
        disabled={disabled}
        className="rounded-lg border border-gray-300 px-3 py-2 text-base font-normal text-gray-900 outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-200 disabled:bg-gray-100 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100"
        required
      />
    </label>
  );
}
