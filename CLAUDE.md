# Daily wojak content run for @dailytipsonself

This repo holds everything needed to make and schedule 4 wojak self-improvement posts a day for the Instagram account @dailytipsonself, posted through Eden: 3 slideshow Reels with music and 1 carousel.

Files:
- `pack/` the user's 178 wojak images. `list.txt` maps index numbers to files. `CATALOG.md` describes what each useful index looks like and when to use it. Read CATALOG.md before picking images.
- `carousel.py` the slide renderer (1080x1080 square slides, cream background, Poppins fonts in `fonts/`).
- `reel.py` turns slides into a 9:16 slideshow Reel (silent video; Instagram adds the music).
- `tools.py` helpers: `render` (carousel JPEGs), `sheet` (preview sheet), `reel` (Reel mp4 plus a frames preview), `slots` (epoch ms for a day's slots).
- `specs/` example specs for every layout. Copy their structure.
- `posted.md` every topic already used. Never repeat an exact topic.
- `posts/YYYY-MM-DD/<slug>/` files Eden imports by public link.

## Daily schedule (Asia/Manila)
| Time | Format |
|---|---|
| 07:00 | Slideshow Reel with music |
| 12:00 | Carousel (no music; Instagram doesn't allow music on carousels posted through Eden) |
| 17:00 | Slideshow Reel with music |
| 22:00 | Slideshow Reel with music |

Every post goes to Instagram (Reel or carousel) and to TikTok (photo carousel with auto music) at the same time. Every post is a new topic.

## Steps for each run
1. **Pick the target day.** The run fills TOMORROW (Manila date of the run + 1). Get the 4 slot times with `python3 tools.py slots YYYY-MM-DD`. Check Eden `eden_list_scheduled_posts` (status `scheduled`): skip any slot that already has an Instagram post within 30 minutes of it. If all 4 are taken, stop and report that the day is already full.
2. **Research.** Eden `eden_search_social_content`, scope global, platforms instagram/tiktok/twitter/youtube, `minOutlierScore` 4 or more, `since` month or quarter, queries around men's self-improvement (discipline, habits, confidence, dopamine, money, fitness, social skills, lessons, mindset). Results are large and get saved to a file, so summarize them with a short python script (outlier, platform, username, views, url, first 230 chars). Pick one winner per open slot whose angle fits wojaks and isn't in `posted.md`. Prefer high outlier scores and clear list or comparison structures.
3. **Write one spec per post** in `specs/<slug>.json`. Vary layouts across the day. Reels work best with 5 to 8 slides and short text per slide; the carousel can go up to 9. Layout kinds:
   - `cover` (kicker, title with `*highlight*`, one image or `[before, after]`)
   - `single` (label, head, img, sub; optional `fix: true` plus `badge` text; optional `stamp: "STOP"`; optional `level: [n, total]` progress bar)
   - `split` (head, ltag, rtag, l: [img, text], r: [img, text]; `flip: true` makes the left side green)
   - `duo` (two numbered items per slide; `n` can be a number, a time like 6:00, or a word)
   - `grid` (2x2 cells of [img, label])
   - `statement` (dark full-text twist slide, `pre` and `text`)
   - `end` (head, optional sub, img; adds the follow button)
   Rules: the highlight marks every word inside the stars, so never put a word inside the stars that also appears elsewhere in the same title. Don't reuse an image within one post. Copy is specific and concrete, no generic self-help phrases, never uses em dashes.
4. **Render and check.**
   - Carousel: `python3 tools.py render specs/<slug>.json /tmp/<slug>` then `python3 tools.py sheet /tmp/<slug> /tmp/<slug>.jpg`.
   - Reel: `python3 tools.py reel specs/<slug>.json /tmp/<slug> "<short header, under 40 characters>"`. It also writes `/tmp/<slug>/frames.jpg`, and run `python3 tools.py sheet /tmp/<slug> /tmp/<slug>.jpg` for the slides.
   LOOK at every preview with the Read tool. Fix text overflow, overlaps, wrong images or bad highlights, then re-render.
5. **Publish files to GitHub.** Carousel: copy `/tmp/<slug>/jpg/*.jpg` to `posts/<post date>/<slug>/`. Reel: copy `/tmp/<slug>/reel.mp4` to `posts/<post date>/<slug>/reel.mp4`. Commit and push to `main`.
6. **Import into Eden** with `eden_import_scheduling_media` and the raw link `https://raw.githubusercontent.com/Aker322/wojak-carousels./main/posts/<date>/<slug>/<file>` (note the period in the repo name). For carousels, import every slide in order.
7. **Schedule** with `eden_schedule_post`: `platforms: ["instagram"]`, `scheduledFor` from step 1, `timezone: "Asia/Manila"`, `idempotencyKey` like `wojak-<date>-<slug>`, and the caption.
   - Carousel: media = the imported slides in order, each with width and height 1080.
   - Reel: media = the imported mp4 (mimeType video/mp4, width 1080, height 1920), plus `perPlatform.instagram.music` = `{audioId, title, artist, volume: 100, videoVolume: 0}`. Use a different track for each of the day's 3 Reels, from:
     - Dark (Slowed), Tony Dark Eyes, audioId 2603949126473975
     - Do Ma Thing, Tony Dark Eyes, audioId 1347176186322399
     - Knockout, Adam Griffith, audioId 1108285910189784
     If a track is refused, search `eden_search_instagram_music` (phonk, dark motivational, gym) and use a returned audioId. Never invent one.
7b. **TikTok (every post, same slot).** Cross-post every post to the TikTok account @dailytipsonself as a photo carousel with TikTok's auto music, because TikTok doesn't accept chosen music on scheduler-uploaded videos:
   - Make 9:16 stills: `python3 tools.py tiktok /tmp/<slug> /tmp/<slug>_tt "<short header>"` (use the NO_SWIPE slide renders; for a carousel slot, re-render the slides with `NO_SWIPE=1 python3 carousel.py ...` into a separate folder first). Look at one still before posting.
   - Push the stills to `posts/<date>/<slug>/tiktok/tt_NN.jpg`, import each in order with `eden_import_scheduling_media`.
   - Schedule a separate `eden_schedule_post` with `platforms: ["tiktok"]`, the same `scheduledFor`, the stills as media (width 1080, height 1920), `perPlatform.tiktok.autoMusic: true`, `perPlatform.tiktok.text` = the same caption, and `idempotencyKey` like `wojak-<date>-<slug>-tt`.
8. **Log.** Append each topic with its date, time and format to `posted.md`. Delete `posts/` folders older than 7 days (Eden keeps its own copies). Commit and push.
9. **Report** each post's time, format, title, music track (Reels) and source post link in a short final message.

## Caption format
Short punchy lines, specific, no em dashes, no generic self-help language, no question at the end. Then a blank line, then exactly:
`Follow @dailytipsonself for more short and actionable advice like this`
Then a blank line and at most 5 hashtags, always including #wojak and #selfimprovement.

## If something fails
- Eden import or scheduling fails: retry once, then report it. Never post anything that wasn't checked in step 4.
- Never schedule outside the 07:00 / 12:00 / 17:00 / 22:00 slots and never post to platforms other than Instagram and TikTok.
- A Reel must never go out without music. If no track can be attached, schedule nothing for that slot and report it.
