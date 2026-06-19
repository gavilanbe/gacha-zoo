"""
Gacha Zoo – Cozy Village Background Loop  v2
AABA  (8 bars each = 32 bars total)
100 BPM, swung 8ths (~62/38 ratio), F major / Bbmaj7 modulation in B

Instruments chosen from snes.sf2:
  Lead melody   → prog 79  Ocarina         (ch 0)
  Comping       → prog 11  Vibraphone      (ch 1)
  Bass          → prog 32  Acoustic Bass   (ch 2)
  Percussion    → ch 9 (GM drum channel)

Harmony:
  A section (F major, jazzy):
    Bar 1-2:  Fmaj7              (I maj7)
    Bar 3-4:  Gm7 → C7           (ii7 – V7)
    Bar 5-6:  Am7 → Dm7          (iii7 – vi7)
    Bar 7-8:  Gm9 → C7sus4→C7   (ii9 – V turnaround back to I)

  B section (modulates to IV / relative minor):
    Bar 17-18: Bbmaj7            (IV maj7)
    Bar 19-20: Gm7 → C7         (ii7 – V7 of F)
    Bar 21-22: Dm7 → Am7        (vi7 – iii7, relative minor colour)
    Bar 23-24: Gm7 → C7sus4     (ii7 – V resolves back to A)

Motif (2 bars, whistleable C5-G5-A5 arc):
  Bar 1: C5(q) D5(e) F5(e) G5(dh.)  — rising 4th + sustained peak
  Bar 2: E5(e) D5(e) C5(q) A4(h)    — descending answer + rest
"""

from mido import Message, MidiFile, MidiTrack, MetaMessage, bpm2tempo
from collections import defaultdict
import random

random.seed(42)

TPB  = 480
BPM  = 100
TEMPO = bpm2tempo(BPM)

# Swing durations (ticks at TPB=480, 100 BPM)
SW_ON  = round(480 * 0.62)   # 298 — first 8th of a beat
SW_OFF = round(480 * 0.38)   # 182 — second (swung) 8th

def q():     return 480
def h():     return 960
def dh():    return 1440
def e_on():  return SW_ON
def e_off(): return SW_OFF

def human_vel(v, spread=12):
    return max(1, min(127, v + random.randint(-spread, spread)))

# ---------------------------------------------------------------------------
# Event list: (start_tick, channel, note, velocity, duration_ticks)
# ---------------------------------------------------------------------------
events = []

def add(start, ch, note, vel, dur):
    events.append((start, ch, note, human_vel(vel), dur))

def T(bar, beat, sub=0):
    """Absolute tick for (1-indexed bar, 1-indexed beat, sub 0=on / 1=swung-off)."""
    return (bar - 1) * 4 * 480 + (beat - 1) * 480 + (SW_ON if sub == 1 else 0)

# ---------------------------------------------------------------------------
# CHORD VOICINGS (Vibraphone, ch 1)
# Voiced mid-register to leave space above for melody (C5+)
# ---------------------------------------------------------------------------
FMAJ7   = [53, 57, 60, 64]     # F3 A3 C4 E4
GM7     = [55, 58, 62, 65]     # G3 Bb3 D4 F4
C7      = [48, 52, 55, 58]     # C3 E3 G3 Bb3
AM7     = [57, 60, 64, 67]     # A3 C4 E4 G4
DM7     = [50, 53, 57, 60]     # D3 F3 A3 C4
GM9     = [55, 58, 62, 69]     # G3 Bb3 D4 A4
C7SUS4  = [48, 53, 55, 58]     # C3 F3 G3 Bb3
BBMAJ7  = [50, 53, 57, 65]     # D3 F3 A3 F4

def comp(bar, beat, sub, notes, vel=62, dur=None):
    if dur is None:
        dur = q()
    t = T(bar, beat, sub)
    for n in notes:
        add(t, 1, n, vel, dur)

