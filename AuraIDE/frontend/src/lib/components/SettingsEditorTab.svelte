<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  let fontSize = 14;
  let fontFamily = 'monospace';
  let tabSize = 4;
  let lineNumbers = true;
  let minimap = true;
  let wordWrap = false;
  const dispatch = createEventDispatcher();
  onMount(() => {
    try {
      const s = JSON.parse(localStorage.getItem('editorSettings') || '{}');
      fontSize = s.fontSize ?? fontSize;
      fontFamily = s.fontFamily ?? fontFamily;
      tabSize = s.tabSize ?? tabSize;
      lineNumbers = s.lineNumbers ?? lineNumbers;
      minimap = s.minimap ?? minimap;
      wordWrap = s.wordWrap ?? wordWrap;
    } catch {}
  });
  function save() {
    const s = { fontSize, fontFamily, tabSize, lineNumbers, minimap, wordWrap };
    localStorage.setItem('editorSettings', JSON.stringify(s));
    dispatch('change', { settings: s });
  }
</script>
<div>
  <label>Font Size: <input type="number" min="8" max="32" bind:value={fontSize} on:change={save} /></label><br>
  <label>Font Family: <input type="text" bind:value={fontFamily} on:change={save} /></label><br>
  <label>Tab Size: <input type="number" min="2" max="8" bind:value={tabSize} on:change={save} /></label><br>
  <label><input type="checkbox" bind:checked={lineNumbers} on:change={save} /> Show Line Numbers</label><br>
  <label><input type="checkbox" bind:checked={minimap} on:change={save} /> Show Minimap</label><br>
  <label><input type="checkbox" bind:checked={wordWrap} on:change={save} /> Word Wrap</label><br>
</div> 