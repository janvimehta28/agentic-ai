"use client";

import { ReactNode, useState } from "react";
import { Clipboard, Check } from "lucide-react";
import { cn } from "@/lib/utils";

export type AgentStatus = "idle" | "running" | "complete" | "error";
export type AgentColor = "purple" | "teal" | "red";

interface AgentPanelProps {
  name: string;
  role: string;
  color: AgentColor;
  status: AgentStatus;
  outputPath?: string;
  copyContent?: string;
  children: ReactNode;
  className?: string;
}

export function AgentPanel({
  name,
  role,
  color,
  status,
  outputPath,
  copyContent,
  children,
  className,
}: AgentPanelProps) {
  const [copied, setCopied] = useState(false);

  const colorConfig = {
    purple: {
      gradient: "linear-gradient(90deg, #6D28D9, #8B5CF6)",
      dot: "#6D28D9",
      badgeBg: "#EDE9FE",
      badgeText: "#6D28D9",
      badgeBorder: "#DDD6FE",
    },
    teal: {
      gradient: "linear-gradient(90deg, #0D9488, #14B8A6)",
      dot: "#0D9488",
      badgeBg: "#CCFBF1",
      badgeText: "#0D9488",
      badgeBorder: "#99F6E4",
    },
    red: {
      gradient: "linear-gradient(90deg, #DC2626, #EF4444)",
      dot: "#DC2626",
      badgeBg: "#FEE2E2",
      badgeText: "#DC2626",
      badgeBorder: "#FECACA",
    },
  };

  const statusConfig = {
    idle: {
      bg: "#F5F4F0",
      text: "#A8A29E",
      label: "Idle",
    },
    running: {
      bg: "#EDE9FE",
      text: "#6D28D9",
      label: "Running",
    },
    complete: {
      bg: "#D1FAE5",
      text: "#059669",
      label: "Done",
    },
    error: {
      bg: "#FEE2E2",
      text: "#DC2626",
      label: "Error",
    },
  };

  const config = colorConfig[color];
  const statusStyle = statusConfig[status];

  const handleCopy = async () => {
    if (copyContent) {
      await navigator.clipboard.writeText(copyContent);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div
      className={cn(
        "bg-white border border-[#E4E2DC] rounded-2xl shadow-card overflow-hidden transition-all duration-200 hover:shadow-card-hover hover:border-[#C9C7BF] flex flex-col h-full",
        className
      )}
    >
      {/* Gradient accent bar */}
      <div className="h-1" style={{ background: config.gradient }} />

      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-[#E4E2DC]">
        <div className="flex items-center gap-2">
          <div
            className="w-2.5 h-2.5 rounded-sm"
            style={{ backgroundColor: config.dot }}
          />
          <span className="text-[15px] font-semibold text-[#1C1917]">{name}</span>
          <span
            className="text-[11px] px-2 py-0.5 rounded-full border"
            style={{
              backgroundColor: config.badgeBg,
              color: config.badgeText,
              borderColor: config.badgeBorder,
            }}
          >
            {role}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <span
            className="text-[11px] px-2 py-0.5 rounded-full flex items-center gap-1.5"
            style={{
              backgroundColor: statusStyle.bg,
              color: statusStyle.text,
            }}
          >
            {status === "running" && (
              <span
                className="w-1.5 h-1.5 rounded-full animate-pulse-dot"
                style={{ backgroundColor: config.dot }}
              />
            )}
            {statusStyle.label}
          </span>
          {copyContent && (
            <button
              onClick={handleCopy}
              className="p-1.5 rounded hover:bg-[#F5F4F0] transition-colors"
              title="Copy to clipboard"
            >
              {copied ? (
                <Check className="w-4 h-4 text-[#059669]" />
              ) : (
                <Clipboard className="w-4 h-4 text-[#A8A29E] hover:text-[#6D28D9]" />
              )}
            </button>
          )}
        </div>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-hidden">{children}</div>

      {/* Footer */}
      {outputPath && (
        <div className="flex items-center justify-between px-5 py-3 border-t border-[#E4E2DC] bg-[#F9F8F6]">
          <span className="text-[12px] text-[#A8A29E] flex items-center gap-1.5">
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            {outputPath}
          </span>
          <button
            onClick={handleCopy}
            className="text-[12px] text-[#6D28D9] hover:underline"
          >
            Copy code
          </button>
        </div>
      )}
    </div>
  );
}
