# ClauseIQ

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=000000)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-Build-646CFF?logo=vite&logoColor=white)](https://vitejs.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15%2B-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)

ClauseIQ is an AI contract intelligence platform that automates contract review for legal, procurement, vendor management, and M&A teams.

Users upload PDF or DOCX contracts, and ClauseIQ:

1. Extracts text from the document, including OCR fallback for scanned files.
2. Segments the contract into individual clauses.
3. Classifies each clause by type using NLP/LLM analysis.
4. Flags risky or non-standard clauses with a HIGH, MEDIUM, or LOW severity score.
5. Benchmarks clause language against market-standard language for the contract type.
6. Generates negotiation guidance with clear pushback recommendations.
7. Produces a one-page executive summary plus a full clause-by-clause report.
8. Exports analysis to downloadable PDF or Word reports.

## Value Proposition

ClauseIQ helps teams cut review time from hours or weeks to minutes by removing the manual contract-analysis bottleneck before lawyers or outside counsel step in.

## Who It’s For

- In-house legal teams
- Law firms using a white-label workflow
- Procurement and vendor management teams
- M&A due-diligence teams

## Tech Stack

- Backend: Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0 async, PostgreSQL or SQLite for local development, Alembic
- Frontend: React 18, TypeScript, Vite, Tailwind CSS, Zustand, TanStack Query
- AI/NLP: Gemini or Claude APIs, clause extraction and risk analysis, pdfplumber, PyMuPDF, Tesseract OCR fallback
- Auth: JWT, email/password, optional OAuth
- Storage: Local filesystem for MVP, S3-compatible storage later
- Deployment: Render or Railway for backend, Vercel for frontend

## Architecture Principles

- Layered backend structure: routers, services, repositories, models
- All AI calls flow through a single `ai_service` abstraction
- Risk scoring logic lives server-side as the single source of truth
- Contract analysis is persisted so users can revisit past reviews
- Frontend components are typed and composable, with no `any` types

## Current Status

Update this section as the project evolves. Example:

- Backend skeleton exists with upload and analyze endpoints.
- Need help building clause comparison against market-standard language.
- Frontend dashboard exists, but the contract detail analysis view still needs inline risk highlighting.

## Repository Notes

- `.gitignore` keeps local, generated, and machine-specific files out of version control.
- This README should stay aligned with the product scope, stack, and workflow as the codebase grows.
