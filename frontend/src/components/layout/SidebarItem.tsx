"use client";

import { LibraryItem } from "@/lib/types";

interface SidebarItemProps {
  item: LibraryItem;
  active: boolean;
  onClick: () => void;
}

export default function SidebarItem({ item, active, onClick }: SidebarItemProps) {
  const label = item.title || item.filename;
  const date = new Date(item.created_at).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });

  return (
    <button
      onClick={onClick}
      className={`
        w-full text-left px-3 py-2.5 rounded-lg
        transition-all duration-200 group relative cursor-pointer
        ${active
          ? "bg-accent-dim text-accent"
          : "text-text-secondary hover:bg-surface-hover hover:text-text-primary"
        }
      `}
    >
      {active && (
        <div className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 bg-accent rounded-r" />
      )}
      <div className="text-sm font-medium truncate">{label}</div>
      <div className="flex items-center gap-1.5 mt-0.5 text-xs text-text-muted">
        <span>{date}</span>
        <span className="text-border-bright">/</span>
        <span>{item.num_topics} topics</span>
        <span className="text-border-bright">/</span>
        <span>{item.total_responses} resp.</span>
      </div>
    </button>
  );
}
