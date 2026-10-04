import React from 'react';
import {AbsoluteFill, Img} from 'remotion';
import {C,ramp,asset,Enter,Title,Source,Matte,Shot,SceneProps} from './shared';
import timeline from '../timeline-v4.json';

const Icon:React.FC<{kind:string;color?:string;size?:number}>=({kind,color=C.bronze,size=58})=><svg width={size} height={size} viewBox="0 0 60 60" fill="none" stroke={color} strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
  {kind==='customer'?<><circle cx="30" cy="19" r="9"/><path d="M12 50v-6c0-11 36-11 36 0v6"/></>:kind==='product'?<><path d="M30 7L50 18v25L30 54 10 43V18zM10 18l20 12 20-12M30 30v24M20 12l21 12"/></>:kind==='time'?<><rect x="9" y="13" width="42" height="40" rx="5"/><path d="M9 25h42M20 7v12M40 7v12M20 34h4M34 34h5M20 43h4M34 43h5"/></>:kind==='trend'?<><path d="M9 8v43h44M16 41l13-13 9 6 13-18M40 16h11v11"/></>:<><path d="M15 6h24l10 10v38H15zM39 6v11h10M23 29h18M23 37h18M23 45h12"/></>}
</svg>;

const ExcelIcon:React.FC=()=> <svg width="46" height="46" viewBox="0 0 64 64" aria-label="Excel" style={{flexShrink:0,filter:'drop-shadow(0 3px 3px #107c4122)'}}>
  <rect x="23" y="9" width="37" height="46" rx="4" fill="#21a366"/>
  <path d="M27 9h29a4 4 0 0 1 4 4v13H27Z" fill="#33c481"/>
  <path d="M27 26h33v14H27Z" fill="#21a366"/>
  <path d="M27 40h33v11a4 4 0 0 1-4 4H27Z" fill="#107c41"/>
  <path d="M40 14v35M49 14v35M30 22h25M30 33h25M30 44h25" stroke="#fff" strokeOpacity=".55" strokeWidth="1.7"/>
  <rect x="4" y="18" width="33" height="33" rx="3" fill="#185c37"/>
  <path d="M13 26h4.5l3.6 6.5 3.7-6.5H29l-5.6 8.6L29 43h-4.4l-3.8-6.4-3.7 6.4H13l5.7-8.6Z" fill="white"/>
</svg>;

export const Pain:React.FC<SceneProps>=({frame:f})=>{
  const papers=[{title:'合同登记.xlsx',x:170,y:370,r:-5},{title:'发货进度.xlsx',x:735,y:416,r:1},{title:'回款记录.xlsx',x:1300,y:350,r:5}];
  return <AbsoluteFill>
    <Title index="痛点" detail="重复填写、来回复制，数据散落各处。">别让业务，困在无数 Excel 里。</Title>
    {papers.map((p,i)=><div key={p.title} style={{position:'absolute',left:p.x,top:p.y,width:450,height:382,rotate:`${p.r+ramp(f,0,70,1,0)}deg`,translate:`0 ${Math.sin(f/22+i)*3}px`}}><div className="paper-document"><div className="paper-tab" style={{padding:'15px 19px',gap:13}}><ExcelIcon/>{p.title}<span className="paper-x">×</span></div><div style={{padding:'20px 25px'}}><div className="paper-row paper-head"><span>客户</span><span>合同</span><span>金额</span></div>{[0,1,2,3].map(j=><div className="paper-row" key={j}><span className="skeleton-line" style={{width:96}}/><span className="skeleton-line" style={{width:110}}/><span className="skeleton-line" style={{width:76}}/></div>)}</div><div className="copy-label" style={{opacity:ramp(f,10+i*12,18+i*12)}}>{i===0?'填一遍':i===1?'再复制一遍':'还要再核对'}</div></div></div>)}
    <div style={{position:'absolute',left:645,top:560,fontSize:56,color:C.clay,opacity:ramp(f,8,16)}}>⇄</div><div style={{position:'absolute',left:1210,top:574,fontSize:56,color:C.clay,opacity:ramp(f,20,28)}}>⇄</div>
    <Enter frame={f} start={28} style={{position:'absolute',left:120,top:858,width:1680,textAlign:'center'}}><div style={{fontSize:44,fontWeight:600}}>填得越多，却越看不清全局。</div></Enter>
  </AbsoluteFill>;
};

