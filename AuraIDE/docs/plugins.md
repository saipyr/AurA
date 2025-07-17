# Plugin/Extension System in AurA (Deep Dive)

This guide details the implementation of a plugin/extension system, inspired by VSCode, Eclipse, Cursor, and Claude IDE.

---

## 1. Plugin Manifest
### Overview & Goals
- Define a standard format for plugin metadata and contributions.

### Implementation Steps
- Use JSON or JS module for manifest.
- Specify name, version, main entry, and contributions (commands, menus, etc.).

```json
{
  "name": "Sample Plugin",
  "version": "1.0.0",
  "main": "index.js",
  "contributes": {
    "commands": [
      { "command": "sayHello", "title": "Say Hello" }
    ]
  }
}
```

### Advanced Usage
- Support localization and dependencies in manifest.

### Error Handling
- Validate manifest schema on load.

### Testing
- Test manifest parsing and error reporting.

---

## 2. Plugin API
### Overview & Goals
- Expose safe, powerful APIs for plugins to interact with the IDE.

### Implementation Steps
- Provide APIs for commands, UI, events, and editor access.

```js
window.AurA.registerCommand('sayHello', () => alert('Hello from plugin!'));
```

### Advanced Usage
- Allow plugins to add panels, overlays, and decorations.
- Support async APIs and event subscriptions.

### Error Handling
- Isolate plugin errors and prevent IDE crashes.

### Security
- Restrict API surface and sandbox plugin code.

### Testing
- Test API calls, error handling, and isolation.

---

## 3. Plugin Loader
### Overview & Goals
- Dynamically discover and load plugins at runtime.

### Implementation Steps
- Use dynamic import for JS plugins.
- Track loaded plugins and manage lifecycle (activate/deactivate).

```js
async function loadPlugin(url) {
  const plugin = await import(url);
  plugin.activate();
}
```

### Advanced Usage
- Support hot-reloading and plugin updates.

### Error Handling
- Handle load failures and version mismatches.

### Testing
- Test plugin loading/unloading and error recovery.

---

## 4. Sandboxing
### Overview & Goals
- Run plugins in a secure, isolated context.

### Implementation Steps
- Use iframe, VM, or web worker for isolation.
- Communicate via postMessage or RPC.

### Advanced Usage
- Limit resource usage and API access per plugin.

### Error Handling
- Detect and terminate misbehaving plugins.

### Security
- Prevent access to sensitive APIs and data.

### Testing
- Test sandbox escape attempts and resource limits.

---

## 5. Plugin Management UI
### Overview & Goals
- Provide UI for browsing, installing, enabling/disabling, and configuring plugins.

### Implementation Steps
- Build Svelte components for plugin list, details, and settings.
- Show plugin status, version, and update options.

### Advanced Usage
- Support plugin search, ratings, and reviews.

### Error Handling
- Handle install/update failures gracefully.

### Testing
- UI tests for all management actions.

---

## 6. Plugin Marketplace/Registry
### Overview & Goals
- Enable sharing and discovery of plugins (like VSCode Marketplace).

### Implementation Steps
- Create a registry backend and frontend search UI.
- Allow users to submit, install, and review plugins.

### Advanced Usage
- Support plugin dependencies and compatibility checks.

### Error Handling
- Handle registry downtime and invalid plugins.

### Testing
- Test plugin publishing, search, and install flows.

---

## 7. Developer Documentation
- Provide guides, API docs, and sample plugins for authors.

---

## 8. Security & Performance
- Enforce sandboxing and API restrictions.
- Optimize plugin loading and execution.

---

