"use client";

import { useEffect, useState } from "react";

const steps = [
  "Parsing file",
  "Cleaning responses",
  "Running topic analysis",
  "Generating labels",
];

export default function AnalyzingState({ filename }: { filename: string }) {
  const [step, setStep] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setStep((s) => (s < steps.length - 1 ? s + 1 : s));
    }, 2500);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center py-28 text-center animate-fade-in">
      {/* Pulsing amber ring */}
      <div className="relative w-20 h-20 mb-8">
        <div className="absolute inset-0 rounded-full border-2 border-accent/20 animate-glow-pulse" />
        <div className="absolute inset-2 rounded-full border border-border" />
        <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-accent animate-spin-slow" />
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-2.5 h-2.5 rounded-full bg-accent shadow-[0_0_12px_var(--color-accent)]" />
        </div>
      </div>

      <h2 className="font-display text-xl font-medium italic text-text-primary mb-1">
        Analyzing
      </h2>
      {filename && (
        <p className="text-sm text-text-muted mb-6 font-mono">{filename}</p>
      )}

      <div className="space-y-2.5 text-left">
        {steps.map((label, i) => (
          <div
            key={label}
            className={`flex items-center gap-3 text-sm transition-all duration-500 ${
              i < step
                ? "text-sage"
                : i === step
                ? "text-text-primary"
                : "text-text-muted/40"
            }`}
          >
            <div className={`w-5 h-5 rounded-full border flex items-center justify-center transition-all duration-500 ${
              i < step
                ? "border-sage bg-sage-dim"
                : i === step
                ? "border-accent bg-accent-dim"
                : "border-border"
            }`}>
              {i < step ? (
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={3}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              ) : i === step ? (
                <div className="w-1.5 h-1.5 rounded-full bg-accent animate-glow-pulse" />
              ) : null}
            </div>
            {label}
          </div>
        ))}
      </div>
    </div>
  );
}
