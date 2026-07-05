import React from "react";

interface SpinnerProps {
  size?: "sm" | "md" | "lg";
  className?: string;
}

export const Spinner: React.FC<SpinnerProps> = ({
  size = "md",
  className = "",
}) => {
  const sizes = {
    sm: "h-4 h-4 border-2",
    md: "h-8 w-8 border-2",
    lg: "h-12 w-12 border-3",
  };

  return (
    <div
      className={`animate-spin rounded-full border-t-zinc-950 border-zinc-200 ${sizes[size]} ${className}`}
      role="status"
    />
  );
};
