// Single source of truth for the v2 edit: picture segments, captions and the
// sound cue sheet. Times are seconds on the source timeline; the narration is
// never moved or retimed (see deliverables/transcript.md).

export const FPS = 30;
export const W = 1080;
export const H = 1920;
export const SRC_FRAMES = 570; // 18.999 s of source
export const DURATION = 585; // + 0.5 s held-frame fade to black

export const f = (s: number) => Math.round(s * FPS);

export type SegKind = 'aroll' | 'ai_stack' | 'stream_list' | 'one_place';
export type Segment = {
  id: string;
  start: number;
  end: number;
  kind: SegKind;
  zoom?: [number, number]; // A-roll punch-in, start → end
  transIn?: {type: 'blur' | 'dissolve'; dur: number};
};

export const SEGMENTS: Segment[] = [
  {id: 'V1', start: 0, end: 3.2, kind: 'aroll', zoom: [1.0, 1.06]},
  {id: 'G1', start: 3.2, end: 7.68, kind: 'ai_stack', transIn: {type: 'blur', dur: 0.3}},
  {id: 'V2', start: 7.68, end: 9.5, kind: 'aroll', zoom: [1.12, 1.14], transIn: {type: 'dissolve', dur: 0.2}},
  {id: 'G2', start: 9.5, end: 12.3, kind: 'stream_list', transIn: {type: 'blur', dur: 0.3}},
  {id: 'V3', start: 12.3, end: 14.74, kind: 'aroll', zoom: [1.03, 1.09], transIn: {type: 'dissolve', dur: 0.2}},
  {id: 'G3', start: 14.74, end: 16.86, kind: 'one_place', transIn: {type: 'blur', dur: 0.25}},
  {id: 'V4', start: 16.86, end: 19.5, kind: 'aroll', zoom: [1.02, 1.08], transIn: {type: 'dissolve', dur: 0.2}},
];

// Brand names exactly as spoken; drawn as plain type with generic glyphs (no logos).
export const AI_TILES: {name: string; at: number; glyph: 'chat' | 'spark' | 'diamond' | 'brush'}[] = [
  {name: 'ChatGPT Plus', at: 3.28, glyph: 'chat'},
  {name: 'Claude', at: 4.24, glyph: 'spark'},
  {name: 'Gemini', at: 4.8, glyph: 'diamond'},
  {name: 'Canva Pro', at: 5.52, glyph: 'brush'},
];
export const STACK_AT = 6.25;
export const COST_AT = 6.72;
export const JODTE_AT = [7.36, 7.6];

export const STREAM_CARDS: {name: string; at: number; glyph: 'chat' | 'play'}[] = [
  {name: 'ChatGPT', at: 9.52, glyph: 'chat'},
  {name: 'Netflix', at: 10.4, glyph: 'play'},
  {name: 'Prime', at: 10.96, glyph: 'play'},
  {name: 'Crunchyroll', at: 11.44, glyph: 'play'},
];

export const DISCOUNT_AT = 13.44;
export const ONE_PLACE = ['ChatGPT Plus', 'Claude', 'Gemini', 'Canva Pro', 'Netflix', 'Prime', 'Crunchyroll'];
export const GATHER_AT = 14.8;
export const CHECK_AT = 15.68;
export const CHECK_STEP = 0.08;

// PROVISIONAL caption style (brief not supplied yet): sans phrase + one script
// keyword. `script` names the word set in the script face; `at` is when a
// token-timed keyword lights up (null = from caption start).
export type Caption = {start: number; end: number; text: string; script?: string; at?: number | null};
export const CAPTIONS: Caption[] = [
  {start: 0.1, end: 1.24, text: 'Har cheez ke liye alag-alag'},
  {start: 1.24, end: 2.12, text: 'subscription lena'},
  {start: 2.12, end: 3.2, text: 'kaafi expensive ho gaya hai.', script: 'expensive', at: 2.32},
  {start: 3.24, end: 4.2, text: 'ChatGPT Plus,'},
  {start: 4.2, end: 5.48, text: 'Claude, Gemini ya'},
  {start: 5.48, end: 6.18, text: 'Canva Pro —'},
  {start: 6.18, end: 7.68, text: 'sabka cost jodte-jodte', script: 'cost', at: 6.72},
  {start: 7.68, end: 8.72, text: 'kaafi zyada ho jaata hai.', script: 'zyada'},
  // 8.90–9.48 unclear fragment: not captioned
  {start: 9.5, end: 10.92, text: 'ChatGPT aur Netflix,'},
  {start: 10.92, end: 12.28, text: 'Prime aur Crunchyroll jaisi'},
  {start: 12.3, end: 13.42, text: 'premium subscription wahaan'},
  {start: 13.42, end: 14.74, text: 'discounted rates advertised hain.', script: 'discounted', at: 13.44},
  {start: 14.76, end: 15.64, text: 'Isliye options ek jagah', script: 'jagah'},
  {start: 15.64, end: 16.74, text: 'check karna aasaan ho jaata hai,', script: 'aasaan'},
  {start: 16.96, end: 18.16, text: 'jahaan aapke paise bachte hain.', script: 'paise'},
  // 18.25–18.93 unclear and cut off by the source: not captioned
];

