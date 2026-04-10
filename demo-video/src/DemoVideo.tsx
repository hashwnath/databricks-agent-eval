import { AbsoluteFill, Sequence } from "remotion";
import { Scene1Hook } from "./scenes/Scene1Hook";
import { Scene2Problem } from "./scenes/Scene2Problem";
import { Scene3Mechanism } from "./scenes/Scene3Mechanism";
import { Scene4Demo } from "./scenes/Scene4Demo";
import { Scene5CTA } from "./scenes/Scene5CTA";
import { Captions } from "./components/Captions";

// 30fps, 60 seconds = 1800 frames
// Scene 1: 0-150 (0-5s)
// Scene 2: 150-450 (5-15s)
// Scene 3: 450-1050 (15-35s)
// Scene 4: 1050-1650 (35-55s)
// Scene 5: 1650-1800 (55-60s)

const BG = "#0f172a";

export const DemoVideo: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: BG }}>
      <Sequence from={0} durationInFrames={150}>
        <Scene1Hook />
      </Sequence>
      <Sequence from={150} durationInFrames={300}>
        <Scene2Problem />
      </Sequence>
      <Sequence from={450} durationInFrames={600}>
        <Scene3Mechanism />
      </Sequence>
      <Sequence from={1050} durationInFrames={600}>
        <Scene4Demo />
      </Sequence>
      <Sequence from={1650} durationInFrames={150}>
        <Scene5CTA />
      </Sequence>
      <Captions />
    </AbsoluteFill>
  );
};
