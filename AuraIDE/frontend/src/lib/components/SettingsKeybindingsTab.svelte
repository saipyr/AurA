<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  let keybindings = [
    { action: 'Fuzzy Finder', key: 'Ctrl+P' },
    { action: 'Settings', key: 'Ctrl+,' },
    { action: 'Rename', key: 'F2' },
    { action: 'Delete', key: 'Del' },
    // Add more as needed
  ];
  const dispatch = createEventDispatcher();
  onMount(() => {
    try {
      const kb = JSON.parse(localStorage.getItem('keybindings') || '[]');
      if (kb.length) keybindings = kb;
    } catch {}
  });
  function updateKey(i, e) {
    keybindings[i].key = e.target.value;
    localStorage.setItem('keybindings', JSON.stringify(keybindings));
    dispatch('change', { keybindings });
  }
  function reset() {
    localStorage.removeItem('keybindings');
    location.reload();
  }
</script>
<div>
  <table>
    <tr><th>Action</th><th>Shortcut</th></tr>
    {#each keybindings as kb, i}
      <tr>
        <td>{kb.action}</td>
        <td><input type="text" bind:value={kb.key} on:change={e => updateKey(i, e)} /></td>
      </tr>
    {/each}
  </table>
  <button on:click={reset}>Reset to Defaults</button>
</div> 