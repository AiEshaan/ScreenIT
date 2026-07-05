import React from "react";

interface BadgeProps {
  variant?: "success" | "warning" | "error" | "info" | "neutral";
  children: React.ReactNode;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  variant = "neutral",
  children,
  className = "",
}) => {
  const base = "inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium tracking-tight";
  
  const variants = {
    success: "bg-emerald-50 text-emerald-700 border border-emerald-100",
    warning: "bg-amber-50 text-amber-700 border border-amber-100",
    error: "bg-rose-50 text-rose-700 border border-rose-100",
    info: "bg-zinc-100 text-zinc-800 border border-zinc-200",
    neutral: "bg-zinc-50 text-zinc-600 border border-zinc-200",
  };

  return (
    <span className={`${base} ${variants[variant]} ${className}`}>
      {children}
    </span>
  );
};