// ---------------------------------------------------------------------------
// Sound cue sheet (ue-sound-design passes). `at` is the target time; `align`
// says which point of the sound locks to it: 'peak' = the measured transient /
// loudest point (whooshes on the fastest frame, risers + hits on the transition
// frame), 'start' = file start. Levels are dB relative to the -16 LUFS
// normalised file (scripts/prep_sfx.py).
export type Family = 'WHOOSHES' | 'TEXTURES' | 'RISERS' | 'HITS';
export type Cue = {family: Family; sfx: string; at: number; align: 'peak' | 'start'; db: number; why: string};

const ticks: Cue[] = ONE_PLACE.map((_, i) => ({
  family: 'TEXTURES',
  sfx: 'scifi_click_6',
  at: CHECK_AT + i * CHECK_STEP,
  align: 'peak',
  db: -7,
  why: `Check ${i + 1}/7 (one emphasis per element)`,
}));

export const CUES: Cue[] = [
  // PASS 1 — WHOOSHES: peak on the fastest frame of each movement
  {family: 'WHOOSHES', sfx: 'swipe_right', at: 3.35, align: 'peak', db: -11, why: 'Hook → body blur transition (fastest frame of the 0.30 s ease)'},
  {family: 'WHOOSHES', sfx: 'whoosh_18', at: 6.5, align: 'peak', db: -12, why: 'Tiles slide into the stack (6.25–6.75)'},
  {family: 'WHOOSHES', sfx: 'swoosh_transition', at: 9.65, align: 'peak', db: -11, why: 'A → B transition into the subscription list'},
  {family: 'WHOOSHES', sfx: 'wind_wipe_high', at: 14.87, align: 'peak', db: -11, why: 'A → B transition into "one place"'},
  {family: 'WHOOSHES', sfx: 'eene_5_running_by', at: 15.2, align: 'peak', db: -12, why: 'Chips converge into the panel'},
  // PASS 2 — TEXTURES: on the event frame
  {family: 'TEXTURES', sfx: 'mouth_pop', at: 2.32, align: 'peak', db: -7, why: '"expensive" keyword pops'},
  ...AI_TILES.map((t, i): Cue => ({family: 'TEXTURES', sfx: 'ui_10', at: t.at, align: 'peak', db: -7, why: `AI tile ${i + 1} pops in (${t.name})`})),
  {family: 'TEXTURES', sfx: 'data_04', at: COST_AT, align: 'start', db: -7, why: 'Cost curve writes on'},
  {family: 'TEXTURES', sfx: 'camera_shutter', at: 7.68, align: 'peak', db: -6, why: 'B → A cut to her reaction'},
  ...STREAM_CARDS.map((c, i): Cue => ({family: 'TEXTURES', sfx: 'ui_6', at: c.at, align: 'peak', db: -7, why: `List card ${i + 1} pops in (${c.name})`})),
  {family: 'TEXTURES', sfx: 'camera_shutter', at: 12.3, align: 'peak', db: -6, why: 'B → A cut'},
  {family: 'TEXTURES', sfx: 'swish_boom', at: DISCOUNT_AT, align: 'peak', db: -6, why: 'Discount pill revealed — loudest moment of V3'},
  ...ticks,
  {family: 'TEXTURES', sfx: 'success_bell', at: 17.62, align: 'peak', db: -6, why: '"paise bachte" — conclusion'},
  // PASS 3 — RISERS (stand-ins: the library has no risers) peak on the transition frame, HITS under them
  {family: 'RISERS', sfx: 'eene_6_jet_stop', at: 3.2, align: 'peak', db: -5, why: 'Build: hook → body'},
  {family: 'RISERS', sfx: 'whoosh_back', at: 9.5, align: 'peak', db: -5, why: 'Build: reaction → list'},
  {family: 'RISERS', sfx: 'bell_transition', at: 14.74, align: 'peak', db: -5, why: 'Build: claim → "one place"'},
  {family: 'RISERS', sfx: 'whoosh_back', at: 16.86, align: 'peak', db: -5, why: 'Build: into the payoff line'},
  {family: 'HITS', sfx: 'impact_mid_bass', at: 3.2, align: 'peak', db: -8, why: 'Lands the hook → body cut'},
  {family: 'HITS', sfx: 'deep_impact', at: 9.5, align: 'peak', db: -8, why: 'Lands the cut into the list'},
  {family: 'HITS', sfx: 'impact_cinematic', at: 14.74, align: 'peak', db: -8, why: 'Lands the cut into "one place"'},
  {family: 'HITS', sfx: 'impact_mid_bass', at: 16.86, align: 'peak', db: -8, why: 'Lands the payoff cut'},
];
