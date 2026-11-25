# Rishabh & Poojan wedding site

- The live page is `website/index.html`, one self-contained file. Pushing to `main` deploys it to GitHub Pages through `.github/workflows/deploy.yml`, which publishes only `index.html`, `media/vaaroon-clip.mp3` and `website/photos/` (the `.webp` files and `photos.js`).
- After each design change, a full copy of the page goes in `website/versions/vNN-short-name/index.html`, with a row added to `website/versions/README.md`. In the copy, point the song at `../../media/vaaroon-clip.mp3` and set `PHOTOS_BASE` to `'../../photos/'`.
- Storyboards for proposed changes live in `storyboards/`. The user picks options from a storyboard before anything is built, and pushes changes together once they are final.

## Photos: adding, replacing or reordering

Always use the script. Never copy camera files into the repo or point the page at them.

```
python3 scripts/build_photos.py "/path/to/folder" [--order "cover.jpg,second.jpg,..."]
```

- The folder must hold the **complete set** to show. The script deletes and rewrites every `.webp` in `website/photos/`. To add photos, put the new ones beside the existing originals and run it on that folder.
- Order is by file name unless `--order` is given; any files not named in `--order` follow in name order. **The first photo is the cover** (the marigold ring).
- It needs `sips` (built into macOS), `cwebp` (`brew install webp`) and `ffmpeg`, all already installed here.
- About 25 seconds for 12 photos of 45 megapixels.

What the script does, and why. Keep these when changing it:

1. **Turns each photo upright** using its EXIF orientation tag. WebP files carry no orientation, so a phone or camera photo stored sideways would otherwise show sideways. One of the current photos (`0Q6A5609`) is stored this way.
2. **Writes three WebP sizes**: 720, 1280 and 2048 px wide, never larger than the original. The settings are quality 80/82/80, `-m 6` and `-sharp_yuv`. Portraits use the full width (the long side is rounded up).
3. **Keeps the colour profile.** The photos are Display P3. The ICC profile is embedded (`-metadata icc`), so colours stay as edited on phones and Macs. Don't convert to sRGB or drop the profile, or the photos look washed out.
4. **Strips all other metadata** (camera details and GPS location), since the site is public.
5. **Makes a tiny copy of each photo**: 40 px wide, blurred and darkened, about 300–700 bytes. It is embedded as base64 in `photos.js`. The page shows it in the photo's place while the full photo loads, so something appears at once without the device running a costly CSS blur. (Behind the photos the viewer is plain black, on phones and computers.)
6. **Writes `website/photos/photos.js`**, the photo list as a small script (`window.__PHOTOS = {...}`) rather than JSON, because browsers refuse to `fetch` a JSON file when the page is opened straight from the folder (`file://`), and the photo section would hide itself. It holds `source`, `file`, `w`, `h`, `widths`, `lqip`, `caption` and `focus` for each photo. `caption` (shown at the bottom of a story) and `focus` (the CSS `object-position` of the round cover crop) can be edited by hand. Both are kept on the next run, matched by the original file name.

How the page loads them (the "Photographs" script at the end of `index.html`). Don't regress this:

- Nothing photo-related is fetched until the section is within 1200 px of the screen. Then the page loads `photos.js` (by adding a script tag) and the cover.
- Every `<img>` uses `srcset` with all widths, plus a `sizes` value set to its laid-out CSS width. The browser then picks the right file for the screen's density: about 720 for the cover, 1280 on phones, and up to 2048 for wide photos on large screens.
- The viewer loads only the photo on screen and its neighbours (`ensure(cur ± 1)`). Pointing at the cover preloads the first photo, after the layout is set so it fetches the right size.
- Each photo's 7 seconds (`DUR`) start only once it has decoded. Holding a finger or the mouse on it pauses it.

After rebuilding, check:

- Open `website/index.html` both straight from the folder and served locally (`python3 -m http.server` in `website/`).
- On a phone-sized and a desktop-sized window, open the stories and look at a portrait photo, a landscape photo and the cover crop. Confirm any rotated photos are upright.
- Keep the files in proportion: around 300 KB or less per 1280 file, and about 5 MB for twelve photos at all sizes.

## Stories viewer settings

- `DUR` in `index.html`: how long each photo shows (7000 ms).
- On a phone (narrower than 760 px) the viewer is full screen. On anything wider it is a card the shape of each photo, as large as the screen allows, which the couple chose over a full-screen layout.
