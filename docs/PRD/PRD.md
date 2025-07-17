# Product Requirements Document (PRD)

## Project: AurA IDE

### Overview
AurA is a modern, extensible IDE platform, rebranded from "aura" to "AurA". It is designed for advanced code editing, project management, and AI-powered development workflows. This PRD details all implemented and planned features, organized by development phases, with references to relevant files and modules.

---

## Phase 1: Core IDE Foundation

### 1. Monaco-based Code Editor
- **Features:**
  - Syntax highlighting, code folding, multi-language support
  - LSP (Language Server Protocol) integration for code intelligence
  - Customizable editor settings (font, theme, keybindings)
- **Files:**
  - `AurA/frontend/src/lib/components/Editor.svelte` (planned)
  - `AurA/frontend/src/lib/components/Settings/EditorTab.svelte`
  - `src/lib/components/Settings/EditorTab.svelte`

### 2. File Explorer
- **Features:**
  - Tree view, context menus, drag-and-drop
  - Git status badges, tooltips, file/folder previews
  - File/folder icons, fuzzy search
- **Files:**
  - `AurA/frontend/src/lib/components/FileExplorer.svelte` (planned)
  - `src/lib/components/FileExplorer.svelte`
  - `src/lib/components/common/Tooltip.svelte`

### 3. Terminal Integration
- **Features:**
  - WebSocket backend, multi-tab, resizing
  - Persistent sessions, shell selection
- **Files:**
  - `AurA/backend/app/main.py` (WebSocket/PTY)
  - `AurA/frontend/src/lib/components/Terminal.svelte`

### 4. Git Integration
- **Features:**
  - Status, commit, push/pull, branch management
  - Staging/unstaging, advanced diff viewer (Monaco side-by-side/inline, word-level diff)
- **Files:**
  - `src/lib/components/Git/`
  - `src/lib/apis/git/`
  - `AurA/backend/app/git.py` (planned)

### 5. Fuzzy Finder (Ctrl+P)
- **Features:**
  - Modal with search, recent files, file/folder icons, filters, preview (Monaco/plain), context menu actions
- **Files:**
  - `src/lib/components/FuzzyFinder.svelte`
  - `src/lib/utils/fuzzy.ts`

### 6. Settings Modal
- **Features:**
  - Tabs for General, Editor, Keybindings
  - Customizable, persistent, live application
- **Files:**
  - `src/lib/components/Settings/`
  - `src/lib/stores/index.ts`

### 7. Theme System
- **Features:**
  - Multiple Monaco/UI themes, theme switcher, persistence, custom theme support
- **Files:**
  - `src/lib/components/ThemeSwitcher.svelte`
  - `src/lib/constants.ts`
  - `static/themes/`

### 8. Context Menus & Shortcuts
- **Features:**
  - Quick actions throughout UI, customizable keybindings
- **Files:**
  - `src/lib/components/common/ContextMenu.svelte`
  - `src/lib/components/common/Shortcut.svelte`

---

## Phase 2: Advanced Enhancements

### 1. File/Folder Preview
- **Features:**
  - Tooltip and side panel preview for files/folders
- **Files:**
  - `src/lib/components/FileExplorer.svelte`
  - `src/lib/components/common/Tooltip.svelte`

### 2. Fuzzy Finder Enhancements
- **Features:**
  - Folder search, expand/open actions, preview customization
- **Files:**
  - `src/lib/components/FuzzyFinder.svelte`

### 3. Recent Files Tracking
- **Features:**
  - Display and manage recent files in fuzzy finder and sidebar
- **Files:**
  - `src/lib/stores/index.ts`

### 4. File Type Icons
- **Features:**
  - Consistent icons in explorer and fuzzy finder
- **Files:**
  - `src/lib/components/common/Icon.svelte`

### 5. Workspace/Project Settings
- **Features:**
  - Backend API for `.aura/settings.json`, frontend UI, logic for merging with user settings
- **Files:**
  - `AurA/backend/app/settings.py` (planned)
  - `AurA/frontend/src/lib/components/SettingsProjectTab.svelte` (deleted, to be restored)

---

## Phase 3: Branding Refactor

### 1. Rebranding to AurA
- **Features:**
  - Remove all "aura" references, update to "AurA" and new GitHub URL
  - Update code, configs, docs, UI, translation files, and metadata
- **Files:**
  - All project files (see automated refactor plan)

---

## Phase 4: Pending/Planned Features

### 1. Plugin System
- **Features:**
  - Extensible plugin architecture for IDE and AI features
- **Files:**
  - `AurA/frontend/src/lib/plugins/` (planned)
  - `AurA/backend/app/plugins.py` (planned)

### 2. AI Features
- **Features:**
  - Code completion, chat, review, inline suggestions
- **Files:**
  - `AurA/frontend/src/lib/components/AI/` (planned)
  - `AurA/backend/app/ai.py` (planned)

### 3. Debugging & Testing Integration
- **Features:**
  - Debugger UI, test runner, result viewer
- **Files:**
  - `AurA/frontend/src/lib/components/Debug/` (planned)
  - `AurA/backend/app/debug.py` (planned)

### 4. Collaboration
- **Features:**
  - Real-time collaboration, shared cursors, chat
- **Files:**
  - `AurA/frontend/src/lib/components/Collaboration/` (planned)
  - `AurA/backend/app/collab.py` (planned)

### 5. Performance & Polish
- **Features:**
  - Optimization, accessibility, UI/UX improvements
- **Files:**
  - All frontend/backend files

### 6. Documentation & Testing
- **Features:**
  - Comprehensive docs, automated and manual tests
- **Files:**
  - `docs/`, `test/`, `cypress/`

---

## Appendix: File Mapping
- See above for feature-to-file mapping. For full details, refer to the codebase and implementation notes.

---

*This PRD is a living document and will be updated as the AurA IDE evolves.* 