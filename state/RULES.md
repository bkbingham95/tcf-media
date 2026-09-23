# Tough Country Fitness posting rules

Standing rules for the photo-to-social pipeline. Read this before any run.

## Scheduling

- **Both platforms, as of 2026-08-18.** Every post goes to Instagram *and* the Facebook
  page, mirrored: same image, caption, hashtags and first comment, same slot time.
  - Instagram `tcfitness702`, Blotato accountId `65798`, platform `instagram`
  - Facebook page Tough Country Fitness, Blotato accountId `43833`,
    platform `facebook`, pageId `400966506670459`
- **Posting schedule** (America/Los_Angeles, all seven days):
  `05:00, 09:00, 12:00, 13:30, 15:00, 17:30`
- **If a requested time has already passed, do not ask and do not skip the post.
  Fall back to the next available slot** in the schedule above. Say which slot it
  resolved to.
- Never schedule into a slot that already has a post on that platform. Check first
  with `blotato_list_posts` filtered to the target day.

## Blotato mechanics

- **Scheduling runs through Blotato.** Buffer is read-only history now: its free plan
  rejects first comments outright, with `InvalidInputError: First comment requires a
  paid plan`. Nothing is created in Buffer.
- Schedule with `blotato_create_post`, one call per platform.
- Every post carries a `firstComment`. No exceptions. Blotato supports it on both
  Instagram and Facebook.
- Do **not** set `mediaType`. Omitting it gives a normal feed post; `reel` and `story`
  both reject the 4:5 crop.
- `altText` is accepted for Instagram only. Blotato does not take it for Facebook, so
  the Facebook copy of a mirrored post goes without it.
- After every schedule call, confirm with `blotato_get_post_status` that the status is
  `scheduled` and the time matches. Do not report done without it.
- `Failed to fetch media URL: 400 Bad Request` means the composite was never pushed to
  GitHub, or the URL is wrong. Fix the push, do not substitute an image.
- A failed submission cannot be retried. Create a fresh post instead of polling it.
- `get_post_status` returns `in-progress` for a submission that was **deleted** in the
  Blotato UI, not an error. Only `blotato_list_posts` can confirm a post still exists.

## Reading history

`blotato_list_posts` returns every page in the workspace mixed together (Backyard
Flocks, Nevada, Arizona Native Histories) and its items carry no account or page field.
Tough Country posts are the ones whose text contains `#ToughCountryFitness`.

Anything sent before 2026-08-18 lives only in Buffer and will not appear in Blotato at
all. Anti-repeat checks have to read both.

## Image hosting

- Blotato only accepts images by public URL, so the repo is the image host:
  `https://raw.githubusercontent.com/bkbingham95/tcf-media/main/out/<date>/slot<n>.jpg`
- The composite must be committed and pushed **before** scheduling. Blotato downloads
  the image at creation time and a 404 fails the post.
- The sandbox proxy returns **403 for `raw.githubusercontent.com`**, so `curl` and
  `wget` cannot read the bank or the images. Use `web_fetch` for repo files. Git over
  SSH to `github.com` does work, so `git ls-remote` is a reliable way to confirm a push
  landed.
- `raw.githubusercontent.com` caches for about five minutes. Right after a push it can
  still serve the old file. That is the CDN, not a failed push.
- The sandbox cannot push to the repo. Either Brian pushes from Terminal, or the repo
  gets attached as a session source at task start, which grants real push credentials.
- `device_bash` cannot delete files, so git leaves a stale `.git/index.lock`. Any push
  command handed to Brian must start with `rm -f .git/index.lock`.

## Content

**Direction changed 2026-09-15: this page publishes ENCOURAGING posts, not teaching
posts.** Brian made the call in an interactive session. Teaching content is retired.

- Three pillars: **Welcoming the Intimidated**, **Mindset and Perseverance**,
  **Gratitude and Gym Culture**. Rotate in that order; position is found from the most
  recent encouraging entries in `drafts.json`.
- **Member spotlights are out of scope for automation.** No named members, no
  celebrating one person's progress. That needs Brian's judgment about who appears and
  in what light, so he builds those by hand. Gratitude and Gym Culture is about the room
  and the habits of the place, not individuals.
- **No teaching posts.** No mechanisms, rep schemes, percentages, numbers to hit or myth
  takedowns. A concrete detail in passing is good; a lesson is not.
- The `pillars` field in `photos/INDEX.json` is tagged to the retired teaching pillars
  and will never name the three above. **Ignore it when matching** and select on `desc`.
  Empty rooms and equipment at rest suit Welcoming the Intimidated; solo effort and early
  light suit Mindset and Perseverance; the room, the rig, the flag and the lot at sunrise
  suit Gratitude and Gym Culture.
- If no photo suits the pillar that is up next, match the pillar to the image instead of
  forcing it, and leave the skipped pillar at the front of the queue.
- Style rotation cycles amber, ice blue, clay red, green by `style_index` in `used.json`.

### Retired pillars

