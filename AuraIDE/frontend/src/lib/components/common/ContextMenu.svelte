<script lang="ts">
  import { createEventDispatcher, onMount, onDestroy } from 'svelte';
  export let x = 0;
  export let y = 0;
  export let visible = false;
  export let actions = [
    { label: 'Open', value: 'open' },
    { label: 'Rename', value: 'rename', shortcut: 'F2' },
    { label: 'Delete', value: 'delete', shortcut: 'Del' },
    { label: 'Copy Path', value: 'copy' }
  ];
  const dispatch = createEventDispatcher();

  function handleAction(action) {
    dispatch('action', { action });
  }

  function handleKeydown(e) {
    if (!visible) return;
    if (e.key === 'F2') handleAction('rename');
    if (e.key === 'Delete') handleAction('delete');
  }

  onMount(() => {
    window.addEventListener('keydown', handleKeydown);
  });
  onDestroy(() => {
    window.removeEventListener('keydown', handleKeydown);
  });
</script>

{#if visible}
  <div class="context-menu" style="position:fixed;top:{y}px;left:{x}px;z-index:1000;background:#fff;border:1px solid #ccc;box-shadow:2px 2px 8px #aaa;min-width:140px;">
    {#each actions as a}
      <div class="item" on:click={() => handleAction(a.value)}>
        {a.label}
        {#if a.shortcut}
          <span style="float:right;color:#888;font-size:0.9em;">{a.shortcut}</span>
        {/if}
      </div>
    {/each}
  </div>
{/if}

<style>
  .context-menu > .item {
    padding: 6px 16px;
    cursor: pointer;
    user-select: none;
  }
  .context-menu > .item:hover {
    background: #f0f0f0;
  }
</style> 