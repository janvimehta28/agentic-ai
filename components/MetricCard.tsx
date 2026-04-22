"use client";

import { useEffect, useState, useRef } from "react";

interface MetricCardProps {
  label: string;
  value: number;
  color?: "default" | "success" | "danger" | "warning" | "muted";
}

export function MetricCard({ 
  label, 
  value, 
  color = "default",
}: MetricCardProps) {
  const [displayValue, setDisplayValue] = useState(0);
  const prevValueRef = useRef(0);

  useEffect(() => {
    if (value === prevValueRef.current) return;
    
    const startValue = prevValueRef.current;
    const endValue = value;
    const duration = 600;
    const steps = 30;
    const increment = (endValue - startValue) / steps;
    let current = startValue;
    let step = 0;

    const interval = setInterval(() => {
      step++;
      current += increment;
      if (step >= steps) {
        setDisplayValue(endValue);
        clearInterval(interval);
      } else {
        setDisplayValue(Math.round(current));
      }
    }, duration / steps);

    prevValueRef.current = value;
    return () => clearInterval(interval);
  }, [value]);

  const colorStyles = {
    default: {
      value: "text-[#1C1917]",
      label: "text-[#57534E]",
    },
    success: {
      value: "text-[#059669]",
      label: "text-[#059669]",
    },
    danger: {
      value: "text-[#DC2626]",
      label: "text-[#DC2626]",
    },
    warning: {
      value: "text-[#D97706]",
      label: "text-[#D97706]",
    },
    muted: {
      value: "text-[#57534E]",
      label: "text-[#57534E]",
    },
  };

  const styles = colorStyles[color];

  return (
    <div className="bg-[#F9F8F6] border border-[#E4E2DC] rounded-lg px-3 py-2.5 text-center flex-1">
      <div className={`text-[22px] font-bold ${styles.value}`}>
        {displayValue}
      </div>
      <div className={`text-[11px] mt-0.5 ${styles.label}`}>
        {label}
      </div>
    </div>
  );
}
