#!/usr/bin/env python3
"""
render_pages.py — wood-44 / milestone M3 (copyright-safe public content)

Renders ONLY the exact method-book / Real-Book pages that the Woodshed app
(index.html) actually embeds in exercises, as ~150 DPI PNG images, and writes
a manifest (page-manifest.json) describing each one.

POLICY (locked in M0): the public POC may show the EXACT pages used in
exercises rendered as page images. The full source PDFs are NEVER shipped.
This script reads the page references out of index.html so the rendered set
stays in sync with what the app shows. Source PDFs are read-only inputs and
are never copied into public-assets/.

Sources & page indexing:
  - Real Book      (RB_OFFSET = -1):  pdfPage = printedPage - 1
  - Technical Studies (Clarke):       the `pdf:` numbers are PDF page indices
  - Cichowicz:                        the `pdf:` numbers are PDF page indices

Regenerate:
    cd "Projects/Trumpet"
    python3 public-assets/render_pages.py
Requires /usr/bin/pdftoppm (poppler-utils).
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                 # Projects/Trumpet
PAGES_DIR = os.path.join(HERE, "pages")
DPI = 150

RB_PDF    = os.path.join(ROOT, "Real Book.pdf")
CLARKE_PDF= os.path.join(ROOT, "Technical Studies.pdf")
CICH_PDF  = os.path.join(ROOT, "Cichowicz.pdf")
RB_OFFSET = -1   # pdfPage = printedPage + RB_OFFSET

# --- The 24 tunes actually wired into the app (TUNES table in index.html).
#     id, title, printedPage, and any page2 (a second printed page some tunes use).
TUNES = [
    ("blues",       "Straight No Chaser",            386, ("Au Privave (Bird head)", 37)),
    ("autumn",      "Autumn Leaves",                  39, None),
    ("bossa",       "Blue Bossa",                     50, None),
    ("atrain",      'Take the "A" Train',            398, None),
    ("attya",       "All The Things You Are",         22, None),
    ("four",        "Four",                          149, None),
    ("beautiful",   "Beautiful Love",                 40, None),
    ("solar",       "Solar",                         363, None),
    ("twnbay",      "There Will Never Be Another You",407, None),
    ("oleo",        "Oleo (Rhythm Changes)",         309, None),
    ("father",      "Song for My Father",            373, None),
    ("footprints",  "Footprints",                    144, None),
    ("cherokee",    "Cherokee",                       77, None),
    ("confirmation","Confirmation",                   87, None),
    ("misty",       "Misty",                         277, None),
    ("stella",      "Stella by Starlight",           382, None),
    ("tingl",       "There Is No Greater Love",      406, None),
    ("tunisia",     "A Night in Tunisia",            302, None),
    ("ornithology", "Ornithology",                   317, None),
    ("missjones",   "Have You Met Miss Jones?",      172, None),
    ("nowhere",     "Out of Nowhere",                318, None),
    ("valentine",   "My Funny Valentine",            287, None),
    ("recordame",   "Recorda Me",                    337, None),
    ("bessies",     "Bessie's Blues (Eb blues)",      42, None),
    # --- wood-77 (M2): coverage gaps closed. Each printedPage was visually
    #     verified against the Real Book PDF page (printedPage-1) before adding.
    ("allblues",    "All Blues",                      18, None),
    ("allofme",     "All of Me",                      20, None),
    ("blacknile",   "Black Nile",                     48, None),
    ("bluemonk",    "Blue Monk",                      52, None),
    ("bfalice",     "Blues for Alice",                55, None),
    ("cottontail",  "Cotton Tail",                    90, None),
    ("daahoud",     "Daahoud",                        96, None),
    ("donnalee",    "Donna Lee",                     123, None),
    ("freddie",     "Freddie Freeloader",            151, None),
    ("ipanema",     "The Girl from Ipanema",         158, None),
    ("joyspring",   "Joy Spring",                    229, None),
    ("ladybird",    "Lady Bird",                     235, None),
    ("sowhat",      "So What",                       364, None),
]

# --- Clarke (Technical Studies) sections. pdf: numbers are PDF page indices.
#     Second Study spans pages [6,7]; the rest are single pages.
CLARKE_SECTIONS = [
    ("First Study (sotto voce!)", [3],   False),
    ("Etude I",                   [5],   False),
    ("Second Study",              [6,7], False),
    ("Third Study",               [8],   False),
    ("Fourth Study",              [12],  True),   # approx flag in source
    ("Fifth Study",               [17],  True),   # approx flag in source
]

# --- Cichowicz long-tone groups. pdf: numbers are PDF page indices.
#     Warm-up card default = Group D (pdf 14). The inline pager exposes the
#     reachable range CICH_LO..CICH_HI = pdf 11..17 (Groups A..G). "Set 2"
#     (pdf 21) lives in CICH_SECTIONS / config picker but is NOT reachable in
#     the warm-up pager, so it is flagged confirm rather than treated as used.
CICH_SECTIONS = [
    ("Long Tones - Group A", 11, "reachable"),
    ("Group B",              12, "reachable"),
    ("Group C",              13, "reachable"),
    ("Group D",              14, "default"),    # warm-up default group
    ("Group E",              15, "reachable"),
    ("Group F",              16, "reachable"),
    ("Group G",              17, "reachable"),
    ("Set 2 - Groups A-G",   21, "picker-only"),# confirm: not in warm-up pager
]


def slug(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def render(pdf_path, pdf_page, out_base):
    """Render one PDF page to PAGES_DIR/<out_base>.png at DPI. Returns path.

    Idempotent: if the target PNG already exists and is non-empty, reuse it
    instead of re-invoking pdftoppm. The render of a fixed PDF page at a fixed
    DPI is deterministic, so this changes nothing about the output — it only
    keeps a full regenerate fast enough to complete the manifest write on a
    large (73MB) source PDF. Delete a page file to force a fresh render.
    """
    out_prefix = os.path.join(PAGES_DIR, out_base)
    out_png = out_prefix + ".png"
    if os.path.isfile(out_png) and os.path.getsize(out_png) > 0:
        return out_png
    subprocess.run(
        ["/usr/bin/pdftoppm", "-png", "-r", str(DPI),
         "-f", str(pdf_page), "-l", str(pdf_page),
         "-singlefile", pdf_path, out_prefix],
        check=True,
    )
    return out_prefix + ".png"


def rel(p):
    return os.path.relpath(p, HERE)


def main():
    os.makedirs(PAGES_DIR, exist_ok=True)
    manifest = []

    # Real Book tunes
    for tid, title, printed, page2 in TUNES:
        pdf_page = printed + RB_OFFSET
        out = f"realbook-p{printed}-{slug(title)}"
        img = render(RB_PDF, pdf_page, out)
        manifest.append({
            "id": tid, "title": title, "source": "Real Book.pdf",
            "printedPage": printed, "pdfPage": pdf_page,
            "image": rel(img), "note": "pdfPage = printedPage - 1 (RB_OFFSET)",
        })
        if page2:
            p2label, p2printed = page2
            p2pdf = p2printed + RB_OFFSET
            out2 = f"realbook-p{p2printed}-{slug(p2label)}"
            img2 = render(RB_PDF, p2pdf, out2)
            manifest.append({
                "id": tid + "-page2", "title": f"{title} - {p2label}",
                "source": "Real Book.pdf", "printedPage": p2printed,
                "pdfPage": p2pdf, "image": rel(img2),
                "note": "secondary page2 reference for this tune",
            })

    # Clarke / Technical Studies
    for name, pages, approx in CLARKE_SECTIONS:
        for pg in pages:
            out = f"clarke-pdf{pg}-{slug(name)}"
            img = render(CLARKE_PDF, pg, out)
            entry = {
                "id": "clarke-" + slug(name), "title": "Clarke - " + name,
                "source": "Technical Studies.pdf", "printedPage": None,
                "pdfPage": pg, "image": rel(img),
                "note": "Clarke pdf: index is the PDF page directly",
            }
            if approx:
                entry["confirm"] = "source marks this section page as approx:true"
            manifest.append(entry)

    # Cichowicz
    for name, pg, status in CICH_SECTIONS:
        out = f"cichowicz-pdf{pg}-{slug(name)}"
        img = render(CICH_PDF, pg, out)
        entry = {
            "id": "cichowicz-" + slug(name), "title": "Cichowicz - " + name,
            "source": "Cichowicz.pdf", "printedPage": None,
            "pdfPage": pg, "image": rel(img),
            "note": "Cichowicz pdf: index is the PDF page directly; "
                    "warm-up default = Group D" if status == "default"
                    else "Cichowicz pdf: index is the PDF page directly",
        }
        if status == "picker-only":
            entry["confirm"] = ("Set 2 appears in config picker but is NOT "
                                "reachable in the warm-up inline pager "
                                "(capped at pdf 17); rendered for completeness")
        if status == "default":
            entry["default"] = True
        manifest.append(entry)

    out_path = os.path.join(HERE, "page-manifest.json")
    with open(out_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"Wrote {len(manifest)} entries -> {out_path}")
    print(f"Rendered images -> {PAGES_DIR}")


if __name__ == "__main__":
    main()
