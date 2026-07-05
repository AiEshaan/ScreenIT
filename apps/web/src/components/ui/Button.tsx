import React from "react";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger" | "ghost";
  size?: "sm" | "md" | "lg";
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = "secondary",
  size = "md",
  className = "",
  ...props
}) => {
  const base = "inline-flex items-center justify-center font-medium rounded-lg transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-zinc-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed";
  
  const variants = {
    primary: "bg-zinc-950 text-white hover:bg-zinc-900 border border-transparent shadow-sm",
    secondary: "bg-white text-zinc-800 hover:bg-zinc-50 border border-zinc-200 shadow-sm",
    danger: "bg-red-50 text-red-600 hover:bg-red-100 border border-red-200",
    ghost: "bg-transparent text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900",
  };

  const sizes = {
    sm: "px-3 py-1.5 text-xs font-semibold",
    md: "px-4 py-2 text-sm",
    lg: "px-5 py-2.5 text-base",
  };

  return (
    <button
      className={`${base} ${variants[variant]} ${sizes[size]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};
