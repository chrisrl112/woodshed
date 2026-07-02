# Real drum loops for the Woodshed band

Drop jazz drum-loop audio files in this folder and the band will play them instead of the
generated/GM kit, tempo-matched to each tune and started on the downbeat. If no file loads,
the band falls back to the synth kit automatically (nothing breaks).

## What makes a good loop
- **Feel:** swing ride-led jazz, brushes or sticks — whatever "classy/sophisticated" means to you.
- **Seamless:** an exact, clean loop of **2 or 4 bars** of 4/4 at a **steady tempo** (so downbeats align).
- **Format:** `.wav`, `.mp3`, or `.ogg` (anything the browser can decode).
- **Tempo coverage:** one loop is tempo-matched via playback speed. Small speed changes sound natural;
  big ones shift the cymbal pitch. So for the full 120–220 range, 2–3 loops at different tempos is ideal
  (e.g. ~130, ~170, ~200) — the engine picks the nearest and trims.

## How to register them
Edit the `DrumLoop.manifest` array in `index.html` (search for `lib/drums/swing.wav`):

```js
manifest:[
  {url:'lib/drums/swing-130.wav', bpm:130},
  {url:'lib/drums/swing-170.wav', bpm:170},
  {url:'lib/drums/swing-200.wav', bpm:200},
],
```

Just tell me the filenames + their real bpm and I'll wire the manifest for you.
