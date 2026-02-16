import { HTMLAttributes } from "react";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  hover?: boolean;
  glow?: boolean;
}

export default function Card({
  hover = false,
  glow = false,
  className = "",
  children,
  ...props
}: CardProps) {
  return (
    <div
      className={`
        bg-surface rounded-xl border border-border
        ${hover ? "transition-all duration-300 hover:border-border-bright hover:bg-surface-hover hover:-translate-y-0.5" : ""}
        ${glow ? "hover:shadow-[0_0_30px_var(--color-accent-glow)]" : ""}
        ${className}
      `}
      {...props}
    >
      {children}
    </div>
  );
}
