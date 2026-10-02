---
name: rough-cut
description: Stage 1. Turns raw clips in projects/<job>/raw/ into the shortest cut that still delivers the value. Transcribes with WhisperX (word-level timestamps), applies the brand.md mishear list, decides kills, writes transcript/cutsheet.json, splices with one FFmpeg filtergraph, and writes a transcript remapped onto the edited timeline. Use when asked to edit, cut, or start a new video job, or when raw footage has no transcript yet.
---

# Rough cut

Whole job: turn raw clips into the shortest cut that still delivers the value. Claude cannot hear audio, so the sub-second timing of every word from WhisperX is what makes cutting possible. Cutting raw footage is a pure transcript problem.

Read `brand.md` (mishear list) and the active style `style.json` first.

## Job setup

- Folder `projects/<job>/`, kebab-case, named after the content. Never a camera filename, a date, or a stage suffix like `-final` or `-v2`. One folder carries the piece across every stage.
- Subfolders: `raw/ broll/ audio/ assets/ transcript/ graphics-build/ outputs/`. Add nothing else.
- Copy source clips into `raw/`. Never move them.

## Pipeline

1. **Transcribe once.** WhisperX `large-v3` with wav2vec2 alignment (the `whisperx` uv tool; never system Python). Write `transcript/transcript.json`. Re-running must skip straight to that saved copy. This is the slowest step and runs exactly once per video, ever.
2. **Also transcribe `broll/`.** Creators narrate direction inside their own B-roll takes ("zoom in here", "use this for the pricing bit"). That never appears in the main script. Save it alongside, and surface it to the graphics skill.
3. **Apply mishears** (see below), then read the transcript and write `transcript/cutsheet.json`: an ordered list of segments, each with `source` clip, `start`, `end`, and `text`. The `text` field lets you sanity-check the whole edit by reading it without watching anything.
4. **Splice with a single FFmpeg filtergraph.** One trim per kept segment, concat, then polish the audio once on the assembled track.
5. **Write the remapped transcript** onto the edited timeline into `outputs/`. Every downstream skill reads that file. Nothing ever re-transcribes.

## What to cut automatically

- Filler words when vestigial
- Stutters and false starts
- Silences over about 0.4 s
- Tangents that do not serve the hook
- Throat clears and "let me start over"
- Any preamble before the hook lands

Every video opens on the hook. When a line was recorded several times, **take the last one, always**. It is the warmest delivery and comparing takes wastes an hour.

Preserve cadence. Do not surgically remove every "like". Some are rhythm.

## Decision table: voiced vs voiceless footage

(Adaptation for this channel, not from the playbook: Priya's videos are mostly voiceless.)

| Footage | What the transcript gives | How to cut |
|---|---|---|
| Voiced | Word-level timings | Everything above. Cut on words. |
| Voiceless | Empty or only stray sounds, so no cut points | Do not invent a transcript. Use the `watch` skill on a low-fps pass to describe each clip, write `cutsheet.json` with `text` = a one-line description of what is visible ("glues petal 3 onto the base"), and cut on visible action boundaries and the music beat if music is already supplied. Keep ambient craft sounds. |
| Mixed | Transcript for spoken bits only | Voiced rules for spoken segments, description-based for silent stretches. |

Tell the user explicitly when a job is running the voiceless path, since the "last take wins" and filler rules cannot apply.

## FFmpeg rules (each cost real time to find)

- **No stream copy on arbitrary cut points.** `-c copy` desyncs audio and video. Re-encode each segment with hardware acceleration (`h264_videotoolbox` on this Mac). Roughly 15 s per minute of output.
- **Never encode audio per segment.** Ride it through the cut lossless, then amplify and limit once on the assembled track. Per-piece encodes click at every join.
- **Do not auto-snap cuts to silence.** Word-level alignment is the advantage. Silence detection drags deliberate boundaries into filler and awkward pauses.
- **Retake seams clip word tails.** When a speaker cuts in on top of their own previous word, the kept word sounds chopped. Extend the out point slightly into the stumble and fade that segment's audio to zero over its last fraction of a second so the word rings out.
- **Stumbles hide inside long word spans.** WhisperX sometimes merges a stumble and its retake into one word span over 1.2 s. If a word's duration looks wrong for what it should sound like, run silence detection across that span before deciding the cut.
- **The transcript will mishear.** Cross-check before killing a line. "Claude" heard as "cloud" makes a good sentence look broken.
- **Screen recordings can carry a chapter track** that inflates reported duration and leaves a black tail. Probe with `ffprobe` and strip chapters (`-map_chapters -1`) when re-encoding.
- **Long form is cut at 4K (3840x2160).** Scale every segment to 3840x2160 and never downscale a 4K source to 1080p. Use hardware decode (`-hwaccel videotoolbox`) and encode at about 45 to 50 Mbps with `h264_videotoolbox`. If a source is below 4K, tell the user before upscaling anything. A crop-based punch-in stays sharp only while the crop is 1920x1080 or larger in the source; smaller crops upscale and should be used sparingly.
- Probe the real frame rate with `ffprobe`. Never guess. (23.976 is `24000/1001`, not 24.)

## Mishear handling

Two layers:

1. **Fixed list.** `brand.md` mishear list. Apply to every transcript automatically. A mishear fixed once is fixed in every future video. Keep the list in `brand.md`, never a separate file.
2. **Automatic dictionary pass.** Compare every transcript word against a system dictionary (`/usr/share/dict/words` on macOS). Print only words that are neither ordinary English nor already known, and judge them in context.
   - Recurring brand name: add to the permanent list in `brand.md`.
   - One-off: add to a per-video list in `transcript/`.
   - **Only auto-apply single-word, whole-word swaps.** A two-words-into-one fix changes the word count and breaks every timestamp downstream. Multi-word fixes are review-only: correct the text, never the timings.

## Outputs

- `transcript/transcript.json` (raw, durable, never overwritten)
- `transcript/cutsheet.json` (segments with `source`, `start`, `end`, `text`)
- `outputs/` base cut and the remapped transcript

## Gotchas checklist before handing to graphics

- [ ] Hook is the first thing in the cut
- [ ] Every kept retake is the last take
- [ ] No `-c copy` anywhere in the splice
- [ ] Audio encoded once, on the assembled track
- [ ] Chapters stripped on screen recordings
- [ ] Remapped transcript written to `outputs/`
