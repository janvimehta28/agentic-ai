"use client";

export type Severity = "HIGH" | "MEDIUM" | "LOW";

interface FindingCardProps {
  severity: Severity;
  title: string;
  description: string;
  suggestedFix: string;
}

export function FindingCard({
  severity,
  title,
  description,
  suggestedFix,
}: FindingCardProps) {
  const severityConfig = {
    HIGH: {
      borderColor: "#DC2626",
      badgeBg: "#FEE2E2",
      badgeText: "#DC2626",
    },
    MEDIUM: {
      borderColor: "#D97706",
      badgeBg: "#FEF3C7",
      badgeText: "#D97706",
    },
    LOW: {
      borderColor: "#A8A29E",
      badgeBg: "#F5F4F0",
      badgeText: "#57534E",
    },
  };

  const config = severityConfig[severity];

  return (
    <div
      className="bg-white border border-[#E4E2DC] rounded-lg p-3.5 mb-2 transition-all duration-150 hover:shadow-card-hover hover:border-[#C9C7BF] hover:-translate-y-px cursor-default"
      style={{ borderLeftWidth: "3px", borderLeftColor: config.borderColor }}
    >
      <div className="flex items-center gap-2 mb-1.5">
        <span
          className="text-[10px] uppercase tracking-wide font-medium px-2 py-0.5 rounded"
          style={{
            backgroundColor: config.badgeBg,
            color: config.badgeText,
          }}
        >
          {severity}
        </span>
        <span className="text-[13px] font-medium text-[#1C1917] truncate flex-1">
          {title}
        </span>
      </div>

      <p className="text-[12px] text-[#57534E] mt-1.5 line-clamp-2">
        {description}
      </p>

      <p className="text-[12px] text-[#0D9488] mt-1.5 line-clamp-1">
        <span className="font-medium">Fix: </span>
        {suggestedFix}
      </p>
    </div>
  );
}