export const Flow:React.FC<SceneProps>=({frame:f})=>{
  const start=timeline.scenes.find(s=>s.id==='flow')!.start;
  const icons=['customer','file','product','file','file','product','file','trend'];
  const notes=timeline.flowNotes;
  const first=notes[0].frame-start,last=notes[7].frame-start;
  // Keep the moving packet and the eight activation beats on the same clock.
  const step=Math.max(0,Math.min(7,(f-first)/15));const packetX=235+step*208;
  return <AbsoluteFill>
    <Title index="贯通" detail="合同一次登记，业务记录持续留存。">一次录入，打通整条业务链。</Title>
    <svg width="1920" height="1080" style={{position:'absolute',inset:0}}><path d="M235 504H1691" stroke="#e5dfd4" strokeWidth="3"/><path d={`M235 504H${packetX}`} stroke="#21a366" strokeWidth="5" strokeLinecap="round" opacity={f>=first?1:0}/>{f>=first&&f<last&&<circle cx={packetX} cy="504" r="8" fill="#21a366" style={{filter:'drop-shadow(0 0 8px #21a36699)'}}/>}</svg>
    {notes.map((note,i)=>{const hit=note.frame-start,age=f-hit,lit=age>=0;
      const pulse=lit?Math.exp(-Math.max(0,age)/6):0;
      return <div key={note.id} style={{position:'absolute',left:145+i*208,top:397,width:180,height:214,opacity:lit?1:.62,scale:lit?1+.025*pulse:.98,translate:`0 ${lit?-6*pulse:0}px`}}>
        {lit&&age<14&&<div style={{position:'absolute',inset:-7-age*.7,border:'2px solid #21a366',borderRadius:24,opacity:.45*(1-age/14)}}/>}
        <div className="v4-flow-node" style={{borderColor:lit?'#21a366':'#ded7ca',background:lit?'#eef8f0':'#fff',boxShadow:lit?`0 13px 34px #107c4119,0 0 ${18+22*pulse}px #21a366${Math.round(15+25*pulse).toString(16).padStart(2,'0')}`:'0 9px 24px #57483006'}}>
          <span style={{position:'absolute',right:15,top:15,width:9,height:9,borderRadius:'50%',background:lit?'#21a366':'#d4ccbe'}}/>
          <Icon kind={icons[i]} color={lit?'#107c41':'#b8ae9d'} size={51}/>
          <div style={{fontSize:33,fontWeight:600,marginTop:17,color:lit?C.ink:'#8e8372'}}>{note.label}</div>
        </div>
      </div>;
    })}
    <Enter frame={f} start={last-30} distance={14} style={{position:'absolute',left:120,top:736,width:1680,textAlign:'center'}}><div style={{fontSize:47,fontWeight:600}}>数据真正流动起来。</div><div style={{fontSize:29,color:C.muted,marginTop:24}}>从客户到利润，同一笔业务，持续关联。</div></Enter>
  </AbsoluteFill>;
};

const Quadrant:React.FC<{x:number;y:number;width:number;height:number;color:string;frame:number;start:number;label?:string}>=({x,y,width,height,color,frame,start,label})=>{
  const p=ramp(frame,start,start+26);
  return <div style={{position:'absolute',left:x,top:y,width,height,pointerEvents:'none'}}>
    <svg width={width} height={height} style={{position:'absolute',inset:0,overflow:'visible',opacity:p}}><rect x="2" y="2" width={width-4} height={height-4} rx="13" fill={color} fillOpacity=".045" stroke={color} strokeWidth="3.5" pathLength="1" strokeDasharray="1" strokeDashoffset={1-p}/></svg>
    {label&&<div style={{position:'absolute',left:16,top:16,padding:'10px 17px',background:color,color:'white',borderRadius:9,fontSize:24,fontWeight:600,boxShadow:`0 6px 22px ${color}33`,opacity:ramp(frame,start+12,start+28)}}>{label}</div>}
  </div>;
};

