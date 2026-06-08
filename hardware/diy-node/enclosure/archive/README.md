# Enclosure archive — superseded versions

These are the designs that came before the current one. **None of them should be printed for deployment as-is** — each was superseded for a concrete reason, kept here because the lineage is itself workshop material: every folder is a lesson in designing for FDM and for real parts. Review, improve, or cannibalise — don't blindly print.

| Version | What it is | Why it was superseded |
|---|---|---|
| [`v1-box/`](v1-box/) | Louvered Stevenson-screen box, 3 flat parts | Never printed. Flat panels + slot louvers are laser-cutter thinking — it under-uses the printer. Also sized for the bare HM3301 can and a 5×7 perfboard. |
| [`v2-lantern/`](v2-lantern/) | D-section revolved lantern, 2 parts, snap-fit | Printed and failed. The PM bay fit the bare 40×38 can, but the Grove module is the can on an **80×40 carrier PCB**. The snap joint jammed: 0.2 mm clearance, guide towers colliding the cup wall. |
| [`v3-gourd/`](v3-gourd/) | Lantern with a wide rounded-rect foot for the full module, screwed joint | Worked on paper, fit the real module, joint fixed — but the 88×48 foot makes it bulky. Replaced by the vertical-module column. |
| [`v4-column/`](v4-column/) | Slim Ø66 column, module vertical behind a ring-louvered grille, text labels, LiPo bay | Functionally sound — its core architecture carries on. Superseded aesthetically: smooth rings and debossed text gave way to the pine-cone scale skin and physical footprint guides. Print this one if you want the plainest, fastest build. |

Each folder has the parametric `enclosure.scad`; regenerate STLs with the commands in the main [enclosure README](../README.md). Dimensions of record for the Grove HM3301 module (from Seeed's Eagle files, see [`../ref_hm3301_board.pdf`](../ref_hm3301_board.pdf)): carrier 80 × 40 mm, Ø3.2 holes at ±36/±16, bare can 40 × 38 × 15 on top.

The recurring lessons, so the next fork doesn't repeat them: design for the **full purchased module**, not the bare sensor in the datasheet; joints need hard stops, ≥0.5 mm radial clearance, and chamfered lead-ins at FDM tolerances; rain protection is geometry (skirts, sight-line breaks, downward apertures), not gaskets; and verify with full renders — OpenSCAD's preview lies about `intersection()` + `rotate_extrude`.
