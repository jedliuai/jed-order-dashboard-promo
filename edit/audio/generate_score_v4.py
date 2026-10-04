"""60 s progressive electronica, single-layer recorded paper, eight rising chimes.

Run: python edit/audio/generate_score_v4.py
Requires NumPy, SciPy, and FFmpeg for the integrated-loudness check.
Reads timeline-v4.json and writes V4 assets/report only. No network access.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import shutil
import subprocess
import sys

import numpy as np
from scipy import signal
from scipy.io import wavfile
import synth_instruments as synth


if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[2]
BASE_ASSETS = ROOT / "edit/presentation/public/assets"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output-dir", default=str(ROOT / "output/audio"), help="Ignored metric report and generated notes")
parser.add_argument("--assets-dir", default=str(BASE_ASSETS), help="Output WAV directory; use output/audio/assets for a non-destructive experiment")
parser.add_argument("--timeline", default=str(ROOT / "edit/presentation/src/timeline-v4.json"))
parser.add_argument("--paper-source", default=str(BASE_ASSETS / "paper-turn-source.wav"))
args = parser.parse_args()
OUT = Path(args.output_dir).resolve()
ASSETS = Path(args.assets_dir).resolve()
OUT.mkdir(parents=True, exist_ok=True)
ASSETS.mkdir(parents=True, exist_ok=True)
TIMELINE_PATH = Path(args.timeline).resolve()
SOURCE_PATH = Path(args.paper_source).resolve()
TIMELINE = json.loads(TIMELINE_PATH.read_text(encoding="utf-8"))
SR, FPS = 48_000, int(TIMELINE["fps"])
BPM = float(TIMELINE["bpm"])
SECONDS = TIMELINE["durationFrames"] / FPS
SAMPLES = round(SECONDS * SR)
BEAT, BAR = 60 / BPM, 240 / BPM
assert (FPS, SECONDS, SAMPLES, BPM) == (30, 60, 2_880_000, 120)
synth.SECONDS, synth.SAMPLES = SECONDS, SAMPLES
synth.BEAT, synth.BAR = BEAT, BAR
synth.RNG = np.random.default_rng(202610034)
RNG = np.random.default_rng(2026100344)
music = np.zeros((SAMPLES, 2))
paper_bus = np.zeros_like(music)
chime_bus = np.zeros_like(music)
musical_events = []


def put(bus, audio, start, gain=1, pan=0):
    first = round(start * SR)
    skip, first = max(0, -first), max(0, first)
    n = min(len(audio) - skip, len(bus) - first)
    if n <= 0:
        return
    x = audio[skip:skip+n] * gain
    if x.ndim == 1:
        angle = (pan+1) * np.pi/4
        bus[first:first+n, 0] += x*np.cos(angle)
        bus[first:first+n, 1] += x*np.sin(angle)
    else:
        bus[first:first+n] += x


def stage(t):
    if t < 7: return 0
    if t < 19: return 1
    if t < 34.5: return 2
    if t < 51: return 3
    if t < 56.5: return 4
    return 5


def musical(audio, start, gain, pan=0, instrument="other", midi=None):
    put(music, audio, start, gain, pan)
    musical_events.append({"time": start, "instrument": instrument, "midi": midi})


def chord_stab(notes, seconds=.34, bright=1):
    t = np.arange(round(seconds*SR))/SR
    x = np.zeros(len(t))
    for note in notes:
        f = synth.hz(note)
        x += np.sin(2*np.pi*f*t) + .22*np.sin(4*np.pi*f*t) + .07*bright*np.sin(6*np.pi*f*t)
    x = synth.lowpass(x/len(notes), 2600+bright*1200)
    return x*np.exp(-t/.16)*synth.envelope(len(t), .004, .06)


def shaker(seconds=.065):
    t = np.arange(round(seconds*SR))/SR
    x = synth.bandpass(RNG.normal(size=len(t)), 4200, 10000)
    return x*np.exp(-t/.012)*synth.envelope(len(t), .0013, .02)


def clap():
    t = np.arange(round(.17*SR))/SR
    x = synth.bandpass(RNG.normal(size=len(t)), 1200, 7600)*np.exp(-t/.030)
    return x*synth.envelope(len(t), .0012, .04)


def rim(midi=54, seconds=.12):
    t = np.arange(round(seconds*SR))/SR
    f = synth.hz(midi)
    x = np.sin(2*np.pi*f*t)*np.exp(-t/.033)
    x += .20*np.sin(2*np.pi*f*2.71*t)*np.exp(-t/.012)
    x += .13*synth.bandpass(RNG.normal(size=len(t)), 750, 3500)*np.exp(-t/.008)
    return x*synth.envelope(len(t), .001, .045)


def melodic_lead(midi, seconds=.48):
    t = np.arange(round(seconds*SR))/SR
    f = synth.hz(midi)
    x = np.sin(2*np.pi*f*t) + .20*np.sin(2*np.pi*f*2*t) + .07*np.sin(2*np.pi*f*3*t)
    x += .16*np.sin(2*np.pi*f*1.003*t)
    x = synth.lowpass(x, 5600)
    return x*np.exp(-t/.28)*synth.envelope(len(t), .017, .12)


# An eight-bar harmonic phrase supplies variation rather than one fixed loop.
# Cmaj9 / Gadd9-B / Am9 / Fmaj9 / Dm9 / G13 / Fmaj9 / C6-9.
chords = ([48,55,59,64,74], [47,55,62,67,69], [45,52,55,60,71], [41,53,57,64,67],
          [50,57,60,64,69], [43,53,57,62,64], [41,53,57,64,72], [48,55,57,64,74])
roots = (36,35,33,29,38,31,29,36)
patterns = ([60,67,74,64,67,71,64,67], [59,67,74,62,69,67,62,67],
            [57,64,71,60,64,67,60,64], [57,65,72,64,67,65,60,64],
            [62,69,76,65,69,72,64,69], [59,67,74,65,69,71,62,67],
            [60,65,72,64,69,72,65,67], [60,67,74,64,69,76,67,72])
lead_motifs = ([72,76,79,81], [74,79,81,79], [72,76,79,76], [72,77,81,79],
               [74,77,81,84], [74,79,83,81], [72,77,81,84], [76,79,84,86])

for bar in range(30):
    start = bar*BAR
    idx = bar % 8
    if start >= 56: idx = 7
    s = stage(start)
    pad_gain = [.25,.27,.31,.36,.39,.27][s]
    musical(synth.pad(chords[idx], 3.6), start, pad_gain, instrument="pad")
    for step in range(16):
        time = start + step*BEAT/4
        s = stage(time)
        # Open with just felt-like tones and a sustained harmonic bed.
        if s == 0:
            if step in (0,8):
                note = patterns[idx][0 if step == 0 else 3]
                tone = synth.lowpass(synth.pluck(note, 1.2), 1700)
                musical(tone, time, .078, -.2 if step == 0 else .2, "felt", note)
            continue
        if s == 5:
            if time < 58 and step in (0,8):
                musical(synth.kick(), time, .14, instrument="kick")
                musical(synth.bass(36, .50), time, .16, instrument="bass", midi=36)
            if time < 58.3 and step in (0,4,8):
                note = [79,76,72][(step//4) % 3]
                musical(melodic_lead(note,.85), time, .075, .15, "closing-lead", note)
            continue

        ramp = np.clip((time-7)/12, 0, 1)
        formed = s >= 2
        active = s >= 3
        climax = s == 4
        # Drum density changes by section, not just level.
        is_beat = step % 4 == 0
        sparse_kick = step in (0,8) or (time >= 13 and step in (4,12))
        if is_beat and (formed or sparse_kick):
            gain = (.14+.09*ramp) if s == 1 else (.255 if s == 2 else .27)
            musical(synth.kick(), time, gain, instrument="kick")
        if active and step in (7,14) and (bar % 2 == 1 or climax):
            musical(synth.kick(), time, .102 if not climax else .135, instrument="ghost-kick")
        if step in (4,12) and time >= 10.5:
            gain = (.09+.10*ramp) if s == 1 else (.24 if s == 2 else .29)
            musical(synth.snare(), time, gain, -.07, "snare")
            if formed:
                musical(clap(), time+.009, .052 if s == 2 else .068, .12, "clap")
        hat_hit = (step % 4 == 2 and time >= 9) or (step % 2 == 0 and time >= 14) or active
        if hat_hit:
            if step % 2:
                gain = .017 if not climax else .023
            elif step % 4 == 2:
                gain = .044 if s < 3 else .055
            else:
                gain = .023 if s < 3 else .033
            if s == 1: gain *= (.55+.4*ramp)*1.25
            elif s == 2: gain *= 1.80
            elif s == 3: gain *= 2.30
            else: gain *= 2.60
            musical(synth.hat(step % 4 == 2 and step == 14), time,
                    gain, -.32 if step % 4 == 0 else .32, "hat")
        if formed and (step % 2 == 1 or active):
            musical(shaker(), time+.045, .030 if s == 2 else .055,
                    -.42 if step % 2 else .42, "shaker")
        if active and step in (3,6,11,15):
            musical(rim(54 if step % 2 else 57), time, .045 if not climax else .065,
                    -.24 if step < 8 else .24, "rim")

        # Bass moves from held roots to increasingly syncopated octaves/fifths.
        bass_steps = (0,8) if time < 11 else ((0,6,8,14) if time < 19 else (0,3,6,8,11,14))
        if active: bass_steps = (0,3,6,8,10,11,14,15)
        if step in bass_steps:
            note = roots[idx] + (12 if step in (6,11) else (7 if step == 10 else 0))
            duration = .40 if s == 1 else (.28 if not active else .24)
            musical(synth.bass(note,duration), time, .17 if s == 1 else (.225 if s == 2 else .25),
                    instrument="bass", midi=note)

        arp_steps = (0,8) if time < 12 else ((0,6,8,14) if not formed else (0,2,6,8,10,14))
        if active: arp_steps = (0,2,3,6,8,10,11,14)
        if step in arp_steps:
            note = patterns[idx][(step//2) % 8]
            if active and step in (3,11): note += 12
            tone = synth.pluck(note,.78,1 if step in (0,8) else .76)
            pan = -.24 if step < 8 else .24
            musical(tone, time, .078 if s == 1 else (.113 if s == 2 else .14), pan, "arpeggio", note)
            put(music, tone, time+.375, .018 if s < 3 else .028, -pan)
        if formed and step in (2,6,10,14):
            musical(chord_stab(chords[idx][1:4], bright=1 if s == 2 else 1.5), time,
                    .095 if s == 2 else .13, .13, "chord-stab")
        if active and step in (0,4,8,12):
            note = lead_motifs[idx][step//4]
            if climax and step in (8,12): note += 12 if note < 80 else 0
            musical(melodic_lead(note,.55), time, .085 if not climax else .12,
                    -.16 if step < 8 else .16, "lead", note)

    # Phrase-end fills evolve from two notes into four/six rising subdivisions.
    if bar in (8,16,20,24,25,26,27):
        fill_steps = [14,15] if bar < 17 else ([12,13,14,15] if bar < 25 else [10,11,12,13,14,15])
        for number, step in enumerate(fill_steps):
            time = start+step*BEAT/4
            musical(rim(48+number*2, .15), time, .045+number*.008,
                    -.3+number*.10, "fill")

# Harmony rests on C6/9 while the last 3.5 seconds remove percussion and fade.
musical(synth.pad([48,55,57,64,74], 3.5), 56.5, .22, instrument="resolution-pad")
musical(synth.bass(36, 1.6), 58, .14, instrument="resolution-bass", midi=36)
for channel in range(2): music[:,channel] = synth.lowpass(music[:,channel], 14000)
t = np.arange(SAMPLES)/SR
fade = np.sin(np.clip(t/.08,0,1)*np.pi/2)**2
fade *= np.cos(np.clip((t-56.5)/3.5,0,1)*np.pi/2)**2
music *= fade[:,None]
music[0] = music[-1] = 0


def rms_energy(x, width=481):
    e = np.mean(x*x,axis=1) if x.ndim == 2 else x*x
    return signal.fftconvolve(e,np.ones(width)/width,mode="same")


def write_and_measure(name, audio, peak_db=None):
    if peak_db is not None:
        audio = audio*10**(peak_db/20)/max(np.max(np.abs(audio)),1e-12)
    assert np.isfinite(audio).all() and np.max(np.abs(audio)) < 1
    wavfile.write(ASSETS/name,SR,np.rint(audio*32767).astype(np.int16))
    rate,pcm = wavfile.read(ASSETS/name)
    stored = pcm.astype(float)/32768
    peak,rms = np.max(np.abs(stored)),np.sqrt(np.mean(stored*stored))
    data = {"file":name,"sample_rate":rate,"channels":stored.shape[1],"sample_frames":len(stored),
            "duration_seconds":len(stored)/rate,"peak_dbfs":float(20*np.log10(max(peak,1e-12))),
            "rms_dbfs":float(20*np.log10(max(rms,1e-12))),"clipped_samples":int(np.count_nonzero(np.abs(stored)>=1)),
            "max_adjacent_sample_delta":float(np.max(np.abs(np.diff(stored,axis=0)))),
            "first_sample_max_abs":float(np.max(np.abs(stored[0]))),"last_sample_max_abs":float(np.max(np.abs(stored[-1])))}
    assert len(stored) == SAMPLES and rate == SR and data["clipped_samples"] == 0
    assert data["peak_dbfs"] <= -1 and data["first_sample_max_abs"] == data["last_sample_max_abs"] == 0
    return data,stored


def loudness(name):
    if not shutil.which("ffmpeg"): return {"status":"ffmpeg unavailable"}
    r = subprocess.run(["ffmpeg","-hide_banner","-i",str(ASSETS/name),"-af",
                        "loudnorm=I=-15.5:TP=-3:LRA=10:print_format=json","-f","null","-"],
                       capture_output=True,text=True,encoding="utf-8",errors="replace")
    begin,end = r.stderr.rfind("{\n"),r.stderr.rfind("}")
    if r.returncode != 0 or begin < 0: return {"status":"measurement failed"}
    d = json.loads(r.stderr[begin:end+1])
    return {"integrated_lufs":float(d["input_i"]),"true_peak_dbtp":float(d["input_tp"]),"loudness_range_lu":float(d["input_lra"])}


# Preserve section-to-section dynamics. Constant soft saturation trims the
# occasional coincident drum peak; no time-varying loudness normalization.
master_trials = []
low,high,drive = .15,16.0,2.4
for trial in range(8):
    mastered = np.tanh(music*drive)/drive
    music_metrics,music_stored = write_and_measure("music-v4.wav",mastered,-3.10)
    music_loudness = loudness("music-v4.wav")
    value = music_loudness.get("integrated_lufs")
    master_trials.append({"drive":drive,"measured_lufs":value})
    if value is None or abs(value+15.5) <= .20: break
    if value < -15.5: low=drive
    else: high=drive
    drive=(low+high)/2
assert music_loudness.get("true_peak_dbtp",-3) <= -2.95


def pcm_float(pcm):
    if np.issubdtype(pcm.dtype,np.integer):
        limit=max(abs(np.iinfo(pcm.dtype).min),np.iinfo(pcm.dtype).max)
        return pcm.astype(float)/limit
    return pcm.astype(float)


source_rate,source_pcm = wavfile.read(SOURCE_PATH)
paper = pcm_float(source_pcm)
if paper.ndim == 2: paper=np.mean(paper,axis=1)
paper-=np.mean(paper)
if source_rate != SR:
    divisor=math.gcd(source_rate,SR)
    paper=signal.resample_poly(paper,SR//divisor,source_rate//divisor)
paper*=synth.envelope(len(paper),.004,.018)
paper[0]=paper[-1]=0
paper/=np.max(np.abs(paper))
paper_rms_peak=int(np.argmax(rms_energy(paper)))
paper_wave_peak=int(np.argmax(np.abs(paper)))
paper_events={}
for scene in TIMELINE["scenes"][1:]:
    paper_events.setdefault(scene["start"],[]).append({"id":scene["id"],"kind":"scene","peak":-16.0,"lead":TIMELINE["transitionLeadFrames"]})
for accent in TIMELINE["accents"]:
    level=-21.5 if accent["type"]=="success" else (-18.5 if accent["type"]=="focus" else -20.0)
    paper_events.setdefault(accent["frame"],[]).append({"id":accent["id"],"kind":accent["type"],"peak":level,"lead":accent["leadFrames"]})
paper_cues=[]
for number,(frame,requests) in enumerate(sorted(paper_events.items())):
    target=round(frame*SR/FPS)
    first=target-paper_rms_peak
    pan=-.07 if number%2 else .07
    angle=(pan+1)*np.pi/4
    stereo=np.column_stack((paper*np.cos(angle),paper*np.sin(angle)))
    level=max(r["peak"] for r in requests)
    stereo*=10**(level/20)/np.max(np.abs(stereo))
    put(paper_bus,stereo,first/SR)
    paper_cues.append({"labels":[r["id"] for r in requests],"kind":"paper","arrival_frame":frame,
                       "arrival_sample":target,"audio_start_sample":first,"audio_end_sample_exclusive":first+len(paper),
                       "visual_lead_frames":max(r["lead"] for r in requests),"target_peak_dbfs":level,"layer_count":1,
                       "source_energy_peak_sample":paper_rms_peak,"source_waveform_peak_sample":paper_wave_peak,
                       "audio_start_offset_ms":-paper_rms_peak*1000/SR})


def glass_wood_chime(midi):
    """Wood-bar fundamental plus brief inharmonic glass modes and mallet."""
    n=round(.42*SR)
    tt=np.arange(n)/SR
    f=synth.hz(midi)
    x=.84*np.sin(2*np.pi*f*tt)*np.exp(-tt/.105)
    x+=.12*np.sin(2*np.pi*f*1.003*tt+.3)*np.exp(-tt/.12)
    x+=.22*np.sin(2*np.pi*f*2.756*tt+.2)*np.exp(-tt/.042)
    x+=.075*np.sin(2*np.pi*f*5.404*tt+.5)*np.exp(-tt/.017)
    mallet=synth.bandpass(RNG.normal(size=n),1200,4900)*np.exp(-tt/.0028)
    x+=.037*mallet
    x=synth.lowpass(x,6800,order=3)
    x*=synth.envelope(n,.0025,.075)
    x[0]=x[-1]=0
    return x/np.max(np.abs(x))


flow_notes=TIMELINE["flowNotes"]
assert [n["frame"] for n in flow_notes]==[225,240,255,270,285,300,315,330]
assert [n["midi"] for n in flow_notes]==[72,74,76,79,81,84,86,88]
chime_cues=[]
for index,note in enumerate(flow_notes):
    tone=glass_wood_chime(note["midi"])
    energy_peak=int(np.argmax(rms_energy(tone)))
    wave_peak=int(np.argmax(np.abs(tone)))
    target=round(note["frame"]*SR/FPS)
    first=target-energy_peak
    pan=-.12+index*.24/7
    angle=(pan+1)*np.pi/4
    stereo=np.column_stack((tone*np.cos(angle),tone*np.sin(angle)))
    level=-12.5+index*.07
    stereo*=10**(level/20)/np.max(np.abs(stereo))
    put(chime_bus,stereo,first/SR)
    chime_cues.append({"label":note.get("id",f"flow-{index+1}"),"kind":"flow-chime","arrival_frame":note["frame"],
                       "arrival_sample":target,"midi":note["midi"],"expected_frequency_hz":synth.hz(note["midi"]),
                       "audio_start_sample":first,"audio_end_sample_exclusive":first+len(tone),
                       "audio_start_seconds":first/SR,"audio_end_seconds":(first+len(tone))/SR,
                       "source_segment_start_sample":0,"source_segment_end_sample_exclusive":len(tone),
                       "source_main_energy_peak_offset_samples":energy_peak,"target_peak_dbfs":level,
                       "source_energy_peak_sample":energy_peak,"source_waveform_peak_sample":wave_peak,
                       "audio_start_offset_ms":-energy_peak*1000/SR,"waveform_peak_offset_ms":(wave_peak-energy_peak)*1000/SR})

paper_metrics,paper_stored=write_and_measure("paper-turns-v4.wav",paper_bus)
chime_metrics,chime_stored=write_and_measure("flow-chimes-v4.wav",chime_bus)


def inspect_cues(cues,stored,check_pitch=False):
    for cue in cues:
        first,end=cue["audio_start_sample"],cue["audio_end_sample_exclusive"]
        fragment=stored[first:end]
        measured=first+int(np.argmax(rms_energy(fragment)))
        wave=first+int(np.argmax(np.max(np.abs(fragment),axis=1)))
        cue.update({"measured_energy_peak_sample":measured,"measured_energy_peak_frame":measured*FPS/SR,
                    "measured_energy_peak_offset_from_clip_start_samples":measured-first,
                    "energy_peak_error_samples":measured-cue["arrival_sample"],
                    "measured_waveform_peak_sample":wave,"measured_waveform_peak_offset_ms":(wave-cue["arrival_sample"])*1000/SR,
                    "measured_peak_dbfs":float(20*np.log10(np.max(np.abs(fragment)))),
                    "boundary_adjacent_sample_delta":float(max(np.max(np.abs(stored[first]-stored[first-1])),np.max(np.abs(stored[end]-stored[end-1]))))})
        assert abs(cue["energy_peak_error_samples"])<=1
        assert cue["boundary_adjacent_sample_delta"]==0
        if check_pitch:
            mono=np.mean(fragment,axis=1)*np.hanning(len(fragment))
            nfft=262144
            spectrum=np.abs(np.fft.rfft(mono,n=nfft))
            frequencies=np.fft.rfftfreq(nfft,1/SR)
            mask=(frequencies>cue["expected_frequency_hz"]*.8)&(frequencies<cue["expected_frequency_hz"]*1.2)
            measured_hz=float(frequencies[np.flatnonzero(mask)[np.argmax(spectrum[mask])]])
            cue["measured_fundamental_hz"]=measured_hz
            cue["pitch_error_cents"]=1200*math.log2(measured_hz/cue["expected_frequency_hz"])
            assert abs(cue["pitch_error_cents"])<10


inspect_cues(paper_cues,paper_stored)
inspect_cues(chime_cues,chime_stored,True)
assert np.all(np.diff([c["measured_fundamental_hz"] for c in chime_cues])>0)


def section_measurement(label,start,end):
    audio=music_stored[round(start*SR):round(end*SR)]
    # Average Welch spectra measure acoustic brightness, independent of level.
    frequency,power=signal.welch(np.mean(audio,axis=1),fs=SR,nperseg=4096)
    centroid=float(np.sum(frequency*power)/np.sum(power))
    high=float(np.sum(power[frequency>=2500])/np.sum(power))
    audible=frequency>=250
    mid_centroid=float(np.sum(frequency[audible]*power[audible])/np.sum(power[audible]))
    percussion_names={"kick","ghost-kick","snare","clap","hat","shaker","rim","fill"}
    events=[e for e in musical_events if start<=e["time"]<end]
    percussions=[e for e in events if e["instrument"] in percussion_names]
    pitches=[e["midi"] for e in events if e["midi"] is not None and e["instrument"] not in {"bass","resolution-bass"}]
    return {"label":label,"start_seconds":start,"end_seconds":end,
            "rms_dbfs":float(20*np.log10(np.sqrt(np.mean(audio*audio)))),
            "spectral_centroid_hz":centroid,"spectral_centroid_above_250hz":mid_centroid,
            "energy_above_2500hz_ratio":high,
            "percussion_attacks":len(percussions),"percussion_attacks_per_second":len(percussions)/(end-start),
            "instrument_layers":sorted(set(e["instrument"] for e in events)),
            "melodic_midi_min":min(pitches) if pitches else None,"melodic_midi_max":max(pitches) if pitches else None}


sections=[section_measurement("简洁铺陈",0,7),section_measurement("鼓贝斯渐入",7,19),
          section_measurement("节奏成型",19,34.5),section_measurement("切分高音推进",34.5,51),
          section_measurement("品牌高潮",51,56.5),section_measurement("自然收束",56.5,60)]
first_four=sections[:4]
progression={"rms_increases_across_first_four":bool(np.all(np.diff([s["rms_dbfs"] for s in first_four])>0)),
             "percussion_density_increases_across_first_four":bool(np.all(np.diff([s["percussion_attacks_per_second"] for s in first_four])>0)),
             "brightness_increases_across_first_four":bool(np.all(np.diff([s["energy_above_2500hz_ratio"] for s in first_four])>0)),
             "brightness_indicator":"energy ratio above 2500 Hz; full-band centroid can fall as sub bass enters",
             "flow_note_pitch_strictly_ascending":True,
             "max_paper_energy_peak_error_samples":max(abs(c["energy_peak_error_samples"]) for c in paper_cues),
             "max_chime_energy_peak_error_samples":max(abs(c["energy_peak_error_samples"]) for c in chime_cues)}
assert progression["rms_increases_across_first_four"]
assert progression["percussion_density_increases_across_first_four"]
assert progression["brightness_increases_across_first_four"]
report={"bpm":BPM,"fps":FPS,"duration_frames":TIMELINE["durationFrames"],"samples_per_frame":SR//FPS,
        "timeline_sha256":hashlib.sha256(TIMELINE_PATH.read_bytes()).hexdigest(),
        "paper_source_sha256":hashlib.sha256(SOURCE_PATH.read_bytes()).hexdigest(),
        "music_synthesized_locally":True,"paper_contains_only_single_layer_recorded_paper":True,
        "paper_contains_chimes_or_mouse_clicks":False,"chime_cue_count":len(chime_cues),
        "mouse_clicks_in_film_sequence_frames":[c["frame"] for c in TIMELINE["clicks"]],
        "files":[music_metrics,paper_metrics,chime_metrics],"music_loudness":music_loudness,
        "music_master_constant_saturation_trials":master_trials,"music_sections":sections,
        "progression_checks":progression,"paper_cues":paper_cues,"flow_chime_cues":chime_cues}
(OUT/"audio_metrics_v4.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
section_rows="\n".join(f"| {s['label']} | {s['start_seconds']:g}–{s['end_seconds']:g} | {s['rms_dbfs']:.2f} | {s['spectral_centroid_above_250hz']:.0f} | {s['energy_above_2500hz_ratio']*100:.3f}% | {s['percussion_attacks_per_second']:.1f} | {s['melodic_midi_max']} |" for s in sections)
note_rows="\n".join(f"| {c['arrival_frame']} | {c['midi']} | {c['measured_fundamental_hz']:.2f} | {c['audio_start_offset_ms']:.3f} | {c['measured_energy_peak_sample']:,} | {c['energy_peak_error_samples']} | {c['measured_waveform_peak_offset_ms']:.3f} |" for c in chime_cues)
description=f"""# V4 声音说明

