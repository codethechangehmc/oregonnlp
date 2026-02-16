"use client";

import { LibraryItem } from "@/lib/types";
import SidebarItem from "./SidebarItem";

interface SidebarProps {
  open: boolean;
  onClose: () => void;
  library: LibraryItem[];
  activeId: string | null;
  onSelect: (id: string) => void;
  loading: boolean;
}

export default function Sidebar({
  open,
  onClose,
  library,
  activeId,
  onSelect,
  loading,
}: SidebarProps) {
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
          fixed top-14 bottom-0 left-0 z-40 w-[260px]
          bg-base border-r border-border
          flex flex-col
          transition-transform duration-300 ease-out
          lg:translate-x-0 lg:static lg:z-auto
          ${open ? "translate-x-0" : "-translate-x-full"}
        `}
      >
        <div className="px-4 py-3 border-b border-border">
          <h2 className="text-[10px] font-semibold text-text-muted uppercase tracking-[0.15em] font-body">
            Library
          </h2>
        </div>

        <div className="flex-1 overflow-y-auto px-2 py-2 space-y-0.5">
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
                  onClose();
                }}
              />
            ))
          )}
        </div>
      </aside>
    </>
  );
}
