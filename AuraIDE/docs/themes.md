# Themes & Layouts in AurA (Deep Dive)

This guide details the implementation of themes and layouts, inspired by VSCode, Eclipse, Cursor, and Claude IDE.

---

## 1. Theme Switching
### Overview & Goals
- Allow users to switch between light, dark, and custom themes easily.

### Implementation Steps
- Use Monaco's built-in themes and provide a UI selector.
- Store user preference in localStorage or DB.

```js
monaco.editor.setTheme('vs-dark');
```

### Advanced Usage
- Support per-project or per-workspace themes.
- Allow keyboard shortcuts for theme switching.

### Error Handling
- Fallback to default theme if custom theme fails to load.

### Testing
- Test theme switching and persistence across reloads.

---

## 2. Custom Themes
### Overview & Goals
- Enable users to define, import, and share custom themes.

### Implementation Steps
- Allow users to upload or paste JSON theme definitions.
- Use Monaco's `defineTheme` API to register new themes.

```js
monaco.editor.defineTheme('myCustomTheme', themeData);
```

### Advanced Usage
- Validate theme JSON and provide live preview.
- Support exporting and sharing themes.

### Error Handling
- Validate theme schema and handle parse errors.

### Testing
- Test theme import/export and error cases.

---

## 3. Layout Persistence
### Overview & Goals
- Remember user panel/sidebar layout across sessions.

### Implementation Steps
- Store layout state in localStorage or DB.
- Restore layout on app load.

### Advanced Usage
- Support multiple saved layouts per user/project.
- Allow layout reset to default.

### Error Handling
- Handle corrupted or missing layout data.

### Testing
- Test layout save/restore and edge cases.

---

## 4. Drag-and-Drop UI
### Overview & Goals
- Allow users to rearrange panels and sidebars via drag-and-drop.

### Implementation Steps
- Use Svelte's drag-and-drop actions for UI elements.

```svelte
<div use:drag on:dragend={saveLayout}>Sidebar</div>
```

### Advanced Usage
- Support snapping, resizing, and docking panels.
- Animate panel transitions for smooth UX.

### Error Handling
- Prevent invalid panel positions and overlaps.

### Testing
- UI tests for drag-and-drop and layout changes.

---

## 5. Security & Performance
- Sanitize all user-supplied theme/layout data.
- Optimize layout rendering for large/complex UIs.

---

## 6. References
- [VSCode Themes](https://code.visualstudio.com/api/extension-guides/color-theme)
- [Eclipse Themes](https://www.eclipse.org/eclipseide/)
- [Cursor Themes](https://github.com/getcursor/cursor)
- [Claude IDE Docs](https://docs.anthropic.com/claude) 