这版配乐从轻到有动感：0–7 秒只有温暖和弦和疏朗的柔和拨弦；7–19 秒先进入两拍底鼓与根音贝斯，再逐步加军鼓、踩镲和切分；19–34.5 秒形成完整四拍律动；34.5–51 秒加入十六分打击、切分贝斯、较高音区的主题旋律和鼓 fill；51–56.5 秒再加密鼓组和高音旋律，55.5 秒品牌出现时保持高潮；最后 3.5 秒逐层退鼓，落回 C6/9 并自然淡出。和声采用八小节变化，推进来自乐器层次、音区、节奏密度与乐句变化。

音乐实测 {music_loudness.get('integrated_lufs')} LUFS，采样峰值 {music_metrics['peak_dbfs']:.2f} dBFS，真峰值 {music_loudness.get('true_peak_dbtp')} dBTP。母带只用固定强度柔和饱和与整体增益，没有随时间拉平各段响度。三轨都是 60 秒、48 kHz、16 bit、立体声，每声道 2,880,000 采样，严格对应 1800 帧。

亮度同时记录中高频频谱重心与 2.5 kHz 以上能量比例；前四段两项均逐步增加。全频频谱重心另存 JSON，鼓和贝斯进入时低频会将它拉低，因此不单独把它当成亮度判断。