export const Value:React.FC<SceneProps>=({frame:f})=>{
  const width=1640,content=1612,scale=content/1500;
  return <AbsoluteFill>
    <Title index="04" detail="右上：高回款、高利润 · 左下：当前经营贡献较低">哪些客户，值得重点经营？</Title>
    <Matte width={width} height={28+content*680/1500} left={140} top={285} frame={f}>
      <div style={{position:'relative'}}><Source name="customer-value" width={content}/>
        <Quadrant x={538*scale} y={78*scale} width={440*scale} height={239*scale} color="#397b60" frame={f} start={15} label="高价值 · 重点经营"/>
        <Quadrant x={124*scale} y={327*scale} width={404*scale} height={232*scale} color="#b46849" frame={f} start={72}/>
        <div style={{position:'absolute',left:650*scale,top:416*scale,width:284,height:80,padding:'11px 17px',background:'#b46849',color:'white',borderRadius:10,fontSize:23,fontWeight:600,boxShadow:'0 7px 23px #b4684933',opacity:ramp(f,84,100)}}>低回款 · 低利润<div style={{fontSize:20,fontWeight:400,marginTop:5}}>当前经营贡献较低</div></div>
        <svg width={content} height={content*680/1500} style={{position:'absolute',inset:0,pointerEvents:'none',opacity:ramp(f,84,100)}}><path d={`M${646*scale} ${451*scale}H${534*scale}`} fill="none" stroke="#b46849" strokeWidth="2"/><path d={`M${543*scale} ${443*scale}l${-9*scale} ${8*scale} ${9*scale} ${8*scale}`} fill="none" stroke="#b46849" strokeWidth="2"/></svg>
      </div>
    </Matte>
  </AbsoluteFill>;
};

export const Perspectives:React.FC<SceneProps>=({frame:f})=>{
  const panels=[{label:'客户',note:'看贡献',icon:'customer',color:C.sage},{label:'产品',note:'看结构',icon:'product',color:C.bronze},{label:'月份 · 财年',note:'看变化',icon:'time',color:C.clay},{label:'趋势',note:'看走向',icon:'trend',color:'#558b97'}];
  return <AbsoluteFill>
    <Title index="05" detail="客户、产品、月份、财年，多角度看趋势。">数据越积越多，业务越看越清。</Title>
    <svg width="1920" height="1080" style={{position:'absolute',inset:0}}><path d="M185 706C435 725 626 666 817 663S1187 607 1710 555" fill="none" stroke="#b0895620" strokeWidth="40" strokeLinecap="round"/><path d="M185 706C435 725 626 666 817 663S1187 607 1710 555" fill="none" stroke={C.bronze} strokeWidth="2" pathLength="1" strokeDasharray="1" strokeDashoffset={1-ramp(f,10,95)}/></svg>
    {panels.map((p,i)=><Enter key={p.label} frame={f} start={i*12-12} style={{position:'absolute',left:120+i*430,top:369,width:390,height:284}}><div className="perspective-card" style={{borderTop:`3px solid ${p.color}`}}><Icon kind={p.icon} color={p.color} size={63}/><div style={{fontSize:36,fontWeight:600,marginTop:25}}>{p.label}</div><div style={{fontSize:27,color:C.muted,marginTop:14}}>{p.note}</div></div></Enter>)}
    <Enter frame={f} start={42} style={{position:'absolute',left:0,top:807,width:'100%',textAlign:'center'}}><div style={{fontSize:47,fontWeight:600}}>微观细节 <span style={{color:C.bronze,margin:'0 22px'}}>↔</span> 宏观全局</div><div style={{fontSize:29,color:C.muted,marginTop:24}}>每一笔积累，都是下一次判断的依据。</div></Enter>
  </AbsoluteFill>;
};

export const Balance:React.FC<SceneProps>=({frame:f})=>{
  const left=190,top=282,width=1540,content=width-28,scale=content/1280;
  const zero=left+14+546.2*scale,negative=left+14+390.3*scale,positive=left+14+702.1*scale;
  const bottom=top+28+536*scale;const orange=ramp(f,12,32),green=ramp(f,45,65);
  return <AbsoluteFill>
    <Title index="07" detail="客户货款平衡 · 看清交付与回款的两侧责任">钱与货，哪一边还没跟上？</Title>
    <Matte {...{width,left,top}} height={28+536*scale} frame={f}>
      <div style={{position:'relative'}}><Source name="customer-balance" width={content}/>
        <div style={{position:'absolute',left:238*scale,top:88*scale,width:302*scale,height:390*scale,borderRadius:8,background:`linear-gradient(90deg,#c5754818,#c5754805)`,border:'2px solid #b76a4655',opacity:orange,clipPath:`inset(0 ${(1-orange)*100}% 0 0)`}}/>
        <div style={{position:'absolute',left:551*scale,top:88*scale,width:302*scale,height:390*scale,borderRadius:8,background:`linear-gradient(90deg,#417b5b05,#417b5b18)`,border:'2px solid #417b5b55',opacity:green,clipPath:`inset(0 ${(1-green)*100}% 0 0)`}}/>
      </div>
    </Matte>
    <svg width="1920" height="1080" style={{position:'absolute',inset:0,pointerEvents:'none'}}><path d={`M${zero-15} ${bottom+13}H${negative}`} stroke="#b6644b" strokeWidth="2.5" opacity={orange}/><path d={`M${zero+15} ${bottom+13}H${positive}`} stroke="#47785b" strokeWidth="2.5" opacity={green}/><path d={`M${negative+9} ${bottom+6}l-9 7 9 7M${positive-9} ${bottom+6}l9 7-9 7`} fill="none" strokeWidth="2.5" stroke={C.bronze}/></svg>
    {[{x:negative,color:'#b6644b',show:orange,title:'← 我方待交货',note:'收款多于发货'},{x:positive,color:'#47785b',show:green,title:'客户待付款 →',note:'发货多于收款'}].map(p=><div key={p.title} className="balance-callout" style={{position:'absolute',left:p.x-168,top:bottom+28,width:336,height:83,background:p.color,opacity:p.show,scale:.94+.06*p.show,boxShadow:`0 13px 28px ${p.color}33`}}><div style={{fontSize:31,fontWeight:700,lineHeight:1.35}}>{p.title}</div><div style={{fontSize:19,opacity:.86,marginTop:3}}>{p.note}</div></div>)}
  </AbsoluteFill>;
};

