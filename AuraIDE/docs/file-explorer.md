# File Explorer & Project Management in AurA (Deep Dive)

This guide covers the implementation of a file explorer and project management system, inspired by VSCode, Eclipse, Cursor, and Claude IDE.

---

## 1. Tree View UI
### Overview & Goals
- Provide a hierarchical, interactive view of project files and folders.
- Support expand/collapse, icons, and context menus.

### Implementation Steps
- Use a recursive Svelte component for the file tree.
- Fetch file/folder structure from backend API.
- Render icons based on file type.

```svelte
<script>
  export let files = [];
  function toggle(file) { file.expanded = !file.expanded; }
</script>
<ul>
  {#each files as file}
    <li>
      <span on:click={() => toggle(file)}>{file.expanded ? '▼' : '▶'} {file.name}</span>
      {#if file.expanded && file.children}
        <FileTree files={file.children} />
      {/if}
    </li>
  {/each}
</ul>
```

### Advanced Usage
- Virtualize large trees for performance (see VSCode's tree virtualization).
- Support keyboard navigation and search/filter.

### Error Handling
- Handle empty folders, permission errors, and deep recursion.

### Testing
- Unit and UI tests for tree rendering and interaction.

---

## 2. File Operations (CRUD)
### Overview & Goals
- Allow users to create, rename, delete, and move files/folders.

### Implementation Steps
- Backend: Implement REST APIs for file operations.
- Frontend: Call APIs and update tree state.

```python
# Backend (FastAPI)
@app.post('/api/files/create')
def create_file(path: str):
    open(path, 'w').close()
    return {'status': 'created'}
```

### Advanced Usage
- Support batch operations and undo/redo.
- Integrate with version control for safe deletes/moves.

### Error Handling
- Handle name conflicts, permission errors, and invalid paths.

### Security
- Sanitize paths and restrict operations to project root.

### Testing
- Test all CRUD operations with valid/invalid input.

---

## 3. Drag-and-Drop
### Overview & Goals
- Enable intuitive file/folder reorganization via drag-and-drop.

### Implementation Steps
- Use HTML5 drag-and-drop events in Svelte.
- On drop, call backend API to move file/folder.

```svelte
<li draggable="true" on:dragstart={...} on:drop={...}>...</li>
```

### Advanced Usage
- Show drop targets and visual feedback.
- Support multi-select drag.

### Error Handling
- Prevent dropping into invalid locations (e.g., a file into itself).

### Testing
- UI tests for drag-and-drop scenarios.

---

## 4. Workspace Management
### Overview & Goals
- Allow users to open, close, and switch between projects/workspaces.

### Implementation Steps
- Store recent projects in localStorage or backend DB.
- Provide UI for switching and managing workspaces.

### Advanced Usage
- Support multi-root workspaces (like VSCode).
- Persist workspace state (open files, layout).

### Error Handling
- Handle missing or corrupted workspace data.

### Testing
- Test workspace switching and persistence.

---

## 5. Security & Performance
- Restrict file operations to authorized users and project directories.
- Optimize API calls and tree rendering for large projects.

---

## Implementation Example: File Explorer (Increment)

### Backend (FastAPI)
```python
@app.get('/api/files/list', response_class=JSONResponse)
def list_dir(path: str = Query('')):
    # ... see code for details ...
@app.post('/api/files/create_file')
def create_file(path: str = Query(...)):
    # ... see code for details ...
@app.post('/api/files/create_folder')
def create_folder(path: str = Query(...)):
    # ... see code for details ...
@app.post('/api/files/rename')
def rename_path(old_path: str = Query(...), new_path: str = Query(...)):
    # ... see code for details ...
@app.post('/api/files/delete')
def delete_path(path: str = Query(...)):
    # ... see code for details ...
```

### Frontend API (TypeScript)
```ts
export async function listDir(path: string = ''): Promise<Array<{name: string, isDir: boolean}>> {
  // ... see code for details ...
}
export async function createFile(path: string): Promise<void> {
  // ... see code for details ...
}
export async function createFolder(path: string): Promise<void> {
  // ... see code for details ...
}
export async function renamePath(oldPath: string, newPath: string): Promise<void> {
  // ... see code for details ...
}
export async function deletePath(path: string): Promise<void> {
  // ... see code for details ...
}
```

### Svelte FileExplorer Component
```svelte
<FileExplorer on:open={handleOpen} />
```

### Monaco Integration
```svelte
<MonacoEditor filePath={currentFile} language="markdown" theme="vs-dark" />
```

### App Integration Example
```svelte
<script lang="ts">
  import FileExplorer from './components/FileExplorer.svelte';
  import MonacoEditor from './components/MonacoEditor.svelte';
  let currentFile = 'README.md';
  function handleOpen(e) {
    currentFile = e.detail.path;
  }
</script>
<div style="display: flex; height: 100vh;">
  <div style="width: 300px; border-right: 1px solid #ccc; overflow-y: auto;">
    <FileExplorer on:open={handleOpen} />
  </div>
  <div style="flex: 1;">
    <MonacoEditor filePath={currentFile} language="markdown" theme="vs-dark" />
  </div>
</div>
```

### Test Case (Jest/Vitest)
```ts
import { render, fireEvent } from '@testing-library/svelte';
import FileExplorer from './FileExplorer.svelte';
test('renders file tree and opens file', async () => {
  // Mock listDir and test open event
});
```

## 6. References
- [VSCode Explorer](https://github.com/microsoft/vscode/tree/main/src/vs/workbench/contrib/files)
- [Eclipse Project Explorer](https://www.eclipse.org/eclipseide/)
- [Cursor File Tree](https://github.com/getcursor/cursor)
- [Claude IDE Docs](https://docs.anthropic.com/claude) 