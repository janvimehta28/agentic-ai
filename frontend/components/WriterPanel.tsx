"use client";

import { AgentPanel, AgentStatus } from "./AgentPanel";
import { WriterSkeleton } from "./SkeletonLoader";
import { cn } from "@/lib/utils";

interface WriterPanelProps {
  status: AgentStatus;
  code: string | null;
  className?: string;
}

// Simple syntax highlighting for Python
function highlightCode(code: string): JSX.Element[] {
  const lines = code.split("\n");
  
  return lines.map((line, lineIndex) => {
    // Keywords
    let highlighted = line
      .replace(
        /\b(def|class|if|else|elif|return|import|from|async|await|try|except|finally|with|as|for|while|in|not|and|or|True|False|None|raise|yield)\b/g,
        '<span style="color: #C084FC">$1</span>'
      )
      // Strings
      .replace(
        /(["'])(?:(?=(\\?))\2.)*?\1/g,
        '<span style="color: #86EFAC">$&</span>'
      )
      // Comments
      .replace(
        /(#.*)$/g,
        '<span style="color: #64748B">$1</span>'
      )
      // Numbers
      .replace(
        /\b(\d+)\b/g,
        '<span style="color: #FCA5A5">$1</span>'
      )
      // Function calls
      .replace(
        /\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(/g,
        '<span style="color: #93C5FD">$1</span>('
      );

    return (
      <div key={lineIndex} className="flex">
        <span className="w-10 pr-3 mr-3 text-right text-[#4A4268] border-r border-[#2D2A45] select-none flex-shrink-0">
          {lineIndex + 1}
        </span>
        <span 
          className="flex-1"
          dangerouslySetInnerHTML={{ __html: highlighted || "&nbsp;" }}
        />
      </div>
    );
  });
}

export function WriterPanel({ status, code, className }: WriterPanelProps) {
  const isEmpty = !code || code.length === 0;
  const isLoading = status === "running" && isEmpty;

  return (
    <AgentPanel
      name="Writer Agent"
      role="Senior Engineer"
      color="purple"
      status={status}
      outputPath="output/generated_code.py"
      copyContent={code || undefined}
      className={className}
    >
      <div className="h-full">
        {isLoading ? (
          <div className="bg-[#1E1B2E] min-h-[360px] max-h-[480px]">
            <WriterSkeleton />
          </div>
        ) : isEmpty ? (
          <div className="bg-[#1E1B2E] min-h-[360px] max-h-[480px] flex flex-col items-center justify-center">
            <svg className="w-12 h-12 text-[#3D3654]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
            </svg>
            <p className="text-[14px] text-[#4A4268] mt-3">Generated code will appear here</p>
            <p className="text-[12px] text-[#3D3654] mt-1">Run the pipeline to see results</p>
          </div>
        ) : (
          <div className={cn(
            "bg-[#1E1B2E] min-h-[360px] max-h-[480px] overflow-y-auto dark-scrollbar p-5",
            "font-mono text-[13px] leading-[1.7] text-[#E2E8F0]"
          )}>
            <code className="block">
              {highlightCode(code)}
            </code>
          </div>
        )}
      </div>
    </AgentPanel>
  );
}