Strength and Performance, Simple Nutrition, Real-Life Fitness, Community and Coaching and
Consistency and Accountability are no longer drafted. Their entries stay in the bank, the
drafts archive and the ledger as anti-repeat history: **never reuse their photos,
headlines or hero words.** Do not rewrite an old teaching concept into the new voice
either. Start from a real moment, not from an old post.

Approved teaching entries already in `queue.json` still ship, verbatim, until the bank
drains. Do not "update" one into the encouraging voice; it goes out as approved or not at
all. Meal Prep Monday recipe cards are built separately and are unaffected.

## Anti-repeat

**Published history is the source of truth. `state/used.json` is not.** Posts created
by hand in a platform UI, or by any other tool, never reach the ledger.

That history now lives in two places. Blotato holds everything from 2026-08-18 onward.
Buffer holds everything before it. **Check both or you will re-post old content.**

Before choosing a single concept, every run:

1. `blotato_list_posts` for `instagram` and `facebook`, plus Buffer `list_posts` with
   status `sent`, `channelIds` set, and a `dueAt` window covering **at
   least the last 7 days up to right now**. Do not use a fixed post count; recently sent
   posts fall outside a count-limited pull and that is exactly how repeats slip through.
2. Read every caption returned. Write the topics down before picking anything.
3. Only then consult `used.json` for pillar and style rotation position.

On 2026-08-11 two posts were rebuilt **word for word** from concepts published on
2026-08-10, because those posts were created outside this pipeline and the history pull
stopped before they sent. Both had to be deleted. Assume this failure mode is live.

On 2026-08-20 it happened again, from a different cause. `blotato_list_posts` returns at
most **250 items per page**, newest first, and this workspace publishes roughly 40 posts a
day across all its pages. One page therefore reaches back about **two days** no matter what
`since` you asked for. The run asked for 21 days, got two, saw no match, and rescheduled two
posts that had gone out four days earlier. **Always page through with the returned `cursor`
until it stops coming back, and judge coverage by the oldest post you actually saw, not by
the `since` you requested.** If coverage falls short, schedule nothing.

### The `used` flag in `queue.json`

History checking is the braces. `queue.json` schema v2 is the belt: every entry carries
`used`, `posted_on` and `posted_to`.

- `used: true` is **authoritative and outranks history**. An entry with it set is never
  scheduled again, no history lookup required.
- Set `used` true when an entry is **scheduled**, not when it publishes. The gap between
  the two is where duplicates get in.
- The nightly scheduler **only reads** this file; it has no push credentials. Flags get set
  by an interactive session or by hand, then pushed.
- Never flip `used` back to false to clear a low-water warning. Add new entries instead.
- The ledger **cannot detect a reused photo**. Posts before 2026-08-10 were uploaded
  straight into Buffer, so their image URLs say nothing about the source file. Brian
  flags photo reuse manually; record every flag in `photos_flagged_used_offline`.
- `photos/INDEX.json` describes all photos in the library with pillar fits, a
  `bottom_third_busy` flag for headline placement, and quality warnings.

## Copy

**Voice, as of 2026-09-15:** warm, plain-spoken and specific. Encouraging, not saccharine.
The reader should feel recognised rather than cheered at. Write like a coach who noticed
something true about their week, not like a poster on a locker room wall. Keep the dryness
and the respect for the reader's intelligence the teaching posts had, and drop the lecture.

Concreteness is what keeps this from becoming wallpaper. Anchor each post to one
recognisable moment: the walk from the car to the door, the set someone talked themselves
out of and then did anyway, the person who racks your plates without being asked, the lot
at five in the morning in January. Name the moment and stay in it. **A caption any gym in
the country could have posted is a failed caption.**

- No em dashes anywhere.
- Exactly 5 hashtags, in their own block after the caption, never inline.
- The first comment never contains hashtags, and its question must differ from the
  question closing the caption.
- No engagement bait. No "tag a friend", "share if you agree", "drop a comment".
  Close with a real question instead. Encouraging copy drifts toward bait much harder
  than teaching copy did; "tag someone who needs to hear this" is exactly the line never
  to write.
- Headlines stay warm and plain. No commands, no slogans. "Show up and grind" is wrong.
  "The hardest part is the parking lot" is right.

### Encouragement has failure modes

Avoiding these is part of the brief, not a nicety.

- **No shame, guilt or comparison as motivation.** No "no excuses". Nothing implying rest
  days, missed sessions or slow progress are a character defect. Nothing about what other
  people were doing while the reader slept.
- **Pain and exhaustion are not virtues.** Do not sell them as such.
- **Nothing about anyone's body, weight, size or appearance**, and never suggest the
  reason to train is how someone will look.
- **No promised transformations or outcomes.**
- No medical advice, no claims about treating injury or disease. Where a topic brushes a
  health condition, point at a doctor rather than giving a number.

Warmth means meeting people where they are, including the ones who are struggling. A post
that would leave a nervous beginner feeling worse has missed the brief completely.


## Working alongside Brian

Brian edits the same queue in the Blotato UI while sessions are running. If a post
disappears, flips state, or returns 404 shortly after being scheduled, that is very
likely him, not a
bug. Stop mutating, read the current state, and ask before recreating anything.
