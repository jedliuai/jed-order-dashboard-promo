import React from 'react';
import {Composition, Folder, registerRoot} from 'remotion';
import {FilmV4, V4ScenePreview} from './FilmV4';
import timeline from './timeline-v4.json';

const Root: React.FC = () => <>
  <Composition id="TradeDashboard" component={FilmV4} durationInFrames={timeline.durationFrames} fps={timeline.fps} width={1920} height={1080}/>
  <Folder name="Final-Scenes">
    {timeline.scenes.map(scene => <Composition key={scene.id} id={`Scene-${scene.id}`} component={V4ScenePreview} defaultProps={{sceneId:scene.id}} durationInFrames={scene.duration} fps={timeline.fps} width={1920} height={1080}/>)}
  </Folder>
</>;
registerRoot(Root);
