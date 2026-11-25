# Saved designs

Each folder is a complete copy of the site at that point. Open its `index.html` to compare.

| Folder | What it is |
|---|---|
| `v1-lake-tap-to-light` | Lake palace scene, tap to light, fireworks |
| `v2-scroll-into-venue` | Footage slot that scrolls into the Shakti Vilas drawing |
| `v3-scratch-date` | v2 plus scratch-to-reveal date cards |
| `v4-city-palace-match-cut` | Scroll plays City Palace footage, which melts into a drawing traced from its last frame |
| `v5-lake-palace-detailed` | Back to the v1 lake scene with a redrawn, layered palace; keeps the scratch cards |
| `v6-gate-fly-through` | v5 plus a scroll fly-through: into the palace gate, down a hall of arches, out into the invitation |
| `v7-transition-options` | v6 plus a Preview bar to compare four scroll transitions: gate, envelope, diya, toran |
| `v8-gate-3d-hall` | Gate fly-through; the hall beyond the gate is a 60-frame Blender render (frames and scripts in its own `media/hall`) |
| `v9-layered-depth` | Shakti Vilas forecourt from v2, rebuilt in 2D depth layers; scrolling moves through them and past the gate |
| `v10-layered-lake` | v9's layered palace set on the lake: floating diyas, ghat steps with diyas, mountains; no fountain or forecourt |
| `v11-lake-v8-sky` | v10 with v8's fifteen candles in their v8 positions, and v8's mountains and sky |
| `v12-fewer-ghat-diyas` | v11 with half as many diyas on the ghat steps |

A new folder is added before every design change.
| v13-boat-date-rickshaw-lane | Palace stays; then invitation with both families, a boat that reveals the date, days to go, a rickshaw lane for the four functions (new Rajasthani dress illustration), Shakti Vilas with map card and travel, smaller night footer. Scratch cards, photos and the gate fly-through removed. |
| v14-daybreak-boat-day-lane | Night palace fades into a daytime lake at daybreak (jharokha scenery, boat and date, with days to go); blessings card is the first stop in a daytime rickshaw lane (haveli-ki-gali colours); Shakti Vilas section as in jharokha. Hero lamps and date removed, names smaller in Italiana, palace lower. |
| v15-music | v14 plus music when the diyas are lit (Vaaroon from 0:20, O Rangrez from 0:51) and a small temporary song switcher in the top right. |
| v16-light-before-scroll | v15, but the page stays on the palace until the diyas have lit; scrolling first lights them instead of skipping the animation. |
| v17-smoother-light-up | v16 with a lighter light-up: the palace is painted twice and blended, drawing resolution steps down if frames run long, and the song is loaded before the tap. |
| v18-vaaroon-only | v17 without the song switcher: Vaaroon plays from 0:20 to 2:55, fades out and loops. |
| v19-trimmed-song | v18 using a trimmed clip (media/vaaroon-clip.mp3, 2:35, fade in and out) instead of the full song; more space under the calendar button. |
| v20-title-and-icon | v19 with the tab title "Rishabh & Poojan" and a diya icon for the browser tab and phone home screen. |
| v21-kalash-icon | v20 with a kalash tab icon (brass pot, mango leaves, coconut, red swastik on maroon), as PNG and SVG so it shows in Safari too. |
| v22-boat-timing-shubh-vivah-top | v21 with less dead scroll after the boat, "Shadi" renamed to "Shubh Vivah", and a back-to-top button that keeps the light and the song. |
| v23-mute-button | v22 with a mute button in place of "Close it again": a speaker in the bottom-right corner, shown once the song starts, fades the song out and back in from the same spot (remembered while the tab is open). Back-to-top stacks above it; "Scroll to ride" moved clear of both. |
| v24-stories-sideways-lane | v23 with the rickshaw lane one screen tall and moving only sideways (swipe, drag, trackpad, arrow keys, dots with names; the next doorway peeks in, a one-time nudge and a hint), and a photo section between the lane and Shakti Vilas: a marigold-ring cover that opens the photos as stories (7 s each, hold to pause, tap sides, swipe down or × to close, closes after the last photo). On a computer the viewer is a card the shape of each photo. Photos come from website/photos (scripts/build_photos.py). |
| v25-fewer-diyas-scroll-lane-black-viewer | v24 with half as many diyas on the ghat steps and 11 instead of 15 in the water; the rickshaw lane rides on scrolling down again and also on a sideways swipe, drag, trackpad, arrow keys or dots (they scroll the page to match; the one-time nudge is gone); and the photo viewer on a phone sits on black, like the shaped card. |
| v26-smoother-palace-to-lake | v25 with a lighter palace-to-lake transition: the palace canvas stops redrawing once the daybreak starts covering it (its last frame is scaled instead), the morning lake is split into layers (sky, noon sky, scene, two sets of ripples) so scrolling and the ripples no longer repaint it, the date is revealed through a sliding window instead of a changing clip, and on phones the page follows the finger closely instead of easing behind it. Looks the same. |
| v27-story-zoom-smooth-lane | v26 with two-finger zoom on the photos, as on Instagram stories (the story pauses, the photo follows the fingers and springs back when they lift; zooming in loads the sharpest file), and a smoother sideways ride: the street now stays under the finger instead of lagging then racing, carries on from the finger's speed when let go instead of stopping and lurching, and a dot glides across doorways without stalling at each one. |
| v28a-quiet-lake | One of two candidates from `storyboards/hero-lit.html` (A), built on v27; `website/index.html` is unchanged until one is picked. The ghat is gone; 7 diyas float on the water, placed by hand in a loose V that opens towards the viewer (the one lit before the tap sits at the bottom middle); every diya has a smaller glow. Garland, fireworks and the light-up as in v27. |
| v28b-steps-in-front | The other candidate (B), built on v27. Three dark stone steps across the bottom replace the ghat, with a row of diyas along each of the two lower edges (the middle one at the water's edge is lit before the tap); 3 diyas float on the water; every diya has a smaller glow; "Tap to light the diyas" and "Scroll down" sit in the middle of the top step. Garland, fireworks and the light-up as in v27. |
| v29-quiet-lake | v28a picked and finished: the diya in the middle of the water is gone and each line has one more, so eight diyas float in two lines of four that open towards the viewer like a V. The nearest on the left, just above "Tap to light the diyas", is the one already lit before the tap. No ghat; smaller glow round every diya. Garland, fireworks and the light-up as in v27. |
| v30-garland-space-dark-diyas | v29 with space under the garland: the names, the palace and the mountains move down together and the lake gets that much shorter (44 px on a 390 × 844 phone, 66 px on a 1440 × 900 computer, as a share of the screen height; the morning lake follows the new waterline). No diya is lit before the tap any more. Options are in `storyboards/hero-gap.html`. |
