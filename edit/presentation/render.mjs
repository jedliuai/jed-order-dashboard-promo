import path from 'node:path';
import fs from 'node:fs/promises';
import {existsSync} from 'node:fs';
import {bundle} from '@remotion/bundler';
import {openBrowser, renderMedia, renderStill, selectComposition} from '@remotion/renderer';

const root = path.resolve(import.meta.dirname, '../..');
const edge = ['C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', 'C:/Program Files/Microsoft/Edge/Application/msedge.exe'].find(existsSync);
const browserExecutable = process.env.REMOTION_BROWSER_EXECUTABLE || (process.platform === 'win32' ? edge : undefined);
const serveUrl = await bundle({entryPoint:path.resolve(import.meta.dirname,'src/index.tsx'),outDir:path.resolve(root,'output/bundle'),publicDir:path.resolve(import.meta.dirname,'public')});
const browser = await openBrowser('chrome',{browserExecutable,chromiumOptions:{headless:true}});
try {
  const composition = await selectComposition({serveUrl,id:'TradeDashboard',puppeteerInstance:browser});
  console.log('Composition:',composition.width,composition.height,composition.fps,composition.durationInFrames);
  const requested = process.argv.find(a=>a.startsWith('--frames='));
  const frames = requested ? requested.slice(9).split(',').map(Number) : [0,140,240,330,450,618,760,945,1125,1375,1463,1610,1750];
  if (frames.some(f=>!Number.isInteger(f)||f<0||f>=composition.durationInFrames)) throw new Error('Frames must be integers from 0 to 1799.');
  const outputArg = process.argv.find(a=>a.startsWith('--output='));
  const output = outputArg ? path.resolve(outputArg.slice(9)) : path.resolve(root,'output/render/promo-60s-music-only.mp4');
  if (process.argv.includes('--stills')) {
    const directory = path.resolve(root,'output/stills');
    await fs.mkdir(directory,{recursive:true});
    for (const frame of frames) {
      await renderStill({composition,serveUrl,puppeteerInstance:browser,frame,output:path.join(directory,`frame-${String(frame).padStart(4,'0')}.png`),imageFormat:'png'});
      console.log('Keyframe:',frame);
    }
  } else {
    await fs.mkdir(path.dirname(output),{recursive:true});
    let last=-1;
    await renderMedia({composition,serveUrl,puppeteerInstance:browser,outputLocation:output,codec:'h264',audioCodec:'aac',audioBitrate:'256k',crf:17,pixelFormat:'yuv420p',colorSpace:'bt709',concurrency:4,x264Preset:'medium',imageFormat:'jpeg',jpegQuality:96,onProgress:({progress})=>{const pct=Math.floor(progress*10)*10;if(pct>last){last=pct;console.log('Render:',pct+'%');}}});
    console.log('Rendered:',output);
  }
} finally {
  await browser.close({silent:true});
}
