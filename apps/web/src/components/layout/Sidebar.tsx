import React from "react";
import { NavLink } from "react-router-dom";
import {
  FilePlus2,
  History,
  Settings,
  BarChart3,
  LayoutGrid,
} from "lucide-react";

export const Sidebar: React.FC = () => {
  const links = [
    { to: "/", label: "Dashboard", icon: LayoutGrid },
    { to: "/screen/new", label: "New Screening", icon: FilePlus2 },
    { to: "/history", label: "History Log", icon: History },
    { to: "/analytics", label: "Analytics", icon: BarChart3 },
    { to: "/settings", label: "Settings", icon: Settings },
  ];

  return (
    <aside className="w-64 bg-zinc-50 border-r border-zinc-200 flex flex-col h-screen fixed left-0 top-0 z-20">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 border-b border-zinc-200 gap-2.5">
        <div className="w-8 h-8 rounded bg-zinc-950 flex items-center justify-center text-white font-mono font-bold text-lg select-none">
          S
        </div>
        <div className="flex flex-col">
          <span className="font-semibold text-sm text-zinc-900 tracking-tight leading-none">
            ScreenIt
          </span>
          <span className="text-[10px] text-zinc-500 font-mono tracking-wider uppercase mt-1">
            Recruiter OS
          </span>
        </div>
      </div>

      {/* Primary Navigation Links */}
      <nav className="flex-1 px-4 py-6 space-y-1.5">
        {links.map((link) => {
          const Icon = link.icon;
          return (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                  isActive
                    ? "bg-zinc-200/60 text-zinc-900"
                    : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900"
                }`
              }
            >
              <Icon className="w-4 h-4 stroke-[2]" />
              <span>{link.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Footer System Status Banner */}
      <div className="p-4 border-t border-zinc-200 bg-zinc-50/50">
        <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-emerald-50 border border-emerald-100/50">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-xs font-semibold text-emerald-800 tracking-tight">
            AI Engine Online
          </span>
        </div>
      </div>
    </aside>
  );
};
