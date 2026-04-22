"use client";

import { AgentPanel, AgentStatus } from "./AgentPanel";
import { MetricCard } from "./MetricCard";
import { TesterSkeleton } from "./SkeletonLoader";
import { Check, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface TestResult {
  name: string;
  status: "passed" | "failed";
  error?: string;
}

interface TesterPanelProps {
  status: AgentStatus;
  totalTests: number;
  passed: number;
  failed: number;
  coveragePercent: number;
  testResults: TestResult[];
  className?: string;
}

export function TesterPanel({
  status,
  totalTests,
  passed,
  failed,
  coveragePercent,
  testResults,
  className,
}: TesterPanelProps) {
  const isEmpty = testResults.length === 0;
  const isLoading = status === "running" && isEmpty;

  // Coverage bar color based on percentage
  const getCoverageColor = () => {
    if (coveragePercent <= 50) return "#DC2626";
    if (coveragePercent <= 75) return "#D97706";
    return "#0D9488";
  };

  return (
    <AgentPanel
      name="Tester Agent"
      role="QA Engineer"
      color="teal"
      status={status}
      outputPath="output/test_suite.py"
      copyContent={testResults.map((t) => `${t.name}: ${t.status}`).join("\n") || undefined}
      className={className}
    >
      {isLoading ? (
        <TesterSkeleton />
      ) : (
        <div className="p-4 flex flex-col gap-3.5 h-full">
          {/* Metrics Row */}
          <div className="flex gap-2">
            <MetricCard label="Tests Run" value={totalTests} />
            <MetricCard label="Passed" value={passed} color="success" />
            <MetricCard label="Failed" value={failed} color="danger" />
          </div>

          {/* Coverage Section */}
          <div className="mt-1">
            <div className="flex items-center justify-between">
              <span className="text-[12px] font-medium text-[#57534E]">Coverage</span>
              <span className="text-[12px] font-semibold text-[#1C1917]">{coveragePercent}%</span>
            </div>
            <div className="mt-1.5 h-2 bg-[#F5F4F0] border border-[#E4E2DC] rounded overflow-hidden">
              <div
                className="h-full rounded transition-all duration-700 ease-out"
                style={{ 
                  width: `${coveragePercent}%`,
                  backgroundColor: getCoverageColor()
                }}
              />
            </div>
          </div>

          {/* Test Results List */}
          <div className="flex-1 min-h-0 mt-1">
            <p className="text-[12px] font-medium text-[#57534E] mb-2">Test Results</p>
            
            {isEmpty ? (
              <div className="h-[120px] flex items-center justify-center">
                <span className="text-[13px] text-[#A8A29E]">
                  Test results will appear here
                </span>
              </div>
            ) : (
              <div className="max-h-[200px] overflow-y-auto space-y-0">
                {testResults.map((test, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-2 py-1.5 border-b border-[#F5F4F0] last:border-b-0"
                  >
                    <div className={cn(
                      "w-[18px] h-[18px] rounded-full flex items-center justify-center flex-shrink-0",
                      test.status === "passed" ? "bg-[#D1FAE5]" : "bg-[#FEE2E2]"
                    )}>
                      {test.status === "passed" ? (
                        <Check className="w-3 h-3 text-[#059669]" />
                      ) : (
                        <X className="w-3 h-3 text-[#DC2626]" />
                      )}
                    </div>
                    <span className="text-[12px] font-mono text-[#1C1917] truncate flex-1">
                      {test.name}
                    </span>
                    <span
                      className={cn(
                        "text-[10px] font-medium px-1.5 py-0.5 rounded",
                        test.status === "passed"
                          ? "bg-[#D1FAE5] text-[#059669]"
                          : "bg-[#FEE2E2] text-[#DC2626]"
                      )}
                    >
                      {test.status === "passed" ? "PASSED" : "FAILED"}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </AgentPanel>
  );
}
