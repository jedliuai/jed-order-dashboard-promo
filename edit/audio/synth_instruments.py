"""Instrument primitives used by generate_score_v4.py.

Instrument sounds use local synthesis only. Importing this module writes no
files and does not allocate full-duration audio buses.
"""

import numpy as np
from scipy import signal


SR = 48_000
SECONDS = 60.0
SAMPLES = int(SR * SECONDS)
BPM = 120
BEAT = 60 / BPM
BAR = BEAT * 4
RNG = np.random.default_rng(20261003)


def hz(midi):
    return 440 * 2 ** ((midi - 69) / 12)


def lowpass(x, cutoff, order=2):
    sos = signal.butter(order, cutoff, fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def bandpass(x, lo, hi, order=2):
    sos = signal.butter(order, (lo, hi), btype="bandpass", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def envelope(length, attack=.01, release=.15):
    e = np.ones(length)
    a = min(length, max(1, int(attack * SR)))
    r = min(length - a, max(1, int(release * SR)))
    e[:a] = np.sin(np.linspace(0, np.pi / 2, a)) ** 2
    if r > 0:
        e[-r:] = np.cos(np.linspace(0, np.pi / 2, r)) ** 2
    return e


def put(bus, x, start, gain=1, pan=0):
    first = int(round(start * SR))
    if first >= len(bus) or first + len(x) <= 0:
        return
    skip = max(0, -first)
    first = max(0, first)
    n = min(len(x) - skip, len(bus) - first)
    x = x[skip:skip + n] * gain
    if x.ndim == 1:
        # Equal-power pan law; keep stereo ambience out of the sub bass.
        angle = (pan + 1) * np.pi / 4
        bus[first:first + n, 0] += x * np.cos(angle)
        bus[first:first + n, 1] += x * np.sin(angle)
    else:
        bus[first:first + n] += x


def pad(notes, seconds):
    n = int(SR * seconds)
    t = np.arange(n) / SR
    stereo = np.zeros((n, 2))
    for idx, midi in enumerate(notes):
        f = hz(midi)
        for ch, detune in enumerate((-.0031, .0027)):
            voice = np.zeros(n)
            # Smooth additive spectrum: rounded saw/triangle blend.
            for harmonic in range(1, 9):
                phase = RNG.uniform(-np.pi, np.pi)
                amplitude = np.exp(-harmonic / 3.1) / harmonic ** 1.35
                mod = .007 * np.sin(2 * np.pi * (.14 + idx * .015) * t)
                voice += amplitude * np.sin(2 * np.pi * f * harmonic * (1 + detune) * t + phase + mod)
            stereo[:, ch] += voice
    for ch in range(2):
        stereo[:, ch] = lowpass(stereo[:, ch], 1800)
    stereo *= envelope(n, .65, 1.65)[:, None]
    stereo *= (1 + .06 * np.sin(2 * np.pi * .25 * t))[:, None]
    return stereo / len(notes)


def pluck(midi, seconds=1.2, velocity=1):
    n = int(SR * seconds)
    t = np.arange(n) / SR
    f = hz(midi)
    x = np.zeros(n)
    # The high partials decay first, leaving a mellow electric-piano tail.
    for h in range(1, 7):
        decay = .24 + .48 / h
        x += (.72 / h ** 1.75) * np.sin(2 * np.pi * f * h * t) * np.exp(-t / decay)
    x += .06 * np.sin(2 * np.pi * f * 2.006 * t) * np.exp(-t / .2)
    x = lowpass(x, 3600) * envelope(n, .008, .16)
    return x * velocity


def bass(midi, seconds=.7):
    n = int(SR * seconds)
    t = np.arange(n) / SR
    f = hz(midi)
    x = .88 * np.sin(2 * np.pi * f * t)
    x += .15 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / .3)
    x += .055 * np.sin(2 * np.pi * 3 * f * t)
    return lowpass(x, 330) * envelope(n, .018, .18) * np.exp(-t / 1.5)


def kick():
    n = int(SR * .36)
    t = np.arange(n) / SR
    freq = 46 + 65 * np.exp(-t / .024)
    phase = np.cumsum(freq) * 2 * np.pi / SR
    x = np.sin(phase) * np.exp(-t / .092)
    click = lowpass(RNG.normal(size=n), 1200) * np.exp(-t / .007) * .055
    return (x + click) * envelope(n, .001, .09)


def snare():
    n = int(SR * .25)
    t = np.arange(n) / SR
    air = bandpass(RNG.normal(size=n), 850, 6500) * np.exp(-t / .034)
    body = np.sin(2 * np.pi * 185 * t) * np.exp(-t / .039)
    # A soft, compact rim/snare layer that stays behind product typography.
    return (.24 * air + .22 * body) * envelope(n, .0018, .1)


def hat(open_hat=False):
    sec = .17 if open_hat else .065
    n = int(SR * sec)
    t = np.arange(n) / SR
    x = bandpass(RNG.normal(size=n), 5300, 12500)
    return x * np.exp(-t / (.032 if open_hat else .010)) * envelope(n, .0015, .02)


