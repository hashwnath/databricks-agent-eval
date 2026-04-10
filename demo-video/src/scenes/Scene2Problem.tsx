import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

const FailCard: React.FC<{
  title: string;
  value: string;
  subtitle: string;
  delay: number;
  color: string;
}> = ({ title, value, subtitle, delay, color }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const enter = spring({
    frame: frame - delay,
    fps,
    config: { damping: 14, mass: 0.6 },
  });
  const opacity = interpolate(frame, [delay, delay + 10], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        background: "#1e293b",
        borderRadius: 16,
        padding: "40px 48px",
        border: `2px solid ${color}30`,
        transform: `scale(${enter})`,
        opacity,
        textAlign: "center",
        width: 380,
      }}
    >
      <div
        style={{
          fontSize: 20,
          color: "#94a3b8",
          fontFamily: "Inter, system-ui, sans-serif",
          fontWeight: 500,
          marginBottom: 12,
        }}
      >
        {title}
      </div>
      <div
        style={{
          fontSize: 72,
          fontWeight: 900,
          fontFamily: "Inter, system-ui, sans-serif",
          color,
          lineHeight: 1,
          letterSpacing: -2,
        }}
      >
        {value}
      </div>
      <div
        style={{
          fontSize: 18,
          color: "#64748b",
          fontFamily: "Inter, system-ui, sans-serif",
          marginTop: 12,
        }}
      >
        {subtitle}
      </div>
    </div>
  );
};

export const Scene2Problem: React.FC = () => {
  const frame = useCurrentFrame();

  const titleOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: "clamp" });
  const titleY = interpolate(frame, [0, 15], [20, 0], { extrapolateRight: "clamp" });

  // Pulsing red glow for "silently"
  const pulse = Math.sin(frame * 0.15) * 0.3 + 0.7;

  const fadeOut = interpolate(frame, [270, 300], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0f172a",
        justifyContent: "center",
        alignItems: "center",
        opacity: fadeOut,
      }}
    >
      {/* Subtle red vignette */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(ellipse at center, transparent 40%, rgba(239,68,68,0.05) 100%)",
        }}
      />

      <div style={{ textAlign: "center", zIndex: 1 }}>
        <div
          style={{
            fontSize: 48,
            fontWeight: 700,
            fontFamily: "Inter, system-ui, sans-serif",
            color: "#e2e8f0",
            opacity: titleOpacity,
            transform: `translateY(${titleY}px)`,
            marginBottom: 16,
          }}
        >
          Multi-agent systems fail{" "}
          <span
            style={{
              color: "#ef4444",
              textShadow: `0 0 ${40 * pulse}px rgba(239,68,68,${pulse * 0.4})`,
            }}
          >
            silently
          </span>
        </div>

        <div
          style={{
            fontSize: 22,
            color: "#64748b",
            fontFamily: "Inter, system-ui, sans-serif",
            opacity: titleOpacity,
            marginBottom: 60,
          }}
        >
          Routing errors, cost blowouts, and regressions go undetected
        </div>

        <div style={{ display: "flex", gap: 40, justifyContent: "center" }}>
          <FailCard
            title="Routing Accuracy"
            value="40%"
            subtitle="tasks sent to wrong agent"
            delay={30}
            color="#ef4444"
          />
          <FailCard
            title="Cost per Run"
            value="$200"
            subtitle="3x budget, no alert"
            delay={60}
            color="#f59e0b"
          />
          <FailCard
            title="Regressions"
            value="Silent"
            subtitle="zero visibility on drift"
            delay={90}
            color="#ef4444"
          />
        </div>
      </div>
    </AbsoluteFill>
  );
};
