# Assets

Static assets (diagrams, images, exported Mermaid renders) referenced by the
documentation and runbooks.

Most diagrams in this repository are authored inline as
[Mermaid](https://mermaid.js.org/) so they render directly on GitHub and stay
version-controlled as text. Add binary assets here only when a static image is
genuinely necessary (e.g. a hand-drawn architecture export), and prefer SVG for
crispness and small diffs.

## Conventions

- Use descriptive, `kebab-case` filenames (e.g. `agent-execution-loop.svg`).
- Reference assets with relative links from the referring document.
- Keep files small; optimize images before committing.
