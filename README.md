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

## Quick start

Edits run in Claude Code, opened in this folder.

### 1. Create a job and copy in footage

Run this whole block in one Terminal session. Change only `JOBNAME` for each new project, and replace the sample source path with the real path to your clip. Name the job after what the video is about, in kebab-case (never a camera filename, a date, or a suffix like `-final`). The `${JOBNAME:?...}` guard stops the paths from falling back to `projects/` if the variable is empty or unset.

```bash
cd /path/to/video-editor
JOBNAME="paper-sketch"
mkdir -p "projects/${JOBNAME:?Set JOBNAME before running the setup commands}"/{raw,broll,audio,assets,transcript,graphics-build,outputs}
mkdir -p "projects/${JOBNAME:?Set JOBNAME before running the setup commands}/audio/sound-effects"

cp -R sfx/sounds-effects/. "projects/${JOBNAME:?Set JOBNAME before running the setup commands}/audio/sound-effects/"

cp "/absolute/path/to/your-clip.mp4" "projects/${JOBNAME:?Set JOBNAME first}/raw/"
```

Keep the original clip where it is; `cp` makes a working copy. The sound-effects copy comes from the shared `sfx/sounds-effects/` library. Supporting screen recordings or extra footage go in `broll/`.

If you have a licensed background music track, copy it into the job's `audio/` folder:

```bash
cp "/absolute/path/to/licensed-music.mp3" "projects/${JOBNAME:?Set JOBNAME first}/audio/"
```

The finishing pass uses only real sample files from the job's `audio/sound-effects/`. If that folder is empty, the sound-effects step is skipped.

### 2. Start the edit in Claude Code

Open Claude Code in this folder and invoke the umbrella skill with the job path:

```text
/craft-video-editor projects/paper-sketch
```

Use the real job name in the Claude Code command. The Terminal variable `JOBNAME` does not carry into the chat.

You can add creative direction in the same message:

```text
/craft-video-editor projects/paper-sketch — open on the most satisfying close-up.
```

The current style (`styles/editorial`) is long form 16:9 only. A 9:16 short needs its own short-form style first, so ask for that before requesting one.

### What the umbrella skill does

It runs rough cut, graphics, finishing and export in order. AI B-roll is skipped (generated media is not used on this channel). It follows the EarthSkyAndCo style from `brand.md` and `styles/editorial/`.

It may pause and ask you if:

- the footage contains speech and it's unclear whether to cut it as voiced or voiceless
- no music track is in `audio/`
- a review needs a creative decision
- export wants to delete files (export always shows a dry-run plan first and waits for your yes)
- anything needs `sudo` or a download

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
