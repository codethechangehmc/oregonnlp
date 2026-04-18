"use client";

import { LibraryItem } from "@/lib/types";
import SidebarItem from "./SidebarItem";

interface SidebarProps {
  open: boolean;
  onToggle: () => void;
  onClose: () => void;
  library: LibraryItem[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
  loading: boolean;
}

export default function Sidebar({
  open,
  onToggle,
  onClose,
  library,
  activeId,
  onSelect,
  onDelete,
  loading,
}: SidebarProps) {
  const closeIfMobile = () => {
    if (typeof window === "undefined") return;
    if (window.matchMedia("(max-width: 1023px)").matches) {
      onClose();
    }
  };

  return (
    <>
      {open && (
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-30 lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`
          fixed lg:top-14 top-0 bottom-0 left-0 z-40
          bg-base border-r border-border
          flex flex-col
          transition-[transform,width] duration-300 ease-out
          lg:static lg:z-auto lg:shrink-0
          ${open ? "w-[260px] translate-x-0" : "w-[260px] -translate-x-full lg:w-12 lg:translate-x-0"}
        `}
      >
        <div
          className={`py-3 border-b border-border flex items-center gap-2 ${
            open ? "px-3 justify-between" : "px-2 justify-center"
          }`}
        >
          {open ? (
            <h2 className="text-[10px] font-semibold text-text-muted uppercase tracking-[0.15em] font-body">
              Library
            </h2>
          ) : (
            <span className="sr-only">Library</span>
          )}

          <button
            type="button"
            onClick={onToggle}
            className="p-1.5 rounded-md hover:bg-surface-hover text-text-muted transition-colors cursor-pointer shrink-0"
            aria-label={open ? "Collapse sidebar" : "Expand sidebar"}
            title={open ? "Collapse sidebar" : "Expand sidebar"}
          >
            <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01" />
            </svg>
          </button>
        </div>

        <div className={`flex-1 overflow-y-auto px-2 py-2 space-y-0.5 ${open ? "" : "lg:hidden"}`}>
          {loading ? (
            <div className="px-3 py-6 text-sm text-text-muted">Loading...</div>
          ) : library.length === 0 ? (
            <div className="px-3 py-6">
              <p className="text-sm text-text-muted">No saved analyses yet</p>
              <p className="text-xs text-text-muted/60 mt-1">
                Analyses you save will appear here
              </p>
            </div>
          ) : (
            library.map((item) => (
              <SidebarItem
                key={item.id}
                item={item}
                active={item.id === activeId}
                onClick={() => {
                  onSelect(item.id);
                  closeIfMobile();
                }}
                onDelete={onDelete}
              />
            ))
          )}
        </div>
      </aside>
    </>
  );
}
