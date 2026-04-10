import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export const Scene5CTA: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const repoScale = spring({
    frame,
    fps,
    config: { damping: 12, mass: 0.8 },
  });
  const repoOpacity = interpolate(frame, [0, 10], [0, 1], { extrapolateRight: "clamp" });

  const builtByOpacity = interpolate(frame, [25, 40], [0, 1], { extrapolateRight: "clamp" });
  const builtByY = interpolate(frame, [25, 40], [15, 0], { extrapolateRight: "clamp" });

  const stackOpacity = interpolate(frame, [50, 65], [0, 1], { extrapolateRight: "clamp" });

  // Pulsing green glow
  const pulse = Math.sin(frame * 0.1) * 0.3 + 0.7;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0f172a",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      {/* Radial green glow */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(ellipse at center, rgba(34,197,94,0.06) 0%, transparent 60%)",
        }}
      />

      <div style={{ textAlign: "center", zIndex: 1 }}>
        {/* Repo URL */}
        <div
          style={{
            fontSize: 46,
            fontWeight: 800,
            fontFamily: "'SF Mono', 'Fira Code', Consolas, monospace",
            color: "#22c55e",
            transform: `scale(${repoScale})`,
            opacity: repoOpacity,
            textShadow: `0 0 ${60 * pulse}px rgba(34,197,94,${pulse * 0.3})`,
            letterSpacing: -1,
          }}
        >
          github.com/hashwnath/databricks-agent-eval
        </div>

        {/* "Built for Databricks" */}
        <div
          style={{
            fontSize: 28,
            fontFamily: "Inter, system-ui, sans-serif",
            color: "#94a3b8",
            marginTop: 24,
            opacity: builtByOpacity,
            transform: `translateY(${builtByY}px)`,
            fontWeight: 500,
          }}
        >
          Built for Databricks
        </div>

        {/* Built by */}
        <div
          style={{
            fontSize: 22,
            fontFamily: "Inter, system-ui, sans-serif",
            color: "#64748b",
            marginTop: 12,
            opacity: builtByOpacity,
            transform: `translateY(${builtByY}px)`,
          }}
        >
          by Hashwanth Sutharapu
        </div>

        {/* Tech stack strip */}
        <div
          style={{
            display: "flex",
            gap: 16,
            justifyContent: "center",
            marginTop: 48,
            opacity: stackOpacity,
          }}
        >
          {["Python", "AsyncIO", "LLM Judges", "MLflow", "Databricks"].map(
            (tech) => (
              <div
                key={tech}
                style={{
                  background: "#1e293b",
                  borderRadius: 8,
                  padding: "8px 20px",
                  border: "1px solid #334155",
                  fontSize: 16,
                  fontFamily: "Inter, system-ui, sans-serif",
                  color: "#94a3b8",
                  fontWeight: 500,
                }}
              >
                {tech}
              </div>
            )
          )}
        </div>
      </div>
    </AbsoluteFill>
  );
};
