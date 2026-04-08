# Project Vision & Key Issues

## Objective

Build a **doom-scrolling app for academic content** — like Reddit, but for physics
papers and textbooks. Users scroll through a feed of bite-sized snippets extracted
from technical PDFs, with the option to view AI-generated summaries that make each
snippet self-contained and accessible.

### Core Experience

- A scrollable feed of **snippet cards** from academic sources
- Each card shows extracted text, images/diagrams, and source attribution
- A **toggle to replace raw snippets with AI summaries** that add context
- **"Read more" links** to jump to the original PDF at the exact page
- MathJax rendering for equations

### What Makes It Work

The key insight is **variable reward** — you never know if the next scroll will
surface something fascinating. This is the same mechanic that makes Reddit and
Twitter addictive, applied to academic content. Research students already spend
hours browsing papers aimlessly; this app channels that impulse productively.

### Key Tension

Reddit posts are self-contained. A random paragraph from page 47 of a turbulence
paper often isn't. **AI summaries solve this** — they can make any snippet
understandable without requiring the reader to find and read the full source.

---

## Key Issues

### 1. Snippet Extraction Quality (Critical)

The current extraction pipeline (`pdf_pre_processing.py`) produces low-quality
snippets that won't sustain a doom-scroll experience.

**Problems:**

- **Only 1 random paragraph kept per page** (line 89) — picks one paragraph via
  `random.choice()` and discards the rest. A feed needs all good paragraphs.
- **Crude paragraph splitting** (line 87) — splits on `\n\n`, which produces
  broken results from PDFs: split equations, headers/footers, half-sentences
  from multi-column layouts.
- **Minimum length too low** (line 87) — 20 characters allows junk like
  "See Figure 3.2 below." A doom-scroll snippet needs substance.
- **No quality filtering** — table of contents, references, page headers/footers,
  and equation-only blocks all pass through as "content."
- **No context** — a single paragraph from a dense paper is often meaningless
  without surrounding text.

### 2. Content Source Reliability

- All 7 PDF URLs in `resources.json` are from academic servers that may go
  offline, return 403, or change paths at any time.
- No fallback or caching strategy for unavailable sources.
- Content library is limited to fluid dynamics/turbulence — too narrow for
  general physics audience.

### 3. UI Is Single-Snippet, Not a Feed

- Current UI (`web_display.py`) shows one snippet at a time with a "Get New
  Content" button — this is the opposite of a doom-scroll experience.
- Needs to become a scrollable feed with multiple cards, infinite scroll or
  "load more," and smooth transitions.

### 4. No AI Summary Integration

- `image_summarizer.py` and `random_physics_summarizer_2.py` exist but are not
  wired into the main app.
- The toggle between raw snippet and AI summary is a core feature that doesn't
  exist yet.

---

## Current Priorities

1. **Evaluate and refine the idea** — this document.
2. **Build a feed UI** that surfaces random snippets from technical source material
   with an option to replace snippets with AI summaries.

### Not Priority Right Now

- Expanding the content library (make it work well with limited content first)
- Topic tags / filtering (good idea, not core)
- Bookmarking / saving snippets