def comp_A(sb, intensity=1.0):
    v = lambda x: int(x * intensity)
    # Bar 1-2: Fmaj7
    comp(sb,   1, 0, FMAJ7, v(58), q())
    comp(sb,   2, 1, FMAJ7, v(52), e_off())
    comp(sb,   4, 1, FMAJ7, v(60), e_off())
    comp(sb+1, 2, 0, FMAJ7, v(55), h())
    comp(sb+1, 4, 1, FMAJ7, v(50), e_off())
    # Bar 3-4: Gm7 → C7
    comp(sb+2, 1, 0, GM7,   v(60), q())
    comp(sb+2, 2, 1, GM7,   v(53), e_off())
    comp(sb+2, 4, 0, GM7,   v(57), q())
    comp(sb+3, 1, 1, C7,    v(62), e_off())
    comp(sb+3, 3, 0, C7,    v(55), h())
    comp(sb+3, 4, 1, C7,    v(50), e_off())
    # Bar 5-6: Am7 → Dm7
    comp(sb+4, 1, 0, AM7,   v(58), q())
    comp(sb+4, 2, 1, AM7,   v(52), e_off())
    comp(sb+4, 4, 0, AM7,   v(60), q())
    comp(sb+5, 1, 1, DM7,   v(65), e_off())
    comp(sb+5, 3, 0, DM7,   v(55), q())
    comp(sb+5, 4, 1, DM7,   v(50), e_off())
    # Bar 7-8: Gm9 → C7sus4 → C7 turnaround
    comp(sb+6, 1, 0, GM9,    v(60), q())
    comp(sb+6, 2, 1, GM9,    v(53), e_off())
    comp(sb+6, 4, 0, GM9,    v(58), q())
    comp(sb+7, 1, 0, C7SUS4, v(62), q())
    comp(sb+7, 2, 1, C7,     v(58), e_off())
    comp(sb+7, 3, 0, C7,     v(60), h())
    comp(sb+7, 4, 1, C7,     v(55), e_off())

def comp_B(sb):
    # Bar 17-18: Bbmaj7
    comp(sb,   1, 0, BBMAJ7, 68, q())
    comp(sb,   2, 1, BBMAJ7, 55, e_off())
    comp(sb,   4, 1, BBMAJ7, 60, e_off())
    comp(sb+1, 2, 0, BBMAJ7, 58, h())
    comp(sb+1, 4, 1, BBMAJ7, 52, e_off())
    # Bar 19-20: Gm7 → C7
    comp(sb+2, 1, 0, GM7,  65, q())
    comp(sb+2, 3, 1, GM7,  55, e_off())
    comp(sb+3, 1, 1, C7,   68, e_off())
    comp(sb+3, 2, 0, C7,   62, q())
    comp(sb+3, 4, 0, C7,   58, q())
    # Bar 21-22: Dm7 → Am7
    comp(sb+4, 1, 0, DM7,  60, q())
    comp(sb+4, 2, 1, DM7,  55, e_off())
    comp(sb+4, 4, 0, DM7,  63, q())
    comp(sb+5, 1, 1, AM7,  65, e_off())
    comp(sb+5, 3, 0, AM7,  58, h())
    # Bar 23-24: Gm7 → C7sus4 (leads back to A)
    comp(sb+6, 1, 0, GM7,    62, q())
    comp(sb+6, 2, 1, GM7,    55, e_off())
    comp(sb+6, 4, 0, GM7,    60, q())
    comp(sb+7, 1, 0, C7SUS4, 65, h())
    comp(sb+7, 3, 0, C7,     62, q())
    comp(sb+7, 4, 1, C7,     55, e_off())

# ---------------------------------------------------------------------------
# MELODY (Ocarina, ch 0)
# Target range: A4(69)–C6(84). Motif arc: C5(72)→G5(79)→rest→descent→A4
# ---------------------------------------------------------------------------
def mel(bar, beat, sub, note, dur, vel=78):
    add(T(bar, beat, sub), 0, note, vel, dur)