## 9. References
- [VSCode Extension API](https://code.visualstudio.com/api)
- [Eclipse Plugin System](https://www.eclipse.org/eclipseide/)
- [Cursor Plugins](https://github.com/getcursor/cursor)
- [Claude IDE Docs](https://docs.anthropic.com/claude) 

---

## Example: Complex Plugin with Custom Panel, Settings, and Async Operations

### Plugin Manifest (plugin.json)
```json
{
  "name": "Weather Panel Plugin",
  "version": "1.0.0",
  "main": "index.js",
  "contributes": {
    "commands": [
      { "command": "weatherPanel.show", "title": "Show Weather Panel" }
    ],
    "settings": [
      { "key": "weatherPanel.apiKey", "type": "string", "default": "", "description": "OpenWeatherMap API Key" },
      { "key": "weatherPanel.defaultCity", "type": "string", "default": "San Francisco", "description": "Default city for weather info" }
    ],
    "panels": [
      { "id": "weatherPanel", "title": "Weather", "icon": "🌤️" }
    ]
  }
}
```

### Plugin Entry (index.js)
```js
export function activate(context) {
  // Register command to show the panel
  context.registerCommand('weatherPanel.show', () => {
    context.showPanel('weatherPanel');
  });

  // Register the panel UI
  context.registerPanel('weatherPanel', WeatherPanelComponent);
}

// Example Svelte-like component for the panel UI
const WeatherPanelComponent = {
  async render({ context }) {
    const apiKey = await context.getSetting('weatherPanel.apiKey');
    const city = await context.getSetting('weatherPanel.defaultCity');
    let weather = 'Loading...';
    if (apiKey) {
      try {
        const res = await fetch(`https://api.openweathermap.org/data/2.5/weather?q=${encodeURIComponent(city)}&appid=${apiKey}&units=metric`);
        const data = await res.json();
        weather = `${data.weather[0].main}, ${data.main.temp}°C`;
      } catch (e) {
        weather = 'Failed to fetch weather.';
      }
    } else {
      weather = 'Set your API key in plugin settings.';
    }
    return `<div><h3>Weather in ${city}</h3><p>${weather}</p></div>`;
  }
};

export function deactivate() {
  // Cleanup if needed
}
```

### Plugin Settings UI (Example)
- The host IDE should render a settings page for the plugin based on the `settings` manifest section.
- Users can enter their API key and default city, which are persisted and accessible via `context.getSetting`.

---

## Detailed Architecture Diagram (Mermaid)

```mermaid
graph TD
  subgraph Frontend (Svelte)
    FE_Editor["Monaco Editor"]
    FE_Explorer["File Explorer"]
    FE_Terminal["Terminal"]
    FE_PluginHost["Plugin Host (Sandboxed)"]
    FE_Plugin["Plugin UI (Weather Panel, etc.)"]
    FE_Collab["Collaboration UI"]
    FE_AI["AI Suggestions UI"]
  end

  subgraph Backend (Python/FastAPI)
    BE_API["REST/WebSocket API"]
    BE_LSP["LSP Server"]
    BE_Git["Git Integration"]
    BE_PluginAPI["Plugin API"]
    BE_DB["Database"]
    BE_Collab["Collaboration Server (Yjs)"]
    BE_AI["AI Service (OpenAI, LLM)"]
  end

  FE_Editor -- "API Calls" --> BE_API
  FE_Explorer -- "API Calls" --> BE_API
  FE_Terminal -- "WebSocket" --> BE_API
  FE_PluginHost -- "Plugin API" --> FE_Plugin
  FE_PluginHost -- "API Calls" --> BE_PluginAPI
  BE_PluginAPI -- "Register/Invoke" --> BE_API
  BE_API -- "DB Access" --> BE_DB
  BE_API -- "LSP" --> BE_LSP
  BE_API -- "Git" --> BE_Git
  FE_Collab -- "WebSocket/CRDT" --> BE_Collab
  FE_Editor -- "Collab Events" --> FE_Collab
  FE_AI -- "API Calls" --> BE_AI
  FE_Editor -- "AI Suggestions" --> FE_AI
  BE_API -- "Collab/AI Routing" --> BE_Collab
  BE_API -- "Collab/AI Routing" --> BE_AI
```

--- 