"use client";

import { cn } from "@/lib/utils";
import { Download } from "lucide-react";

interface DownloadReportProps {
  onDownload: () => void;
  className?: string;
}

export function DownloadReport({ onDownload, className }: DownloadReportProps) {
  return (
    <div
      className={cn(
        "bg-white border border-[#E4E2DC] rounded-2xl p-7 shadow-card",
        "flex items-center justify-between",
        className
      )}
    >
      {/* Left Side */}
      <div>
        <h2 className="text-[18px] font-semibold text-[#1C1917]">
          Pipeline Complete
        </h2>
        <p className="text-[13px] text-[#57534E] mt-1 max-w-[480px]">
          All three agents finished successfully. Your report includes generated
          code, test results, and security findings.
        </p>
      </div>

      {/* Right Side */}
      <div className="flex flex-col items-center">
        <button
          onClick={onDownload}
          className={cn(
            "flex items-center gap-2 px-6 py-2.5 rounded-lg text-[14px] font-medium",
            "bg-[#6D28D9] text-white",
            "shadow-[0_1px_3px_rgba(109,40,217,0.3)]",
            "hover:bg-[#5B21B6] hover:shadow-[0_4px_12px_rgba(109,40,217,0.35)]",
            "transition-all"
          )}
        >
          <Download className="w-4 h-4" />
          Download Report
        </button>
        <p className="text-[11px] text-[#A8A29E] mt-1.5 text-center">
          report.md · includes code, tests and findings
        </p>
      </div>
    </div>
  );
}
