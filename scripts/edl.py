"""Edit decision list for Raw_Cinematic_Broll_9x16.mp4 — single source of truth.

All times are seconds on the source timeline (the narration is never retimed).
Word anchors come from Parakeet-TDT token timestamps and the 40 ms energy envelope
(see work/transcript/ and deliverables/transcript.md).
"""

FPS = 30
W, H = 1080, 1920
SRC_DUR = 18.999          # source duration (s)
TAIL = 0.5                # held last frame + fade to black after the narration ends
OUT_DUR = 19.5            # = 585 frames

FACE = (560, 640)         # punch-in anchor (face/upper chest) in source pixels

# ---------------------------------------------------------------------------
# Visual timeline. kind: "speaker" (original footage, digital reframe) or a
# motion-graphics scene rendered over a blurred, darkened plate of the speaker.
# zoom = (start, end) scale of the reframe; trans_in = (type, seconds).
SEGMENTS = [
    dict(id="V1", start=0.00, end=3.20, kind="speaker", zoom=(1.00, 1.06), trans_in=None,
         spoken="Har cheez ke liye alag-alag subscription lena kaafi expensive ho gaya hai.",
         meaning="Hook: the problem statement — keep her face and delivery on screen.",
         move="Slow eased push-in 1.00→1.06 toward the face"),
    dict(id="G1", start=3.20, end=7.68, kind="mg_ai_stack", trans_in=("blur", 0.30),
         spoken="ChatGPT Plus, Claude, Gemini ya Canva Pro — sabka cost jodte-jodte",
         meaning="The list of separate AI subscriptions; then the cost piling up.",
         move="Cards slide in on each spoken name (3.28 / 4.24 / 4.80 / 5.52); at 6.25 they "
              "collapse into a stacked pile and a gold meter fills on 'cost jodte-jodte' (6.72–7.60)"),
    dict(id="V2", start=7.68, end=9.50, kind="speaker", zoom=(1.12, 1.14), trans_in=("dissolve", 0.20),
         spoken="kaafi zyada ho jaata hai. … [unclear ~8.9–9.48]",
         meaning="Emotional emphasis — return to her expression. Cut sits on the 7.68 s inter-word gap.",
         move="Medium close-up punch-in 1.12, near-static drift"),
    dict(id="G2", start=9.50, end=12.30, kind="mg_stream_grid", trans_in=("blur", 0.30),
         spoken="ChatGPT aur Netflix, Prime aur Crunchyroll jaisi",
         meaning="The premium subscriptions she lists, shown as a 2×2 grid.",
         move="Tiles pop in on each name (9.52 / 10.40 / 10.96 / 11.44); slow group push 1.00→1.03"),
    dict(id="V3", start=12.30, end=14.74, kind="speaker", zoom=(1.03, 1.09), trans_in=("dissolve", 0.20),
         spoken="premium subscription wahaan discounted rates advertised hain.",
         meaning="Key claim delivered by the speaker; a gold price-tag-with-down-arrow icon marks 'discounted rates'.",
         move="Slow push-in 1.03→1.09; tag icon pops in at 13.44 over the dark wall slats (top-right)"),
    dict(id="G3", start=14.74, end=16.86, kind="mg_one_place", trans_in=("blur", 0.25),
         spoken="Isliye options ek jagah check karna aasaan ho jaata hai,",
         meaning="'Options in one place': scattered chips gather into one panel; ticks on 'check'.",
         move="Chips converge 14.80–15.55 into one gold-outlined panel; check marks cascade from 15.68"),
    dict(id="V4", start=16.86, end=19.50, kind="speaker", zoom=(1.02, 1.08), trans_in=("dissolve", 0.20),
         spoken="jahaan aapke paise bachte hain. … [unclear, cut off at 18.93]",
         meaning="Payoff line on the speaker. Last source frame is held 0.5 s and faded to black.",
         move="Slow push-in 1.02→1.08; fade to black 19.00→19.50"),
]

# Brand names exactly as spoken; rendered as plain typography (no logos).
AI_CARDS = [("ChatGPT Plus", 3.28), ("Claude", 4.24), ("Gemini", 4.80), ("Canva Pro", 5.52)]
STREAM_TILES = [("ChatGPT", 9.52), ("Netflix", 10.40), ("Prime", 10.96), ("Crunchyroll", 11.44)]
ONE_PLACE = ["ChatGPT Plus", "Claude", "Gemini", "Canva Pro", "Netflix", "Prime", "Crunchyroll"]
STACK_AT, COST_AT, JODTE_AT = 6.25, 6.72, (7.36, 7.60)
TAG_AT = 13.44
GATHER_AT, CHECK_AT = 14.80, 15.68

# ---------------------------------------------------------------------------
# Captions: exact spoken words (romanised Hinglish), phrase groups between word
# boundaries. Highlight = (word, time or None). A time means the word turns gold
# when it is spoken (anchored on a Parakeet token); None = gold for the phrase.
CAPTIONS = [
    (0.10, 1.24, "Har cheez ke liye alag-alag", []),
    (1.24, 2.12, "subscription lena", []),
    (2.12, 3.20, "kaafi expensive ho gaya hai.", [("expensive", 2.32)]),
    (3.24, 4.20, "ChatGPT Plus,", []),
    (4.20, 5.48, "Claude, Gemini ya", []),
    (5.48, 6.18, "Canva Pro —", []),
    (6.18, 7.68, "sabka cost jodte-jodte", [("cost", 6.72)]),
    (7.68, 8.72, "kaafi zyada ho jaata hai.", [("zyada", None)]),
    # 8.90–9.48 unclear fragment: intentionally not captioned
    (9.50, 10.92, "ChatGPT aur Netflix,", []),
    (10.92, 12.28, "Prime aur Crunchyroll jaisi", []),
    (12.30, 13.42, "premium subscription wahaan", []),
    (13.42, 14.74, "discounted rates advertised hain.", [("discounted", 13.44), ("rates", 13.84)]),
    (14.76, 15.64, "Isliye options ek jagah", [("ek", None), ("jagah", None)]),
    (15.64, 16.74, "check karna aasaan ho jaata hai,", [("aasaan", None)]),
    (16.96, 18.16, "jahaan aapke paise bachte hain.", [("paise", None), ("bachte", None)]),
    # 18.25–18.93 unclear and cut off by the source: intentionally not captioned
]

# ---------------------------------------------------------------------------
# Sound design cues (all synthesised locally in scripts/audio.py).
SFX = [
    ("impact_soft", 2.30, -27, "Low, soft thump under 'expensive'"),
    ("whoosh", 3.02, -26, "Into the AI-tools graphic (peaks on the 3.20 cut)"),
    ("tick", 3.28, -36, "Card 1"), ("tick", 4.24, -37, "Card 2"),
    ("tick", 4.80, -37, "Card 3"), ("tick", 5.52, -37, "Card 4"),
    ("whoosh", 9.32, -27, "Into the streaming grid"),
    ("chime", 13.44, -31, "Discount tag reveal"),
    ("whoosh_rev", 14.50, -29, "Gather into one place"),
    ("chime", 17.62, -34, "Soft resolve on 'paise bachte'"),
]
