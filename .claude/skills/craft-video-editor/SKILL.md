---
name: craft-video-editor
description: Umbrella skill that edits one EarthSkyAndCo craft video end to end. Takes a job path like projects/paper-sketch plus optional direction, then runs rough-cut, graphics, finishing-pass and export in order, skipping AI B-roll (no Higgsfield or generative media on this channel). Use when the user invokes /craft-video-editor, or says "edit this video", "make the video", or points at a projects/<job>/raw/ folder and asks for the full edit.
argument-hint: projects/<job> [optional format or creative direction]
---

# Craft video editor (orchestrator)

Runs the whole pipeline for one job by calling the stage skills in order. This skill holds sequencing and pause points only. Every rule, table and gotcha lives in the stage skill that owns it, so read each stage skill when you reach it rather than working from memory.

## Input

`$ARGUMENTS` = a job path (`projects/<job>`) optionally followed by direction ("make it 16:9 opening on the most satisfying close-up"). If no path is given, list `projects/` and ask which job. Do not guess.

## Preflight (stop and report if anything fails)

1. `projects/<job>/` exists with `raw/` containing at least one video. Job name is kebab-case content name (no camera filename, date or stage suffix); if not, ask before renaming.
2. Read `brand.md` and the active style (`styles/editorial/` unless told otherwise): `style.md` and `style.json`. If the requested format is not in the style's `formats` (this style is long form 16:9 only), stop and tell the user; do not improvise a short-form look.
3. Tools: `ffmpeg -version`, `ffprobe -version`, `node --version` (22+), `uv --version`, `python3 -c "import PIL"`, `whisperx --help`, `npx hyperframes@0.8.107 doctor`. Expected doctor failures: upgrade nag, Docker, optional whisper-cpp/Kokoro/MusicGen. Check that the watch skill is available. Never run sudo without asking.
4. `assets/fonts/` has the brand font files.
5. Note what is present: music in `audio/` (licensed, user-supplied) and sound samples in `projects/<job>/audio/sound-effects/`. If that folder is missing or empty, copy from the top-level `sfx/sounds-effects/` library (`cp -R sfx/sounds-effects/. projects/<job>/audio/sound-effects/`). Music may be absent; never download it.

## Run order

| # | Skill | Notes |
|---|---|---|
| 1 | `rough-cut` | Voiced, voiceless or mixed footage decides the cutting method. Say which path is running. |
| 2 | `graphics` | Plan, validate, build, composite. Early spot review at 10% of the build. |
| 3 | `ai-broll` | **Skipped by default.** Run only if the user explicitly asks for motion-graphic B-roll. Never use Higgsfield or any generative AI media. |
| 4 | `finishing-pass` | Captions off for long form. Music only if a licensed track is in `audio/`. SFX only from real samples. Then the two-pass watch review via sub-agents, looping until clean. |
| 5 | `export` | Dry run first. Show the plan, wait for a yes, then apply. |

Each stage reads the previous stage's output from the job folder and never re-does it (the transcript is made once, the base cut is never re-rendered).

## Pause and ask the user when

- Source clips contain speech and the voiced/voiceless path is unclear, or speech content conflicts with the hook.
- No music track is in `audio/`. Never download one. Offer to finish without a bed.
- A script comment conflicts with a style convention (flag, do not decide quietly).
- Review findings need a creative decision rather than a fix.
- Export would delete anything, and before any style-file update from review corrections (show the diff first).
- Anything needs sudo or a download.

Otherwise keep going without asking.

## Hard rules (pointers, details in the stage skills)

- Source footage is copied into `raw/`, never moved or modified.
- Colours are tokens from `brand.md` (`$accent`), never hex. Fonts load from `assets/fonts/`.
- Pin `npx hyperframes@0.8.107`.
- Add no new top-level folders or notes files.

## Finish

Report: final file path (and Downloads copy), which stages ran or were skipped and why, review passes completed, any items flagged as skipped, and any standing corrections proposed for the style file.
