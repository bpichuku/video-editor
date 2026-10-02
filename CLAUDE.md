# Pipeline contract

This workspace edits videos for Priya (@EarthSkyAndCo, art and craft, long form 16:9, mostly voiceless). Claude cannot use a video editor, so every stage is something Claude can do: read a transcript, decide, write code, run a CLI tool. Detailed rules live in the skills, not here.

## Stages and skills

| Stage | Skill | Runs on |
|---|---|---|
| 1 Rough cut | `rough-cut` | WhisperX, FFmpeg |
| 2 Graphics | `graphics` | HyperFrames, FFmpeg |
| 3 B-roll (HyperFrames motion graphics only, skipped by default) | `ai-broll` | HyperFrames |
| 4 Finishing | `finishing-pass` | FFmpeg, watch |
| 5 Export | `export` | FFmpeg |

Stages run in this order for every format. Format only changes how graphics and captions behave, and that comes from the style file.

## Workspace

```
brand.md          colours, fonts, voice, hook, mishear list. The one file to personalise
styles/<name>/    style.md (prose) + style.json (knobs). One folder per look
assets/           fonts/ logos/ sfx/  (permanent, shared)
projects/<job>/   raw/ broll/ audio/ assets/ transcript/ graphics-build/ outputs/
```

Top half is taste (permanent). `projects/` is jobs (disposable). Do not add notes files, config files or temp folders. Anything that fits neither half means the design drifted.

## Always

- Read `brand.md` and the active `styles/<name>/style.json` before any creative decision. Colours are tokens (`$accent`), never hex.
- Job folder: kebab-case, named after what the video is about. Never a camera filename, a date, or a stage suffix (`-final`, `-v2`).
- Source footage is copied into `raw/`, never moved, never modified.
- Do not start editing until the user drops a clip into `projects/<job>/raw/` and asks.
- Ask before running anything that needs sudo. Ask before downloading anything.
- Corrections that should apply to every future video get written back into the style file (see `export` skill).

## Pinned tooling

- HyperFrames: `hyperframes@0.8.107`. Always call `npx hyperframes@0.8.107 ...`. Do not upgrade without asking. Expected `doctor` failures: upgrade nag, Docker not running, optional whisper-cpp/Kokoro/MusicGen. Ignore them.
- WhisperX is installed as a `uv tool`. Never install it into system Python.
- Node 22+ required (machine has 24). macOS VideoToolbox is available for hardware encoding.
- Verify binaries exist before building: `ffmpeg -version`, `node --version`, `uv --version`, `python3 -c "import PIL"`.
- No Higgsfield, no AI-generated footage or images. Do not install or suggest it. Stage 3 is HyperFrames motion graphics only, and only when asked.
