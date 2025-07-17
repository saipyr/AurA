# Integrated Terminal in AurA (Deep Dive)

This guide details the implementation of an integrated terminal, inspired by VSCode, Eclipse, Cursor, and Claude IDE.

---

## 1. xterm.js Integration (Frontend)
### Overview & Goals
- Provide a fully interactive terminal emulator in the browser.
- Support ANSI colors, resizing, and copy/paste.

### Implementation Steps
- Install xterm.js and import in Svelte component.
- Mount terminal in `onMount` and connect to backend WebSocket.

```svelte
<script>
  import { Terminal } from 'xterm';
  import { onMount } from 'svelte';
  let term;
  onMount(() => {
    term = new Terminal();
    term.open(document.getElementById('terminal'));
    // Connect to backend WebSocket here
  });
</script>
<div id="terminal" style="height:300px;"></div>
```

### Advanced Usage
- Use xterm.js addons for fit, search, and Unicode support.
- Support custom keybindings and themes.

### Error Handling
- Handle terminal resize and disconnect events.

### Testing
- UI tests for terminal rendering and input/output.

---

## 2. Backend Shell Process
### Overview & Goals
- Spawn and manage shell processes (bash, zsh, etc.) per user/session.

### Implementation Steps
- Use Python's subprocess to spawn shell.
- Stream stdin/stdout via WebSocket.

```python
import subprocess
from fastapi import WebSocket

@app.websocket('/ws/terminal')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    proc = subprocess.Popen(['bash'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    # Read/write between proc and websocket
```

### Advanced Usage
- Support environment variable injection and working directory selection.
- Implement shell process cleanup on disconnect.

### Error Handling
- Handle shell process crashes and resource limits.

### Security
- Restrict shell access to authorized users and project directories.

### Testing
- Integration tests for shell process lifecycle.

---

## 3. WebSocket Streaming
### Overview & Goals
- Enable real-time, bidirectional communication between frontend and backend.

### Implementation Steps
- Use FastAPI WebSocket for backend.
- On frontend, connect xterm.js to WebSocket and relay input/output.

### Advanced Usage
- Support binary data and large output streaming.
- Implement reconnect logic for dropped connections.

### Error Handling
- Handle network errors and partial messages.

### Testing
- Simulate network interruptions and test recovery.

---

## 4. Multi-Terminal Support
### Overview & Goals
- Allow users to open multiple terminal sessions/tabs.

### Implementation Steps
- Assign unique IDs to each terminal session.
- Track sessions in backend and frontend state.
- Provide UI for switching/closing terminals.

### Advanced Usage
- Persist terminal history and state across reloads.

### Error Handling
- Clean up orphaned sessions on disconnect.

### Testing
- Test multiple concurrent terminals per user.

---

## 5. Security & Performance
- Limit resource usage per session (CPU, memory).
- Sanitize all input/output to prevent injection attacks.
- Use process isolation for each terminal.

---

## Persistent Terminal Sessions

- Each terminal tab is assigned a unique session ID (UUID).
- The frontend passes the session ID to the backend via /ws/terminal?session=...
- The backend keeps a mapping of session IDs to shell processes.
- If a session ID is reused (e.g., after reload), the backend reattaches to the existing shell process.
- On disconnect, the shell process is kept alive for 5 minutes before cleanup.

### Usage
- Open multiple terminals, run commands, reload the page, and verify that each terminal resumes its previous session.
- Test tab renaming and keyboard shortcuts as before.

---

## 6. References
- [VSCode Terminal](https://github.com/microsoft/vscode/tree/main/src/vs/workbench/contrib/terminal)
- [xterm.js](https://github.com/xtermjs/xterm.js)
- [Cursor Terminal](https://github.com/getcursor/cursor)
- [Eclipse Terminal](https://www.eclipse.org/eclipseide/)
- [Claude IDE Docs](https://docs.anthropic.com/claude) 

---

## Implementation Example: Integrated Terminal (Increment)

### Backend (FastAPI)
```python
@app.websocket('/ws/terminal')
async def terminal_ws(websocket: WebSocket):
    # ... see code for details ...
```

### Frontend (Svelte + xterm.js)
```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  let term;
  let socket: WebSocket;
  let container: HTMLDivElement;
  let error = '';
  onMount(async () => {
    const { Terminal } = await import('xterm');
    term = new Terminal();
    term.open(container);
    try {
      socket = new WebSocket('ws://localhost:8000/ws/terminal');
      socket.onmessage = (event) => {
        term.write(event.data);
      };
      socket.onerror = (e) => {
        error = 'Terminal connection error';
      };
      term.onData(data => {
        if (socket.readyState === WebSocket.OPEN) {
          socket.send(data);
        }
      });
    } catch (e) {
      error = 'Failed to connect to terminal: ' + e.message;
    }
  });
</script>
<div>
  {#if error}
    <div class="error">{error}</div>
  {/if}
  <div bind:this={container} style="height:400px;width:100%;background:#111;"></div>
</div>
```

### Usage
- Add `<Terminal />` to your app to show a live shell.

### Test Case (Manual)
- Open the app, type commands in the terminal, and verify output.
- Check backend logs for errors on connect/disconnect. 