export const ExportValue:React.FC<SceneProps>=({frame:f})=>{
  const reports=['生产协调','订单月度汇总','正本合同登记','销售 · 回款 · 应收','开票申请','发货明细'];
  return <AbsoluteFill>
    <Title index="09" detail="按业务需要与公司的定期报表要求，选好范围，直接导出。">该交的表，一键就到手。</Title>
    <div style={{position:'absolute',left:120,top:382,width:630,height:312,rotate:`${ramp(f,0,32,-2,0)}deg`}}><div className="time-comparison old"><div className="eyebrow" style={{color:C.muted}}>过去 · 手工制表</div><div style={{fontSize:88,fontWeight:700,marginTop:23}}>数小时</div><div style={{fontSize:29,color:C.muted,marginTop:18}}>复制、粘贴、核对，反复重来。</div></div></div>
    <div style={{position:'absolute',left:812,top:483,fontSize:77,color:C.bronze}}>→</div>
    <Enter frame={f} start={8} style={{position:'absolute',left:981,top:382,width:819,height:312}}><div className="time-comparison now"><div className="eyebrow" style={{color:C.sage}}>现在 · 导出 Excel</div><div style={{fontSize:88,fontWeight:700,color:C.sage,marginTop:23}}>1 次点击</div><div style={{fontSize:29,color:C.muted,marginTop:18}}>把做表的时间，还给业务。</div></div></Enter>
    <div style={{position:'absolute',left:120,top:795,width:1680,display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:18}}>{reports.map((label,i)=><div key={label} className="report-chip" style={{opacity:ramp(f,24+i*5,33+i*5),translate:`0 ${ramp(f,24+i*5,37+i*5,16,0)}px`}}><span style={{color:C.sage,fontSize:24}}>▤</span>{label}<span style={{marginLeft:'auto',fontSize:17,color:C.sage,fontFamily:'Segoe UI'}}>EXCEL</span></div>)}</div>
  </AbsoluteFill>;
};

export const Outro:React.FC<SceneProps>=({frame:f})=><AbsoluteFill>
  <div className="outro-orbit" style={{rotate:`${f*.07}deg`}}/>
  <Img src={asset('brand.svg')} style={{position:'absolute',left:839,top:73,width:242}}/>
  <div style={{position:'absolute',left:0,top:287,width:'100%',textAlign:'center'}}><div style={{fontSize:79,fontWeight:700,letterSpacing:3}}>外贸订单驾驶舱</div><div style={{fontSize:41,fontWeight:600,color:C.bronze,marginTop:33}}>让一线业务，也拥有全局视野。</div><div style={{fontSize:28,color:C.muted,marginTop:22,letterSpacing:2}}>从一笔订单，到整个经营。</div></div>
  <div style={{position:'absolute',left:0,top:675,width:'100%',textAlign:'center'}}><div style={{height:2,width:70,background:C.bronze,margin:'0 auto 25px'}}/><div style={{fontSize:29,color:C.muted,letterSpacing:3}}>体验 Demo</div><div style={{fontFamily:"'Segoe UI', sans-serif",fontSize:44,fontWeight:600,color:C.bronze,letterSpacing:1,marginTop:18}}>deskdemo.jedliuai.com</div></div>
  <div style={{position:'absolute',left:0,top:980,width:'100%',textAlign:'center',fontSize:20,color:C.muted,opacity:ramp(f,12,24)}}>界面与业务数据来自公开演示，均为虚构。</div>
</AbsoluteFill>;
