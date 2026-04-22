"use client";

interface SkeletonLineProps {
  width?: string;
  height?: string;
  className?: string;
}

export function SkeletonLine({ width = "100%", height = "14px", className = "" }: SkeletonLineProps) {
  return (
    <div
      className={`animate-shimmer rounded ${className}`}
      style={{ width, height }}
    />
  );
}

export function WriterSkeleton() {
  return (
    <div className="flex flex-col gap-2.5 p-5 min-h-[360px]">
      <div className="h-3.5 w-full bg-[#2D2A45] rounded animate-pulse" />
      <div className="h-3.5 w-[85%] bg-[#2D2A45] rounded animate-pulse" />
      <div className="h-3.5 w-[92%] bg-[#2D2A45] rounded animate-pulse" />
      <div className="h-3.5 w-[78%] bg-[#2D2A45] rounded animate-pulse" />
      <div className="h-3.5 w-[60%] bg-[#2D2A45] rounded animate-pulse" />
    </div>
  );
}

export function TesterSkeleton() {
  return (
    <div className="p-4">
      <div className="flex gap-2 mb-4">
        <SkeletonLine height="60px" className="flex-1" />
        <SkeletonLine height="60px" className="flex-1" />
        <SkeletonLine height="60px" className="flex-1" />
      </div>
      <SkeletonLine width="100%" height="8px" className="mb-4" />
      <div className="flex flex-col gap-2">
        <SkeletonLine width="100%" height="32px" />
        <SkeletonLine width="100%" height="32px" />
        <SkeletonLine width="100%" height="32px" />
      </div>
    </div>
  );
}

export function RedTeamSkeleton() {
  return (
    <div className="p-4">
      <div className="flex gap-2 mb-4">
        <SkeletonLine height="60px" className="flex-1" />
        <SkeletonLine height="60px" className="flex-1" />
        <SkeletonLine height="60px" className="flex-1" />
      </div>
      <div className="flex flex-col gap-2">
        <SkeletonLine width="100%" height="80px" />
        <SkeletonLine width="100%" height="80px" />
      </div>
    </div>
  );
}
