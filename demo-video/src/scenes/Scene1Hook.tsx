import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export const Scene1Hook: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const statScale = spring({ frame, fps, config: { damping: 12, mass: 0.8 } });
  const statOpacity = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: "clamp" });

  const questionOpacity = interpolate(frame, [40, 55], [0, 1], { extrapolateRight: "clamp" });
  const questionY = interpolate(frame, [40, 55], [30, 0], { extrapolateRight: "clamp" });

  const subtitleOpacity = interpolate(frame, [75, 90], [0, 1], { extrapolateRight: "clamp" });

  // Fade out at end
  const fadeOut = interpolate(frame, [130, 150], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0f172a",
        justifyContent: "center",
        alignItems: "center",
        opacity: fadeOut,
      }}
    >
      {/* Subtle grid background */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage:
            "linear-gradient(rgba(34,197,94,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(34,197,94,0.03) 1px, transparent 1px)",
          backgroundSize: "60px 60px",
        }}
      />

      <div style={{ textAlign: "center", zIndex: 1 }}>
        {/* Stat number */}
        <div
          style={{
            fontSize: 140,
            fontWeight: 900,
            fontFamily: "Inter, system-ui, sans-serif",
            color: "#22c55e",
            transform: `scale(${statScale})`,
            opacity: statOpacity,
            lineHeight: 1,
            letterSpacing: -4,
            textShadow: "0 0 80px rgba(34,197,94,0.3)",
          }}
        >
          327%
        </div>

        {/* Subtitle line */}
        <div
          style={{
            fontSize: 36,
            fontFamily: "Inter, system-ui, sans-serif",
            color: "#94a3b8",
            marginTop: 12,
            opacity: subtitleOpacity,
            fontWeight: 400,
          }}
        >
          surge in multi-agent deployments
        </div>

        {/* Question */}
        <div
          style={{
            fontSize: 52,
            fontWeight: 700,
            fontFamily: "Inter, system-ui, sans-serif",
            color: "#e2e8f0",
            marginTop: 48,
            opacity: questionOpacity,
            transform: `translateY(${questionY}px)`,
            lineHeight: 1.3,
          }}
        >
          But who evaluates the supervisor?
        </div>
      </div>

      {/* Databricks context tag */}
      <div
        style={{
          position: "absolute",
          top: 50,
          right: 60,
          opacity: subtitleOpacity,
          display: "flex",
          alignItems: "center",
          gap: 10,
        }}
      >
        <div
          style={{
            width: 8,
            height: 8,
            borderRadius: 4,
            backgroundColor: "#ef4444",
          }}
        />
        <span
          style={{
            fontFamily: "Inter, system-ui, sans-serif",
            fontSize: 18,
            color: "#64748b",
            fontWeight: 500,
          }}
        >
          Databricks 2026 State of AI Agents
        </span>
      </div>
    </AbsoluteFill>
  );
};
