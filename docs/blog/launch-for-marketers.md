# Take “write three scripts tonight” off the overtime list: a marketer’s launch note for skill-video-script

It is 9 p.m. on a Tuesday and the sunscreen still has no shoot. The operator deletes the first line again: it has to stop the scroll, but it cannot sound like a carnival barker; it has to mention SPF, but WeChat Channels should not read like a manual. The editor asks in the group chat whether a storyboard exists. Paid media wants three A/B variants before noon. The shortage is not inspiration. It is a **filmable structure** for today.

[skill-video-script](https://github.com/samjia12/skill-video-script) collapses that into one brief. You supply a product name, selling points, and a platform (Douyin, WeChat Channels, or Bilibili). It always returns three styles: recommendation, how-to, and story twist. Each style carries a timed storyboard, a teleprompter voiceover, a golden three-second opening, BGM search keywords for the licensed library, and subtitle rules. The default engine is offline and needs no API key. An agent that reads `SKILL.md` runs the same CLI.

## Before and after, with hours attached

Use the bundled sunscreen example as a stand-in for a three-person weekly cadence.

**Before.** Monday’s 40-minute huddle agrees on “light texture, SPF50+, student price.” Monday into Tuesday, copy writes a recommendation draft and an editor breaks it into shots: about **2.5 hours**. Wednesday, someone remembers Channels needs a softer CTA: another **hour**. Thursday, how-to and twist still do not exist: **45 minutes** each. Across three platforms, before anyone aligns captions or music, the week has burned **six to eight hours** getting from a blank page to something shootable. The opening three seconds are still vague. Completion rate is a coin flip.

**After.** The brief is a JSON file (or three CLI flags). The machine returns three skeletons in seconds; switch the platform and run again. Human work becomes **pick a version, change two lines, shoot to the table**. From cloning the repo to a timecoded voiceover is **under five minutes** if you can read a README:

```bash
python3 scripts/generate_script.py examples/douyin_skincare.json
```

If a team ships six short videos a week, moving “structure time” from roughly 50 minutes a piece to 8 minutes gives back about **four hours**. Those hours belong on completion data, not on the first sentence.

The number is not a lab claim. The job changed. The generator does not replace talent on camera. It replaces inventing storyboard grammar from zero.

## Three desks, three stories

**Ecommerce ops.** SKUs rotate. Sunscreen today, a capsule machine tomorrow. Every script used to start with the same “hey I found this,” and the Channels cut still sounded like Douyin. Now the Channels example pushes follow-and-DM rather than a shop cart; the Bilibili example carries unboxing tags and a longer clock. Operators maintain selling points in the brief so the voiceover cannot invent a medical claim that legal never saw.

**Brand social.** They do not need more punch lines. They need A/B. The same point, as result-first, as a table of contents, or as a plot twist, will not hold completion the same way. Three scripts are the experiment. Watch which golden three seconds keeps people, then put budget on that shape. The radar in the [browser demo](../../demo/index.html) and the [sample report](../../examples/report-sample/report-sample.md) is something you can paste into a planning doc without apologizing for “the model’s vibe.”

**MCN floors and one-person crews.** With no dedicated director, an agent collects fields, runs the CLI, and presents three versions in a fixed order. People still choose the cut and stand in front of the lens. A solo creator reads the timecode. They do not first have to learn how to draw a storyboard.

## Four steps to first filmable output

1. Clone https://github.com/samjia12/skill-video-script . Python 3.9+. `pip install -r requirements.txt` pulls pytest; generation itself is standard-library only.  
2. Copy `examples/douyin_skincare.json` and change `name`, `selling_points`, and `platform`.  
3. `python3 scripts/generate_script.py your.json -o output/script.md`.  
4. Hand the Markdown to an editor or a teleprompter. Open `demo/index.html` when you need to walk a non-engineer through the loop.

On architecture, the template pipeline is in front and the LLM is on the side. How modules split, and how failures exit, is in [docs/architecture.md](../architecture.md): flowcharts and a sequence diagram. A validation error never yields a half script. The LLM may rewrite spoken lines and titles; it may not rewrite the clock. That is a promise to whoever cuts the film: 0.0–3.0 remains the golden three seconds.

## What it will not do

It will not render a video, ship an audio file, or upload. Spoken copy is Chinese. The `tiktok` alias follows the Douyin playbook, not US/EU TikTok rules. Default copy is deterministic; turn on `--backend llm` only if you want a looser rewrite and you have a key. Legal still reads the brief. The tool refuses to fabricate efficacy you did not provide.

## Write a brief the camera can honor

The generator is not a wishing well. The more concrete the fields, the less the golden three seconds sound like a slogan in a vacuum. Name, platform, and at least one selling point are mandatory. Audience, price, and category are how “79 yuan” and “students” actually land in the hook and the hashtags. Duration may be omitted; the engine falls into the platform sweet spot (about 27 seconds on Douyin, 36 on Channels, 60 on Bilibili). An illegal number is an error, not a silent five-second ad.

The sample report spreads nine scripts across a bar, a line, a pie, a radar, and a heatmap so a planning meeting can answer “who do we shoot first.” It does not replace the completion dashboard. It does stop a structural argument before the camera rolls. The heatmap already shows roughly 200 characters on Douyin and about 300 on Bilibili. Stuffing more spec into the Douyin teleprompter is a fight with speaking rate, not a creative choice.

A note on collaboration: Markdown is for editors and talent. JSON is for anything you might script later. The browser demo exists so a non-engineer can press three example chips and see the same three styles without installing Python. None of those surfaces is a second product. They are three doors into the pipeline drawn in the architecture doc: validate, generate three versions, render, then optionally rewrite spoken copy if a key is present.

If you already have an agent in the loop, do not let it free-compose a script and call it this Skill. Point it at `SKILL.md`. The skill’s job is to collect the brief, run the CLI, and present all three versions in order — hook, board, voiceover, BGM, subtitles, CTA. That order is how an editor scans a packet. Breaking it costs the four hours you just saved.

For a marketing team the launch is specific: take “write three scripts tonight” off the overtime list, and give the hours back to the shoot and the retro. The repo is MIT. Issue and pull-request forms are already there. The next step is your SKU in the JSON, not another brainstorm.
