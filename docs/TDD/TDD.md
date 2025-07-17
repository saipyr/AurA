# Technical Design Document (TDD)

## Project: AurA IDE

### Overview
This TDD describes the technical architecture, design decisions, and implementation details for the AurA IDE project, rebranded from "aura". It covers all major modules, backend/frontend structure, integration points, and technical rationale, organized by development phase and mapped to relevant files.

---

## 1. Architecture Overview

- **Frontend:** Svelte-based SPA, Monaco Editor integration, modular component structure, state management via Svelte stores.
- **Backend:** Python (FastAPI), WebSocket for terminal and collaboration, REST APIs for file, git, settings, and plugin management.
- **Persistence:** Filesystem for project/workspace, JSON for settings, database for user data and history.
- **DevOps:** Docker, Kubernetes, CI/CD, multi-environment support.

---

## 2. Technology Stack

- **Frontend:** Svelte, TypeScript, Monaco Editor, Tailwind CSS, WebSockets
- **Backend:** Python 3.11+, FastAPI, SQLAlchemy, Alembic, Redis, WebSockets, PyJWT
- **DevOps:** Docker, Kubernetes, Helm, GitHub Actions

---

## 3. Module Breakdown & File Mapping

### Phase 1: Core IDE Foundation

#### 1. Editor (Monaco)
- **Files:** `AurA/frontend/src/lib/components/Editor.svelte`, `Settings/EditorTab.svelte`
- **Design:**
  - Monaco loaded as a dynamic module for performance
  - LSP integration via WebSocket/REST bridge
  - Editor options persisted in Svelte store and `.aura/settings.json`

#### 2. File Explorer
- **Files:** `FileExplorer.svelte`, `common/Tooltip.svelte`
- **Design:**
  - Tree structure from backend API
  - Context menu actions via event bus
  - Git status via backend polling

#### 3. Terminal
- **Files:** `Terminal.svelte`, `backend/app/main.py`
- **Design:**
  - WebSocket PTY backend, multi-tab frontend
  - Session persistence via backend state

#### 4. Git Integration
- **Files:** `components/Git/`, `apis/git/`, `backend/app/git.py`
- **Design:**
  - REST API for git actions, WebSocket for live status
  - Monaco diff viewer for side-by-side/inline

#### 5. Fuzzy Finder
- **Files:** `FuzzyFinder.svelte`, `utils/fuzzy.ts`
- **Design:**
  - Indexed file/folder list in memory
  - Modal UI, keyboard navigation, preview via Monaco/plain

#### 6. Settings Modal
- **Files:** `components/Settings/`, `stores/index.ts`
- **Design:**
  - Tabbed modal, settings persisted to localStorage and backend
  - Keybindings editor with live update

#### 7. Theme System
- **Files:** `ThemeSwitcher.svelte`, `constants.ts`, `static/themes/`
- **Design:**
  - Monaco and UI theme sync, custom theme loader

#### 8. Context Menus & Shortcuts
- **Files:** `common/ContextMenu.svelte`, `common/Shortcut.svelte`
- **Design:**
  - Global event bus for context menu
  - Shortcut manager with conflict detection

---

### Phase 2: Advanced Enhancements

#### 1. File/Folder Preview
- **Files:** `FileExplorer.svelte`, `common/Tooltip.svelte`
- **Design:**
  - Hover/side panel preview, file type detection

#### 2. Fuzzy Finder Enhancements
- **Files:** `FuzzyFinder.svelte`
- **Design:**
  - Folder search, expand/collapse logic, preview customization

#### 3. Recent Files Tracking
- **Files:** `stores/index.ts`
- **Design:**
  - Recent files stack, persisted in store

#### 4. File Type Icons
- **Files:** `common/Icon.svelte`
- **Design:**
  - Icon mapping by extension/type

#### 5. Workspace/Project Settings
- **Files:** `backend/app/settings.py`, `SettingsProjectTab.svelte`
- **Design:**
  - API for `.aura/settings.json`, merge logic with user settings

---

### Phase 3: Branding Refactor

#### 1. Rebranding to AurA
- **Files:** All project files
- **Design:**
  - Automated search/replace for "aura" to "AurA"
  - Update GitHub URLs, docs, UI, and metadata

---

### Phase 4: Pending/Planned Features

#### 1. Plugin System
- **Files:** `frontend/src/lib/plugins/`, `backend/app/plugins.py`
- **Design:**
  - Plugin manifest, dynamic loading, API hooks

#### 2. AI Features
- **Files:** `frontend/src/lib/components/AI/`, `backend/app/ai.py`
- **Design:**
  - LLM API integration, inline suggestions, chat UI

#### 3. Debugging & Testing
- **Files:** `frontend/src/lib/components/Debug/`, `backend/app/debug.py`
- **Design:**
  - Debugger protocol bridge, test runner API

#### 4. Collaboration
- **Files:** `frontend/src/lib/components/Collaboration/`, `backend/app/collab.py`
- **Design:**
  - WebSocket shared state, CRDT for real-time sync

#### 5. Performance & Polish
- **Files:** All frontend/backend files
- **Design:**
  - Code splitting, lazy loading, accessibility

#### 6. Documentation & Testing
- **Files:** `docs/`, `test/`, `cypress/`
- **Design:**
  - Sphinx/Markdown docs, Cypress/E2E/unit tests

---

## 4. API Design & Integration Points
- **REST APIs:** File, git, settings, plugin, AI
- **WebSocket:** Terminal, collaboration, LSP bridge
- **Persistence:** Filesystem, JSON, DB

---

## 5. UI Structure
- **Component-based Svelte UI**
- **Monaco Editor as core widget**
- **Modal/side panel for fuzzy finder, settings, git, etc.**

---

## 6. DevOps & Deployment
- **Docker Compose, Kubernetes, Helm**
- **CI/CD via GitHub Actions**
- **Multi-environment support**

---

## 7. Technical Rationale
- **Svelte for fast, modern UI**
- **Monaco for rich code editing**
- **FastAPI for async backend**
- **WebSocket for real-time features**
- **Modular, extensible design for future growth**

---

*This TDD is a living document and will be updated as the AurA IDE evolves.* 