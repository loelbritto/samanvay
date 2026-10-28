# Samanvay identity — 28 October 2026

The implemented recommendation is **Shared direction**: a custom two-part S monogram. Two open channels align into one recognisable letter while an eight-unit centre gap keeps the shapes separate. That distinction reflects the product: a shared institutional plan does not merge complaints or replace their owners.

The mark is original geometric artwork authored for this prototype. It uses no government insignia, official SIH mark, national emblem or AICTE visual. It is not a trademark clearance or an official identity claim.

## Six concepts explored

| Concept | Idea | Decision |
| --- | --- | --- |
| Shared direction | Two independent channels form S | Selected as the implementation default; memorable name initial and strong silhouette |
| Common ground | Opposing voices share a central interval | Retained as an alternative; dialogue is clear, monogram less direct |
| Open knot | Two folded forms align without closing | Retained; connection is expressive, but less identifiable as Samanvay |
| Records in concert | Distinct vertical records share a baseline | Retained; functional but more easily mistaken for a chart |
| Assembly | Separate participants surround a common plan | Retained; useful collaboration metaphor, more detail at small sizes |
| Next step | Reciprocal routes convey follow-through | Retained; literal arrows are less distinctive than the S silhouette |

The user delegated creative choices. Selection is the implementation recommendation, not a claim that the user approved a visual proof.

## Assets

- `frontend/public/brand/samanvay-mark.svg`: monochrome `currentColor` source, viewBox `0 0 100 100`.
- `samanvay-mark-teal.svg` and `samanvay-mark-ivory.svg`: explicit colours for external `<img>` use. A standalone `currentColor` SVG loaded as an image does not inherit the parent page's text colour.
- `samanvay-wordmark-dark.svg` and `samanvay-wordmark-light.svg`: accessible mark/name lockups, 441 × 100 coordinate space. Lowercase **samanvay.**, Manrope 700, with a clay `#b86b28` period, aligned to the application's actual identity.
- `samanvay-mark-16.png`, `-32.png`, `-128.png`, `-1024.png`: transparent teal raster exports.
- `samanvay-wordmark-dark.png` and `samanvay-wordmark-light.png`: transparent 1323 × 300 exports.
- `wordmark-provenance.json`: source font hash, glyph IDs, exact advances, tracking and outline extraction method.
- `MANROPE-OFL.txt`: the installed font package's SIL Open Font License.
- `frontend/public/brand/concepts/`: six SVG alternatives, `concepts.json` rationale manifest and self-contained `index.html` comparison gallery.

The gallery adapts the Logo Generator skill's comparison template into a dependency-free document: six concepts, large inspection view, size slider, light/dark comparison and SVG downloads. Its controls are local presentation controls only. No network service, application setting or complaint record is modified.

## Usage

Use deep teal `#123b3b` on ivory `#f8f6ef`, or ivory on deep teal. The mark itself works in one colour; clay/saffron may support the surrounding interface but is not required to understand the symbol. Keep the two source paths intact. Do not join their centre gap, rotate the components independently or place them in an official-looking seal.

Use a minimum 16px artboard for the standalone mark and at least 32px for routine application branding. The SVG artboard includes 13 units of side breathing room. Wordmark letters are actual outlined Manrope 700 glyphs from the already installed `@fontsource/manrope` 5.3.0 package, with explicitly authored spacing. They require no installed font and do not fall back to operating-system typography. The app retains live text using its self-hosted Manrope font; the downloadable lockup is a fixed artwork composition.

## Verification and limits

Commands actually run included reading the Logo Generator skill, its pattern reference and showcase template; a Python XML check over all 11 SVGs; a check for exactly six gallery concepts and no external gallery dependencies; and raster exports using the bundled Sharp library. The skill's CairoSVG exporter was inspected, but CairoSVG is not installed, so Sharp was used for faithful SVG rasterisation instead. Fonttools and fontkit were absent. The exact nine required characters were extracted directly from the installed Manrope 700 WOFF using Python standard-library WOFF decompression, Unicode cmap lookup and simple TrueType quadratic-contour parsing. Every requested glyph was a supported simple outline; no approximation or new tool installation was needed. The source SHA-256 and glyph advances are recorded in `wordmark-provenance.json`.

Observed: all 11 SVGs parse; every SVG has an accessible title and `currentColor` paths; no embedded script or external asset references are present. Both final wordmark SVGs contain no `<text>` elements or external font dependencies. The selected 128px and 16px PNG marks and final outlined dark wordmark were visually inspected as standalone artwork. The marks retain two separate paths and no raster background. Initial system-font wordmarks were superseded by the outlined lowercase Manrope identity and their PNGs were regenerated.

The interactive gallery has **not** been exercised in a browser. The existing local-origin browser policy block is not bypassed by this standalone artwork inspection. Current application layout, keyboard and zoom checks remain the parent task's separate acceptance gate. No Gemini credentials or generated mockup service are configured, and no photorealistic showcase images are claimed.
