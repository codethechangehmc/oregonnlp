"use client";

import { useState } from "react";
import SampleResponse from "./SampleResponse";
import { TopicResult } from "@/lib/types";

interface OutlierSectionProps {
  outlier: TopicResult;
}

export default function OutlierSection({ outlier }: OutlierSectionProps) {
  const [expanded, setExpanded] = useState(false);

  if (outlier.count === 0) return null;

  return (
    <div className="bg-surface rounded-xl border border-border overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full text-left px-5 py-4 flex items-center gap-3 cursor-pointer"
      >
        <div className="flex-1">
          <h3 className="text-sm font-medium text-text-muted">
            Unclassified
          </h3>
          <p className="text-xs text-text-muted/60 mt-0.5">
            {outlier.count} responses ({outlier.percentage}%)
          </p>
        </div>
        <svg
          width="14"
          height="14"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
          className={`text-text-muted shrink-0 transition-transform duration-300 ${
            expanded ? "rotate-180" : ""
          }`}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
        </svg>
      </button>

      <div
        className={`overflow-hidden transition-[max-height] duration-300 ease-in-out ${
          expanded ? "max-h-[400px]" : "max-h-0"
        }`}
      >
        <div className="px-5 pb-5 border-t border-border pt-3">
          <ul>
            {outlier.sample_responses.slice(0, 5).map((resp, i) => (
              <SampleResponse key={i} text={resp} />
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
