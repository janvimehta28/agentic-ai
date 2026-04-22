"use client";

import { useState, useEffect, useCallback } from "react";
import { Navbar } from "@/components/Navbar";
import { HeroInput } from "@/components/HeroInput";
import { PipelineStatusBar, StepStatus } from "@/components/PipelineStatusBar";
import { WriterPanel } from "@/components/WriterPanel";
import { TesterPanel } from "@/components/TesterPanel";
import { RedTeamPanel } from "@/components/RedTeamPanel";
import { LiveLogStream } from "@/components/LiveLogStream";
import { DownloadReport } from "@/components/DownloadReport";
import { AgentStatus } from "@/components/AgentPanel";
import { Severity } from "@/components/FindingCard";

// API URL from environment or fallback
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Type definitions
type LogLevel = "info" | "success" | "warning" | "error";
type AgentType = "WRITER" | "TESTER" | "RED TEAM" | "SYSTEM";

interface LogEntry {
  timestamp: string;
  agent: AgentType;
  message: string;
  level: LogLevel;
}

interface TestResult {
  name: string;
  status: "passed" | "failed";
  error?: string;
}

interface Finding {
  severity: Severity;
  title: string;
  description: string;
  suggestedFix: string;
}

interface WriterOutput {
  code: string | null;
  status: AgentStatus;
}

interface TesterOutput {
  totalTests: number;
  passed: number;
  failed: number;
  coveragePercent: number;
  testResults: TestResult[];
  status: AgentStatus;
}

interface RedTeamOutput {
  findings: Finding[];
  counts: { high: number; medium: number; low: number };
  status: AgentStatus;
}

