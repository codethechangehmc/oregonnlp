interface BadgeProps {
  children: React.ReactNode;
  className?: string;
}

export default function Badge({ children, className = "" }: BadgeProps) {
  return (
    <span
      className={`
        inline-flex items-center px-2.5 py-1
        bg-accent-dim text-accent
        rounded-md text-xs font-medium font-body
        border border-accent/10
        ${className}
      `}
    >
      {children}
    </span>
  );
}
