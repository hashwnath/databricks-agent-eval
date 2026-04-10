import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
} from "remotion";

interface TermLine {
  text: string;
  color?: string;
  delay: number; // frame offset within scene
  prefix?: string;
}

const TERMINAL_LINES: TermLine[] = [
  { text: "$ python -m eval --scenarios scenarios/routing.yaml --baseline baseline.json", delay: 0, color: "#e2e8f0" },
  { text: "", delay: 15 },
  { text: "Loading scenarios from scenarios/routing.yaml...", delay: 20, color: "#94a3b8" },
  { text: "Loaded 12 scenarios", delay: 35, color: "#22c55e" },
  { text: "", delay: 40 },
  { text: "Running evaluation...", delay: 50, color: "#94a3b8" },
  { text: "", delay: 55 },
  { text: "[1/12] pipeline_failure_cascade         ", delay: 70, color: "#e2e8f0" },
  { text: "  CorrectnessJudge ............ PASS  (0.92)", delay: 85, color: "#22c55e" },
  { text: "  RoutingAccuracyJudge ........ PASS  (0.88)", delay: 95, color: "#22c55e" },
  { text: "  GroundednessJudge ........... PASS  (0.85)", delay: 105, color: "#22c55e" },
  { text: "  CostEfficiencyJudge ......... PASS  (0.79)", delay: 115, color: "#22c55e" },
  { text: "", delay: 120 },
  { text: "[2/12] schema_drift_detection           ", delay: 130, color: "#e2e8f0" },
  { text: "  CorrectnessJudge ............ PASS  (0.90)", delay: 145, color: "#22c55e" },
  { text: "  RoutingAccuracyJudge ........ FAIL  (0.40)", delay: 155, color: "#ef4444" },
  { text: "  GroundednessJudge ........... PASS  (0.82)", delay: 165, color: "#22c55e" },
  { text: "  CostEfficiencyJudge ......... PASS  (0.71)", delay: 175, color: "#22c55e" },
  { text: "", delay: 180 },
  { text: "[3/12] query_optimization_spark         ", delay: 190, color: "#e2e8f0" },
  { text: "  CorrectnessJudge ............ PASS  (0.95)", delay: 205, color: "#22c55e" },
  { text: "  RoutingAccuracyJudge ........ PASS  (0.91)", delay: 215, color: "#22c55e" },
  { text: "  GroundednessJudge ........... PASS  (0.87)", delay: 225, color: "#22c55e" },
  { text: "  CostEfficiencyJudge ......... PASS  (0.83)", delay: 235, color: "#22c55e" },
  { text: "", delay: 240 },
  { text: "... [4-12] evaluating remaining scenarios", delay: 260, color: "#64748b" },
  { text: "", delay: 275 },
  { text: "============================================", delay: 300, color: "#e2e8f0" },
  { text: "         EVALUATION RESULTS", delay: 305, color: "#e2e8f0" },
  { text: "============================================", delay: 310, color: "#e2e8f0" },
  { text: "", delay: 315 },
  { text: "Pass Rate:        83% (10/12 scenarios)", delay: 325, color: "#22c55e" },
  { text: "Aggregate Score:  0.84", delay: 335, color: "#22c55e" },
  { text: "Duration:         4,231ms", delay: 345, color: "#94a3b8" },
  { text: "", delay: 355 },
  { text: "Dimension Scores:", delay: 365, color: "#e2e8f0" },
  { text: "  correctness        ████████████████████░░  92%", delay: 375, color: "#22c55e" },
  { text: "  routing_accuracy   █████████████████░░░░░  85%", delay: 385, color: "#22c55e" },
  { text: "  groundedness       ██████████████████░░░░  88%", delay: 395, color: "#22c55e" },
  { text: "  cost_efficiency    ███████████████░░░░░░░  73%", delay: 405, color: "#22c55e" },
  { text: "", delay: 415 },
  { text: "REGRESSION DETECTED:", delay: 430, color: "#ef4444" },
  { text: "  routing_accuracy: 95% -> 85% (-10.0%)", delay: 445, color: "#ef4444" },
  { text: "  Threshold: 10% | Status: REGRESSION", delay: 455, color: "#ef4444" },
  { text: "", delay: 465 },
  { text: "HTML report saved to: eval_report.html", delay: 480, color: "#22c55e" },
  { text: "Exit code: 1 (regression detected)", delay: 490, color: "#f59e0b" },
];

export const Scene4Demo: React.FC = () => {
  const frame = useCurrentFrame();

  const titleOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: "clamp" });
  const fadeOut = interpolate(frame, [570, 600], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Scrolling: shift terminal up as lines accumulate
  const visibleLines = TERMINAL_LINES.filter((l) => frame >= l.delay);
  const maxVisibleLines = 22;
  const scrollOffset =
    visibleLines.length > maxVisibleLines
      ? (visibleLines.length - maxVisibleLines) * 26
      : 0;

  return (
    <AbsoluteFill style={{ backgroundColor: "#0f172a", opacity: fadeOut }}>
      {/* Title */}
      <div
        style={{
          position: "absolute",
          top: 30,
          width: "100%",
          textAlign: "center",
          opacity: titleOpacity,
        }}
      >
        <div
          style={{
            fontSize: 32,
            fontWeight: 700,
            fontFamily: "Inter, system-ui, sans-serif",
            color: "#e2e8f0",
          }}
        >
          Real CLI Output
        </div>
      </div>

      {/* Terminal window */}
      <div
        style={{
          position: "absolute",
          left: 160,
          top: 90,
          right: 160,
          bottom: 50,
          background: "#0c0c0c",
          borderRadius: 12,
          border: "1px solid #334155",
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {/* Title bar */}
        <div
          style={{
            height: 36,
            background: "#1a1a2e",
            display: "flex",
            alignItems: "center",
            padding: "0 16px",
            gap: 8,
            borderBottom: "1px solid #334155",
            flexShrink: 0,
          }}
        >
          <div style={{ width: 12, height: 12, borderRadius: 6, background: "#ef4444" }} />
          <div style={{ width: 12, height: 12, borderRadius: 6, background: "#f59e0b" }} />
          <div style={{ width: 12, height: 12, borderRadius: 6, background: "#22c55e" }} />
          <span
            style={{
              marginLeft: 12,
              fontSize: 13,
              color: "#64748b",
              fontFamily: "monospace",
            }}
          >
            databricks-agent-eval
          </span>
        </div>

        {/* Terminal content */}
        <div
          style={{
            flex: 1,
            padding: "16px 20px",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              transform: `translateY(-${scrollOffset}px)`,
              transition: "transform 0.1s ease",
            }}
          >
            {TERMINAL_LINES.map((line, i) => {
              const lineOpacity = interpolate(
                frame,
                [line.delay, line.delay + 3],
                [0, 1],
                { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
              );

              return (
                <div
                  key={i}
                  style={{
                    fontFamily: "'SF Mono', 'Fira Code', 'Consolas', monospace",
                    fontSize: 17,
                    lineHeight: "26px",
                    color: line.color || "#e2e8f0",
                    opacity: lineOpacity,
                    whiteSpace: "pre",
                  }}
                >
                  {line.text || "\u00A0"}
                </div>
              );
            })}

            {/* Blinking cursor */}
            {frame > 490 && (
              <span
                style={{
                  display: "inline-block",
                  width: 10,
                  height: 20,
                  background:
                    Math.floor(frame / 15) % 2 === 0 ? "#22c55e" : "transparent",
                  marginTop: 4,
                }}
              />
            )}
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
