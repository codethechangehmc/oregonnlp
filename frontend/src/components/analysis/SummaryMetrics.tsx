import { Summary, TopicResult } from "@/lib/types";

interface SummaryMetricsProps {
  summary: Summary;
  topics: TopicResult[];
}

export default function SummaryMetrics({ summary, topics }: SummaryMetricsProps) {
  const outlier = topics.find((t) => t.topic_id === -1);
  const outlierCount = outlier?.count ?? 0;
  const classified = summary.total_responses - outlierCount;
  const outlierRate =
    summary.total_responses > 0
      ? ((outlierCount / summary.total_responses) * 100).toFixed(1)
      : "0.0";

  const metrics = [
    { label: "Responses", value: summary.total_responses.toLocaleString() },
    { label: "Topics", value: summary.num_topics.toString() },
    { label: "Classified", value: classified.toLocaleString() },
    { label: "Outlier Rate", value: `${outlierRate}%` },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-px bg-border rounded-xl overflow-hidden border border-border">
      {metrics.map((m, i) => (
        <div
          key={m.label}
          className={`bg-surface p-5 animate-fade-up delay-${i + 1}`}
        >
          <p className="text-[10px] font-semibold text-text-muted uppercase tracking-[0.15em] font-body mb-2">
            {m.label}
          </p>
          <p className="font-display text-3xl font-medium text-text-primary tracking-tight">
            {m.value}
          </p>
          <div className="mt-2 h-px w-8 bg-gradient-to-r from-accent/60 to-transparent" />
        </div>
      ))}
    </div>
  );
}
