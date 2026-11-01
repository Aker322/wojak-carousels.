# Daily wojak carousel run for @dailytipsonself

This repo holds everything needed to make and schedule 3 wojak self-improvement carousels a day for the Instagram account @dailytipsonself, posted through Eden.

Files:
- `pack/` the user's 178 wojak images. `list.txt` maps index numbers to files. `CATALOG.md` describes what each useful index looks like and when to use it. Read CATALOG.md before picking images.
- `carousel.py` the renderer (1080x1080 square slides, cream background, Poppins fonts in `fonts/`).
- `tools.py` render to JPEG and build a preview sheet.
- `specs/` example specs for every layout. Copy their structure.
- `posted.md` every topic already used. Never repeat an exact topic.
- `posts/YYYY-MM-DD/<slug>/` slide JPEGs that Eden imports by public link.

## Posting rules
- 3 posts a day at 06:00, 14:00 and 22:00 Asia/Manila. Instagram only.
- Each run fills the next 3 free slots after the latest post already scheduled in Eden.
- Square 1080x1080 slides, 5 to 9 slides per carousel.

## Steps for each run
1. **Find the queue end.** Eden `eden_list_scheduled_posts` with status `scheduled`. Take the latest `scheduledFor` among Instagram posts. The next 3 slots are the next three of 06:00 / 14:00 / 22:00 Manila after that time and after now. If nothing is scheduled, start from the next upcoming slot.
2. **Research.** Eden `eden_search_social_content`, scope global, platforms instagram/tiktok/twitter/youtube, `minOutlierScore` 4 or more, `since` month or quarter, queries around men's self-improvement (discipline, habits, confidence, dopamine, money, fitness, social skills, lessons, mindset). Results are big; they get saved to a file, so summarize them with a short python script (outlier, platform, username, views, url, first 230 chars). Pick 3 winners whose angle fits wojaks and is not in `posted.md`. Prefer high outlier scores and clear list or comparison structures.
3. **Write 3 specs** in `specs/<slug>.json`. Vary the layout across the 3 posts. Layout kinds:
   - `cover` (kicker, title with `*highlight*`, one image or `[before, after]`)
   - `single` (label, head, img, sub; optional `fix: true` plus `badge` text; optional `stamp: "STOP"`; optional `level: [n, total]` progress bar)
   - `split` (head, ltag, rtag, l: [img, text], r: [img, text]; `flip: true` makes the left side green)
   - `duo` (two numbered items per slide; `n` can be a number, a time like 6:00, or a word)
   - `grid` (2x2 cells of [img, label])
   - `statement` (dark full-text twist slide, `pre` and `text`)
   - `end` (head, optional sub, img; adds the follow button)
   Rules: the highlight marks every word inside the stars, so never put a word inside the stars that also appears elsewhere in the same title. Don't reuse the same image twice in one carousel. Copy is specific and concrete, no generic self-help phrases, and never uses em dashes.
4. **Render and check.** `python3 tools.py render specs/<slug>.json /tmp/<slug>` then `python3 tools.py sheet /tmp/<slug> /tmp/<slug>.jpg` and LOOK at the sheet with the Read tool. Fix text overflow, overlaps, wrong images or bad highlights, then re-render.
5. **Publish slides to GitHub.** Copy `/tmp/<slug>/jpg/*.jpg` to `posts/<YYYY-MM-DD of the post>/<slug>/`. Commit and push to `main`.
6. **Import into Eden.** For each slide call `eden_import_scheduling_media` with `https://raw.githubusercontent.com/Aker322/wojak-carousels./main/posts/<date>/<slug>/slide_NN.jpg` (note the period in the repo name). Keep slide order.
7. **Schedule.** `eden_schedule_post` with `platforms: ["instagram"]`, `scheduledFor` epoch ms for the slot, `timezone: "Asia/Manila"`, an `idempotencyKey` like `wojak-<date>-<slug>`, the imported assets in order (width and height 1080), and the caption.
8. **Log.** Append each topic with its slot to `posted.md`. Delete `posts/` folders older than 7 days (Eden keeps its own copies). Commit and push.
9. **Report** the 3 titles, times and source posts in a short final message.

## Slideshow Reels (only when the user asks for one)
The daily format is carousels. Instagram does not allow music on carousels posted through Eden, so carousels go out without music. Make a slideshow Reel only when the user asks for one, and every Reel must carry music:
1. Render the slides with `NO_SWIPE=1 python3 carousel.py specs/<slug>.json /tmp/<slug>`, then `python3 reel.py /tmp/<slug> /tmp/<slug>.mp4 "<short header>"`. Check a few frames with ffmpeg before posting.
2. Push the mp4 to `posts/<date>/<slug>/reel.mp4` and import it with `eden_import_scheduling_media`.
3. Schedule it with `perPlatform.instagram.music` set to a track from Instagram's library (get the id from `eden_search_instagram_music`; never invent one), `volume: 100`, `videoVolume: 0`. Default tracks, rotate between them:
   - Dark (Slowed), Tony Dark Eyes, audioId 2603949126473975
   - Do Ma Thing, Tony Dark Eyes, audioId 1347176186322399
   - Knockout, Adam Griffith, audioId 1108285910189784

## Caption format
Short punchy lines, specific, no em dashes, no generic self-help language, no question at the end. Then a blank line, then exactly:
`Follow @dailytipsonself for more short and actionable advice like this`
Then a blank line and at most 5 hashtags, always including #wojak and #selfimprovement.

## If something fails
- Eden import or scheduling fails: retry once, then report it. Never post anything that wasn't checked in step 4.
- Never schedule outside the 06:00 / 14:00 / 22:00 slots and never post to platforms other than Instagram.
