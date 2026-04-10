import { interpolate, useCurrentFrame } from "remotion";

interface Caption {
  text: string;
  from: number;
  to: number;
}

const CAPTIONS: Caption[] = [
  // Scene 1
  { text: "327% surge in multi-agent deployments.", from: 0, to: 60 },
  { text: "But who evaluates the supervisor?", from: 60, to: 150 },
  // Scene 2
  { text: "Multi-agent systems fail silently.", from: 150, to: 270 },
  { text: "Routing errors. Cost blowouts. Zero visibility.", from: 270, to: 450 },
  // Scene 3
  { text: "4 LLM judges grade every agent response.", from: 450, to: 630 },
  { text: "Correctness. Routing accuracy. Groundedness. Cost efficiency.", from: 630, to: 810 },
  { text: "Automated regression detection with baseline comparison.", from: 810, to: 1050 },
  // Scene 4
  { text: "One CLI command. 12 scenarios. 4 judges.", from: 1050, to: 1200 },
  { text: "Real-time scoring with pass/fail per dimension.", from: 1200, to: 1380 },
  { text: "Regression detected: routing accuracy dropped 10%.", from: 1380, to: 1530 },
  { text: "HTML report generated automatically.", from: 1530, to: 1650 },
  // Scene 5
  { text: "github.com/hashwnath/databricks-agent-eval", from: 1650, to: 1800 },
];

export const Captions: React.FC = () => {
  const frame = useCurrentFrame();

  const active = CAPTIONS.find((c) => frame >= c.from && frame < c.to);
  if (!active) return null;

  const fadeIn = interpolate(frame, [active.from, active.from + 8], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const fadeOut = interpolate(frame, [active.to - 8, active.to], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const opacity = Math.min(fadeIn, fadeOut);

  return (
    <div
      style={{
        position: "absolute",
        bottom: 20,
        width: "100%",
        display: "flex",
        justifyContent: "center",
        pointerEvents: "none",
        zIndex: 100,
      }}
    >
      <div
        style={{
          background: "rgba(0,0,0,0.75)",
          borderRadius: 8,
          padding: "10px 28px",
          opacity,
          maxWidth: 1400,
        }}
      >
        <div
          style={{
            fontSize: 24,
            fontFamily: "Inter, system-ui, sans-serif",
            color: "#e2e8f0",
            fontWeight: 500,
            textAlign: "center",
            lineHeight: 1.4,
          }}
        >
          {active.text}
        </div>
      </div>
    </div>
  );
};
