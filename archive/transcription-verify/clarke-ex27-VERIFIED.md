# Clarke Second Study — Exercise 27 · VERIFIED (Chris-transcribed)

**Source:** `Technical Studies.pdf` p.8 · **Key:** G major (1 sharp, every F = F♯) · **Meter:** cut time (2/2) · **Rhythm:** all eighth notes except the final G (held) · **Register:** low, below the staff.

Ground truth transcribed by Chris from the book; my render of it matches the source ledger-line depth bar for bar.

## The notes (written pitch)

| Bar | Notes |
|---|---|
| 1 | G A B G A B C A |
| 2 | B C D B G A B G |
| 3 | A B C A F♯ G A F♯ |
| 4 | G B A G A C B A |
| end | G (held) |

Scale-degree view (G major) — confirms it's a clean Clarke sequence: `1 2 3 1 2 3 4 2 | 3 4 5 3 1 2 3 1 | 2 3 4 2 7 1 2 7 | 1 3 2 1 2 4 3 2 | 1`.

## ABC (saved as `clarke-ex27.abc`)

```
X:1
T:Clarke Technical Studies - Second Study, Ex. 27
M:2/2
L:1/8
Q:"half=80-120"
K:G
(G, A, B, G, A, B, C A, | B, C D B, G, A, B, G, |
 A, B, C A, F, G, A, F, | G, B, A, G, A, C B, A,) :|
G,8 |]
```

Render: `clarke-ex27-render.png` · Side-by-side vs source: `clarke-ex27-compare.png`.

## Woodshed warmup entry

```js
window.USER_CHARTS=(window.USER_CHARTS||[]).concat([{
  id:'clarke-2-ex27',
  title:'Clarke Second Study — Ex. 27',
  source:'Clarke Technical Studies (PD)',
  kind:'warmup', style:'etude', bpm:100, bars:[],
  abc:`X:1\nT:Clarke Second Study Ex.27\nM:2/2\nL:1/8\nK:G\n(G, A, B, G, A, B, C A, | B, C D B, G, A, B, G, | A, B, C A, F, G, A, F, | G, B, A, G, A, C B, A,) :|\nG,8 |]`
}]);
```
