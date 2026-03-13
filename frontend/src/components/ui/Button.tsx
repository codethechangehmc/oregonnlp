"use client";

import { ButtonHTMLAttributes, forwardRef } from "react";

type Variant = "primary" | "secondary" | "ghost";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
}

const variantStyles: Record<Variant, string> = {
  primary:
    "bg-accent hover:bg-accent-hover text-base font-semibold shadow-[0_0_20px_var(--color-accent-glow)]",
  secondary:
    "bg-surface hover:bg-surface-hover text-text-secondary hover:text-text-primary border border-border hover:border-border-bright",
  ghost:
    "bg-transparent hover:bg-surface text-text-muted hover:text-text-secondary",
};

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = "primary", className = "", children, disabled, ...props }, ref) => (
    <button
      ref={ref}
      disabled={disabled}
      className={`
        inline-flex items-center justify-center gap-2 px-4 py-2.5
        rounded-lg text-sm font-medium font-body
        transition-all duration-200 cursor-pointer
        active:scale-[0.97]
        disabled:opacity-40 disabled:pointer-events-none
        ${variantStyles[variant]}
        ${className}
      `}
      {...props}
    >
      {children}
    </button>
  )
);

Button.displayName = "Button";

export default Button;
