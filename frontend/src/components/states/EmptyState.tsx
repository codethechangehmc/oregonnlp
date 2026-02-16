export default function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-28 text-center animate-fade-in">
      {/* Decorative rings */}
      <div className="relative w-24 h-24 mb-8">
        <div className="absolute inset-0 rounded-full border border-border" />
        <div className="absolute inset-3 rounded-full border border-border-bright" />
        <div className="absolute inset-6 rounded-full bg-accent-dim border border-accent/20 flex items-center justify-center">
          <svg
            width="20"
            height="20"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            className="text-accent"
            strokeWidth={1.5}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5"
            />
          </svg>
        </div>
      </div>

      <h2 className="font-display text-2xl font-medium italic text-text-primary mb-3">
        Upload survey data
      </h2>
      <p className="text-sm text-text-muted max-w-xs leading-relaxed">
        Drop a CSV, Excel, JSON, or text file to discover topics
        using AI-powered analysis
      </p>
    </div>
  );
}
