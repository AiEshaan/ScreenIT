import React from "react";
import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";

export const Shell: React.FC = () => {
  return (
    <div className="min-h-screen bg-white text-zinc-900 font-sans flex">
      {/* Fixed Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <main className="flex-1 pl-64 min-h-screen flex flex-col bg-white">
        <Outlet />
      </main>
    </div>
  );
};
