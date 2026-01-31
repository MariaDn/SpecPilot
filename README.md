# SpecPilot

SpecPilot is an AI-powered assistant that transforms short project briefs into detailed technical specifications. Designed for developers, product managers, and startup founders, SpecPilot streamlines the early-stage planning process by asking smart follow-up questions and delivering ready-to-use, editable, and exportable tech specs.

---

## Features

- AI-based tech spec generation
- Short brief input with smart follow-up questions
- Editable output (manual or AI-assisted refinement)
- Export to PDF or shareable link
- Built as a TypeScript-based SPA (no Angular/React)

---

## Technology Stack

- **Frontend**: TypeScript, Lit (Web Components), Parcel, CSS
- **AI Logic**: AI prompting (template-based + prompt chaining), manual feedback cycle + regeneration
- **Export Formats**: PDF (via jsPDF or Puppeteer), Markdown (conversion from HTML), Link (optional backend backup or blob URL)

---

## Getting Started

1. Clone the repository
2. Run docker-compose up