def melody_A1(sb):
    """First A — states the motif plainly."""
    # Bar 1: C5(q) D5(e_on) F5(e_off) G5(dh.)
    mel(sb,   1, 0, 72, q(),     82)
    mel(sb,   2, 0, 74, e_on(),  76)
    mel(sb,   2, 1, 77, e_off(), 70)
    mel(sb,   3, 0, 79, dh(),    85)
    # Bar 2: answer — E5(e_off) D5(e_on) C5(q) A4(h) [rest beat 4]
    mel(sb+1, 2, 1, 76, e_off(), 72)
    mel(sb+1, 3, 0, 74, e_on(),  68)
    mel(sb+1, 3, 1, 72, e_off(), 72)
    mel(sb+1, 4, 0, 69, h(),     75)
    # Bar 3: sequence up — D5 E5 G5 A5
    mel(sb+2, 1, 0, 74, q(),     80)
    mel(sb+2, 2, 0, 76, e_on(),  74)
    mel(sb+2, 2, 1, 79, e_off(), 68)
    mel(sb+2, 3, 0, 81, dh(),    84)
    # Bar 4: answer — G5 F5 E5 C5
    mel(sb+3, 2, 1, 79, e_off(), 70)
    mel(sb+3, 3, 0, 77, e_on(),  66)
    mel(sb+3, 3, 1, 76, e_off(), 70)
    mel(sb+3, 4, 0, 72, h(),     73)
    # Bar 5: ornament — A4 pickup, C5 D5 E5 F5 A5 leap
    mel(sb+4, 1, 1, 69, e_off(), 68)
    mel(sb+4, 2, 0, 72, q(),     78)
    mel(sb+4, 3, 0, 74, e_on(),  72)
    mel(sb+4, 3, 1, 76, e_off(), 76)
    mel(sb+4, 4, 0, 81, q(),     82)
    # Bar 6: G5 F5 E5 D5 long [rest]
    mel(sb+5, 1, 0, 79, q(),     80)
    mel(sb+5, 1, 1, 77, e_off(), 72)
    mel(sb+5, 2, 0, 76, e_on(),  68)
    mel(sb+5, 3, 0, 74, h(),     75)
    # Bar 7: turnaround — C5 D5 E5 G5, F5 off-beat
    mel(sb+6, 1, 0, 72, q(),     76)
    mel(sb+6, 2, 0, 74, e_on(),  70)
    mel(sb+6, 2, 1, 76, e_off(), 74)
    mel(sb+6, 3, 0, 79, q(),     80)
    mel(sb+6, 4, 1, 77, e_off(), 68)
    # Bar 8: turnaround tail — E5 D5 C5 [D5 E5 anticipation]
    mel(sb+7, 1, 0, 76, e_on(),  75)
    mel(sb+7, 1, 1, 74, e_off(), 70)
    mel(sb+7, 2, 0, 72, q(),     78)
    mel(sb+7, 3, 1, 74, e_off(), 72)
    mel(sb+7, 4, 0, 76, q(),     80)

def melody_A2(sb):
    """Second A — more ornamented, faster rhythm, extra passing tones."""
    # Bar 1: motif compressed — two 8ths then F5 G5 A5 arriving
    mel(sb,   1, 0, 72, e_on(),  80)
    mel(sb,   1, 1, 74, e_off(), 74)
    mel(sb,   2, 0, 77, e_on(),  72)
    mel(sb,   2, 1, 79, e_off(), 76)
    mel(sb,   3, 0, 81, q(),     85)
    mel(sb,   3, 1, 79, e_off(), 78)
    mel(sb,   4, 0, 77, h(),     75)
    # Bar 2:
    mel(sb+1, 2, 0, 76, e_on(),  70)
    mel(sb+1, 2, 1, 74, e_off(), 66)
    mel(sb+1, 3, 0, 72, q(),     72)
    mel(sb+1, 4, 0, 69, q(),     70)
    # Bar 3: same shape but add B5 passing tone
    mel(sb+2, 1, 0, 74, q(),     78)
    mel(sb+2, 2, 0, 76, e_on(),  72)
    mel(sb+2, 2, 1, 79, e_off(), 68)
    mel(sb+2, 3, 0, 81, q(),     82)
    mel(sb+2, 3, 1, 83, e_off(), 74)
    mel(sb+2, 4, 0, 81, q(),     78)
    # Bar 4:
    mel(sb+3, 1, 1, 79, e_off(), 72)
    mel(sb+3, 2, 0, 77, e_on(),  68)
    mel(sb+3, 3, 0, 76, q(),     72)
    mel(sb+3, 4, 0, 72, h(),     76)
    # Bar 5: descent from G5
    mel(sb+4, 1, 0, 79, q(),     82)
    mel(sb+4, 1, 1, 77, e_off(), 76)
    mel(sb+4, 2, 0, 76, q(),     72)
    mel(sb+4, 3, 0, 74, e_on(),  70)
    mel(sb+4, 3, 1, 72, e_off(), 74)
    mel(sb+4, 4, 0, 69, q(),     68)
    # Bar 6: climb back C5→F5 long
    mel(sb+5, 1, 0, 72, e_on(),  76)
    mel(sb+5, 1, 1, 74, e_off(), 72)
    mel(sb+5, 2, 0, 76, e_on(),  78)
    mel(sb+5, 3, 0, 77, dh(),    80)
    # Bar 7-8: same turnaround as A1
    mel(sb+6, 1, 0, 72, q(),     76)
    mel(sb+6, 2, 0, 74, e_on(),  70)
    mel(sb+6, 2, 1, 76, e_off(), 74)
    mel(sb+6, 3, 0, 79, q(),     80)
    mel(sb+6, 4, 1, 77, e_off(), 68)
    mel(sb+7, 1, 0, 76, e_on(),  75)
    mel(sb+7, 1, 1, 74, e_off(), 70)
    mel(sb+7, 2, 0, 72, q(),     78)
    mel(sb+7, 3, 1, 74, e_off(), 72)
    mel(sb+7, 4, 0, 76, q(),     80)

