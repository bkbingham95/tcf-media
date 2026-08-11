# Tough Country Fitness posting rules

Standing rules for the photo-to-Instagram pipeline. Read this before any run.

## Scheduling

- **Instagram only right now.** Channel `tcfitness702`, id `6a74c8ea99afb4434913b71c`.
  Do not post to the Facebook page unless Brian asks.
- **Posting schedule** (America/Los_Angeles, all seven days):
  `05:00, 09:00, 12:00, 13:30, 15:00, 17:30`
- **If a requested time has already passed, do not ask and do not skip the post.
  Fall back to the next available slot.** In Buffer that is `mode: "addToQueue"`,
  which lands on the next open slot in the schedule above and skips filled ones.
  Say which slot it resolved to.
- Never schedule into a slot that already has a post. Check first with `list_posts`
  filtered to the target day and channel.

## Buffer mechanics

- Always schedule with `execute_mutation` on `createPost`. **Never** the `create_post`
  tool: it silently drops the first comment.
- Every post carries a `firstComment`. No exceptions.
- Instagram metadata: `type: "post"`, `shouldShareToFeed: true`. Never reel or story,
  the 4:5 crop is rejected there.
- `schedulingType: "automatic"`, `needsApproval: false`, `aiAssisted: true`.
- After every schedule call, read the post back with `get_post` and confirm the image
  dimensions, alt text, and first comment actually landed. Do not report done without it.
- On HTTP 429, the fix is disconnecting and reconnecting the Buffer connector. Waiting
  does not clear it.

## Image hosting

- Buffer only accepts images by public URL. The cloud sandbox can reach GitHub and
  nothing else, so the repo is the image host:
  `https://raw.githubusercontent.com/bkbingham95/tcf-media/main/out/<date>/slot<n>.jpg`
- The composite must be committed and pushed **before** scheduling. Buffer downloads
  the image at creation time and a 404 fails the post.
- The sandbox cannot push to the repo. Either Brian pushes from Terminal, or the repo
  gets attached as a session source at task start, which grants real push credentials.
- `device_bash` cannot delete files, so git leaves a stale `.git/index.lock`. Any push
  command handed to Brian must start with `rm -f .git/index.lock`.

## Content

- Five pillars: Strength and Performance, Simple Nutrition, Real-Life Fitness,
  Community and Coaching, Consistency and Accountability. Rotate in order; the current
  position lives in `state/used.json` under `next_pillars`.
- Simple Nutrition has **no supporting photography** in the library. Either skip it with
  a note or ask Brian for food images. Do not force an unrelated gym photo onto it.
- If no photo fits the pillar that is up next, match the pillar to the image instead of
  forcing it, and leave the skipped pillar at the front of the queue.
- Style rotation cycles amber, ice blue, clay red, green by `style_index` in `used.json`.

## Anti-repeat

- `state/used.json` concept history is **not** sufficient on its own. Before picking a
  concept, pull real post history with `list_posts` filtered to `sent` and read the
  captions. A concept was duplicated on 2026-08-11 because the ledger stopped at 08-07.
- The ledger **cannot detect a reused photo**. Posts before 2026-08-10 were uploaded
  straight into Buffer, so their image URLs say nothing about the source file. Brian
  flags photo reuse manually; record every flag in `photos_flagged_used_offline`.
- `photos/INDEX.json` describes all photos in the library with pillar fits, a
  `bottom_third_busy` flag for headline placement, and quality warnings.

## Copy

- No em dashes anywhere.
- Exactly 5 hashtags, in their own block after the caption, never inline.
- The first comment never contains hashtags, and its question must differ from the
  question closing the caption.
- No engagement bait. No "tag a friend", "share if you agree", "drop a comment".
  Close with a real question instead.
