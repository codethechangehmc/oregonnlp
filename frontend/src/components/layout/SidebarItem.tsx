"use client";

import { useState } from "react";
import { LibraryItem } from "@/lib/types";

interface SidebarItemProps {
  item: LibraryItem;
  active: boolean;
  onClick: () => void;
  onDelete: (id: string) => void;
}

export default function SidebarItem({ item, active, onClick, onDelete }: SidebarItemProps) {
  const [confirmDelete, setConfirmDelete] = useState(false);
  const label = item.title || item.filename;
  const date = new Date(item.created_at).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirmDelete) {
      onDelete(item.id);
      setConfirmDelete(false);
    } else {
      setConfirmDelete(true);
    }
  };

  const handleCancelDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    setConfirmDelete(false);
  };

  return (
    <div
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
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium truncate">{label}</div>
          <div className="flex items-center gap-1.5 mt-0.5 text-xs text-text-muted">
            <span>{date}</span>
            <span className="text-border-bright">/</span>
            <span>{item.num_topics} topics</span>
            <span className="text-border-bright">/</span>
            <span>{item.total_responses} resp.</span>
          </div>
        </div>
        
        {confirmDelete ? (
          <div className="flex items-center gap-1 shrink-0">
            <button
              onClick={handleDelete}
              className="p-1 text-xs text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded transition-colors"
              title="Confirm delete"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
                <path fillRule="evenodd" d="M16.704 4.153a.75.75 0 01.143 1.052l-8 10.5a.75.75 0 01-1.127.075l-4.5-4.5a.75.75 0 011.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 011.05-.143z" clipRule="evenodd" />
              </svg>
            </button>
            <button
              onClick={handleCancelDelete}
              className="p-1 text-xs text-text-muted hover:text-text-primary hover:bg-surface-hover rounded transition-colors"
              title="Cancel"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
                <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
              </svg>
            </button>
          </div>
        ) : (
          <button
            onClick={handleDelete}
            className="p-1 opacity-0 group-hover:opacity-100 text-text-muted hover:text-red-400 hover:bg-red-500/10 rounded transition-all shrink-0"
            title="Delete from library"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
              <path fillRule="evenodd" d="M8.75 1A2.75 2.75 0 006 3.75v.443c-.795.077-1.584.176-2.365.298a.75.75 0 10.23 1.482l.149-.022.841 10.518A2.75 2.75 0 007.596 19h4.807a2.75 2.75 0 002.742-2.53l.841-10.519.149.023a.75.75 0 00.23-1.482A41.03 41.03 0 0014 3.193V3.75A2.75 2.75 0 0011.25 1h-2.5zM10 4c.84 0 1.673.025 2.5.075V3.75c0-.69-.56-1.25-1.25-1.25h-2.5c-.69 0-1.25.56-1.25 1.25v.325C8.327 4.025 9.16 4 10 4zM8.58 7.72a.75.75 0 00-1.5.06l.3 7.5a.75.75 0 101.5-.06l-.3-7.5zm4.34.06a.75.75 0 10-1.5-.06l-.3 7.5a.75.75 0 101.5.06l.3-7.5z" clipRule="evenodd" />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}
