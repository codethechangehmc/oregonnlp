"use client";

interface HeaderProps {
  onToggleSidebar: () => void;
}

export default function Header({ onToggleSidebar }: HeaderProps) {
  return (
    <header className="h-14 bg-surface border-b border-border px-5 flex items-center gap-4 shrink-0 relative">
      <button
        onClick={onToggleSidebar}
        className="lg:hidden p-1.5 rounded-md hover:bg-surface-hover text-text-muted transition-colors cursor-pointer"
        aria-label="Toggle sidebar"
      >
        <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      <div className="flex items-center gap-2.5">
        <div className="w-2 h-2 rounded-full bg-accent shadow-[0_0_8px_var(--color-accent-glow)]" />
        <h1 className="text-[15px] tracking-tight">
          <span className="font-display italic font-medium text-text-primary">Oregon NLP</span>
          <span className="text-text-muted font-body ml-1.5 font-light">Survey Analyzer</span>
        </h1>
      </div>

      {/* Subtle amber accent line at bottom */}
      <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-accent/20 to-transparent" />
    </header>
  );
}