// Helper function to get current timestamp
function getTimestamp(): string {
  return new Date().toLocaleTimeString("en-US", {
    hour12: false,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

// Format elapsed time
function formatElapsedTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")} elapsed`;
}

export default function Home() {
  // Pipeline state
  const [pipelineStatus, setPipelineStatus] = useState<
    "idle" | "running" | "complete" | "error"
  >("idle");
  const [isConnected, setIsConnected] = useState(false);
  const [ticketInput, setTicketInput] = useState("");
  const [startTime, setStartTime] = useState<number | null>(null);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  // Agent outputs
  const [writerOutput, setWriterOutput] = useState<WriterOutput>({
    code: null,
    status: "idle",
  });
  const [testerOutput, setTesterOutput] = useState<TesterOutput>({
    totalTests: 0,
    passed: 0,
    failed: 0,
    coveragePercent: 0,
    testResults: [],
    status: "idle",
  });
  const [redTeamOutput, setRedTeamOutput] = useState<RedTeamOutput>({
    findings: [],
    counts: { high: 0, medium: 0, low: 0 },
    status: "idle",
  });

  // Logs
  const [logs, setLogs] = useState<LogEntry[]>([]);

  // Add a log entry
  const addLog = useCallback(
    (agent: AgentType, message: string, level: LogLevel = "info") => {
      setLogs((prev) => [
        ...prev,
        {
          timestamp: getTimestamp(),
          agent,
          message,
          level,
        },
      ]);
    },
    []
  );

  // Timer for elapsed seconds
  useEffect(() => {
    if (pipelineStatus !== "running" || !startTime) return;

    const interval = setInterval(() => {
      setElapsedSeconds(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);

    return () => clearInterval(interval);
  }, [pipelineStatus, startTime]);

  // Check API connection on mount
  useEffect(() => {
    const checkConnection = async () => {
      try {
        const response = await fetch(`${API_URL}/health`, {
          method: "GET",
          signal: AbortSignal.timeout(3000),
        });
        setIsConnected(response.ok);
      } catch {
        setIsConnected(false);
      }
    };

    checkConnection();
    const interval = setInterval(checkConnection, 30000);
    return () => clearInterval(interval);
  }, []);

  // Poll for results while running
  useEffect(() => {
    if (pipelineStatus !== "running") return;

    const pollResults = async () => {
      try {
        const response = await fetch(`${API_URL}/results`);
        if (!response.ok) return;

        const data = await response.json();

        // Update writer output
        if (data.writer) {
          setWriterOutput({
            code: data.writer.code || null,
            status: data.writer.status || "running",
          });
        }

        // Update tester output
        if (data.tester) {
          setTesterOutput({
            totalTests: data.tester.totalTests || 0,
            passed: data.tester.passed || 0,
            failed: data.tester.failed || 0,
            coveragePercent: data.tester.coverage || 0,
            testResults: data.tester.testResults || [],
            status: data.tester.status || "running",
          });
        }

        // Update red team output
        if (data.redteam) {
          setRedTeamOutput({
            findings: data.redteam.findings || [],
            counts: data.redteam.counts || { high: 0, medium: 0, low: 0 },
            status: data.redteam.status || "running",
          });
        }

        // Check if all complete
        const allComplete =
          data.writer?.status === "complete" &&
          data.tester?.status === "complete" &&
          data.redteam?.status === "complete";

        const hasError =
          data.writer?.status === "error" ||
          data.tester?.status === "error" ||
          data.redteam?.status === "error";

        if (allComplete) {
          setPipelineStatus("complete");
          addLog("SYSTEM", "Pipeline completed successfully", "success");
        } else if (hasError) {
          setPipelineStatus("error");
          addLog("SYSTEM", "Pipeline encountered an error", "error");
        }
      } catch {
        // Silent fail for polling
      }
    };

    const interval = setInterval(pollResults, 2000);
    return () => clearInterval(interval);
  }, [pipelineStatus, addLog]);

  // SSE log streaming
  useEffect(() => {
    if (pipelineStatus !== "running") return;

    let eventSource: EventSource | null = null;

    try {
      eventSource = new EventSource(`${API_URL}/stream-logs`);

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLogs((prev) => [
            ...prev,
            {
              timestamp: data.timestamp || getTimestamp(),
              agent: data.agent,
              message: data.message,
              level: data.level || "info",
            },
          ]);
        } catch {
          // Invalid JSON, ignore
        }
      };

      eventSource.onerror = () => {
        eventSource?.close();
      };
    } catch {
      // SSE not supported or connection failed
    }

    return () => {
      eventSource?.close();
    };
  }, [pipelineStatus]);

  // Run pipeline
  const handleRunPipeline = async () => {
    if (!ticketInput.trim()) return;

    // Reset state
    setPipelineStatus("running");
    setStartTime(Date.now());
    setElapsedSeconds(0);
    setLogs([]);

    setWriterOutput({ code: null, status: "running" });
    setTesterOutput({
      totalTests: 0,
      passed: 0,
      failed: 0,
      coveragePercent: 0,
      testResults: [],
      status: "idle",
    });
    setRedTeamOutput({
      findings: [],
      counts: { high: 0, medium: 0, low: 0 },
      status: "idle",
    });

    addLog("SYSTEM", "Pipeline started", "info");
    addLog("SYSTEM", "Processing ticket input...", "info");

    try {
      const response = await fetch(`${API_URL}/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ticket: ticketInput }),
      });

      if (!response.ok) {
        throw new Error("Failed to start pipeline");
      }

      addLog("WRITER", "Writer Agent initialized", "info");
    } catch {
      // If API fails, simulate the pipeline for demo purposes
      addLog("SYSTEM", "Running in demo mode (no backend connected)", "warning");
      simulatePipeline();
    }
  };

  // Simulate pipeline for demo purposes
  const simulatePipeline = () => {
    // Writer phase
    setTimeout(() => {
      addLog("WRITER", "Analyzing ticket requirements...", "info");
    }, 500);

    setTimeout(() => {
      addLog("WRITER", "Generating Python code...", "info");
    }, 1500);

    setTimeout(() => {
      setWriterOutput({
        code: `import jwt
import bcrypt
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

app = FastAPI()
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

Base = declarative_base()
engine = create_engine("sqlite:///./users.db")
SessionLocal = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True)
    hashed_password = Column(String)

class LoginRequest(BaseModel):
    username: str
    password: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(
        plain.encode(), hashed.encode()
    )

def create_token(username: str) -> str:
    expires = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(
        {"sub": username, "exp": expires},
        SECRET_KEY, algorithm=ALGORITHM
    )

@app.post("/login")
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.username == request.username
    ).first()
    
    if not user or not verify_password(
        request.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    
    return {"token": create_token(user.username)}`,
        status: "complete",
      });
      addLog("WRITER", "Code generation complete", "success");

      // Start Tester and Red Team
      setTesterOutput((prev) => ({ ...prev, status: "running" }));
      setRedTeamOutput((prev) => ({ ...prev, status: "running" }));
      addLog("TESTER", "Tester Agent initialized", "info");
      addLog("RED TEAM", "Red Team Agent initialized", "info");
    }, 3000);

    // Tester phase
    setTimeout(() => {
      addLog("TESTER", "Running unit tests...", "info");
    }, 4000);

    setTimeout(() => {
      addLog("TESTER", "Analyzing code coverage...", "info");
    }, 5000);

    setTimeout(() => {
      setTesterOutput({
        totalTests: 8,
        passed: 7,
        failed: 1,
        coveragePercent: 87,
        testResults: [
          { name: "test_login_valid_credentials", status: "passed" },
          { name: "test_login_invalid_password", status: "passed" },
          { name: "test_login_nonexistent_user", status: "passed" },
          { name: "test_token_generation", status: "passed" },
          { name: "test_token_expiration", status: "passed" },
          { name: "test_password_verification", status: "passed" },
          { name: "test_db_connection", status: "passed" },
          { name: "test_concurrent_logins", status: "failed", error: "Timeout" },
        ],
        status: "complete",
      });
      addLog("TESTER", "Testing complete: 7/8 passed", "success");
    }, 6500);

    // Red Team phase
    setTimeout(() => {
      addLog("RED TEAM", "Scanning for vulnerabilities...", "info");
    }, 4500);

    setTimeout(() => {
      addLog("RED TEAM", "Analyzing authentication flow...", "info");
    }, 5500);

    setTimeout(() => {
      setRedTeamOutput({
        findings: [
          {
            severity: "HIGH",
            title: "Hardcoded Secret Key",
            description:
              "SECRET_KEY is hardcoded in the source code. This is a critical security vulnerability that could allow attackers to forge JWT tokens.",
            suggestedFix:
              "Load SECRET_KEY from environment variables using os.getenv()",
          },
          {
            severity: "MEDIUM",
            title: "No Rate Limiting",
            description:
              "The login endpoint has no rate limiting, making it vulnerable to brute force attacks.",
            suggestedFix:
              "Implement rate limiting using FastAPI-Limiter or similar middleware",
          },
          {
            severity: "LOW",
            title: "Missing Input Validation",
            description:
              "Username field lacks validation for length and character restrictions.",
            suggestedFix:
              "Add Pydantic validators to enforce username constraints",
          },
        ],
        counts: { high: 1, medium: 1, low: 1 },
        status: "complete",
      });
      addLog("RED TEAM", "Security scan complete: 3 findings", "warning");
    }, 7000);

    // Complete pipeline
    setTimeout(() => {
      setPipelineStatus("complete");
      addLog("SYSTEM", "Pipeline completed successfully", "success");
    }, 8000);
  };

  // Clear input
  const handleClear = () => {
    setTicketInput("");
  };

  // Clear logs
  const handleClearLogs = () => {
    setLogs([]);
  };

  // Download report
  const handleDownloadReport = () => {
    const report = `# AutonomousDev Pipeline Report
Generated: ${new Date().toISOString()}

## Input Ticket
${ticketInput}

## Generated Code
\`\`\`python
${writerOutput.code || "No code generated"}
\`\`\`

## Test Results
- Total Tests: ${testerOutput.totalTests}
- Passed: ${testerOutput.passed}
- Failed: ${testerOutput.failed}
- Coverage: ${testerOutput.coveragePercent}%

### Test Details
${testerOutput.testResults
  .map((t) => `- ${t.name}: ${t.status.toUpperCase()}${t.error ? ` (${t.error})` : ""}`)
  .join("\n")}

## Security Findings
${redTeamOutput.findings
  .map(
    (f) => `### [${f.severity}] ${f.title}
${f.description}
**Fix:** ${f.suggestedFix}
`
  )
  .join("\n")}

## Summary
- High Severity: ${redTeamOutput.counts.high}
- Medium Severity: ${redTeamOutput.counts.medium}
- Low Severity: ${redTeamOutput.counts.low}
`;

    const blob = new Blob([report], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "report.md";
    a.click();
    URL.revokeObjectURL(url);
  };

  // Compute pipeline steps
  const getPipelineSteps = (): { number: number; label: string; status: StepStatus }[] => {
    if (pipelineStatus === "idle") {
      return [
        { number: 1, label: "Input", status: "idle" },
        { number: 2, label: "Writer", status: "idle" },
        { number: 3, label: "Tester + Red Team", status: "idle" },
        { number: 4, label: "Complete", status: "idle" },
      ];
    }

    const writerDone = writerOutput.status === "complete";
    const testerDone = testerOutput.status === "complete";
    const redTeamDone = redTeamOutput.status === "complete";
    const allDone = writerDone && testerDone && redTeamDone;

    return [
      { number: 1, label: "Input", status: "complete" },
      {
        number: 2,
        label: "Writer",
        status: writerOutput.status === "error"
          ? "error"
          : writerDone
          ? "complete"
          : writerOutput.status === "running"
          ? "active"
          : "idle",
      },
      {
        number: 3,
        label: "Tester + Red Team",
        status:
          testerOutput.status === "error" || redTeamOutput.status === "error"
            ? "error"
            : testerDone && redTeamDone
            ? "complete"
            : testerOutput.status === "running" || redTeamOutput.status === "running"
            ? "active"
            : "idle",
      },
      {
        number: 4,
        label: "Complete",
        status: pipelineStatus === "error"
          ? "error"
          : allDone
          ? "complete"
          : "idle",
      },
    ];
  };

  // Status message
  const getStatusMessage = (): string => {
    if (pipelineStatus === "idle") return "";
    if (pipelineStatus === "error") return "Pipeline encountered an error";
    if (pipelineStatus === "complete") return "Pipeline complete";

    if (writerOutput.status === "running") return "Writer Agent generating code...";
    if (testerOutput.status === "running" || redTeamOutput.status === "running") {
      return "Tester and Red Team running in parallel...";
    }
    return "Processing...";
  };

  return (
    <div className="min-h-screen bg-[#F5F4F0]">
      <Navbar isConnected={isConnected} />

      {/* Hero Input Section */}
      <HeroInput
        value={ticketInput}
        onChange={setTicketInput}
        onSubmit={handleRunPipeline}
        onClear={handleClear}
        isRunning={pipelineStatus === "running"}
      />

      <main className="max-w-[1400px] mx-auto px-8 pb-10">
        {/* Pipeline Status Bar - Only visible after running */}
        {pipelineStatus !== "idle" && (
          <PipelineStatusBar
            steps={getPipelineSteps()}
            statusMessage={getStatusMessage()}
            elapsedTime={pipelineStatus === "running" ? formatElapsedTime(elapsedSeconds) : undefined}
          />
        )}

        {/* Three Agent Panels - 2fr 1fr 1fr grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-[2fr_1fr_1fr] gap-5 my-6">
          <WriterPanel
            status={writerOutput.status}
            code={writerOutput.code}
            className="md:col-span-2 lg:col-span-1"
          />
          <TesterPanel
            status={testerOutput.status}
            totalTests={testerOutput.totalTests}
            passed={testerOutput.passed}
            failed={testerOutput.failed}
            coveragePercent={testerOutput.coveragePercent}
            testResults={testerOutput.testResults}
          />
          <RedTeamPanel
            status={redTeamOutput.status}
            findings={redTeamOutput.findings}
            counts={redTeamOutput.counts}
          />
        </div>

        {/* Live Log Stream - Only visible after running */}
        {pipelineStatus !== "idle" && (
          <LiveLogStream
            logs={logs}
            onClear={handleClearLogs}
            isRunning={pipelineStatus === "running"}
            className="mb-6"
          />
        )}

        {/* Download Report - Only visible after complete */}
        {pipelineStatus === "complete" && (
          <DownloadReport
            onDownload={handleDownloadReport}
            className="mb-10"
          />
        )}
      </main>
    </div>
  );
}
