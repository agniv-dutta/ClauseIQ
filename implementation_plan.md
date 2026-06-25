# ClauseIQ Frontend Implementation Plan

This document outlines the step-by-step implementation plan for the ClauseIQ frontend, a production-quality, visually distinctive React application.

## User Review Required

Please review the proposed design tokens and technology choices to ensure they align with the Google Stitch frames and project requirements.

- **Color Palette (Derived from images):**
  - **Background (Deep Teal/Black):** `#04110E` (Base), `#081C17` (Surface/Sidebar), `#0C2B24` (Cards/Hover)
  - **Accent (Gold/Amber):** `#EAB308` or `#F2C960` (Primary CTA, Active states, Text highlights)
  - **Text:** `#E2E8F0` (Primary body), `#94A3B8` (Secondary)
  - **Semantic (Risk):** 
    - High: `#C1432D` (Muted red), bg: `#3A1916`
    - Medium: `#D4A547` (Amber), bg: `#3D301B`
    - Low: `#5E846A` (Sage green), bg: `#1F3125`
- **Typography:**
  - **Serif:** `Lora` (or `Fraunces`) for headings, display text, and serif quotes.
  - **Sans-Serif:** `Inter` for UI elements, buttons, data tables, and body.
  - **Monospace:** `JetBrains Mono` for scores, dates, and percentages.
- **Key Libraries:**
  - Vite + React 18 + TS
  - Tailwind CSS + clsx + tailwind-merge
  - React Router v6
  - TanStack Query v5 + Axios
  - Zustand
  - react-dropzone
  - react-pdf
  - Recharts
  - lucide-react
  - react-hook-form + zod
  - framer-motion (for subtle animations, optional if CSS is preferred)

## Open Questions

1. Is the extracted color palette (Deep Teal/Black with Gold accent) accurate to your expectations from the Google Stitch designs?
2. Would you like me to use `framer-motion` for the micro-animations (like the Upload Progress Modal transitions), or rely strictly on CSS and lightweight hooks?

## Proposed Changes

### 1. Foundation & Skeleton
- Initialize Vite React + TS app in `frontend/` subdirectory inside `C:/Users/Agniv Dutta/ClauseIQ`.
- Install all required dependencies.
- Configure Tailwind CSS with the custom theme (colors, fonts).
- Set up project structure (`src/components`, `src/pages`, `src/stores`, etc.).
- Configure React Router with basic empty pages.
- Setup Axios instance and TanStack Query provider.

### 2. Layout & Shell
- Create `AppShell` component (Sidebar + Topbar).
- Implement custom Sidebar styling (matching Image 3 & 4).
- Setup routing inside the shell for `/dashboard`, `/portfolio`, `/settings`.

### 3. Dashboard Page & Upload Flow
- Build `DashboardPage` (Image 3) with aggregate risk stats and sortable `ContractListTable`.
- Implement `UploadDropzone`.
- Implement `UploadProgressModal` (Image 4) with simulated progress stages and animations.

### 4. Contract Detail Page
- Build `ContractDetailPage` (Image 2) - Two-pane layout.
- Implement Left Pane: `ContractViewer` (PDF preview pane placeholder or actual `react-pdf` setup with mock highlights).
- Implement Right Pane: 
  - `ExecutiveSummaryPanel` with `RiskScoreGauge` (Recharts).
  - `KeyDatesTimeline`.
  - `ClauseList` with filter tabs and `ClauseCard` components.

### 5. Landing Page & Polish
- Build `LandingPage` (Image 1) with hero section, steps, and features.
- Add counting animations, hover states, empty states, and toast notifications (sonner).

## Verification Plan

### Automated Tests
- Run `tsc --noEmit` to ensure no TypeScript strict mode errors.
- Run Vite dev server to verify build works.

### Manual Verification
- Manually navigate through all routes.
- Verify visual accuracy against the provided 4 images (pixel-peeping colors, spacing, and typography).
- Test the simulated upload progress flow.
- Verify responsive layout scaling down to tablet size (1024px).
