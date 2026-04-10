import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

const FlowNode: React.FC<{
  label: string;
  sublabel?: string;
  x: number;
  y: number;
  delay: number;
  color?: string;
  width?: number;
  height?: number;
  icon?: string;
}> = ({
  label,
  sublabel,
  x,
  y,
  delay,
  color = "#22c55e",
  width = 220,
  height = 80,
  icon,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const s = spring({
    frame: frame - delay,
    fps,
    config: { damping: 12, mass: 0.5 },
  });
  const opacity = interpolate(frame, [delay, delay + 8], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        position: "absolute",
        left: x - width / 2,
        top: y - height / 2,
        width,
        height,
        borderRadius: 12,
        background: "#1e293b",
        border: `2px solid ${color}40`,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        transform: `scale(${s})`,
        opacity,
        boxShadow: `0 0 30px ${color}15`,
      }}
    >
      <div
        style={{
          fontSize: 18,
          fontWeight: 700,
          fontFamily: "Inter, system-ui, sans-serif",
          color: "#e2e8f0",
          display: "flex",
          alignItems: "center",
          gap: 8,
        }}
      >
        {icon && <span style={{ fontSize: 20 }}>{icon}</span>}
        {label}
      </div>
      {sublabel && (
        <div
          style={{
            fontSize: 13,
            color: "#64748b",
            fontFamily: "Inter, system-ui, sans-serif",
            marginTop: 4,
          }}
        >
          {sublabel}
        </div>
      )}
    </div>
  );
};

const Arrow: React.FC<{
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  delay: number;
  color?: string;
}> = ({ x1, y1, x2, y2, delay, color = "#22c55e" }) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [delay, delay + 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const dx = x2 - x1;
  const dy = y2 - y1;
  const len = Math.sqrt(dx * dx + dy * dy);
  const angle = Math.atan2(dy, dx) * (180 / Math.PI);

  return (
    <div
      style={{
        position: "absolute",
        left: x1,
        top: y1,
        width: len * progress,
        height: 3,
        background: `linear-gradient(90deg, ${color}60, ${color})`,
        transformOrigin: "0 50%",
        transform: `rotate(${angle}deg)`,
        borderRadius: 2,
        overflow: "hidden",
      }}
    />
  );
};

