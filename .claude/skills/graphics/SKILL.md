---
name: graphics
description: Stage 2. Decides which lines earn a graphic, writes a validated cut sheet (beats with ID, window, kind, direction), then builds each one as HyperFrames HTML/CSS/GSAP from a single build script, renders parts, and composites them over the rough cut with FFmpeg. Contains the HyperFrames timeline contract, silent-render failures, composite traps, safe zones, and the early spot review. Use after the rough cut, when asked for graphics, cards, takeovers, zooms or motion graphics, or when touching anything in graphics-build/.
---

# Graphics

Whole job: decide which lines earn a graphic, then build each one. Two halves that stay separate: **plan** (judgment) then **build** (engineering). Mixing them produces a plan written to be easy to build, which is the wrong optimisation.

Read first: `brand.md`, the active `styles/<name>/style.md` and `style.json`. Colours are tokens (`$accent`). Pin `npx hyperframes@0.8.107`; never silently upgrade.

## 1. The plan

Read three things before deciding any beat:

1. The finished remapped transcript from the rough cut (for voiceless jobs: the visual descriptions in `cutsheet.json`).
2. Comments left in the script document. Pull them from the document's XML (`word/comments.xml` in a .docx), not a library.
3. The narration inside B-roll clips.

For every beat, answer in order:

**Does this line need a graphic?** Default no. Plain beats give rhythm and let the footage carry the moment. A beat earns one when it is the hook, names something concrete and showable (stat, screenshot, before/after), is a payoff worth emphasising, describes a process a picture makes instantly clearer, or was explicitly requested. Connective tissue, transitions, asides and emotional delivery stay plain.

**What kind?** Think rich, then flatten to the fixed set of seven: `stat`, `card`, `screenshot`, `takeover`, `zoom`, `diagram`, `broll-slot`. Show over tell. Screen recordings, screenshots, diagrams and stats beat text cards. Reserve cards for the hook and punchlines, and give them motion and a visual element, not a wall of type. (Voiceless jobs lean on text, so cards are more common; keep each short and animated.)

**Where?** Decision table:

| Format | Layout |
|---|---|
| Short form explainer | Graphics top half, face bottom half |
| Short form raw | Exactly one hook card, nothing else |
| Long form (this channel) | Full-frame takeovers, lower thirds, no reframe |

**What exactly?** Write real creative direction: what is on screen, the hierarchy, the hero element, and what animates in what order. Concrete enough that the build is not guessing.

Write the plan as a machine-readable cut sheet (ID, window, kind, direction, notes per beat) plus a human-readable table. Beats with no graphic are simply not listed.

### Validate before the build ever sees it

A script must check: required fields present, `kind` in the allowed set, start < end, sorted ascending, no overlaps, and the non-obvious one: **consecutive beats must either abut exactly or leave a gap of more than 1 second.** A gap of a few tenths flashes raw un-graphiced footage for a fraction of a second during the composite and almost always means the plan meant to abut and did not.

### Safe zones

| Format | Frame | Keep key visuals inside |
|---|---|---|
| Short form | 1080 x 1920 | y 200 to 1620. Top 200 px and bottom 300 px are background only (platform UI, username, audio tag, progress bar land there). Not a guideline. |
| Long form | 1920 x 1080 | Title safe, 10% margins. Keep the outro's right 40% clear for end-screen cards. |

## 2. The build

Generate compositions from a script. Do not hand-write HTML per graphic. One build script in `projects/<job>/graphics-build/` holds the shared CSS, per-graphic markup and per-graphic animation, and emits one composition file per part plus a render script and an assemble script. **This folder is the real progress on the job. It lives in the project, never only in a temp folder** (temp is volatile; an overnight clear has wiped an entire build). Only heavy regenerable renders belong in a cache. Load fonts from `assets/fonts/` files, never system fonts.

Classify every part by one question: does it change the footage underneath, or float on top?

- **Overlay**: card, panel, callout. Renders standalone to a transparent file and composites at its timestamp.
- **Segment**: takeover, full-screen cutaway, anything that replaces the frame. Renders with its own slice of the base footage baked in, opaque, covering the base for its window.

The base rough cut is **never re-rendered**. Editing one graphic = regenerate one composition, re-render one part, run one FFmpeg composite pass. Lock parts one at a time.

### Non-negotiables

- **Graphics hold until the next part starts.** No early fade-out leaving dead air.
- **Picture-in-picture enters once per graphics run.** Chain everything between entries. Bouncing between full frame and PiP is the most amateur thing an AI editor does. Hard cuts between card contents are fine. A full-screen bounce never is.
- **Continuous motion on any beat 20 s or longer.** A count-up that finishes at 6 s of a 19 s beat reads as a frozen frame for 13 s. On long beats write out what is moving across the entire duration.
- **Real assets over recreations.** Actual logo, screenshot, chart, with a slow pan or push. Never a redrawn approximation.
- **Measure, do not estimate.** Pull the actual frame, measure the element's bounding box in pixels, set the zoom from that.
- **Check the tail of every clip, not just the start.** A retake seam leaves a bad frame at the out point.
- **Assets outlast their window.** Every part gets about 0.5 s tail margin past its nominal end.
- **Local direction never silently overrides a style convention.** If a script comment says "chip in the upper third" and the style says chips sit under the chin, flag the conflict. Following the more recent instruction is recency bias, not judgment.

