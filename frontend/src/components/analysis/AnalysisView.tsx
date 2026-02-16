"use client";

import { useEffect, useState } from "react";
import { AnalysisResponse } from "@/lib/types";
import SummaryMetrics from "./SummaryMetrics";
import TopicList from "./TopicList";
import OutlierSection from "./OutlierSection";
import ActionBar from "./ActionBar";

interface AnalysisViewProps {
  data: AnalysisResponse;
  onSave: () => Promise<void>;
}

export default function AnalysisView({ data, onSave }: AnalysisViewProps) {
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    setSaved(false);
  }, [data.analysis_id]);

  const outlier = data.topics.find((t) => t.topic_id === -1);

  const handleSave = async () => {
    await onSave();
    setSaved(true);
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header row */}
      <div className="flex items-end justify-between flex-wrap gap-4">
        <div>
          <p className="text-[10px] font-semibold text-text-muted uppercase tracking-[0.15em] font-body mb-1">
            Analysis Complete
          </p>
          <h2 className="font-display text-2xl font-medium italic text-text-primary">
            Results
          </h2>
        </div>
        <ActionBar
          analysisId={data.analysis_id}
          onSave={handleSave}
          saved={saved}
        />
      </div>

      {/* Divider */}
      <div className="h-px bg-gradient-to-r from-accent/30 via-border to-transparent" />

      <SummaryMetrics summary={data.summary} topics={data.topics} />
      <TopicList topics={data.topics} />
      {outlier && <OutlierSection outlier={outlier} />}
    </div>
  );
}
