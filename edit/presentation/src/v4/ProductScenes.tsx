import React from 'react';
import {AbsoluteFill, Img} from 'remotion';
import timeline from '../timeline-v4.json';
import {C,ramp,asset,Enter,Title,Source,Matte,Shot,Cursor,SceneProps} from './shared';

export const Intro:React.FC<SceneProps>=({frame:f})=>{
  const p=ramp(f,30,100);
  return <AbsoluteFill>
    <div className="intro-orbit" style={{rotate:`${-22+f*.1}deg`}}/>
    <div style={{position:'absolute',left:120,top:92,display:'flex',alignItems:'center',gap:22}}><Img src={asset('brand.svg')} style={{width:230}}/><span className="brand-rule"/><span style={{fontSize:22,color:C.muted,letterSpacing:3}}>从订单到经营</span></div>
    <div style={{position:'absolute',left:120,top:286,width:900}}><div className="eyebrow">为外贸业务而生的经营看板</div><div style={{fontSize:90,fontWeight:700,lineHeight:1.35,letterSpacing:2}}>外贸订单<span style={{display:'block',color:C.bronze,fontSize:108}}>驾驶舱</span></div><div style={{fontSize:32,marginTop:30,color:C.muted}}>订单、交付、回款、利润，一眼看清。</div></div>
    <div style={{position:'absolute',left:1070,top:278,width:810,rotate:`${ramp(f,0,95,-3.5,-.5)}deg`,translate:`${ramp(f,0,100,22,0)}px ${ramp(f,0,100,28,0)}px`}}><div className="intro-window"><div className="window-rail"><i/><i/><i/><span>经营总览</span></div><Source name="dashboard-metrics" width={780} crop={{x:0,y:64,width:1124,height:455}}/></div><div className="floating-pill" style={{left:-44,top:348,translate:`0 ${Math.sin(f/22)*6}px`}}><span className="status-dot"/>从零散记录，到业务全景</div></div>
    <div style={{position:'absolute',left:120,top:858,display:'flex',alignItems:'center',gap:18,fontSize:25,color:C.muted,opacity:.8}}><span>Excel</span><span className="micro-divider"/><span>邮件</span><span className="micro-divider"/><span>业务记录</span><span style={{color:C.bronze,marginLeft:12,letterSpacing:4}}>→</span><span style={{color:C.ink,opacity:.7+.3*p}}>一个驾驶舱</span></div>
  </AbsoluteFill>;
};

export const Overview:React.FC<SceneProps>=({frame:f})=>{
  const focus=ramp(f,75,105);
  // The metrics capture matches the full PNG at CSS (526,270), confirmed by
  // template matching. Animate one crop instead of crossfading two screenshots.
  const crop={x:526*focus,y:334*focus,width:1920-796*focus,height:855-400*focus};
  return <AbsoluteFill><Title index="01" detail="订单 · 回款 · 发货 · 已确认毛利">业务全景，终于在同一屏。</Title><Shot name="dashboard-full" width={1620-40*focus} left={150+20*focus} top={283+39*focus} frame={f} crop={crop} emphasis={105}/></AbsoluteFill>;
};

export const Priorities:React.FC<SceneProps>=({frame:f})=>{
  const click=timeline.clicks[0].frame-timeline.scenes.find(s=>s.id==='priorities')!.start;const clickX=170+14+(1098/1124)*1552-4;const clickY=384+14+(115-65)/1124*1552-3;
  return <AbsoluteFill><Title index="02" detail="把需要处理的业务，放在眼前。">今天先处理什么？</Title><Shot name="dashboard-priorities" width={1580} left={170} top={384} frame={f} crop={{x:0,y:65,width:1124,height:198}} emphasis={12}/><Enter frame={f} start={8} style={{position:'absolute',left:184,top:768,fontSize:29,color:C.muted}}>优先级、客户、产品、时间，直接看到具体业务。</Enter><Cursor x={ramp(f,12,click-3,1745,clickX)} y={ramp(f,12,click-3,812,clickY)} frame={f} click={click} opacity={ramp(f,8,16)}/></AbsoluteFill>;
};