| 段落 | 秒 | RMS dBFS | 250 Hz 以上重心 Hz | 2.5 kHz 以上能量 | 打击次数/秒 | 旋律最高 MIDI |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
{section_rows}

八个数据链音只出现在第 225、240、255、270、285、300、315、330 帧，MIDI 72、74、76、79、81、84、86、88 逐级升高。使用木条基音、短衰减非整数玻璃泛音和轻槌头噪声，避免电话式纯音与刺耳高频。每颗 0.42 秒，留有短尾；以最强 10.0208 毫秒 RMS 能量窗中心对齐点亮帧，同时记录波形尖峰的微小偏移。

| 点亮帧 | MIDI | 实测基频 Hz | 起音偏移 ms | 能量峰采样 | 误差采样 | 波形峰偏移 ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
{note_rows}

其他转场只用一层真实翻纸录音，保持轻巧：场景 -16 dBFS、聚焦 -18.5 dBFS、卡片 -20 dBFS、下载完成 -21.5 dBFS。纸声以录音最强 RMS 峰对齐场景或强调到达帧，无其他滴声或提示音。两个机械鼠标点击由 Film 在第 618、1463 帧单独播放 mouse-click-v2.wav，不混入任何总轨。

时间统一读取 timeline-v4.json。最大全轨纸声落点误差 {progression['max_paper_energy_peak_error_samples']} 采样，数据链音误差 {progression['max_chime_energy_peak_error_samples']} 采样，所有素材边界差为零且无削波。分段递进指标见 audio_metrics_v4.json。生成入口 generate_score_v4.py，音轨写入指定 assets-dir，报告与说明写入 output-dir。
"""
(OUT/"音乐说明-v4.md").write_text(description,encoding="utf-8")
print(json.dumps({"files":report["files"],"music_loudness":music_loudness,"music_sections":sections,
                  "progression_checks":progression,"master_trials":master_trials},ensure_ascii=False,indent=2))
