export default function ProgressBar({ progress, message }) {
  return (
    <div className="flex flex-col gap-2">
      <div className="h-2.5 w-full overflow-hidden rounded-full bg-gray-200 dark:bg-gray-700">
        <div
          className="h-full rounded-full bg-purple-600 transition-all duration-500 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>
      <p className="text-sm text-gray-600 dark:text-gray-400">{message}</p>
    </div>
  );
}
