<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  export let open = false;
  let tab = 'general';
  const dispatch = createEventDispatcher();
  function close() { dispatch('close'); }
</script>
{#if open}
  <div class="modal-bg" on:click={close}></div>
  <div class="modal">
    <div class="tabs">
      <button class:active={tab==='general'} on:click={() => tab='general'}>General</button>
      <button class:active={tab==='editor'} on:click={() => tab='editor'}>Editor</button>
      <button class:active={tab==='keybindings'} on:click={() => tab='keybindings'}>Keybindings</button>
    </div>
    <div class="content">
      {#if tab==='general'}
        <h3>General Settings</h3>
        <p>Theme, language, etc. (to be implemented)</p>
      {:else if tab==='editor'}
        <h3>Editor Settings</h3>
        <slot name="editor" />
      {:else if tab==='keybindings'}
        <h3>Keybindings</h3>
        <slot name="keybindings" />
      {/if}
    </div>
    <button class="close" on:click={close}>Close</button>
  </div>
{/if}
<style>
  .modal-bg { position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.2);z-index:1000; }
  .modal { position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:#fff;padding:24px 32px;z-index:1001;min-width:400px;min-height:300px;border-radius:8px;box-shadow:0 4px 32px #0002; }
  .tabs { display:flex;gap:12px;margin-bottom:16px; }
  .tabs button { background:none;border:none;padding:8px 16px;cursor:pointer;font-weight:bold; }
  .tabs .active { border-bottom:2px solid #1976d2;color:#1976d2; }
  .content { min-height:180px; }
  .close { position:absolute;top:12px;right:16px;background:none;border:none;font-size:1.2em;cursor:pointer; }
</style> 