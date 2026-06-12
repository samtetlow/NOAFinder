interface AppPlaceholderProps {
  title: string;
  description?: string;
  parentTitle?: string;
}

export function AppPlaceholder({
  title,
  description,
  parentTitle,
}: AppPlaceholderProps) {
  return (
    <div className="max-w-3xl mx-auto mt-12">
      <div className="rounded-2xl bg-white shadow-sm border border-brand/10 p-10 text-center">
        {parentTitle ? (
          <div className="text-xs uppercase tracking-wide text-brand/50 mb-2">
            {parentTitle}
          </div>
        ) : null}
        <h1 className="text-3xl font-semibold text-brand-ink">{title}</h1>
        {description ? (
          <p className="text-sm text-brand/60 mt-3">{description}</p>
        ) : null}
        <div className="mt-8 inline-block rounded-full bg-brand/5 px-4 py-1.5 text-xs uppercase tracking-wide text-brand">
          Coming soon
        </div>
      </div>
    </div>
  );
}
