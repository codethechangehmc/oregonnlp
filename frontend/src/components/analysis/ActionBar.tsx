"use client";

import { useState } from "react";
import Button from "@/components/ui/Button";
import { getPdfUrl } from "@/lib/api";

interface ActionBarProps {
  analysisId: string;
  onSave: () => Promise<void>;
  saved: boolean;
}

export default function ActionBar({ analysisId, onSave, saved }: ActionBarProps) {
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState("");

  const handleSave = async () => {
    setSaving(true);
    try {
      await onSave();
      setToast("Saved to library");
      setTimeout(() => setToast(""), 3000);
    } catch {
      setToast("Failed to save");
      setTimeout(() => setToast(""), 3000);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="flex items-center gap-2.5 relative">
      <a
        href={getPdfUrl(analysisId)}
        download
        className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium font-body transition-all duration-200 active:scale-[0.97] bg-surface hover:bg-surface-hover text-text-secondary hover:text-text-primary border border-border hover:border-border-bright cursor-pointer"
      >
        <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
        </svg>
        PDF
      </a>

      <Button
        variant={saved ? "ghost" : "primary"}
        onClick={handleSave}
        disabled={saving || saved}
      >
        {saved ? "Saved" : saving ? "Saving..." : "Save to Library"}
      </Button>

      {/* Toast */}
      {toast && (
        <div className="absolute -bottom-10 right-0 px-3 py-1.5 bg-surface border border-accent/30 rounded-lg text-xs font-medium text-accent animate-fade-up shadow-[0_0_16px_var(--color-accent-glow)]">
          {toast}
        </div>
      )}
    </div>
  );
}
