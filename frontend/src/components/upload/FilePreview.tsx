"use client";

import Button from "@/components/ui/Button";

interface FilePreviewProps {
  file: File;
  onAnalyze: () => void;
  onClear: () => void;
  disabled?: boolean;
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function FilePreview({
  file,
  onAnalyze,
  onClear,
  disabled,
}: FilePreviewProps) {
  return (
    <div className="flex items-center gap-3 p-3 bg-surface border border-border rounded-xl animate-fade-up">
      <div className="w-10 h-10 rounded-lg bg-accent-dim border border-accent/15 flex items-center justify-center shrink-0">
        <svg
          width="16"
          height="16"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          className="text-accent"
          strokeWidth={1.5}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z"
          />
        </svg>
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-text-primary truncate">
          {file.name}
        </p>
        <p className="text-xs text-text-muted">{formatSize(file.size)}</p>
      </div>
      <button
        onClick={onClear}
        className="p-1.5 rounded-md hover:bg-surface-hover text-text-muted hover:text-text-secondary transition-colors cursor-pointer"
        aria-label="Remove file"
      >
        <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
        </svg>
      </button>
      <Button onClick={onAnalyze} disabled={disabled}>
        Analyze
      </Button>
    </div>
  );
}
