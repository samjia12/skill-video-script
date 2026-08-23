# From a three-hour script pile to three minutes: why marketers should keep skill-video-script on the desk

Short video is no longer a side channel. It is the shelf. The same product has to stop the scroll on Douyin, sound like a friend’s tip on WeChat Channels, and carry real information density on Bilibili. The structure changes, the pacing changes, and the call to action changes. Most teams are not short on ideas. They are short on a shot list they can film today.

[skill-video-script](https://github.com/samjia12/skill-video-script) is an open-source Agent Skill and a command-line tool for marketers, social teams, and creators. You give it a product name, selling points, and a platform. It returns **three style variants**—recommendation (“grass”), how-to, and story twist. Each variant includes a timed storyboard, a teleprompter voiceover, a golden three-second opening, BGM search keywords for the platform’s licensed library, and subtitle rules (font, safe area, highlight color). You can load it as a skill for a coding agent, or run it offline with no API key.

## Where it actually gets used

**Ecommerce operators on a weekly cadence.** Sunscreen one day, a capsule coffee maker the next, a keyboard kit after that. Nobody wants a blank page every time. Drop in the brief, get a filmable structure, then decide whether today’s shoot is the recommendation cut or the tutorial cut. Human time goes to talent and product, not to rewriting the first line.

**Brand social teams running hook experiments.** The same selling point, delivered as result-first, a curiosity gap, or a pattern interrupt, will not hold completion rate the same way. Three scripts are a ready-made A/B set. Watch which golden three seconds keeps people; then put budget behind the winner. You do not need a full reshoot package to learn that—only three openings and a shared storyboard grammar.

**MCN desks and small crews who already live in agents.** People still pick the cut, stay on the right side of claims, and appear on camera. The agent follows `SKILL.md`: collect the fields, run the generator, present all three versions in a fixed order. That is cheaper than a chat that starts from zero every time someone says “write me a Douyin.”

**Solo creators without a director.** They need lines they can read to camera and a board they can shoot, not a paragraph of vibe. Voiceover carries timecodes. Subtitles have a per-line budget. BGM is a library search, not a chart-topping track you cannot license.

## The payoff is operational, not poetic

**Time.** The default engine is offline, deterministic, and returns three drafts in seconds. It separates “what is the structure” from “please make this sentence sparkle.” No key required. A junior operator can produce a first cut of storyboard plus voiceover before the standup ends, instead of blocking a copywriter for half a day.

**Platform rules encoded, not improvised.** Douyin defaults to about 27 seconds, fast cuts, and shop-cart language. WeChat Channels is more restrained; the CTA leans follow and private message. Bilibili runs longer, leaves a danmaku channel at the top, and asks for a triple tap. That is more than swapping hashtags.

**Something you can hand to the next person.** Markdown is for editors. JSON is for whatever sits downstream. The same brief yields the same script twice, which makes review and regression possible. A pure LLM draft often cannot say that.

**Fewer copyright and claims accidents.** BGM output is mood, BPM, and search keywords for the official library. The copy will not invent a medical or financial promise that was not in your brief. That matters when legal reviews every line that goes on a shoppable video, and when a trending song in the draft would never clear in time.

The three styles are not labels on identical paragraphs. Recommendation copy leads with sensation and social proof. How-to copy is a three-step path the viewer can repeat. Story-twist copy opens on conflict and turns the product into the resolution. You can still rewrite a sentence; you should not have to invent that skeleton every morning.

## What it is not

It does not render video, book a creator, or upload to a platform. The template engine has a ceiling; if you want looser spoken language, the optional LLM rewrite exists, and it fails closed when the key is missing. Spoken copy is Chinese, because these three products are Chinese-language feeds. TikTok, YouTube Shorts, and Instagram Reels are not first-class playbooks in this release.

For a marketing team, the valuable output is **something you can shoot today**, not another brainstorm. Clone the repo and run:

```bash
python3 scripts/generate_script.py examples/douyin_skincare.json
```

You will get all three versions. The README in the repository has install steps, flags, and the other two worked examples (WeChat Channels and Bilibili).
