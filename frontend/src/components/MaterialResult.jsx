import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function MaterialResult({ content }) {
  return (
    <article className="prose prose-sm sm:prose-base max-w-none dark:prose-invert prose-a:text-purple-600">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
    </article>
  );
}
