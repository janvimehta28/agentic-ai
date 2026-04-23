"use client";

import { AgentPanel, AgentStatus } from "./AgentPanel";
import { MetricCard } from "./MetricCard";
import { FindingCard, Severity } from "./FindingCard";
import { RedTeamSkeleton } from "./SkeletonLoader";
import { Shield } from "lucide-react";

interface Finding {
  severity: Severity;
  title: string;
  description: string;
  suggestedFix: string;
}

interface RedTeamPanelProps {
  status: AgentStatus;
  findings: Finding[];
  counts: {
    high: number;
    medium: number;
    low: number;
  };
  className?: string;
}

export function RedTeamPanel({
  status,
  findings,
  counts,
  className,
}: RedTeamPanelProps) {
  const isEmpty = findings.length === 0;
  const isLoading = status === "running" && isEmpty;

  return (
    <AgentPanel
      name="Red Team Agent"
      role="Security Reviewer"
      color="red"
      status={status}
      outputPath="output/vuln_report.json"
      copyContent={findings.length > 0 ? JSON.stringify(findings, null, 2) : undefined}
      className={className}
    >
      {isLoading ? (
        <RedTeamSkeleton />
      ) : (
        <div className="p-4 flex flex-col gap-3.5 h-full">
          {/* Severity Summary */}
          <div className="flex gap-2">
            <MetricCard label="HIGH" value={counts.high} color="danger" />
            <MetricCard label="MEDIUM" value={counts.medium} color="warning" />
            <MetricCard label="LOW" value={counts.low} color="muted" />
          </div>

          {/* Findings List */}
          <div className="flex-1 min-h-0 mt-1">
            <p className="text-[12px] font-medium text-[#57534E] mb-2">Findings</p>
            
            {isEmpty ? (
              <div className="h-[160px] flex flex-col items-center justify-center">
                <Shield className="w-8 h-8 text-[#E4E2DC]" />
                <span className="text-[13px] text-[#A8A29E] mt-2">
                  Vulnerability findings will appear here
                </span>
              </div>
            ) : (
              <div className="max-h-[280px] overflow-y-auto pr-1">
                {findings.map((finding, index) => (
                  <FindingCard
                    key={index}
                    severity={finding.severity}
                    title={finding.title}
                    description={finding.description}
                    suggestedFix={finding.suggestedFix}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </AgentPanel>
  );
}
