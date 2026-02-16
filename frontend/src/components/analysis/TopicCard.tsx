"use client";

import { useState } from "react";
import KeywordBadge from "./KeywordBadge";
import SampleResponse from "./SampleResponse";
import { TopicResult } from "@/lib/types";

interface TopicCardProps {
  topic: TopicResult;
  rank: number;
}

export default function TopicCard({ topic, rank }: TopicCardProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className={`
      bg-surface rounded-xl border border-border overflow-hidden
      transition-all duration-300
      hover:border-border-bright
      ${expanded ? "shadow-[0_0_30px_var(--color-accent-glow)]" : ""}
    `}>
      {/* Amber left accent bar */}
      <div className="flex">
        <div className={`
          w-0.5 shrink-0 transition-colors duration-300
          ${expanded ? "bg-accent" : "bg-border-bright"}
        `} />

        <div className="flex-1 min-w-0">
          <button
            onClick={() => setExpanded(!expanded)}
            className="w-full text-left px-5 py-4 flex items-start gap-4 cursor-pointer"
          >
            <span className="font-display text-lg font-medium text-accent/70 mt-px tabular-nums">
              {String(rank).padStart(2, "0")}
            </span>
            <div className="flex-1 min-w-0">
              <div className="flex items-baseline gap-2.5 flex-wrap">
                <h3 className="font-display text-base font-medium text-text-primary">
                  {topic.label}
                </h3>
                <span className="text-xs text-text-muted font-body">
                  {topic.count} responses &middot; {topic.percentage}%
                </span>
              </div>
              {topic.category && (
                <p className="text-xs text-text-muted/60 mt-0.5 font-body">{topic.category}</p>
              )}
            </div>
            <svg
              width="14"
              height="14"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
              className={`text-text-muted shrink-0 mt-1.5 transition-transform duration-300 ${
                expanded ? "rotate-180" : ""
              }`}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
            </svg>
          </button>

          <div
            className={`overflow-hidden transition-[max-height] duration-400 ease-in-out ${
              expanded ? "max-h-[700px]" : "max-h-0"
            }`}
          >
            <div className="px-5 pb-5 pt-0 border-t border-border">
              {topic.description && (
                <p className="text-sm text-text-secondary mt-4 mb-4 leading-relaxed italic font-display">
                  {topic.description}
                </p>
              )}

              {topic.keywords.length > 0 && (
                <div className="mb-5">
                  <p className="text-[10px] font-semibold text-text-muted uppercase tracking-[0.15em] font-body mb-2.5">
                    Keywords
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {topic.keywords.filter(Boolean).map((kw, i) => (
                      <KeywordBadge key={`${i}-${kw}`} keyword={kw} />
                    ))}
                  </div>
                </div>
              )}

              {topic.sample_responses.length > 0 && (
                <div>
                  <p className="text-[10px] font-semibold text-text-muted uppercase tracking-[0.15em] font-body mb-2">
                    Sample Responses
                  </p>
                  <ul>
                    {topic.sample_responses.slice(0, 5).map((resp, i) => (
                      <SampleResponse key={i} text={resp} />
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