## 3. HyperFrames gotchas

HyperFrames builds each graphic as HTML, CSS and GSAP, rendered in a headless browser. No ceiling on graphic count, and all the sharp edges live here.

### Timeline contract (compositions are seeked, not played)

- One master timeline, created **paused**, every tween at an **absolute second**, never relative offsets.
- **No random values.** The same frame must render identically on every seek.
- **No real-time timers** (`setTimeout`, animation-frame loops). Everything comes off timeline position.
- **Every exit landing on a boundary needs an explicit hard kill**: opacity set to 0 at that exact time. An unresolved tween pops instead of finishing.
- Time is always **seconds**, never frames.
- Every entrance is a **from-to** tween, never a bare `to` (no defined start state when seeked mid-tween).
- Never put a CSS transform and a GSAP tween on the **same property**.

### Things that silently do not render (nothing errors)

| Trap | What happens | Fix |
|---|---|---|
| Transforming a `<video>` directly | Headless render composites it away. The face vanishes. | Wrap the video in a div with hidden overflow and animate the wrapper's `left/top/width/height`. The parent crops the untransformed video. |
| CSS blur filters | Not render-safe | Per-letter opacity stagger, about 0.045 s between letters |
| Grayscale filters | Same failure | Tween the colour toward a flatter value |
| Class-name tweens | Do not survive the seek and can wipe the base class styling | Tween the actual CSS properties directly |
| Near-zero-duration tweens (e.g. 0.001 s) | Unreliable: two identical ones, one applied, one did not | Every instant change gets a real 0.2 to 0.35 s duration. It still reads as a cut. |
| Raw emoji glyphs | Hang the render at full CPU, no error, no timeout. A 5 s part takes 5 minutes. | Fake the look with the brand font, or pre-render the glyph as a transparent PNG and overlay it. Tell: a render going at 3x the length of a same-sized part is an emoji, not a real hang. |
| Backdrop blur on transparent overlays | Nothing behind them, no blur | Design frosted panels to read on their own fill |

### Composite traps (FFmpeg, found at assembly)

- **Match every part to the base frame rate exactly.** Probe it. Mixed rates drift.
- **Segments carry their own base slice**, cut once from the base so first and last frame match at the seam.
- **Cut that slice at the time it is placed, not the time it was built.** If the base is re-spliced and graphics shift, a slice cut at the old time makes footage jump at the seam and drift out of sync with audio for the whole duration. Overlays just slide. Only segments carry footage, so only segments need re-cutting and re-rendering.
- **Every overlay's end-of-file behaviour must be `pass`, not `repeat`.** Chain several short overlays over a long base and the frame scheduler duplicates frames on a periodic cadence (exactly one in four in the original). Output is dead-even constant frame rate, so every tool reads it as fine, but content updates only about 18 times a second wearing a 24 fps costume. Visible judder on smooth motion; every input measures clean alone, so you keep "fixing" a zoom that was never broken. **Detect by counting exact duplicate frames in the output: clean is under 3%, the bug is about 25%. Wire that check into the assemble script and make it fail above 8%.** Do not mask it by forcing a frame rate.
  - Exception: a deliberately held frame (e.g. an outro push-in that must not zoom back out) gets `repeat`.
- **Do not use frame padding to hold a zoom.** It never reaches end of file and can balloon a few-second clip into gigabytes.
- **Browser segments darken footage** (about 3% luma lost round-tripping through the headless browser, so faces dip at every seam). Fix at the root, in order:
  1. Do footage motion in FFmpeg, not the browser. A zoom or push-in is pure geometry. Use a browser segment only when live graphics must reveal behind the moving face.
  2. If it must be a browser segment, render source frames as **PNG** (halves the dip), then close the remainder with a **gamma** correction at assemble time. Gamma, not flat gain: it pins black and white and does not clip highlights.
- **An FFmpeg zoom on a mid-video slice needs its frame counter reset**, or the zoom comes out constant and reads as a hard cut instead of a ramp. Build the slice by trimming inside the filtergraph and resetting timestamps (`trim` + `setpts=PTS-STARTPTS`), never by seeking to a start point. Invisible when a part starts at zero, so an intro zoom works by luck and every later one silently fails.
- **Anchor footage motion to measured scene cuts, not nominal ones.** The rendered base drifts a few hundred ms from the cut sheet by the end of a reel, and the transcript drifts with it. Run scene detection on the rendered file and use that time.
- **Screen recordings carry black bars.** Run `cropdetect` before compositing into a card, or you scale the bars in and shrink readable content. Size cards bigger than feels right in CSS: numbers that look generous as CSS render noticeably small.

### Lint and workflow

- `lint` and `validate` are the gate. Run both on every part before rendering.
- Contrast warnings on deliberately dim text: raise **opacity**, not brightness. Keeps the intended look.
- A dense-track warning on a short build is normal. Do not refactor parts into sub-compositions to silence it.
- No generated images on this channel. If an icon or illustration cannot be drawn in HTML/SVG, use a real asset from `assets/` or flag it to the user.
- Every graphic is front-end design: use any installed taste skill to avoid generic slop.

## 4. Early spot review

Run a spot review after the first **10%** of the build, not only at the end. A wrong placement habit caught once is a fix; at the end it is a rebuild. Use sub-agents with the `watch` skill (see `finishing-pass` for the two-pass review protocol), because frame dumps flood the main context.
