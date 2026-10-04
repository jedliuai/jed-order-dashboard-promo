"""Use the user's installed CosyVoice2 environment; never change its model files."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import sys
import time

if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
parser=argparse.ArgumentParser()
parser.add_argument('--model-root',default=os.environ.get('COSYVOICE_ROOT'),help='Existing local CosyVoice2 checkout; otherwise set COSYVOICE_ROOT')
parser.add_argument('--jobs',required=True)
parser.add_argument('--output-dir',required=True)
parser.add_argument('--voice',default='女主播')
parser.add_argument('--seed',type=int,default=20261004)
args=parser.parse_args()
if not args.model_root:parser.error('Pass --model-root or set COSYVOICE_ROOT; model weights are not included')
model_root=Path(args.model_root).resolve()
if not model_root.is_dir():parser.error('The supplied model root is not a directory')
output=Path(args.output_dir).resolve();output.mkdir(parents=True,exist_ok=True)
jobs=json.loads(Path(args.jobs).resolve().read_text(encoding='utf-8'))
os.environ['HF_HUB_OFFLINE']='1'
os.environ['TRANSFORMERS_OFFLINE']='1'
os.environ['HF_HOME']=str(model_root/'hf_download')
os.environ['TRANSFORMERS_CACHE']=str(model_root/'tf_download')
os.environ['XFORMERS_FORCE_DISABLE_TRITON']='1'
os.environ['DS_BUILD_AIO']='0'
os.environ['DS_BUILD_SPARSE_ATTN']='0'
os.chdir(model_root)
sys.path.insert(0,str(model_root))
sys.path.insert(0,str(model_root/'third_party/Matcha-TTS'))
dll_handles=[]
for path in [model_root/'py312/Library/bin',model_root/'py312/Lib/site-packages/torch/lib']:
    if os.name=='nt' and path.exists():
        os.environ['PATH']=str(path)+os.pathsep+os.environ.get('PATH','')
        if hasattr(os,'add_dll_directory'):dll_handles.append(os.add_dll_directory(str(path)))

import numpy as np
import torch
from cosyvoice.cli.cosyvoice import CosyVoice2
from scipy.io import wavfile

assert torch.cuda.is_available(), 'The installed CUDA environment must be used.'
print('Loading local CosyVoice2 on',torch.cuda.get_device_name(),flush=True)
started=time.time()
tts=CosyVoice2(str(model_root/'pretrained_models/CosyVoice2-0.5B'),load_jit=False,load_trt=False,fp16=True)
print('Model ready',round(time.time()-started,2),'seconds; sample rate',tts.sample_rate,flush=True)
profiles={}
report=[]
for index,job in enumerate(jobs):
    voice=job.get('voice',args.voice)
    if voice not in profiles:
        profile_path=model_root/'voices'/f'{voice}.pt'
        profile=torch.load(profile_path,map_location='cpu',weights_only=True)
        prompt=profile['audio_ref'].float()
        tts.add_zero_shot_spk(profile['text_ref'],prompt,voice)
        profiles[voice]={'profile_file':f'voices/{voice}.pt','profile_sha256':hashlib.sha256(profile_path.read_bytes()).hexdigest()}
    seed=int(job.get('seed',args.seed+index))
    torch.manual_seed(seed)
    np.random.seed(seed)
    name=job['id'];path=output/f'{name}.wav'
    stamp=path.with_suffix('.json')
    expected={'text':job['text'],'voice':voice,'speed':float(job.get('speed',1.0)),'seed':seed}
    same=stamp.exists() and json.loads(stamp.read_text(encoding='utf-8'))==expected
    if path.exists() and same and not job.get('regenerate',False):
        sr,pcm=wavfile.read(path)
        report.append({'id':name,'file':path.name,'text':job['text'],'voice':voice,'sample_rate':sr,'duration_seconds':len(pcm)/sr,'cached':True})
        continue
    started=time.time()
    chunks=list(tts.inference_zero_shot(job['text'],'',torch.zeros(1,16000),zero_shot_spk_id=voice,stream=False,speed=float(job.get('speed',1.0)),text_frontend=False))
    speech=torch.cat([chunk['tts_speech'].detach().float().cpu() for chunk in chunks],dim=1).squeeze().numpy()
    assert np.isfinite(speech).all() and len(speech)>0
    peak=float(np.max(np.abs(speech)))
    if peak>.98:speech*=.98/peak
    wavfile.write(path,tts.sample_rate,np.rint(speech*32767).astype(np.int16))
    stamp.write_text(json.dumps(expected,ensure_ascii=False,indent=2),encoding='utf-8')
    item={'id':name,'file':path.name,'text':job['text'],'voice':voice,'speed':job.get('speed',1.0),'sample_rate':tts.sample_rate,'duration_seconds':len(speech)/tts.sample_rate,'generation_seconds':time.time()-started,'peak_dbfs':float(20*np.log10(max(np.max(np.abs(speech)),1e-12))),'cached':False}
    report.append(item)
    print(json.dumps(item,ensure_ascii=False),flush=True)
(output/'generation-report.json').write_text(json.dumps({'model':'CosyVoice2-0.5B','runtime':f'Python {sys.version.split()[0]}','device':torch.cuda.get_device_name(),'ai_generated':True,'profiles':profiles,'segments':report},ensure_ascii=False,indent=2),encoding='utf-8')
print('Completed',len(report),'clips',flush=True)
