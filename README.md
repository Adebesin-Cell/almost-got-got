# Almost Got Got

A field guide to the social-engineering scams aimed at all of us. Fifteen plays, the one line that beats each, and the real cases behind them.

**Live:** https://almostgotgot.vercel.app

It's a CPE 510 (Computer Security Techniques) project at the Federal University of Technology, Akure. Our element was **Policy**, the first of NIST SP 800-83's four malware-prevention elements. Instead of a policy nobody reads, we built one people remember.

## The idea

Most policy reads like a legal notice. This one reads like a playbook: the attacker's **move** on one side, your **counter** on the other. Tap a card to flip it.

- **15 plays** — OTP theft, WhatsApp takeover, deepfake voice, quishing, pig butchering, and more. Each has a move, a counter, and a real cited case.
- **6 habits** — the handful of reflexes that beat almost everything.
- **The pattern** — what 100 real scam reports, gathered across 21 named locations, had in common — with charts regenerated from the raw CSV by `scripts/build_charts.py`.
- **The case file** — six publicly documented incidents (npm maintainers, ReliaQuest, Levi Strauss, Apollo, Retool, Arup) showing the same moves land on trained professionals.
- **The policy** — the adoptable version underneath, grounded in SP 800-83.
- **Read as a book** — the same content as a page-turning field manual.

Nobody who shared a story is quoted word for word. We used the reports to find the pattern.

## How it's built

One file, no build step. `index.html` is a single self-contained page: inline CSS, vanilla JS, fonts from Google Fonts. No framework, no bundler, no dependencies.

- **Type:** Fraunces (display) + Jost (text), loaded from Google Fonts.
- **Theme:** follows the visitor's light/dark setting; a toggle overrides it and remembers the choice in `localStorage`.
- **Book view:** a stacked-page flip built with CSS 3D transforms; the pages are generated from the page's own content, so there's one source of truth.

### Query params (for rendering, not visitors)

- `?theme=light` / `?theme=dark` — force a theme (used for screenshots).
- `?still=1` — show all scroll-reveal content immediately (used for screenshots).
- `#book` — open the book view on load.

## Run it

It's static. Open the file, or serve the folder:

```bash
npx serve .
# then open http://localhost:3000
```

## Regenerate the assets

The OG card, the favicon, and the blog screenshots are all rendered from HTML with headless Chrome. One script does it:

```bash
./scripts/shots.sh
```

It renders `og.html` → `og.png`, `icon.html` → `icon.png`, and grabs page + book screenshots. Edit `og.html` or `icon.html` and re-run to update them.

## Deploy

```bash
vercel deploy --prod
```

The project is already linked (`.vercel/`). Deployment protection is off so the link is public.

## Structure

```
index.html      the whole site
og.html         source for the social-share card  -> og.png
icon.html       source for the favicon            -> icon.png
scripts/shots.sh  regenerates the images above
```

## Credits

Plays researched by Emmanuel Alonge, Ayoola Omotayo, Victor Emmanuel, Adeoti Oluwatimilehin, Peter Aremu, Adesanya Olamide, Ayomide Adeniyi, Adesida Inioluwa, and Adebesin Tolulope, plus everyone who shared a report.

## Sources

- **NIST SP 800-83** — Guide to Malware Incident Prevention and Handling.
- **William Stallings**, *Network Security Essentials: Applications and Standards*, 6th ed. (Pearson, 2017), §10.10, pp. 360–361.
- **Matt Bishop**, *Introduction to Computer Security* (Addison-Wesley, 2005), pp. 7, 19.
- Real cases: the Arup deepfake fraud (CNN, 2024), the NDDC scholarship warning (The PUNCH, 2025), Kaspersky, FBI IC3, and FTC advisories.

*Technology for Self Reliance.*
