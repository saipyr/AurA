# Editor Integration in AurA (Deep Dive)

This guide details the implementation of a modern code editor in AurA, drawing inspiration from VSCode, Cursor, Eclipse, and Claude IDE.

---

## 1. Choosing the Editor Engine
### Overview & Goals
- Select an editor engine that is extensible, performant, and widely supported.
- **Monaco Editor** (used in VSCode, Cursor): Feature-rich, LSP support, theming, extensibility.
- **CodeMirror**: Lightweight, highly customizable, good for web IDEs with smaller footprints.

### Design Decisions
- Monaco is preferred for VSCode-like experience and LSP integration.
- CodeMirror is an option for lightweight or embedded scenarios.

---

## 2. Installing Monaco Editor
### Implementation Steps
- Add Monaco as a dependency:
```bash
npm install monaco-editor
```
- For Svelte, use dynamic import to avoid SSR issues.

### Advanced Usage
- Use [monaco-editor-webpack-plugin](https://github.com/Microsoft/monaco-editor-webpack-plugin) for optimized builds.
- Lazy-load languages to reduce bundle size.

### Error Handling & Edge Cases
- Handle SSR/DOM availability in SvelteKit.
- Fallback to CodeMirror if Monaco fails to load.

---

## 3. Basic Integration in Svelte
### Implementation Steps
- Create a Svelte component for the editor.
- Mount Monaco in `onMount` lifecycle.

```svelte
<script>
  import { onMount } from 'svelte';
  let editor;
  onMount(() => {
    import('monaco-editor').then(monaco => {
      editor = monaco.editor.create(document.getElementById('container'), {
        value: '// Start coding!',
        language: 'javascript',
        theme: 'vs-dark',
      });
    });
  });
</script>
<div id="container" style="height:500px;"></div>
```

### API/Interface Examples
- Expose editor instance via Svelte store for plugin access.
- Provide methods for setValue, getValue, setLanguage, setTheme.

### Error Handling
- Ensure container exists before mounting.
- Clean up editor instance on component destroy.

---

## 4. File Open/Save Integration
### Overview & Goals
- Allow users to open and save files to the backend.

### Implementation Steps
- Frontend: Fetch file content from backend API.
- Backend: Serve file content and handle save requests.

```js
// Frontend
export async function readFile(path) {
  const res = await fetch(`/api/files/read?path=${encodeURIComponent(path)}`);
  return res.text();
}
```
```python
# Backend (FastAPI)
@app.get('/api/files/read')
def read_file(path: str):
    with open(path) as f:
        return f.read()
```

### Advanced Usage
- Support large files with streaming APIs.
- Implement auto-save and file change detection.

### Error Handling
- Handle file not found, permission errors, and concurrent edits.

### Security
- Sanitize file paths to prevent directory traversal.

### Testing
- Unit test file open/save APIs with valid and invalid paths.

---

## 5. Language Server Protocol (LSP) Support
### Overview & Goals
- Provide rich language features (completion, hover, diagnostics) via LSP.

### Implementation Steps
- Use [monaco-languageclient](https://github.com/TypeFox/monaco-languageclient) for frontend.
- Backend: Run LSP servers (e.g., pyright, pylsp, tsserver).
- Connect Monaco to LSP via WebSocket.

```js
// Frontend
import { MonacoLanguageClient, createConnection } from 'monaco-languageclient';
const url = createUrl('ws://localhost:3000/lsp');
const webSocket = new WebSocket(url);
const languageClient = new MonacoLanguageClient({
  // ...
  connectionProvider: { get: () => Promise.resolve(createConnection(webSocket)) }
});
languageClient.start();
```

### API/Interface Examples
- Support multiple languages by routing to different LSP servers.
- Allow plugins to register new language servers.

### Error Handling
- Reconnect on LSP server crash.
- Fallback to basic syntax highlighting if LSP unavailable.

### Security
- Restrict LSP server access to project files only.

### Performance
- Debounce document changes before sending to LSP.

### Testing
- Integration tests for LSP features (completion, hover, diagnostics).

---

## 6. Advanced Features
### Multi-cursor, Minimap, Code Folding, Bracket Matching
- Enable via Monaco options:
```js
monaco.editor.create(container, {
  multiCursorModifier: 'ctrlCmd',
  minimap: { enabled: true },
  folding: true,
  matchBrackets: 'always',
});
```

### Find/Replace
- Use Monaco's built-in actions:
```js
editor.getAction('actions.find').run();
```

### Theming
- Support light/dark and custom themes:
```js
monaco.editor.setTheme('vs-dark');
monaco.editor.defineTheme('myCustomTheme', themeData);
```

### Error Handling
- Handle theme load failures gracefully.

### Testing
- UI tests for all advanced features.

---

## 7. Extensibility
### Overview & Goals
- Allow plugins to extend editor functionality (commands, keybindings, UI contributions).

### Implementation Steps
- Expose editor API via global object or Svelte store.
- Allow plugins to register commands:
```js
window.AurA.registerCommand('sayHello', () => alert('Hello from plugin!'));
```
- Support keybinding registration and context menus.

### Advanced Usage
- Allow plugins to add custom panels, overlays, or decorations.

### Security
- Sandbox plugin code (e.g., run in iframe or web worker).

### Testing
- Test plugin registration, command execution, and error isolation.

---

## 8. References
- [VSCode Source](https://github.com/microsoft/vscode)
- [Cursor IDE](https://github.com/getcursor/cursor)
- [Eclipse Theia](https://github.com/eclipse-theia/theia)
- [Claude IDE Docs](https://docs.anthropic.com/claude) 

---

## Implementation Example: File Open/Save (First Increment)

### Backend (FastAPI)
```python
@app.get('/api/files/read', response_class=PlainTextResponse)
def read_file(path: str = Query(...)):
    # ... see code for details ...

@app.post('/api/files/save')
def save_file(path: str = Query(...), content: str = Body(...)):
    # ... see code for details ...
```

### Frontend API (TypeScript)
```ts
export async function readFile(path: string): Promise<string> {
  // ... see code for details ...
}
export async function saveFile(path: string, content: string): Promise<void> {
  // ... see code for details ...
}
```

### Svelte Editor Component
```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import { readFile, saveFile } from '../apis/files/index';
  let filePath = 'README.md';
  let content = '';
  let error = '';
  let saving = false;
  onMount(async () => {
    try {
      content = await readFile(filePath);
    } catch (e) {
      error = e.message;
    }
  });
  async function save() {
    saving = true;
    error = '';
    try {
      await saveFile(filePath, content);
    } catch (e) {
      error = e.message;
    } finally {
      saving = false;
    }
  }
</script>
<div>
  <label>Editing: {filePath}</label>
  {#if error}
    <div class="error">{error}</div>
  {/if}
  <textarea bind:value={content} rows={20} cols={80}></textarea>
  <button on:click={save} disabled={saving}>{saving ? 'Saving...' : 'Save'}</button>
</div>
```

### Test Case (Jest/Vitest)
```ts
import { readFile, saveFile } from '../apis/files/index';
test('can open and save a file', async () => {
  const path = 'test.txt';
  await saveFile(path, 'hello');
  const content = await readFile(path);
  expect(content).toBe('hello');
});
``` 

---

## Monaco Editor Integration

AurA uses Monaco Editor for a modern, extensible code editing experience.

### Svelte Component Usage
```svelte
<MonacoEditor filePath="README.md" language="markdown" theme="vs-dark" />
```

### Props
- `filePath`: Path to the file to load and save.
- `language`: Language mode (e.g., 'javascript', 'python', 'markdown').
- `theme`: Editor theme (e.g., 'vs-dark', 'vs-light').

### Features
- Loads file content using the backend API.
- Allows editing and saving.
- Emits `change` events on content change.
- Exposes the Monaco editor instance for plugins/extensibility.
- Handles errors gracefully.

### Component Code
```svelte
<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import { readFile, saveFile } from '../apis/files/index';
  let container: HTMLDivElement;
  export let filePath: string;
  export let language: string = 'javascript';
  export let theme: string = 'vs-dark';
  let editor: any;
  let monaco: any;
  let error = '';
  let saving = false;
  const dispatch = createEventDispatcher();
  async function loadContent() {
    try {
      error = '';
      const content = await readFile(filePath);
      editor.setValue(content);
    } catch (e) {
      error = e.message;
    }
  }
  async function save() {
    saving = true;
    error = '';
    try {
      await saveFile(filePath, editor.getValue());
    } catch (e) {
      error = e.message;
    } finally {
      saving = false;
    }
  }
  onMount(async () => {
    try {
      monaco = await import('monaco-editor');
      editor = monaco.editor.create(container, {
        value: '',
        language,
        theme,
        automaticLayout: true
      });
      await loadContent();
      editor.onDidChangeModelContent(() => {
        dispatch('change', { value: editor.getValue() });
      });
    } catch (e) {
      error = 'Failed to load Monaco Editor: ' + e.message;
    }
  });
  export { editor };
</script>
<div>
  <label>Editing: {filePath}</label>
  {#if error}
    <div class="error">{error}</div>
  {/if}
  <div bind:this={container} style="height:500px;"></div>
  <button on:click={save} disabled={saving}>{saving ? 'Saving...' : 'Save'}</button>
</div>
``` 