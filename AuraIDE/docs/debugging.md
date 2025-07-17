# Debugging Tools in AurA (Deep Dive)

This guide details the implementation of debugging tools, inspired by VSCode, Eclipse, Cursor, and Claude IDE.

---

## 1. Debug Adapter Protocol (DAP) Integration
### Overview & Goals
- Support multi-language debugging via the Debug Adapter Protocol (DAP).

### Implementation Steps
- Use [vscode-debugadapter-node](https://github.com/microsoft/vscode-debugadapter-node) or similar for backend.
- Communicate with frontend via WebSocket or JSON-RPC.

```js
// Node.js DAP server example
const { DebugSession } = require('vscode-debugadapter');
class MyDebugSession extends DebugSession { /* ... */ }
DebugSession.run(MyDebugSession);
```

### Advanced Usage
- Support custom debug adapters for new languages.
- Allow plugins to register new debug types.

### Error Handling
- Handle adapter crashes and protocol errors.

### Security
- Restrict debug access to project files only.

### Testing
- Integration tests for DAP message flows.

---

## 2. Breakpoints
### Overview & Goals
- Allow users to set/remove breakpoints in the editor.

### Implementation Steps
- Use Monaco API (`editor.deltaDecorations`) to mark breakpoints.
- Sync breakpoints with backend DAP server.

### Advanced Usage
- Support conditional and logpoint breakpoints.
- Persist breakpoints across sessions.

### Error Handling
- Handle invalid or unreachable breakpoint locations.

### Testing
- UI and integration tests for breakpoint flows.

---

## 3. Stepping Controls
### Overview & Goals
- Provide controls for step in, step over, step out, continue, and pause.

### Implementation Steps
- UI buttons trigger DAP commands to backend.
- Update editor and variable panels on step events.

### Advanced Usage
- Support reverse debugging (if adapter supports).

### Error Handling
- Handle lost debug sessions and out-of-sync state.

### Testing
- Test all stepping actions and edge cases.

---

## 4. Variable Inspection
### Overview & Goals
- Display variables, call stack, and watch expressions in real time.

### Implementation Steps
- Use Svelte panels for variables, call stack, and watches.
- Update values on DAP events.

### Advanced Usage
- Support variable editing and custom watch expressions.

### Error Handling
- Handle missing or large variable values.

### Testing
- Test variable display and updates during stepping.

---

## 5. UI Design
- Use a side panel for breakpoints, variables, and call stack (see VSCode/Eclipse for layout inspiration).
- Highlight current execution line in the editor.

---

## 6. Security & Performance
- Restrict debug access to authorized users and project files.
- Optimize variable updates and UI rendering for large programs.

---

## 7. References
- [VSCode Debugging](https://github.com/microsoft/vscode/tree/main/src/vs/workbench/contrib/debug)
- [Eclipse Debug](https://www.eclipse.org/eclipseide/)
- [Cursor Debug](https://github.com/getcursor/cursor)
- [Claude IDE Docs](https://docs.anthropic.com/claude) 