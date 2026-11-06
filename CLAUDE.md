# CLAUDE.md: Project Guide

This file gives Claude Code (an AI coding assistant) the context and rules for this project. It documents the architecture, the plan, and how AI assistance is used: I own the design and engineering decisions, and Claude Code helps implement, review, and explain.

## Project overview
A personal portfolio site that is also an applied ML system. Visitors can explore my experience through:
- **Semantic search** over my projects, internships, and leadership roles
- **A retrieval-augmented chatbot** that answers questions about my work, grounded only in my own content
- **"Similar experiences" recommendations** on every experience page
- **Visitor-type prediction** that adapts what's emphasized for recruiters vs. engineers

All features run on one shared embedding index of ~40–80 experience entries.

## Tech stack
- **Frontend:** React + TypeScript + Vite, deployed on Vercel (auto-deploys from `main`; preview deploys per PR)
- **Backend:** AWS, defined as infrastructure-as-code with AWS CDK (TypeScript)
  - API Gateway + Lambda (Python): search, chatbot, event logging
  - Amazon Bedrock: Titan Text Embeddings V2 (embeddings), a small Claude model (chatbot generation)
  - DynamoDB: visitor event logs
  - S3: precomputed embedding index and recommendation data
- **Offline ML pipeline:** Python scripts run at build time to embed entries, compute recommendations, generate labels, and run evaluations

### Key design decision: no vector database
With fewer than 100 entries, a vector database adds cost and complexity without benefit. Embeddings are precomputed, stored as JSON, and searched with cosine similarity in NumPy. This keeps latency low and hosting cost near zero. Revisit if the corpus grows by orders of magnitude.

## ML features

### 1. Similar experiences (content-based recommendation)
- Embeddings + cosine similarity, precomputed offline
- **MMR re-ranking** for diversity, mixing entry types (project / internship / leadership)
- **Novelty penalty** for entries the visitor has already viewed (client-side)
- **Progression ordering** (e.g., hackathon → project → internship) using a scale/date field
- Short "why related" label per pair (e.g., "Same skills, at production scale"), generated once offline
- **Objective:** maximize coverage of my experience, not clicks. Recommendations never hide content; the full list is always visible.

### 2. Semantic search
Query embedded via Bedrock and ranked against the entry index by meaning, not keywords.

### 3. "Ask about my work" chatbot (RAG)
- Retrieve the top-k relevant entries, then generate an answer using **only** those entries
- Cite and link the source entries in every answer
- If the answer isn't in the content, say so rather than guessing

### 4. Visitor-type prediction
- Classes: recruiter / engineer / other
- Runs in the browser: **Bayesian updating** from behavioral signals (referrer, clicks, searches, chatbot questions)
- Adapts emphasis (recruiters: impact and resume first; engineers: architecture and code first)
- Editable "Viewing as: ___" label; corrections are logged as labeled data for future model training

### 5. "How this site works" page
Pipeline diagram, design decisions, cost breakdown, and evaluation:
- Search quality on a held-out test query set (recall@k)
- Chatbot groundedness on test questions
- Visitor-type accuracy against user-selected labels

## Content
- One Markdown file per experience in `content/entries/`, with frontmatter:
  `id, title, type (project | internship | leadership | other), date, scale (1–5), skills[], summary, links[]`
- All content is written by me. Never generate or embellish facts about my experience.

## Frontend & design
- The visual design and hand-made assets are my own work. Until the design pass, build only a **minimal, unstyled placeholder UI**.
- Separate logic from presentation: hooks/services (`useSearch`, `useChat`, `useVisitorType`, `useRelated`) vs. presentational components.
- All styling through design tokens (CSS variables) in one place. No decorative styling or generated visual assets.
- Placeholder images live in `/frontend/src/assets/placeholder/`.
- Accessibility: semantic HTML, alt text, keyboard navigation, sufficient contrast.

## Repository structure
```
/frontend          React + Vite app (Vercel root)
/infra             AWS CDK app
/backend           Lambda handlers (Python)
/pipeline          Offline ML scripts (embed, recommend, evaluate)
/content/entries   Experience entries (Markdown)
```

## Build order
1. Frontend scaffold with placeholder UI; deploy to Vercel
2. Content schema + sample entries
3. Offline pipeline: embeddings → similar experiences (MMR) → JSON
4. Experience pages + similar-experiences row (static data)
5. CDK setup + search Lambda + API Gateway
6. RAG chatbot Lambda
7. Client-side visitor-type prediction + event logging
8. Evaluation scripts + "How this site works" page
9. Final design pass

## Security & cost
- **No secrets in the repo.** Credentials live in `.env` (gitignored) or AWS profiles. Flag anything sensitive before it is committed.
- CORS on API Gateway restricted to the production domain and localhost.
- API Gateway rate limiting and a max-token cap on chatbot responses.
- AWS Budgets alert in place.
- Serverless, pay-per-request services only; avoid services with monthly minimums.

## How we work together
- **I make the architecture and design decisions.** Claude Code proposes options and explains tradeoffs.
- **Core ML logic is written by me:** cosine similarity, MMR re-ranking, the Bayesian visitor-type updater, and RAG retrieval. Claude Code helps with explanations, review, and tests for these, not the implementation.
- Claude Code handles scaffolding, boilerplate, infrastructure wiring, tests, and debugging support.
- Every change is reviewed by me before merging. Show a plan before larger changes and explain what changed and why.
- One feature branch per task, merged to `main` via pull request. Never commit directly to `main`.
- Credentials, IAM, and billing are set up manually by me. Never handle or request secrets.
- Ask before deploying infrastructure (`cdk deploy`), adding dependencies or services, or running anything destructive.