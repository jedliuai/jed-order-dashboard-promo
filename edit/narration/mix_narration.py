"""Align local voice clips, recreate V4 stems, and copy its video stream unchanged."""
from pathlib import Path
import argparse, json, re, subprocess, hashlib, sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly

if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')

ROOT=Path(__file__).resolve().parents[2]
DEL=ROOT/'deliverables'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-dir',default=str(ROOT/'output/narration'),help='Ignored intermediate WAVs and numeric report')
parser.add_argument('--source',default=str(DEL/'promo-60s-music-only.mp4'))
parser.add_argument('--target',default=str(DEL/'promo-60s-narrated.mp4'))
parser.add_argument('--narration-output',default=str(DEL/'narration.wav'))
parser.add_argument('--expected-source-sha256',default='BE226EDDCDB0A6C90CDA41921BB9FA60C06A8B146FFCC98D4138B3860C7EB6C4')
args=parser.parse_args()
OUT=Path(args.output_dir).resolve(); OUT.mkdir(parents=True,exist_ok=True)
source=Path(args.source).resolve()
target=Path(args.target).resolve()
voice_path=Path(args.narration_output).resolve()
assert source!=target,'Source and output video must be different files'
source_hash=hashlib.sha256(source.read_bytes()).hexdigest().upper()
assert source_hash==args.expected_source_sha256.upper(),'Original music-only video hash changed'
target.parent.mkdir(parents=True,exist_ok=True)
voice_path.parent.mkdir(parents=True,exist_ok=True)
ASSET=ROOT/'edit/presentation/public/assets'
SR=48000; N=60*SR

def public_name(p):
    try:return p.relative_to(ROOT).as_posix()
    except ValueError:return p.name

def run(args):
    return subprocess.run(args,check=True,capture_output=True,text=True,encoding='utf-8',errors='replace')

def read(p):
    sr,x=wavfile.read(p)
    if np.issubdtype(x.dtype,np.integer):x=x.astype(np.float64)/32768
    else:x=x.astype(np.float64)
    if sr!=SR:x=resample_poly(x,SR,sr,axis=0)
    return x

def write(p,x):
    assert np.isfinite(x).all()
    # Band-limited 24→48 kHz interpolation can reveal peaks above the source PCM.
    if np.max(np.abs(x))>=1:x=x*(.98/np.max(np.abs(x)))
    wavfile.write(p,SR,np.rint(x*32767).astype(np.int16))

def measure(p):
    r=run(['ffmpeg','-hide_banner','-i',str(p),'-af','loudnorm=I=-19:TP=-3:LRA=8:print_format=json','-f','null','-'])
    return json.loads(re.findall(r'\{[^{}]+\}',r.stderr)[-1])

jobs=json.loads((ROOT/'edit/narration/voice-jobs.json').read_text(encoding='utf-8'))
voice=np.zeros(N); segments=[]
for j in jobs:
    raw=OUT/'segments'/f"{j['id']}.wav"
    if not raw.exists():raw=ROOT/'edit/narration/voice-clips'/f"{j['id']}.wav"
    x=read(raw)
    if x.ndim==2:x=np.mean(x,axis=1)
    # Keep quiet consonants and word tails: measure 10 ms RMS, pad 100/140 ms.
    block=480
    rms=np.sqrt(np.mean(np.pad(x,(0,(-len(x))%block)).reshape(-1,block)**2,axis=1))
    active=np.flatnonzero(rms>max(.004,float(np.max(rms))*.025))
    assert len(active)
    first=max(0,int(active[0]*block-.10*SR)); last=min(len(x),int((active[-1]+1)*block+.14*SR))
    trimmed=x[first:last]
    avail=j['end']-j['start']
    factor=max(1,len(trimmed)/SR/avail)
    assert factor<=1.19, f"Rewrite rather than rushing {j['id']}: {factor:.3f}"
    temp=OUT/f"{j['id']}-trim.wav"; processed=OUT/f"{j['id']}-aligned.wav"
    write(temp,trimmed)
    filters=f'highpass=f=70,acompressor=threshold=0.12:ratio=2:attack=8:release=90:makeup=1,atempo={factor:.8f}'
    m=run(['ffmpeg','-hide_banner','-i',str(temp),'-af',filters+',loudnorm=I=-19:TP=-3:LRA=8:print_format=json','-f','null','-'])
    m=json.loads(re.findall(r'\{[^{}]+\}',m.stderr)[-1])
    norm=f"loudnorm=I=-19:TP=-3:LRA=8:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
    run(['ffmpeg','-y','-hide_banner','-i',str(temp),'-af',filters+','+norm+',afade=t=in:d=0.008','-ar',str(SR),'-c:a','pcm_s16le',str(processed)])
    y=read(processed)
    assert len(y)/SR<=avail+.035, (j['id'],len(y)/SR,avail)
    # ffmpeg WSOLA can differ by a few milliseconds. Preserve every spoken sample.
    start=round(j['start']*SR); end=start+len(y)
    assert end<=N and not np.any(voice[start:end]),j['id']
    y[-min(480,len(y)):]*=np.linspace(1,0,min(480,len(y)))
    voice[start:end]=y
    segments.append(dict(j,actual_end=end/SR,raw_duration=len(x)/SR,trim_start=first/SR,trim_end=last/SR,tempo_factor=factor,aligned_duration=len(y)/SR))

