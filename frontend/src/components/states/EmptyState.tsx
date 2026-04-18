export default function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-28 text-center animate-fade-in">

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
