"""Offline ASR cross-check using the user's existing SenseVoiceSmall installation."""
from pathlib import Path
import argparse, json, os, sys
if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
p=argparse.ArgumentParser()
p.add_argument('--input-dir',required=True)
p.add_argument('--report',required=True)
p.add_argument('--glob',default='*.wav')
p.add_argument('--model-root',default=os.environ.get('COSYVOICE_ROOT'),help='Local model installation; otherwise set COSYVOICE_ROOT')
p.add_argument('--device',default='cpu',help='cpu (default) or an available device such as cuda:0')
a=p.parse_args()
if not a.model_root:p.error('Pass --model-root or set COSYVOICE_ROOT; model weights are not included')
root=Path(a.model_root).resolve()
if not (root/'SenseVoiceSmall').is_dir():p.error('SenseVoiceSmall must exist under the supplied model root')
os.environ['HF_HUB_OFFLINE']='1'
os.environ['TRANSFORMERS_OFFLINE']='1'
dll=[]
for d in [root/'py312/Library/bin',root/'py312/Lib/site-packages/torch/lib']:
    if os.name=='nt' and d.exists():
        os.environ['PATH']=str(d)+os.pathsep+os.environ.get('PATH','')
        if hasattr(os,'add_dll_directory'):dll.append(os.add_dll_directory(str(d)))
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess
m=AutoModel(model=str(root/'SenseVoiceSmall'),trust_remote_code=False,device=a.device,disable_update=True)
results=[]
for f in sorted(Path(a.input_dir).resolve().glob(a.glob)):
    r=m.generate(input=str(f),cache={},language='zh',use_itn=True,batch_size_s=60)
    item={'file':f.name,'recognized':rich_transcription_postprocess(r[0]['text'])}
    results.append(item)
    print(json.dumps(item,ensure_ascii=False),flush=True)
report=Path(a.report).resolve();report.parent.mkdir(parents=True,exist_ok=True)
report.write_text(json.dumps({'model':'SenseVoiceSmall (local/offline)','results':results},ensure_ascii=False,indent=2),encoding='utf-8')