time=np.arange(N)/SR
frame=np.floor(time*30)
tl=json.loads((ROOT/'edit/presentation/src/timeline-v4.json').read_text(encoding='utf-8'))
gain=np.full(N,.92)
for c in tl['clicks']:
    f=c['frame'];gain=np.minimum(gain,np.interp(frame,[f-3,f,f+4,f+8],[.92,.65,.65,.92]))
notes=tl['flowNotes']; gain=np.minimum(gain,np.interp(frame,[notes[0]['frame']-6,notes[0]['frame'],notes[-1]['frame']+8,notes[-1]['frame']+20],[.92,.66,.66,.92]))
duck=np.ones(N)
windows=[]
for j in segments:
    if windows and j['start']-windows[-1][1]<=.65:
        windows[-1][1]=j['actual_end']
    else:windows.append([j['start'],j['actual_end']])
for start,end in windows:
    # Pre-duck 120 ms, recover over 280 ms; don't pump between syllables.
    duck=np.minimum(duck,np.interp(time,[max(0,start-.15),start,end,end+.30],[1,.36,.36,1]))
music=read(ASSET/'music-v4.wav')
paper=read(ASSET/'paper-turns-v4.wav')*.68
chimes=read(ASSET/'flow-chimes-v4.wav')*.93
click=np.zeros((N,2)); sample=read(ASSET/'mouse-click-v2.wav')*.90
if sample.ndim==1:sample=np.repeat(sample[:,None],2,axis=1)
for c in tl['clicks']:
    start=round(c['frame']/30*SR); sample_clip=sample[:round(13/30*SR)]
    click[start:start+len(sample_clip)]+=sample_clip
mixed=music*(gain*duck)[:,None]+paper+chimes+click+voice[:,None]
write(OUT/'narration-raw-mix.wav',mixed/ max(1,np.max(np.abs(mixed))/.95))
m=measure(OUT/'narration-raw-mix.wav')
master_gain=10**((-16-float(m['input_i']))/20)
master=OUT/'narration-mix.wav'
run(['ffmpeg','-y','-hide_banner','-i',str(OUT/'narration-raw-mix.wav'),'-af',f'volume={master_gain:.9f},alimiter=limit=0.794328:level=false:latency=true','-ar',str(SR),'-c:a','pcm_s16le',str(master)])
write(voice_path,voice)
run(['ffmpeg','-y','-hide_banner','-i',str(source),'-i',str(master),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','256k','-ar',str(SR),'-movflags','+faststart','-t','60',str(target)])
report={'local_tts_model':'CosyVoice2-0.5B','voice':'女主播','ai_generated':True,'source_video_sha256':source_hash,'video_stream_mode':'copy','music_duck':.36,'voice_mono_target_lufs':-19,'master_gain_db':20*np.log10(master_gain),'mixed_pcm_metrics':measure(master),'segments':segments}
(OUT/'mix-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'output':public_name(target),'narration':public_name(voice_path),'metrics':report['mixed_pcm_metrics'],'segments':[(j['id'],round(j['aligned_duration'],3),round(j['tempo_factor'],3)) for j in segments]},ensure_ascii=False,indent=2))