export const Scene3Mechanism: React.FC = () => {
  const frame = useCurrentFrame();

  const titleOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: "clamp" });
  const titleY = interpolate(frame, [0, 15], [20, 0], { extrapolateRight: "clamp" });

  // Phase 2: judges appear
  const judgesPhase = interpolate(frame, [180, 200], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Phase 3: scores + regression
  const scoresPhase = interpolate(frame, [330, 350], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const fadeOut = interpolate(frame, [570, 600], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const cx = 960;
  const topY = 160;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0f172a",
        opacity: fadeOut,
      }}
    >
      {/* Grid */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage:
            "linear-gradient(rgba(34,197,94,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(34,197,94,0.02) 1px, transparent 1px)",
          backgroundSize: "40px 40px",
        }}
      />

      {/* Title */}
      <div
        style={{
          position: "absolute",
          top: 40,
          width: "100%",
          textAlign: "center",
          opacity: titleOpacity,
          transform: `translateY(${titleY}px)`,
        }}
      >
        <div
          style={{
            fontSize: 42,
            fontWeight: 700,
            fontFamily: "Inter, system-ui, sans-serif",
            color: "#e2e8f0",
          }}
        >
          4 LLM Judges.{" "}
          <span style={{ color: "#22c55e" }}>Automated Regression Detection.</span>
        </div>
        <div
          style={{
            fontSize: 20,
            color: "#64748b",
            fontFamily: "Inter, system-ui, sans-serif",
            marginTop: 8,
          }}
        >
          databricks-agent-eval evaluation pipeline
        </div>
      </div>

      {/* Flow: Scenarios -> Supervisor Agent -> Sub-agents row */}
      <FlowNode label="Scenarios" sublabel="YAML test cases" x={200} y={topY + 100} delay={20} color="#FFD700" />
      <Arrow x1={310} y1={topY + 100} x2={520} y2={topY + 100} delay={35} color="#FFD700" />

      <FlowNode
        label="Supervisor Agent"
        sublabel="Routes to sub-agents"
        x={660}
        y={topY + 100}
        delay={40}
        color="#818cf8"
        width={260}
      />

      {/* Sub-agents */}
      <Arrow x1={790} y1={topY + 100} x2={960} y2={topY + 30} delay={55} color="#818cf8" />
      <Arrow x1={790} y1={topY + 100} x2={960} y2={topY + 100} delay={60} color="#818cf8" />
      <Arrow x1={790} y1={topY + 100} x2={960} y2={topY + 170} delay={65} color="#818cf8" />

      <FlowNode label="pipeline_debugger" x={1120} y={topY + 30} delay={70} color="#818cf8" width={200} height={55} />
      <FlowNode label="schema_analyzer" x={1120} y={topY + 100} delay={75} color="#818cf8" width={200} height={55} />
      <FlowNode label="query_optimizer" x={1120} y={topY + 170} delay={80} color="#818cf8" width={200} height={55} />

      {/* Arrows down to judges */}
      <Arrow x1={660} y1={topY + 140} x2={660} y2={topY + 280} delay={180} color="#22c55e" />

      {/* Judges row */}
      <FlowNode label="CorrectnessJudge" sublabel="LLM-graded" x={320} y={topY + 340} delay={190} color="#22c55e" width={240} />
      <FlowNode label="RoutingAccuracyJudge" sublabel="LLM-graded" x={620} y={topY + 340} delay={200} color="#22c55e" width={240} />
      <FlowNode label="GroundednessJudge" sublabel="LLM-graded" x={920} y={topY + 340} delay={210} color="#22c55e" width={240} />
      <FlowNode label="CostEfficiencyJudge" sublabel="Deterministic" x={1220} y={topY + 340} delay={220} color="#22c55e" width={240} />

      {/* Label for judges */}
      {judgesPhase > 0 && (
        <div
          style={{
            position: "absolute",
            left: 80,
            top: topY + 320,
            fontSize: 14,
            color: "#22c55e",
            fontFamily: "Inter, system-ui, sans-serif",
            fontWeight: 600,
            textTransform: "uppercase",
            letterSpacing: 2,
            opacity: judgesPhase,
            writingMode: "vertical-lr",
            transform: "rotate(180deg)",
          }}
        >
          4 LLM Judges
        </div>
      )}

      {/* Arrows down to scoring */}
      <Arrow x1={660} y1={topY + 380} x2={660} y2={topY + 470} delay={280} color="#f59e0b" />

      {/* Scoring + Regression */}
      <FlowNode label="Aggregator" sublabel="Weighted rubric scoring" x={480} y={topY + 520} delay={300} color="#f59e0b" width={260} />
      <Arrow x1={610} y1={topY + 520} x2={740} y2={topY + 520} delay={320} color="#f59e0b" />
      <FlowNode
        label="Regression Detector"
        sublabel="Baseline comparison, 10% threshold"
        x={920}
        y={topY + 520}
        delay={330}
        color="#ef4444"
        width={300}
        height={80}
      />

      {/* Arrow to report */}
      <Arrow x1={1070} y1={topY + 520} x2={1300} y2={topY + 520} delay={380} color="#22c55e" />
      <FlowNode
        label="HTML Report"
        sublabel="eval_report.html"
        x={1480}
        y={topY + 520}
        delay={400}
        color="#22c55e"
        width={240}
      />

      {/* Score badges appearing */}
      {scoresPhase > 0 && (
        <div
          style={{
            position: "absolute",
            bottom: 60,
            width: "100%",
            display: "flex",
            justifyContent: "center",
            gap: 30,
            opacity: scoresPhase,
          }}
        >
          {[
            { label: "Correctness", score: "92%", color: "#22c55e" },
            { label: "Routing", score: "85%", color: "#22c55e" },
            { label: "Groundedness", score: "88%", color: "#22c55e" },
            { label: "Cost Efficiency", score: "73%", color: "#22c55e" },
          ].map((d) => (
            <div
              key={d.label}
              style={{
                background: "#1e293b",
                borderRadius: 10,
                padding: "12px 24px",
                border: `1px solid ${d.color}30`,
                textAlign: "center",
              }}
            >
              <div
                style={{
                  fontSize: 28,
                  fontWeight: 800,
                  fontFamily: "Inter, system-ui, sans-serif",
                  color: d.color,
                }}
              >
                {d.score}
              </div>
              <div
                style={{
                  fontSize: 13,
                  color: "#94a3b8",
                  fontFamily: "Inter, system-ui, sans-serif",
                }}
              >
                {d.label}
              </div>
            </div>
          ))}
        </div>
      )}
    </AbsoluteFill>
  );
};
