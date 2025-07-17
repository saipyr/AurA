<script lang="ts">
  import { onMount } from 'svelte';
  import { readFile, saveFile } from '../apis/files/index';
  let filePath = 'README.md'; // Example file
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