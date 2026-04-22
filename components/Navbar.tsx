"use client";

import { cn } from "@/lib/utils";

interface NavbarProps {
  isConnected: boolean;
  className?: string;
}

export function Navbar({ isConnected, className }: NavbarProps) {
  return (
    <nav
      className={cn(
        "h-16 flex items-center justify-between px-8 border-b border-[#E4E2DC] bg-white",
        "shadow-[0_1px_3px_rgba(0,0,0,0.06)]",
        className
      )}
    >
      {/* Left Side */}
      <div className="flex items-center gap-2.5">
        {/* Logo Mark */}
        <div className="w-7 h-7 rounded-lg bg-[#6D28D9] flex items-center justify-center">
          <span className="text-white text-[14px]">&lt;/&gt;</span>
        </div>

        {/* Brand Name */}
        <span className="text-[17px] font-semibold text-[#1C1917] ml-1">
          AutonomousDev
        </span>

        {/* Beta Badge */}
        <span className="text-[11px] font-medium px-2 py-0.5 rounded-full border bg-[#EDE9FE] border-[#DDD6FE] text-[#6D28D9] ml-1">
          Beta
        </span>
      </div>

      {/* Center - Agent Pills (Desktop only) */}
      <div className="hidden md:flex items-center gap-2">
        <span className="text-[12px] px-2.5 py-1 rounded-full bg-[#EDE9FE] text-[#4C1D95]">
          Writer
        </span>
        <span className="text-[12px] px-2.5 py-1 rounded-full bg-[#CCFBF1] text-[#134E4A]">
          Tester
        </span>
        <span className="text-[12px] px-2.5 py-1 rounded-full bg-[#FEE2E2] text-[#7F1D1D]">
          Red Team
        </span>
      </div>

      {/* Right Side */}
      <div className="flex items-center gap-4">
        {/* Connection Status */}
        <div className="flex items-center gap-1.5">
          <span
            className={cn(
              "w-2 h-2 rounded-full",
              isConnected ? "bg-[#10B981] animate-pulse-dot" : "bg-[#EF4444]"
            )}
          />
          <span className="text-[13px] text-[#57534E]">
            {isConnected ? "API Connected" : "Disconnected"}
          </span>
        </div>

        {/* Divider */}
        <div className="h-5 w-px bg-[#E4E2DC] hidden sm:block" />

        {/* Powered By */}
        <span className="hidden sm:block text-[12px] text-[#A8A29E]">
          Powered by Groq + CrewAI
        </span>
      </div>
    </nav>
  );
}