def melody_B(sb):
    """B section — modulates to Bb/Dm, develops motif at C6 peak."""
    # Bar 17-18: Bbmaj7 — motif transposed: F5 G5 Bb5 C6 (new peak!)
    mel(sb,   1, 0, 77, q(),     82)
    mel(sb,   2, 0, 79, e_on(),  76)
    mel(sb,   2, 1, 82, e_off(), 70)
    mel(sb,   3, 0, 84, dh(),    85)      # C6 — peak of whole piece
    mel(sb+1, 2, 1, 82, e_off(), 72)
    mel(sb+1, 3, 0, 79, e_on(),  70)
    mel(sb+1, 3, 1, 77, e_off(), 74)
    mel(sb+1, 4, 0, 76, h(),     75)
    # Bar 19-20: Gm7→C7 — spinning sequence down
    mel(sb+2, 1, 0, 74, q(),     78)
    mel(sb+2, 1, 1, 76, e_off(), 72)
    mel(sb+2, 2, 0, 77, e_on(),  74)
    mel(sb+2, 3, 0, 79, q(),     80)
    mel(sb+2, 4, 0, 77, q(),     75)
    mel(sb+3, 1, 0, 76, e_on(),  70)
    mel(sb+3, 1, 1, 74, e_off(), 68)
    mel(sb+3, 2, 0, 72, q(),     76)
    mel(sb+3, 3, 0, 74, h(),     72)
    # Bar 21-22: Dm7→Am7 — minor colour, melodic tension
    mel(sb+4, 1, 0, 77, q(),     80)
    mel(sb+4, 2, 0, 76, e_on(),  74)
    mel(sb+4, 2, 1, 74, e_off(), 68)
    mel(sb+4, 3, 0, 72, q(),     78)
    mel(sb+4, 4, 1, 69, e_off(), 70)
    mel(sb+5, 1, 0, 72, e_on(),  76)
    mel(sb+5, 1, 1, 74, e_off(), 74)
    mel(sb+5, 2, 0, 76, q(),     80)
    mel(sb+5, 3, 0, 79, q(),     82)
    mel(sb+5, 4, 0, 81, q(),     78)
    # Bar 23-24: Gm7→C7sus4 — settle and prepare return to A
    mel(sb+6, 1, 0, 79, q(),     80)
    mel(sb+6, 1, 1, 77, e_off(), 74)
    mel(sb+6, 2, 0, 76, q(),     70)
    mel(sb+6, 3, 0, 74, e_on(),  72)
    mel(sb+6, 3, 1, 72, e_off(), 76)
    mel(sb+6, 4, 0, 74, q(),     78)
    mel(sb+7, 1, 0, 76, e_on(),  75)
    mel(sb+7, 1, 1, 74, e_off(), 70)
    mel(sb+7, 2, 0, 72, q(),     78)
    mel(sb+7, 3, 1, 74, e_off(), 72)
    mel(sb+7, 4, 0, 76, q(),     80)

# ---------------------------------------------------------------------------
# WALKING BASS (Acoustic Bass, ch 2)
# Roots + passing tones, mostly quarters with 8th swing embellishment
# ---------------------------------------------------------------------------
def bn(bar, beat, sub, note, dur, vel=72):
    add(T(bar, beat, sub), 2, note, vel, dur)

