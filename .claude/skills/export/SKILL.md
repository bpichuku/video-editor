---
name: export
description: Stage 5. Turns a messy projects/<job>/outputs/ folder into one clearly named final file, retires superseded drafts, keeps the base cut, transcripts and graphics-build source so the job can be reopened, copies the deliverable to Downloads, then optionally reclaims space. Dry run by default. Also absorbs reusable review corrections into the style file before closing a job. Use when asked to export, finalise, ship, clean up, or close out a video job.
---

# Export

Whole job: turn a messy `outputs/` folder into one unambiguous file. By the end of a job there is a base cut, graphics pass, captions pass, music pass and two drafts, and in a week nobody knows which one shipped.

## Promote

Promote the **newest real render** to a single clearly named final (named after the job, e.g. `outputs/<job>.mp4`). Then:

- Retire superseded drafts.
- **Keep** the base cut, the transcripts (`transcript/`), and the `graphics-build/` source so the job can be reopened.
- Drop a copy of the deliverable somewhere convenient, `~/Downloads` by default.

## Reclaim space (separate, optional)

Render scratch, cached intermediate renders, stray `node_modules`. **Never source footage (`raw/`, `broll/`, `audio/`), never the `outputs/` folder.**

## Two safety rules

1. **Dry run by default, always.** Both halves (promote and reclaim) print exactly what they would promote, delete and keep, and do nothing until an explicit `--apply` flag is passed **after the plan has been read**.
2. **Never delete anything newer than the deliverable.** Put this guard **inside the script**, comparing modification times, so a future session cannot talk itself past it.

Write the script into the job (`graphics-build/`) or generate it each time. Do not create new top-level folders. Show the dry-run plan to the user and wait for a yes before applying. Deleting is outward-facing and hard to reverse: confirm each time.

## Absorb corrections before closing the job

Every note given in the final review is one that will be given again next week unless it is written down.

1. Sort review notes into **standing corrections** (should apply to every future video) and **one-offs** (apply and forget).
2. Write each standing correction back into `styles/<name>/style.md` and the `learned` array in `style.json`.
3. **Show the user the diff before it becomes standing behaviour.** Get a yes first.
4. Do this before the job is closed out.

Review sub-agents read the style fresh each pass, so an absorbed correction tightens every future review with no extra wiring. By the third video the style file has absorbed a dozen corrections and the review loop checks for what the creator personally cares about.
