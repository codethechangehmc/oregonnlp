import { TopicResult } from "@/lib/types";
import TopicCard from "./TopicCard";

interface TopicListProps {
  topics: TopicResult[];
}

export default function TopicList({ topics }: TopicListProps) {
  const sorted = [...topics]
    .filter((t) => t.topic_id !== -1)
    .sort((a, b) => b.count - a.count);

  if (sorted.length === 0) return null;

  return (
    <div>
      <h2 className="font-display text-lg font-medium italic text-text-primary mb-4">
        Discovered Topics
      </h2>
      <div className="space-y-2">
        {sorted.map((topic, i) => (
          <div key={topic.topic_id} className={`animate-fade-up delay-${Math.min(i + 1, 5)}`}>
            <TopicCard topic={topic} rank={i + 1} />
          </div>
        ))}
      </div>
    </div>
  );
}
