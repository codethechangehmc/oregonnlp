"use client";

import { useCallback, useRef, useState } from "react";

const ACCEPT = ".csv,.xlsx,.xls,.json,.txt";

interface DropZoneProps {
  onFileSelect: (file: File) => void;
  disabled?: boolean;
}

export default function DropZone({ onFileSelect, disabled }: DropZoneProps) {
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      if (disabled) return;
      const file = e.dataTransfer.files[0];
      if (file) onFileSelect(file);
    },
    [onFileSelect, disabled]
  );

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) onFileSelect(file);
      e.target.value = "";
    },
    [onFileSelect]
  );

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        if (!disabled) setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={handleDrop}
      onClick={() => !disabled && inputRef.current?.click()}
      className={`
        relative border border-dashed rounded-xl p-8
        flex flex-col items-center justify-center gap-4
        cursor-pointer transition-all duration-300
        ${disabled ? "opacity-40 cursor-not-allowed" : ""}
        ${
          dragOver
            ? "border-accent bg-accent-dim shadow-[0_0_40px_var(--color-accent-glow)]"
            : "border-border hover:border-border-bright hover:bg-surface/50"
        }
      `}
    >
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPT}
        onChange={handleChange}
        className="hidden"
      />

      <div className={`
        w-11 h-11 rounded-lg flex items-center justify-center transition-colors duration-300
        ${dragOver ? "bg-accent/20" : "bg-surface border border-border"}
      `}>
        <svg
          width="18"
          height="18"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          className={`transition-colors duration-300 ${dragOver ? "text-accent" : "text-text-muted"}`}
          strokeWidth={1.5}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5"
          />
        </svg>
      </div>

      <div className="text-center">
        <p className="text-sm text-text-secondary">
          Drop a file here or <span className="text-accent font-medium">browse</span>
        </p>
        <p className="text-xs text-text-muted mt-1.5">
          CSV, Excel, JSON, or TXT
        </p>
      </div>
    </div>
  );
}
