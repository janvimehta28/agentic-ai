"use client";

import { cn } from "@/lib/utils";
import { Check, X } from "lucide-react";

export type StepStatus = "idle" | "active" | "complete" | "error";

interface PipelineStep {
  number: number;
  label: string;
  status: StepStatus;
}

interface PipelineStatusBarProps {
  steps: PipelineStep[];
  statusMessage: string;
  elapsedTime?: string;
  className?: string;
}

export function PipelineStatusBar({
  steps,
  statusMessage,
  elapsedTime,
  className,
}: PipelineStatusBarProps) {
  const getStepStyles = (status: StepStatus) => {
    switch (status) {
      case "idle":
        return {
          circle: "bg-[#F5F4F0] border-[#E4E2DC]",
          text: "text-[#A8A29E]",
          label: "text-[#A8A29E]",
        };
      case "active":
        return {
          circle: "bg-[#6D28D9] border-[#6D28D9]",
          text: "text-white",
          label: "text-[#6D28D9]",
        };
      case "complete":
        return {
          circle: "bg-[#059669] border-[#059669]",
          text: "text-white",
          label: "text-[#059669]",
        };
      case "error":
        return {
          circle: "bg-[#DC2626] border-[#DC2626]",
          text: "text-white",
          label: "text-[#DC2626]",
        };
    }
  };

  const getLineStatus = (currentIndex: number) => {
    const nextStep = steps[currentIndex + 1];
    if (!nextStep) return "idle";
    
    if (nextStep.status === "complete") return "complete";
    if (nextStep.status === "active" || nextStep.status === "error") return "active";
    return "idle";
  };

  return (
    <div className={cn(
      "bg-white border border-[#E4E2DC] rounded-2xl p-5 px-7 mx-auto my-6 shadow-card",
      className
    )}>
      <div className="flex items-center justify-between">
        {/* Steps Row */}
        <div className="flex items-center">
          {steps.map((step, index) => {
            const styles = getStepStyles(step.status);
            const isLast = index === steps.length - 1;
            const lineStatus = getLineStatus(index);

            return (
              <div key={step.number} className="flex items-center">
                {/* Step Node */}
                <div className="flex flex-col items-center">
                  <div
                    className={cn(
                      "w-9 h-9 rounded-full border-2 flex items-center justify-center transition-all duration-300 relative",
                      styles.circle
                    )}
                  >
                    {step.status === "active" && (
                      <span className="absolute inset-0 rounded-full animate-pulse-ring" />
                    )}
                    {step.status === "complete" ? (
                      <Check className="w-4 h-4 text-white" />
                    ) : step.status === "error" ? (
                      <X className="w-4 h-4 text-white" />
                    ) : (
                      <span className={cn("text-[14px] font-medium", styles.text)}>
                        {step.number}
                      </span>
                    )}
                  </div>
                  <span
                    className={cn(
                      "mt-2 text-[12px] font-medium whitespace-nowrap",
                      styles.label
                    )}
                  >
                    {step.label}
                  </span>
                </div>

                {/* Connecting Line */}
                {!isLast && (
                  <div className="w-16 sm:w-20 h-0.5 mx-2 bg-[#E4E2DC] overflow-hidden relative">
                    {(lineStatus === "active" || lineStatus === "complete") && (
                      <div 
                        className={cn(
                          "absolute inset-y-0 left-0 bg-[#6D28D9]",
                          lineStatus === "complete" ? "w-full" : "animate-line-fill"
                        )}
                      />
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Status Text and Timer */}
        <div className="text-right ml-6">
          <p className="text-[15px] font-medium text-[#1C1917]">
            {statusMessage}
          </p>
          {elapsedTime && (
            <p className="text-[13px] text-[#A8A29E] mt-0.5">
              {elapsedTime}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