export const Order:React.FC<SceneProps>=({frame:f})=>{
  return <AbsoluteFill>
    <Title index="03" detail="合同、执行、发货、收款，关键记录连起来。">细到一笔订单，每个节点都有据。</Title>
    <div style={{position:'absolute',left:120,top:332,width:420}}><div className="eyebrow">订单 · 1102</div><div style={{fontSize:42,fontWeight:700,lineHeight:1.5,marginTop:18}}>DEMO 虚构客户 030</div><div style={{width:56,height:3,background:C.bronze,margin:'28px 0'}}/><div style={{fontSize:22,color:C.muted}}>DEMO-C-202607-1102</div><div style={{fontSize:26,color:C.muted,marginTop:14}}>自营 · USD · FOB</div><div style={{fontSize:23,color:C.sage,marginTop:35,opacity:ramp(f,120,135)}}>已发货 · 已结清 · 开票完成</div></div>
    {f<60&&<div style={{opacity:ramp(f,52,60,1,0)}}><Shot name="contract-card" width={1130} left={660} top={309} frame={f} emphasis={15}/></div>}
    {f>=52&&f<120&&<div style={{opacity:Math.min(ramp(f,52,60),ramp(f,112,120,1,0)),translate:`${ramp(f,52,60,64,0)}px 0`}}><Shot name="order-progress" width={1130} left={660} top={353} frame={f} crop={{x:0,y:0,width:846,height:267}} emphasis={75}/><div style={{position:'absolute',left:680,top:810,fontSize:25,color:C.muted}}>QA审批 → 排产 → 入库 → 放行 → 发货</div></div>}
    {f>=112&&<div style={{opacity:ramp(f,112,120),translate:`${ramp(f,112,120,64,0)}px 0`}}><Matte width={1130} height={485} left={660} top={317} frame={f} emphasis={135} color={C.sage}><Source name="order-summary" width={1102}/><div style={{height:30}}/><Source name="order-flows" width={1102}/></Matte><div style={{position:'absolute',left:680,top:846,fontSize:25,color:C.muted}}>每一次发货，每一笔到账，都有记录。</div></div>}
    <div style={{position:'absolute',left:120,top:945,width:1680,display:'flex',alignItems:'center',gap:20}}>{['合同','生产执行','分批交付','回款结清'].map((label,i)=>{const passed=f>=[0,60,120,150][i];return <React.Fragment key={label}><div style={{display:'flex',alignItems:'center',gap:14,fontSize:27,color:passed?C.ink:C.muted,fontWeight:passed?600:400}}><span className="timeline-dot" style={{background:passed?C.bronze:'transparent',borderColor:passed?C.bronze:C.border}}>{passed?'✓':''}</span>{label}</div>{i<3&&<div style={{height:2,width:132,background:C.border,margin:'0 15px'}}><div style={{height:2,background:C.bronze,width:`${ramp(f,[0,60,120][i],[45,105,150][i])*100}%`}}/></div>}</React.Fragment>;})}</div>
  </AbsoluteFill>;
};

export const Concentration:React.FC<SceneProps>=({frame:f})=>{
  const product=f>=60;const imageWidth=1572;
  return <AbsoluteFill><Title index="06" detail="集中度分析 · 看见贡献，也看见依赖">看清客户与产品的贡献。</Title><div className="tabs" style={{position:'absolute',left:140,top:270}}><span className={product?'':'active'}>客户集中度</span><span className={product?'active':''}>产品集中度</span></div>
    {f<60&&<Matte width={1600} height={50+imageWidth*582/1500} left={160} top={349} frame={f} style={{opacity:ramp(f,52,60,1,0)}}><Source name="customer-top" width={imageWidth}/><div style={{height:22}}/><Source name="customer-pareto" width={imageWidth}/></Matte>}
    {f>=52&&<Matte width={1600} height={50+imageWidth*640/1540} left={160} top={349} frame={f} style={{opacity:ramp(f,52,60),translate:`${ramp(f,52,60,64,0)}px 0`}}><Source name="product-core" width={imageWidth}/><div style={{height:22}}/><Source name="product-pareto" width={imageWidth}/></Matte>}
  </AbsoluteFill>;
};

export const Export:React.FC<SceneProps>=({frame:f})=>{
  const click=timeline.clicks[1].frame-timeline.scenes.find(s=>s.id==='export')!.start;const done=ramp(f,46,54);const x=150+14+1032*.51;const y=384+14+1032*(169/630);
  return <AbsoluteFill><Title index="08" detail="把经营信息，变成可用的报表。">经营报表，随时带走。</Title><Shot name="export-card" width={1060} left={150} top={384} frame={f} emphasis={10} color={C.sage}/><Cursor x={ramp(f,7,click-3,1360,x)} y={ramp(f,7,click-3,825,y)} frame={f} click={click} opacity={ramp(f,2,12)*(1-ramp(f,48,60))}/><div style={{position:'absolute',left:1280,top:344,width:470,opacity:done,translate:`0 ${(1-done)*24}px`}}><div className="file-result"><div style={{fontSize:22,fontWeight:700,color:C.sage,letterSpacing:3}}>EXCEL</div><svg width="80" height="90" viewBox="0 0 80 90" style={{marginTop:26}} fill="none" stroke={C.sage} strokeWidth="3"><path d="M18 5h31l18 18v60H18zM49 5v18h18M29 42h27M29 55h27M29 68h27M39 37v37"/></svg><div style={{fontSize:29,fontWeight:600,lineHeight:1.6,marginTop:18}}>客户实际销售、<br/>回款及应收汇总</div><div style={{fontSize:23,color:C.sage,marginTop:26}}>✓ 已下载 · .xlsx</div></div></div><div style={{position:'absolute',left:164,top:850,width:1580,opacity:done,translate:`0 ${(1-done)*18}px`}}><Img src={asset('export-success.png')} style={{width:'100%'}}/></div></AbsoluteFill>;
};
