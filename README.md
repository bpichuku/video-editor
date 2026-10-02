# video-editor

A Claude Code workspace that edits long-form craft videos for @EarthSkyAndCo: art and craft, 16:9, mostly voiceless. You drop a clip in, ask for an edit, and Claude cuts it, builds the on-screen graphics, mixes the audio, reviews its own work, and exports one final file.

Claude can't drive a video editor, so every stage is something it can do from the command line: read a transcript or watch frames, decide, write code, run a tool.

## How it works

Five stages, always in this order. Each is a skill in `.claude/skills/` that holds its own rules.

| Stage | Skill | What it does | Runs on |
|---|---|---|---|
| 1. Rough cut | `rough-cut` | Turns raw clips into the shortest cut that still delivers. Cuts on words for voiced footage, and on visible action for voiceless footage. | WhisperX, FFmpeg |
| 2. Graphics | `graphics` | Decides which moments earn a card, stat or zoom, then builds them from one script and composites them over the cut. | HyperFrames, FFmpeg |
| 3. B-roll | `ai-broll` | Motion-graphic clips for beats with no footage. Skipped unless asked. No generative AI media. | HyperFrames |
| 4. Finishing | `finishing-pass` | Optional captions, a flat music bed, a few real sound effects, then a two-pass review by sub-agents that watch the render back. | FFmpeg, watch |
| 5. Export | `export` | One clearly named final file. Dry run by default. Absorbs reusable corrections into the style file. | FFmpeg |

`craft-video-editor` is the umbrella skill that runs all of them for one job.

## Using it

1. Open this folder in Claude Code.
2. Copy your footage into `projects/<job>/raw/`. The job folder is kebab-case and named after what the video is about.
3. Run `/craft-video-editor projects/<job>`, optionally followed by direction, for example `open on the most satisfying close-up`.

Claude pauses to ask before it downloads anything, deletes anything, or needs `sudo`.

## Layout

```
brand.md             colours, fonts, voice, hook text, mishear list. The one file to personalise
styles/<name>/       style.md (prose) and style.json (knobs). One folder per look
assets/              fonts/, logos/, lib/ (permanent, shared; lib/ holds gsap.min.js)
sfx/sounds-effects/  library of real sound samples, copied into each job
projects/<job>/      raw/ broll/ audio/ assets/ transcript/ graphics-build/ outputs/
.claude/skills/      the five stage skills and the umbrella skill
CLAUDE.md            the pipeline contract Claude reads every session
```

The top half is taste and stays permanent. `projects/` holds the jobs and is disposable.

## House rules

- **4K, always.** Long form is cut and exported at 3840x2160. A 4K source is never downscaled. Graphics are laid out on a 1920x1080 grid and rendered at 2x.
- **Brand tokens, never hex.** Colours come from `brand.md` as tokens (`$accent`, `$ink`, ...). Fonts load from `assets/fonts/`, never system fonts.
- **Source footage is never touched.** It is copied into `raw/`, never moved or modified.
- **No generative AI footage or images.** Everything is real footage or HTML rendered locally.
- **Music and sound effects are user-supplied and cleared.** Nothing is downloaded automatically.
- **Corrections stick.** Notes that should apply to every future video are written back into the style file, after you've seen the diff.

## Requirements

- macOS on Apple silicon (VideoToolbox hardware encoding is used)
- [Claude Code](https://claude.com/claude-code)
- Node 22 or newer, and `ffmpeg` / `ffprobe`
- [`uv`](https://docs.astral.sh/uv/), with WhisperX installed as a `uv tool` (used for voiced footage)
- Python 3 with Pillow
- HyperFrames, pinned: always call `npx hyperframes@0.8.107 ...`
- The `watch` plugin, used by the review sub-agents

## What's in this repo and what isn't

Included: the brand and style files, the skills, shared fonts and GSAP, and the small source files for the first job (`projects/paper-sketch/`): cut sheets, build and audio scripts, the remapped transcript and the YouTube listing.

Not included, by design: video, audio and image files (see `.gitignore`), so the raw footage, renders, music, sound effects and thumbnails live only on the editor's machine. The generated `graphics-build/parts/` folder is also ignored, because `build.py` regenerates it.

## Status

The first job, `paper-sketch` (a pencil mandala), shipped at 1080p. The 4K standard above applies from the next video onward. The style is still a starter, written without a reference video.

## Licences

- Fonts: Fredoka and Nunito, both SIL Open Font License.
- GSAP (`assets/lib/gsap.min.js`): GreenSock's own licence, not open source.
- Music and sound effects for each video are credited in that job's `outputs/youtube-listing.txt`.
