import {Composition} from "remotion";
import {LaunchVideo} from "./LaunchVideo";

export const MyComposition = () => {
  return (
    <Composition
      id="MyComp"
      component={LaunchVideo}
      durationInFrames={540}
      fps={30}
      width={1080}
      height={1920}
    />
  );
};