def bass_A(sb):
    # Bar 1: Fmaj7 — F walking up
    bn(sb,   1, 0, 41, q(),   75)   # F2
    bn(sb,   2, 0, 45, q(),   68)   # A2
    bn(sb,   3, 0, 48, q(),   72)   # C3
    bn(sb,   4, 0, 50, q(),   66)   # D3 passing
    # Bar 2: Fmaj7 — approach Gm7
    bn(sb+1, 1, 0, 52, q(),   70)   # E3
    bn(sb+1, 2, 0, 53, q(),   74)   # F3
    bn(sb+1, 3, 0, 50, q(),   68)   # D3
    bn(sb+1, 4, 0, 48, e_on(),65)   # C3 swing
    bn(sb+1, 4, 1, 46, e_off(),62)  # Bb2 chromatic approach
    # Bar 3: Gm7
    bn(sb+2, 1, 0, 43, q(),   75)   # G2
    bn(sb+2, 2, 0, 46, q(),   68)   # Bb2
    bn(sb+2, 3, 0, 50, q(),   72)   # D3
    bn(sb+2, 4, 0, 52, q(),   66)   # E3 chromatic approach
    # Bar 4: C7
    bn(sb+3, 1, 0, 48, q(),   78)   # C3
    bn(sb+3, 2, 0, 52, q(),   68)   # E3
    bn(sb+3, 3, 0, 55, q(),   72)   # G3
    bn(sb+3, 4, 0, 46, q(),   66)   # Bb2 b7
    # Bar 5: Am7
    bn(sb+4, 1, 0, 45, q(),   75)   # A2
    bn(sb+4, 2, 0, 48, q(),   68)   # C3
    bn(sb+4, 3, 0, 52, q(),   72)   # E3
    bn(sb+4, 4, 0, 50, q(),   66)   # D3 passing to Dm
    # Bar 6: Dm7
    bn(sb+5, 1, 0, 38, q(),   78)   # D2
    bn(sb+5, 2, 0, 41, q(),   68)   # F2
    bn(sb+5, 3, 0, 45, q(),   72)   # A2
    bn(sb+5, 4, 0, 43, q(),   65)   # G2 passing
    # Bar 7: Gm9
    bn(sb+6, 1, 0, 43, q(),   75)   # G2
    bn(sb+6, 2, 0, 46, q(),   68)   # Bb2
    bn(sb+6, 3, 0, 50, q(),   72)   # D3
    bn(sb+6, 4, 0, 47, q(),   66)   # B2 chromatic approach
    # Bar 8: C7sus4 → C7 turnaround
    bn(sb+7, 1, 0, 48, q(),   78)   # C3
    bn(sb+7, 2, 0, 52, q(),   70)   # E3
    bn(sb+7, 3, 0, 55, q(),   72)   # G3
    bn(sb+7, 4, 0, 46, e_on(), 68)  # Bb2 swing
    bn(sb+7, 4, 1, 45, e_off(),64)  # A2 voice lead to F

def bass_B(sb):
    # Bar 17-18: Bbmaj7
    bn(sb,   1, 0, 46, q(),   75)   # Bb2
    bn(sb,   2, 0, 50, q(),   68)   # D3
    bn(sb,   3, 0, 53, q(),   72)   # F3
    bn(sb,   4, 0, 52, q(),   66)   # E3 chromatic
    bn(sb+1, 1, 0, 53, q(),   72)   # F3
    bn(sb+1, 2, 0, 50, q(),   68)   # D3
    bn(sb+1, 3, 0, 48, q(),   70)   # C3
    bn(sb+1, 4, 0, 46, q(),   65)   # Bb2
    # Bar 19-20: Gm7 → C7
    bn(sb+2, 1, 0, 43, q(),   75)
    bn(sb+2, 2, 0, 46, q(),   68)
    bn(sb+2, 3, 0, 50, q(),   72)
    bn(sb+2, 4, 0, 47, q(),   65)   # B2 chromatic
    bn(sb+3, 1, 0, 48, q(),   78)   # C3
    bn(sb+3, 2, 0, 52, q(),   70)
    bn(sb+3, 3, 0, 55, q(),   72)
    bn(sb+3, 4, 0, 50, q(),   66)   # D3
    # Bar 21-22: Dm7 → Am7
    bn(sb+4, 1, 0, 38, q(),   78)   # D2
    bn(sb+4, 2, 0, 41, q(),   68)   # F2
    bn(sb+4, 3, 0, 45, q(),   72)   # A2
    bn(sb+4, 4, 0, 48, q(),   65)   # C3 passing up
    bn(sb+5, 1, 0, 45, q(),   75)   # A2
    bn(sb+5, 2, 0, 48, q(),   68)   # C3
    bn(sb+5, 3, 0, 52, q(),   72)   # E3
    bn(sb+5, 4, 0, 50, q(),   66)   # D3
    # Bar 23-24: Gm7 → C7sus4 turnaround
    bn(sb+6, 1, 0, 43, q(),   75)
    bn(sb+6, 2, 0, 46, q(),   68)
    bn(sb+6, 3, 0, 50, q(),   72)
    bn(sb+6, 4, 0, 47, q(),   65)
    bn(sb+7, 1, 0, 48, q(),   78)
    bn(sb+7, 2, 0, 52, q(),   70)
    bn(sb+7, 3, 0, 55, q(),   72)
    bn(sb+7, 4, 0, 46, e_on(), 68)
    bn(sb+7, 4, 1, 45, e_off(),64)

