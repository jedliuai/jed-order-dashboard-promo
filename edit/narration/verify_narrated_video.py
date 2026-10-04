"""Verify the published music-only and narrated releases using current assets."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import sys

import numpy as np
from scipy.io import wavfile

if hasattr(sys.stdout, "reconfigure"):sys.stdout.reconfigure(encoding="utf-8")


ROOT = Path(__file__).resolve().parents[2]
DELIVERABLES = ROOT / "deliverables"
EXPECTED_SOURCE_SHA256 = "BE226EDDCDB0A6C90CDA41921BB9FA60C06A8B146FFCC98D4138B3860C7EB6C4"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--source", default=str(DELIVERABLES / "promo-60s-music-only.mp4"))
parser.add_argument("--target", default=str(DELIVERABLES / "promo-60s-narrated.mp4"))
parser.add_argument("--narration", default=str(DELIVERABLES / "narration.wav"))
parser.add_argument("--mix-report", default=None)
parser.add_argument("--output-dir", default=str(ROOT / "output/narration"))
parser.add_argument("--expected-source-sha256", default=EXPECTED_SOURCE_SHA256)
args = parser.parse_args()
OUT = Path(args.output_dir).resolve()
OUT.mkdir(parents=True, exist_ok=True)
source, target = Path(args.source).resolve(), Path(args.target).resolve()
narration = Path(args.narration).resolve()
mix_path = Path(args.mix_report).resolve() if args.mix_report else OUT / "mix-report.json"
if not mix_path.exists() and not args.mix_report:
    mix_path = ROOT / "edit/narration/mix-report.json"


def run(command):
    return subprocess.run(command, check=True, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def stream_hash(path):
    return run(["ffmpeg", "-v", "error", "-i", str(path), "-map", "0:v:0",
                "-c:v", "copy", "-f", "hash", "-"]).stdout.strip()


source_sha256 = sha256(source)
assert source_sha256 == args.expected_source_sha256.upper(), "Original music-only release changed"
old, new = stream_hash(source), stream_hash(target)
assert old == new, "Compressed video packet bytes changed"
probe = json.loads(run(["ffprobe", "-v", "error", "-count_frames", "-show_streams",
                        "-show_format", "-of", "json", str(target)]).stdout)
video = next(s for s in probe["streams"] if s["codec_type"] == "video")
audio = next(s for s in probe["streams"] if s["codec_type"] == "audio")
assert (video["width"], video["height"], video["r_frame_rate"], int(video["nb_read_frames"])) == (1920, 1080, "30/1", 1800)
assert float(video["duration"]) == 60 and audio["sample_rate"] == "48000" and audio["channels"] == 2
decoded = run(["ffmpeg", "-v", "error", "-i", str(target), "-f", "null", "-"])
assert not decoded.stderr.strip(), decoded.stderr
decoded_path = OUT / "final-decoded.wav"
run(["ffmpeg", "-y", "-v", "error", "-i", str(target), "-map", "0:a:0",
     "-ar", "48000", "-c:a", "pcm_s16le", str(decoded_path)])
sample_rate, pcm = wavfile.read(decoded_path)
assert np.max(np.abs(pcm.astype(float))) < 32767, "Decoded AAC clips"
loudness = run(["ffmpeg", "-hide_banner", "-i", str(target), "-map", "0:a:0", "-af",
                "loudnorm=I=-16:TP=-2:LRA=8:print_format=json", "-f", "null", "-"])
metrics = json.loads(re.findall(r"\{[^{}]+\}", loudness.stderr)[-1])
assert -17 < float(metrics["input_i"]) < -15 and float(metrics["input_tp"]) < -2
mix = json.loads(mix_path.read_text(encoding="utf-8")) if mix_path.exists() else None
voice_rate, voice = wavfile.read(narration)
assert voice_rate == 48000 and len(voice) == 60 * voice_rate
active = np.flatnonzero(np.any(voice != 0, axis=1) if voice.ndim == 2 else voice != 0)
assert len(active), "Narration track is silent"
measured_voice_end = (int(active[-1]) + 1) / voice_rate
timeline = json.loads((ROOT / "edit/presentation/src/timeline-v4.json").read_text(encoding="utf-8"))
gaps = {}
for click in timeline["clicks"]:
    seconds = click["frame"] / timeline["fps"]
    window = voice[round((seconds - .075) * voice_rate):round((seconds + .075) * voice_rate)]
    assert not np.any(window), f"Narration overlaps the click at {seconds} seconds"
    gaps[click["id"]] = {"frame": click["frame"], "seconds": seconds, "speech_free_window_ms": 150}
assert measured_voice_end < 59.2
if mix:
    assert mix["segments"][-1]["actual_end"] < 59.2
    # The aligned clip includes quiet tail padding after the last nonzero PCM.
    assert measured_voice_end <= mix["segments"][-1]["actual_end"] + 1 / voice_rate
    assert mix["segments"][-1]["actual_end"] - measured_voice_end < .25
report = {
    "music_only_file_sha256": source_sha256,
    "video_packet_hash_original": old,
    "video_packet_hash_narrated": new,
    "video_bytes_identical": True,
    "full_decode_errors": 0,
    "video_frames": 1800,
    "video_duration": 60,
    "container_duration": float(probe["format"]["duration"]),
    "aac_lufs": float(metrics["input_i"]),
    "aac_true_peak_db": float(metrics["input_tp"]),
    "aac_lra": float(metrics["input_lra"]),
    "click_voice_gaps": gaps,
    "final_voice_end": measured_voice_end,
    "final_aligned_clip_end": mix["segments"][-1]["actual_end"] if mix else None,
    "alignment_metadata_used": bool(mix),
    "max_voice_tempo": max(s["tempo_factor"] for s in mix["segments"]) if mix else None,
    "final_file_sha256": sha256(target),
}
(OUT / "verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
