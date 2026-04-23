"use client";

import { cn } from "@/lib/utils";
import { useEffect, useRef, useState } from "react";

type LogLevel = "info" | "success" | "warning" | "error";
type AgentType = "WRITER" | "TESTER" | "RED TEAM" | "SYSTEM";

interface LogEntry {
  timestamp: string;
  agent: AgentType;
  message: string;
  level: LogLevel;
}

interface LiveLogStreamProps {
  logs: LogEntry[];
  onClear: () => void;
  isRunning?: boolean;
  className?: string;
}

export function LiveLogStream({ logs, onClear, isRunning = false, className }: LiveLogStreamProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = useState(true);

  // Auto-scroll to bottom when new logs arrive (if enabled)
  useEffect(() => {
    if (autoScroll && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs, autoScroll]);

  const getAgentBadgeStyles = (agent: AgentType) => {
    switch (agent) {
      case "WRITER":
        return "bg-[#EDE9FE] text-[#6D28D9]";
      case "TESTER":
        return "bg-[#CCFBF1] text-[#0D9488]";
      case "RED TEAM":
        return "bg-[#FEE2E2] text-[#DC2626]";
      case "SYSTEM":
        return "bg-[#F5F4F0] text-[#57534E]";
    }
  };

  const getMessageColor = (level: LogLevel) => {
    switch (level) {
      case "info":
        return "text-[#57534E]";
      case "success":
        return "text-[#059669]";
      case "warning":
        return "text-[#D97706]";
      case "error":
        return "text-[#DC2626]";
    }
  };

  return (
    <div
      className={cn(
        "bg-white border border-[#E4E2DC] rounded-2xl shadow-card overflow-hidden",
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-3.5 border-b border-[#E4E2DC] bg-[#F9F8F6]">
        <div className="flex items-center gap-2">
          {/* Pulse dot */}
          <span
            className={cn(
              "w-2 h-2 rounded-full",
              isRunning ? "bg-[#10B981] animate-pulse-dot" : "bg-[#A8A29E]"
            )}
          />
          <span className="text-[14px] font-semibold text-[#1C1917]">Live Logs</span>
          <span className="text-[11px] px-2 py-0.5 rounded-full bg-[#F5F4F0] border border-[#E4E2DC] text-[#57534E]">
            {logs.length} entries
          </span>
        </div>

        <div className="flex items-center gap-3">
          {/* Auto-scroll toggle */}
          <label className="flex items-center gap-1.5 cursor-pointer">
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
              className="w-3.5 h-3.5 rounded border-[#E4E2DC] text-[#6D28D9] focus:ring-[#6D28D9]"
            />
            <span className="text-[12px] text-[#57534E]">Auto-scroll</span>
          </label>

          {/* Clear button */}
          <button
            onClick={onClear}
            className="text-[12px] text-[#A8A29E] hover:text-[#57534E] transition-colors"
          >
            Clear
          </button>
        </div>
      </div>

      {/* Log Body */}
      <div
        ref={scrollRef}
        className="px-5 py-3 max-h-[220px] overflow-y-auto font-mono text-[12px] leading-[1.8] bg-[#FAFAF9]"
      >
        {logs.length === 0 ? (
          <p className="text-[13px] text-[#A8A29E] text-center py-5">
            Pipeline logs will appear here when you click Run Pipeline
          </p>
        ) : (
          <div className="space-y-0.5">
            {logs.map((log, index) => (
              <div key={index} className="flex items-start gap-2.5">
                {/* Timestamp */}
                <span className="text-[#A8A29E] flex-shrink-0 min-w-[75px]">
                  [{log.timestamp}]
                </span>

                {/* Agent Badge */}
                <span
                  className={cn(
                    "text-[10px] font-medium px-2 py-0.5 rounded-full flex-shrink-0 min-w-[72px] text-center",
                    getAgentBadgeStyles(log.agent)
                  )}
                >
                  {log.agent}
                </span>

                {/* Message */}
                <span className={cn("break-words flex-1", getMessageColor(log.level))}>
                  {log.message}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