# ---------------------------------------------------------------------------
# PERCUSSION (ch 9, GM)
# GM: 35=Kick, 37=Snare Rim, 38=Snare, 42=Closed HH, 46=Open HH
# Sparse jazz brush feel: hi-hat on 2 & 4, off-beat 8ths, occasional snare rim
# ---------------------------------------------------------------------------
def perc(bar, beat, sub, note, vel):
    add(T(bar, beat, sub), 9, note, vel, 40)

def drums_A(sb):
    for off in range(8):
        b = sb + off
        # Hi-hat on beats 2 and 4
        perc(b, 2, 0, 42, human_vel(50, 8))
        perc(b, 4, 0, 42, human_vel(50, 8))
        # Off-beat hi-hat (and of 1, and of 3) on even bars
        if off % 2 == 0:
            perc(b, 1, 1, 42, human_vel(38, 6))
            perc(b, 3, 1, 42, human_vel(38, 6))
        # Snare rim on beat 3 of odd bars
        if off % 2 == 1:
            perc(b, 3, 0, 37, human_vel(45, 8))
        # Soft snare brush on 2-and occasionally
        if off in [1, 3, 5, 7]:
            perc(b, 2, 1, 38, human_vel(35, 6))
    # Soft kick on bar 1 and bar 5 only
    perc(sb,   1, 0, 35, human_vel(52, 6))
    perc(sb+4, 1, 0, 35, human_vel(48, 6))

def drums_B(sb):
    for off in range(8):
        b = sb + off
        perc(b, 2, 0, 42, human_vel(55, 8))
        perc(b, 4, 0, 42, human_vel(55, 8))
        perc(b, 1, 1, 42, human_vel(40, 6))
        perc(b, 3, 1, 42, human_vel(40, 6))
        if off % 2 == 0:
            perc(b, 3, 0, 37, human_vel(50, 8))
        else:
            perc(b, 2, 1, 38, human_vel(42, 6))
            perc(b, 4, 1, 42, human_vel(35, 5))
    perc(sb,   1, 0, 35, human_vel(55, 5))
    perc(sb+4, 1, 0, 35, human_vel(48, 5))

# ---------------------------------------------------------------------------
# BUILD ALL SECTIONS  — A A B A
# A1: bars 1-8    sb=1
# A2: bars 9-16   sb=9
# B:  bars 17-24  sb=17
# A3: bars 25-32  sb=25
# ---------------------------------------------------------------------------
comp_A(1)
comp_A(9,  intensity=0.95)
comp_B(17)
comp_A(25, intensity=1.0)

melody_A1(1)
melody_A2(9)
melody_B(17)
melody_A1(25)

bass_A(1)
bass_A(9)
bass_B(17)
bass_A(25)

drums_A(1)
drums_A(9)
drums_B(17)
drums_A(25)

# ---------------------------------------------------------------------------
# SELF-REVIEW PASS
# ---------------------------------------------------------------------------
melody_notes = [n for (s, ch, n, v, d) in events if ch == 0]
print("=== SELF-REVIEW ===")
print(f"Melody MIDI range: {min(melody_notes)} – {max(melody_notes)}")
print(f"  A4=69  C5=72  C6=84  →  in whistleable range: {69 <= min(melody_notes) and max(melody_notes) <= 84}")

