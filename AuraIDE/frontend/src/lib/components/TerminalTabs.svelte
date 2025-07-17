// Each terminal tab is assigned a unique session ID (UUID).
// The session ID is passed to the backend so the shell process persists across reloads.
// See docs/terminal.md for details.
// Keyboard shortcuts: Ctrl+T/Cmd+T (new), Ctrl+W/Cmd+W (close), Ctrl+Tab (next), Ctrl+Shift+Tab (prev)
// Double-click tab to rename.
// Drag divider to resize terminal area.
<script lang="ts">
  import { onMount } from 'svelte';
  import Terminal from './Terminal.svelte';
  function uuidv4() {
    return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
      (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
    );
  }
  let terminals: Array<{ id: number, title: string, session: string, editing?: boolean }> = [];
  let activeIdx = 0;
  let nextId = 1;
  let termHeight = 300;
  let resizing = false;
  let startY = 0;
  let startHeight = 0;
  const STORAGE_KEY = 'aura_terminal_tabs';
  function saveTabs() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({terminals, activeIdx, nextId, termHeight}));
  }
  function loadTabs() {
    const data = localStorage.getItem(STORAGE_KEY);
    if (data) {
      try {
        const obj = JSON.parse(data);
        terminals = obj.terminals || [];
        activeIdx = obj.activeIdx || 0;
        nextId = obj.nextId || 1;
        termHeight = obj.termHeight || 300;
      } catch {}
    }
  }
  $: saveTabs();

  function newTerminal() {
    terminals = [...terminals, { id: nextId++, title: `Terminal ${nextId - 1}`, session: uuidv4() }];
    activeIdx = terminals.length - 1;
  }
  function closeTerminal(idx: number) {
    terminals = terminals.filter((_, i) => i !== idx);
    if (activeIdx >= terminals.length) activeIdx = terminals.length - 1;
  }
  function startResize(e) {
    resizing = true;
    startY = e.clientY;
    startHeight = termHeight;
    window.addEventListener('mousemove', doResize);
    window.addEventListener('mouseup', stopResize);
  }
  function doResize(e) {
    if (resizing) {
      termHeight = Math.max(100, startHeight + (e.clientY - startY));
    }
  }
  function stopResize() {
    resizing = false;
    window.removeEventListener('mousemove', doResize);
    window.removeEventListener('mouseup', stopResize);
  }
  function startRename(idx: number) {
    terminals = terminals.map((t, i) => i === idx ? { ...t, editing: true } : { ...t, editing: false });
  }
  function finishRename(idx: number, value: string) {
    terminals = terminals.map((t, i) => i === idx ? { ...t, title: value, editing: false } : t);
  }
  function handleKeydown(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 't') { newTerminal(); e.preventDefault(); }
    if ((e.ctrlKey || e.metaKey) && e.key === 'w') { closeTerminal(activeIdx); e.preventDefault(); }
    if (e.ctrlKey && e.key === 'Tab') {
      if (e.shiftKey) {
        activeIdx = (activeIdx - 1 + terminals.length) % terminals.length;
      } else {
        activeIdx = (activeIdx + 1) % terminals.length;
      }
      e.preventDefault();
    }
  }
  onMount(() => { loadTabs(); if (terminals.length === 0) newTerminal(); });
</script>

<div style="display: flex; flex-direction: column; height: 100%;" tabindex="0" on:keydown={handleKeydown}>
  <div style="display: flex; align-items: center; background: #222; color: #fff;">
    {#each terminals as term, idx}
      <button
        on:click={() => activeIdx = idx}
        style="background: {activeIdx === idx ? '#444' : 'transparent'}; color: #fff; border: none; padding: 8px 16px; cursor: pointer;">
        {#if term.editing}
          <input value={term.title} autofocus on:blur={e => finishRename(idx, e.target.value)} on:keydown={e => e.key === 'Enter' && finishRename(idx, e.target.value)} />
        {:else}
          <span on:dblclick={() => startRename(idx)}>{term.title}</span>
        {/if}
        <span style="margin-left: 8px; color: #aaa; cursor: pointer;" on:click={() => closeTerminal(idx)}>×</span>
      </button>
    {/each}
    <button on:click={newTerminal} style="margin-left: 8px;">+</button>
  </div>
  <div style="flex: 1; min-height: 0; position: relative;">
    {#if terminals.length > 0}
      <div style="height: {termHeight}px;">
        <Terminal key={terminals[activeIdx].id} session={terminals[activeIdx].session} />
      </div>
      <div
        style="height: 6px; background: #ccc; cursor: row-resize; position: absolute; left: 0; right: 0; top: {termHeight}px; z-index: 10;"
        on:mousedown={startResize} />
    {/if}
  </div>
</div> 