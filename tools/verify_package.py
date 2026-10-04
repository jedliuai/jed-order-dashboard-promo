"""Verify published asset integrity, cover ratios, timeline, and local document links."""
from pathlib import Path
import hashlib
from html.parser import HTMLParser
import json
import re
import struct
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]

def require(condition, message):
    if not condition:
        raise AssertionError(message)

manifest = ROOT / 'SHA256SUMS.txt'
require(manifest.exists(), 'SHA256SUMS.txt is missing')
verified = 0
for line in manifest.read_text(encoding='utf-8').splitlines():
    if not line.strip():
        continue
    digest, filename = line.split('  ', 1)
    source = ROOT / filename
    require(source.is_file(), f'Missing media: {filename}')
    require(hashlib.sha256(source.read_bytes()).hexdigest() == digest.lower(), f'Checksum differs: {filename}')
    verified += 1

covers = {'4x3':(1448,1086),'3x4':(1086,1448),'16x9':(1680,945),'9x16':(945,1680),'1x1':(1254,1254)}
for ratio, dimensions in covers.items():
    source = ROOT / f'deliverables/covers/cover-{ratio}.png'
    header = source.read_bytes()[:24]
    require(header[:8] == b'\x89PNG\r\n\x1a\n', f'Not PNG: {source.name}')
    require(struct.unpack('>II',header[16:24]) == dimensions, f'Wrong cover size: {ratio}')

timeline = json.loads((ROOT/'edit/presentation/src/timeline-v4.json').read_text(encoding='utf-8'))
require(timeline['fps'] == 30 and timeline['durationFrames'] == 1800, 'Final film duration differs')
cursor = 0
for scene in timeline['scenes']:
    require(scene['start'] == cursor, f'Scene gap/overlap: {scene["id"]}')
    cursor += scene['duration']
require(cursor == 1800 and len(timeline['scenes']) == 13, 'Scene coverage differs')
require([x['frame'] for x in timeline['flowNotes']] == list(range(225,331,15)), 'Flow timing differs')
require([x['frame'] for x in timeline['clicks']] == [618,1463], 'Mouse click timing differs')
require(len(list((ROOT/'edit/narration/voice-clips').glob('*.wav'))) == 15, 'Expected 15 voice clips')

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]
    def handle_starttag(self, tag, attrs):
        self.links.extend(v for k,v in attrs if k in ('href','src') and v)

checked = 0
documents = [ROOT/'index.html', *ROOT.glob('*.md'), *ROOT.glob('docs/*.md')]
for document in documents:
    content = document.read_text(encoding='utf-8')
    parser = Links()
    parser.feed(content)
    links = parser.links + re.findall(r'\]\(([^\s)]+)(?:\s+"[^"]*")?\)', content)
    for link in links:
        parsed = urlparse(link)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        filename = unquote(parsed.path)
        target = (document.parent/filename).resolve()
        require(target.is_relative_to(ROOT), f'Link escapes repository: {document.name}: {link}')
        require(target.is_file() or target.is_dir(), f'Broken local link: {document.name}: {link}')
        checked += 1
    require(not re.search(r'(?:D:[\\/]|C:[\\/]Users[\\/]|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})', content), f'Private path/credential pattern: {document.name}')

require((ROOT/'deliverables/subtitles-zh.vtt').read_text(encoding='utf-8').startswith('WEBVTT\n'), 'Web subtitles missing')
print(f'PASS: {verified} media checksums, five exact cover ratios, 13 scenes / 1800 frames, 15 clips, {checked} local links.')