# Check rests
mel_sorted = sorted([(s, s+d) for (s, ch, n, v, d) in events if ch == 0], key=lambda x: x[0])
gaps = [mel_sorted[i][0] - mel_sorted[i-1][1] for i in range(1, len(mel_sorted))
        if mel_sorted[i][0] - mel_sorted[i-1][1] > 0]
print(f"Rests: {len(gaps)} gaps, avg {int(sum(gaps)/len(gaps))} ticks, max {max(gaps)} ticks (480=quarter)")

# Register collision: bass should stay below C3(48), melody above C5(72), comp middle
bass_notes = [n for (s, ch, n, v, d) in events if ch == 2]
comp_notes  = [n for (s, ch, n, v, d) in events if ch == 1]
print(f"Bass range:   {min(bass_notes)}–{max(bass_notes)}  (target ≤60)")
print(f"Comp range:   {min(comp_notes)}–{max(comp_notes)}  (target 48–72)")
print(f"Melody range: {min(melody_notes)}–{max(melody_notes)}  (target ≥69)")
collision = max(bass_notes) >= min(comp_notes)
print(f"Bass/comp collision: {collision}")
print()
print("Chord progression:")
print("  A (×3): Fmaj7 | Fmaj7 | Gm7 | C7 | Am7 | Dm7 | Gm9 | C7sus4–C7")
print("  B:      Bbmaj7 | Bbmaj7 | Gm7 | C7 | Dm7 | Am7 | Gm7 | C7sus4")
print()
print("Motif: C5(q) D5(e) F5(e) G5(dh.) — bar 2 answer: E5 D5 C5 A4(h) + rest")

# ---------------------------------------------------------------------------
# WRITE MIDI
# ---------------------------------------------------------------------------
mid = MidiFile(ticks_per_beat=TPB)

tempo_track = MidiTrack()
mid.tracks.append(tempo_track)
tempo_track.append(MetaMessage('set_tempo', tempo=TEMPO, time=0))
tempo_track.append(MetaMessage('time_signature', numerator=4, denominator=4,
                               clocks_per_click=24, notated_32nd_notes_per_beat=8, time=0))

track_names = ["Ocarina Lead", "Vibraphone Comp", "Acoustic Bass", "Drums"]
channels    = [0, 1, 2, 9]
programs    = [79, 11, 32, 0]

tracks = []
for name, ch, prog in zip(track_names, channels, programs):
    t = MidiTrack()
    mid.tracks.append(t)
    t.append(MetaMessage('track_name', name=name, time=0))
    if ch != 9:
        t.append(Message('control_change', channel=ch, control=7,  value=95, time=0))
        t.append(Message('control_change', channel=ch, control=11, value=100, time=0))
        t.append(Message('program_change', channel=ch, program=prog, time=0))
    else:
        t.append(Message('control_change', channel=9, control=7,  value=80, time=0))
    tracks.append((ch, t))

chan_events = defaultdict(list)
for (start, ch, note, vel, dur) in events:
    chan_events[ch].append((start, note, vel, dur))

for ch, t in tracks:
    ch_evs = sorted(chan_events[ch], key=lambda x: x[0])
    abs_msgs = []
    for (start, note, vel, dur) in ch_evs:
        abs_msgs.append((start,       'note_on',  note, vel))
        abs_msgs.append((start + dur, 'note_off', note, 0))
    abs_msgs.sort(key=lambda x: (x[0], 0 if x[1] == 'note_off' else 1))
    cursor = 0
    for (tick, mtype, note, vel) in abs_msgs:
        delta = max(0, tick - cursor)
        t.append(Message(mtype, channel=ch, note=note, velocity=vel, time=delta))
        cursor = tick
    t.append(MetaMessage('end_of_track', time=0))

out_midi = "/Users/nahuelgavilan/gacha-zoo/src-music/gacha_zoo_loop.mid"
mid.save(out_midi)

total_ticks = 32 * 4 * 480
expected_s  = total_ticks / (TPB * BPM / 60)
print(f"\nMIDI saved: {out_midi}")
print(f"Expected duration: {expected_s:.2f}s  ({32} bars at {BPM} BPM)")
