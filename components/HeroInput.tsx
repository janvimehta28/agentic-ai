"use client";

import { cn } from "@/lib/utils";
import { Loader2, Zap, Layers, Shield } from "lucide-react";

interface HeroInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  onClear: () => void;
  isRunning: boolean;
  maxLength?: number;
  className?: string;
}

export function HeroInput({
  value,
  onChange,
  onSubmit,
  onClear,
  isRunning,
  maxLength = 1000,
  className,
}: HeroInputProps) {
  const isDisabled = value.trim().length === 0 || isRunning;

  return (
    <section className={cn("bg-white border-b border-[#E4E2DC] py-12 px-8", className)}>
      <div className="max-w-[1400px] mx-auto flex flex-col lg:flex-row gap-12">
        {/* Left Side - 60% */}
        <div className="lg:w-[60%]">
          {/* Label */}
          <p className="text-[12px] uppercase tracking-[0.08em] font-medium text-[#6D28D9] mb-3">
            Multi-Agent AI Pipeline
          </p>

          {/* Headline */}
          <h1 className="text-[36px] font-bold text-[#1C1917] leading-[1.2] text-balance">
            Code that writes, tests,
            <br />
            and audits itself.
          </h1>

          {/* Subheadline */}
          <p className="text-[16px] text-[#57534E] mt-3 leading-[1.6] max-w-[520px] text-pretty">
            Paste a development ticket below. Three specialized AI agents will
            generate code, write unit tests, and find security vulnerabilities —
            autonomously and in real time.
          </p>

          {/* Textarea */}
          <div className="mt-6">
            <textarea
              value={value}
              onChange={(e) => onChange(e.target.value)}
              maxLength={maxLength}
              disabled={isRunning}
              placeholder={`Describe your task or paste a Jira ticket...

Example: Build a login endpoint that validates username and password against a database and returns a JWT token if valid credentials are provided.`}
              className={cn(
                "w-full h-[140px] bg-[#F9F8F6] border-[1.5px] border-[#E4E2DC] rounded-[10px]",
                "px-4 py-3.5 text-[14px] text-[#1C1917] placeholder:text-[#A8A29E] leading-[1.6]",
                "resize-y focus:outline-none focus:border-[#6D28D9] focus:shadow-[0_0_0_3px_rgba(109,40,217,0.15)]",
                "transition-all disabled:opacity-60 disabled:cursor-not-allowed"
              )}
            />
          </div>

          {/* Bottom Row */}
          <div className="flex items-center justify-between mt-3">
            {/* Character Count */}
            <span className="text-[12px] text-[#A8A29E]">
              {value.length} / {maxLength}
            </span>

            {/* Buttons */}
            <div className="flex gap-2">
              {/* Clear Button */}
              <button
                onClick={onClear}
                disabled={value.length === 0 || isRunning}
                className={cn(
                  "px-[18px] py-[9px] rounded-lg text-[13px] border border-[#E4E2DC] text-[#57534E]",
                  "hover:bg-[#F5F4F0] transition-colors",
                  "disabled:opacity-50 disabled:cursor-not-allowed"
                )}
              >
                Clear
              </button>

              {/* Run Pipeline Button */}
              <button
                onClick={onSubmit}
                disabled={isDisabled}
                className={cn(
                  "flex items-center gap-2 px-6 py-2.5 rounded-lg text-[14px] font-medium transition-all",
                  isDisabled
                    ? "bg-[#E4E2DC] text-[#A8A29E] cursor-not-allowed"
                    : "bg-[#6D28D9] text-white hover:bg-[#5B21B6] shadow-[0_1px_3px_rgba(109,40,217,0.3)] hover:shadow-[0_4px_12px_rgba(109,40,217,0.35)]"
                )}
              >
                {isRunning && <Loader2 className="w-4 h-4 animate-spin" />}
                {isRunning ? "Running..." : "Run Pipeline"}
              </button>
            </div>
          </div>
        </div>

        {/* Right Side - 40% - Stat Cards */}
        <div className="lg:w-[40%] flex flex-col gap-3">
          {/* Card 1 - 3 Agents */}
          <div className="flex gap-3 p-4 bg-[#F9F8F6] border border-[#E4E2DC] rounded-xl">
            <div className="w-8 h-8 rounded-lg bg-[#EDE9FE] flex items-center justify-center flex-shrink-0">
              <Zap className="w-4 h-4 text-[#6D28D9]" />
            </div>
            <div>
              <p className="text-[14px] font-medium text-[#1C1917]">3 Agents</p>
              <p className="text-[12px] text-[#57534E] mt-0.5">Writer, Tester, and Red Team work in parallel</p>
            </div>
          </div>

          {/* Card 2 - Parallel Execution */}
          <div className="flex gap-3 p-4 bg-[#F9F8F6] border border-[#E4E2DC] rounded-xl">
            <div className="w-8 h-8 rounded-lg bg-[#CCFBF1] flex items-center justify-center flex-shrink-0">
              <Layers className="w-4 h-4 text-[#0D9488]" />
            </div>
            <div>
              <p className="text-[14px] font-medium text-[#1C1917]">Parallel Execution</p>
              <p className="text-[12px] text-[#57534E] mt-0.5">Testing and security review run simultaneously</p>
            </div>
          </div>

          {/* Card 3 - Adversarial Review */}
          <div className="flex gap-3 p-4 bg-[#F9F8F6] border border-[#E4E2DC] rounded-xl">
            <div className="w-8 h-8 rounded-lg bg-[#FEE2E2] flex items-center justify-center flex-shrink-0">
              <Shield className="w-4 h-4 text-[#DC2626]" />
            </div>
            <div>
              <p className="text-[14px] font-medium text-[#1C1917]">Adversarial Review</p>
              <p className="text-[12px] text-[#57534E] mt-0.5">Red Team agent hunts for vulnerabilities</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
