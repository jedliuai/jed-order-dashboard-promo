import React, {CSSProperties} from 'react';
import {AbsoluteFill, Audio, Easing, Img, Sequence, interpolate, staticFile, useCurrentFrame} from 'remotion';
import timeline from '../timeline-v4.json';
import dimensions from '../../public/assets/manifest.json';
import '../theme.css';

export const C={paper:'#faf7f2',ink:'#2d2922',muted:'#706757',bronze:'#b08956',sage:'#5c8567',clay:'#aa5d44',border:'#e2dac9'};
const ease=Easing.bezier(.22,.8,.2,1);
export const ramp=(f:number,a:number,b:number,from=0,to=1)=>interpolate(f,[a,b],[from,to],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:ease});
export const asset=(name:string)=>staticFile(`assets/${name}`);
export type SceneProps={frame:number};
export type Crop={x:number;y:number;width:number;height:number};
export const native=(name:string)=>(dimensions as Record<string,{width:number;height:number}>)[name];

export const Enter:React.FC<{children:React.ReactNode;frame:number;start?:number;style?:CSSProperties;distance?:number}>=({children,frame,start=0,style,distance=24})=><div style={{...style,opacity:ramp(frame,start,start+12),translate:`0 ${ramp(frame,start,start+18,distance,0)}px`}}>{children}</div>;
export const Title:React.FC<{children:React.ReactNode;detail:React.ReactNode;index:string}>=({children,detail,index})=><div style={{position:'absolute',left:120,top:89}}><div className="section-label"><span>{index}</span><span style={{width:24,height:1,background:C.bronze}}/>外贸订单驾驶舱</div><div className="hero-title">{children}</div><div className="title-detail">{detail}</div></div>;

// Source rectangles use original CSS pixels (the PNGs were captured at 2×).
// The white matte separates emphasis strokes from the original UI borders.
export const Source:React.FC<{name:string;width:number;crop?:Crop}>=({name,width,crop})=>{
  const d=native(name);const rect=crop??{x:0,y:0,width:d.width,height:d.height};const scale=width/rect.width;
  return <div style={{position:'relative',width,height:rect.height*scale,overflow:'hidden',borderRadius:14}}><Img src={asset(`${name}.png`)} style={{position:'absolute',width:d.width*scale,maxWidth:'none',left:-rect.x*scale,top:-rect.y*scale,display:'block'}}/></div>;
};
export const Perimeter:React.FC<{width:number;height:number;progress:number;color?:string}>=({width,height,progress,color=C.bronze})=>{
  // The entire 2 px stroke is outside the matte, with a 9 px clear gap.
  const gap=10;const w=width+gap*2;const h=height+gap*2;
  return <svg width={w+4} height={h+4} style={{position:'absolute',left:-gap-2,top:-gap-2,overflow:'visible',pointerEvents:'none',opacity:progress>.001?.78:0}}><rect x="2" y="2" width={w} height={h} rx="31" fill="none" stroke={color} strokeWidth="2" pathLength="1" strokeDasharray="1" strokeDashoffset={1-progress}/></svg>;
};
export const Matte:React.FC<{children:React.ReactNode;width:number;height:number;left:number;top:number;frame:number;start?:number;emphasis?:number;color?:string;style?:CSSProperties}>=({children,width,height,left,top,frame,start=-15,emphasis,color,style})=><div style={{position:'absolute',left,top,width,height,opacity:ramp(frame,start,start+12),translate:`0 ${ramp(frame,start,start+18,22,0)}px`,...style}}><div className="shot-matte" style={{width,height,padding:14}}>{children}</div>{emphasis!==undefined&&<Perimeter width={width} height={height} progress={ramp(frame,emphasis,emphasis+24)} color={color}/>}</div>;
export const Shot:React.FC<{name:string;width:number;left:number;top:number;frame:number;crop?:Crop;start?:number;emphasis?:number;color?:string;style?:CSSProperties}>=({name,width,left,top,frame,crop,start,emphasis,color,style})=>{
  const d=native(name);const height=28+(width-28)*(crop?.height??d.height)/(crop?.width??d.width);
  return <Matte {...{width,height,left,top,frame,start,emphasis,color,style}}><Source name={name} width={width-28} crop={crop}/></Matte>;
};
export const Cursor:React.FC<{x:number;y:number;frame:number;click:number;opacity:number}>=({x,y,frame,click,opacity})=>{
  const pulse=ramp(frame,click,click+12);const down=frame>=click&&frame<click+3;
  return <div style={{position:'absolute',left:x,top:y,opacity,pointerEvents:'none',scale:down?.86:1,transformOrigin:'4px 3px'}}>{frame>=click&&frame<click+12&&<div style={{position:'absolute',left:-18,top:-18,width:38,height:38,border:`2px solid ${C.bronze}`,borderRadius:'50%',scale:1+pulse*1.8,opacity:1-pulse}}/>}<svg width="38" height="45" viewBox="0 0 38 45" style={{filter:'drop-shadow(0 3px 3px #2d292226)'}}><path d="M4 3L5 34L13 27L20 41L27 37L20 23L32 21Z" fill={C.ink} stroke="white" strokeWidth="2.5" strokeLinejoin="round"/></svg></div>;
};
