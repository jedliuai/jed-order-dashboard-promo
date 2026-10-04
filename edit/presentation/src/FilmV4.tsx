import React from 'react';
import {AbsoluteFill, Audio, Sequence, interpolate, useCurrentFrame} from 'remotion';
import timeline from './timeline-v4.json';
import {C,ramp,asset,SceneProps} from './v4/shared';
import * as Product from './v4/ProductScenes';
import * as Story from './v4/StoryScenes';
import './base.css';
import './v4/v4.css';

const scenes:Record<string,React.FC<SceneProps>>={intro:Product.Intro,pain:Story.Pain,flow:Story.Flow,overview:Product.Overview,priorities:Product.Priorities,order:Product.Order,value:Story.Value,perspectives:Story.Perspectives,concentration:Product.Concentration,balance:Story.Balance,export:Product.Export,exportValue:Story.ExportValue,outro:Story.Outro};

export const V4ScenePreview:React.FC<{sceneId:string}>=({sceneId})=>{
  const Component=scenes[sceneId];const frame=useCurrentFrame();
  return <AbsoluteFill className="film"><AbsoluteFill className="scene"><Component frame={frame}/></AbsoluteFill></AbsoluteFill>;
};

const Scene:React.FC<{index:number}>=({index})=>{
  const spec=timeline.scenes[index];const lead=timeline.transitionLeadFrames;
  const f=useCurrentFrame()-(index===0?0:lead);const Component=scenes[spec.id];
  // Fade through the existing paper background in two halves. Outgoing and
  // incoming text never overlap; no sweeping bar, clipping or perspective flip.
  const enter=index===0?1:ramp(f,-lead/2,0);
  const leave=index===timeline.scenes.length-1?0:ramp(f,spec.duration-lead,spec.duration-lead/2);
  return <AbsoluteFill className="scene" style={{opacity:enter*(1-leave),translate:`0 ${(1-enter)*12-leave*8}px`,scale:1+(1-enter)*.008}}><Component frame={Math.max(0,f)}/></AbsoluteFill>;
};

export const FilmV4:React.FC=()=>{
  const f=useCurrentFrame();
  return <AbsoluteFill className="film">
    <Audio src={asset('music-v4.wav')} volume={af=>Math.min(.92,
      ...timeline.clicks.map(c=>interpolate(af,[c.frame-3,c.frame,c.frame+4,c.frame+8],[.92,.65,.65,.92],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})),
      interpolate(af,[timeline.flowNotes[0].frame-6,timeline.flowNotes[0].frame,timeline.flowNotes[7].frame+8,timeline.flowNotes[7].frame+20],[.92,.66,.66,.92],{extrapolateLeft:'clamp',extrapolateRight:'clamp'}))}/>
    <Audio src={asset('paper-turns-v4.wav')} volume={.68}/>
    <Audio src={asset('flow-chimes-v4.wav')} volume={.93}/>
    {timeline.clicks.map(c=><Sequence key={c.id} name={c.id} from={c.frame} durationInFrames={13}><Audio src={asset('mouse-click-v2.wav')} volume={.90}/></Sequence>)}
    {timeline.scenes.map((s,i)=><Sequence key={s.id} name={s.label} from={Math.max(0,s.start-(i===0?0:timeline.transitionLeadFrames))} durationInFrames={s.duration+(i===0?0:timeline.transitionLeadFrames)}><Scene index={i}/></Sequence>)}
    <div style={{position:'absolute',left:0,bottom:0,height:3,width:`${f/(timeline.durationFrames-1)*100}%`,background:C.bronze,opacity:.35}}/>
  </AbsoluteFill>;
};
