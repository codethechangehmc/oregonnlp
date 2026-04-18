"use client";

import { useState } from "react";
import SampleResponse from "./SampleResponse";
import { TopicResult } from "@/lib/types";

interface OutlierSectionProps {
  outlier: TopicResult;
}

export default function OutlierSection({ outlier }: OutlierSectionProps) {
  const [expanded, setExpanded] = useState(false);
  const [visibleCount, setVisibleCount] = useState(5);
  const visibleResponses = outlier.sample_responses.slice(0, visibleCount);

  console.log(outlier)
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
        className={`transition-[max-height] duration-300 ease-in-out ${
          expanded ? " overflow-scroll max-h-[500px]" : "max-h-0"
        }`}
      >
        {outlier.sample_responses.length > 0 && (
            <div className="px-2 py-2 w-full flex flex-col justify-items-center items-center align-middle text-wrap gap-2">
              <ul className="h-[10%] w-full">
                {visibleResponses.map((resp, i) => (
                  <SampleResponse key={i} text={resp} />
                ))}
              </ul>
              
              <p className='text-xs text-text-secondary'>Viewing {visibleCount} of {outlier.sample_responses.length} Sample Responses</p>
              {visibleCount < outlier.sample_responses.length && (
                <button
                  onClick={() => setVisibleCount((c) => c + 20)}
                  className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium font-body transition-all duration-200 active:scale-[0.97] bg-surface hover:bg-surface-hover text-text-secondary hover:text-text-primary border border-border hover:border-border-bright cursor-pointe"
                >
                  Load More
                </button>
              )}
            </div>
          )}
      </div>
    </div>
  );
}
