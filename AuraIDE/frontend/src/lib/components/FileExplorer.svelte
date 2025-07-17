<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import { listDir, createFile, createFolder, renamePath, deletePath, readFile } from '../apis/files/index';
  import { gitStatus } from '../apis/git/index';
  import MonacoEditor from './MonacoEditor.svelte';
  import Tooltip from '../../../src/lib/components/common/Tooltip.svelte';
  import ContextMenu from './common/ContextMenu.svelte';
  let rootPath = '';
  let tree: Array<{name: string, isDir: boolean}> = [];
  let expanded: Record<string, boolean> = {};
  let error = '';
  let search = '';
  let gitFiles: Record<string, string> = {};
  const dispatch = createEventDispatcher();

  // Context menu state
  let contextMenuVisible = false;
  let contextMenuX = 0;
  let contextMenuY = 0;
  let contextMenuItem: {name: string, isDir: boolean} | null = null;

  function showContextMenu(e, item) {
    e.preventDefault();
    contextMenuVisible = true;
    contextMenuX = e.clientX;
    contextMenuY = e.clientY;
    contextMenuItem = item;
    document.addEventListener('click', hideContextMenu);
  }
  function hideContextMenu() {
    contextMenuVisible = false;
    contextMenuItem = null;
    document.removeEventListener('click', hideContextMenu);
  }
  function handleContextAction(e) {
    const action = e.detail.action;
    if (!contextMenuItem) return;
    if (action === 'open') handleOpen(contextMenuItem.name);
    if (action === 'rename') contextRename();
    if (action === 'delete') contextDelete();
    if (action === 'copy') {
      navigator.clipboard.writeText(contextMenuItem.name);
    }
    hideContextMenu();
  }

  // Drag-and-drop state
  let draggingItem: string | null = null;
  let dropTarget: string | null = null;

  function onDragStart(e, item) {
    draggingItem = item.name;
    e.dataTransfer.setData('text/plain', item.name);
    e.dataTransfer.effectAllowed = 'move';
  }
  function onDragOver(e, item) {
    if (item.isDir && draggingItem !== item.name) {
      e.preventDefault();
      dropTarget = item.name;
    }
  }
  function onDragLeave(e, item) {
    if (dropTarget === item.name) dropTarget = null;
  }
  async function onDrop(e, item) {
    e.preventDefault();
    if (draggingItem && item.isDir && draggingItem !== item.name) {
      try {
        await renamePath(draggingItem, item.name + '/' + draggingItem.split('/').pop());
        await load();
      } catch (e) {
        error = e.message;
      }
    }
    draggingItem = null;
    dropTarget = null;
  }
  function onDragEnd() {
    draggingItem = null;
    dropTarget = null;
  }

  async function load(path = rootPath) {
    try {
      error = '';
      tree = await listDir(path);
      // Fetch git status and build a map for quick lookup
      const gitList = await gitStatus();
      gitFiles = {};
      for (const f of gitList) {
        gitFiles[f.path] = f.status;
      }
    } catch (e) {
      error = e.message;
    }
  }

  onMount(() => load());

  function toggle(folder: string) {
    expanded[folder] = !expanded[folder];
  }

  async function handleOpen(path: string) {
    dispatch('open', { path });
  }

  function filterTree(item) {
    return !search || item.name.toLowerCase().includes(search.toLowerCase());
  }

  function gitBadge(status) {
    if (status === 'staged') return '●';
    if (status === 'unstaged') return '●';
    if (status === 'untracked') return '●';
    return '';
  }
  function gitBadgeColor(status) {
    if (status === 'staged') return '#1976d2'; // blue
    if (status === 'unstaged') return '#d32f2f'; // red
    if (status === 'untracked') return '#388e3c'; // green
    return 'transparent';
  }

  let previewContent = '';
  let previewPath = '';
  let loadingPreview = false;

  async function showPreview(path: string, limit: number = 40) {
    loadingPreview = true;
    previewPath = path;
    try {
      let content = await readFile(path);
      // Limit preview to first N lines
      previewContent = content.split('\n').slice(0, limit).join('\n');
      if (content.split('\n').length > limit) previewContent += '\n...';
    } catch (e) {
      previewContent = 'Error loading preview.';
    } finally {
      loadingPreview = false;
    }
  }

  let folderPreviewContent = '';
  let folderPreviewLoading = false;
  async function showFolderPreview(path: string) {
    folderPreviewLoading = true;
    try {
      const entries = await listDir(path);
      folderPreviewContent = `<b>${entries.length} items</b><br>` + entries.map(e => (e.isDir ? '📁 ' : '📄 ') + e.name).join('<br>');
    } catch (e) {
      folderPreviewContent = 'Error loading folder contents.';
    } finally {
      folderPreviewLoading = false;
    }
  }

  // Context menu actions
  async function contextOpen() {
    if (contextMenuItem) handleOpen(contextMenuItem.name);
    hideContextMenu();
  }
  async function contextRename() {
    if (contextMenuItem) {
      const newName = prompt('New name?', contextMenuItem.name);
      if (newName && newName !== contextMenuItem.name) await renamePath(contextMenuItem.name, newName).then(() => load()).catch(e => error = e.message);
    }
    hideContextMenu();
  }
  async function contextDelete() {
    if (contextMenuItem && confirm('Delete ' + contextMenuItem.name + '?')) await deletePath(contextMenuItem.name).then(() => load()).catch(e => error = e.message);
    hideContextMenu();
  }
  async function contextCreateFile() {
    const name = prompt('File name?');
    if (name) await createFile(name).then(() => load()).catch(e => error = e.message);
    hideContextMenu();
  }
  async function contextCreateFolder() {
    const name = prompt('Folder name?');
    if (name) await createFolder(name).then(() => load()).catch(e => error = e.message);
    hideContextMenu();
  }
</script>

<div style="display:flex;gap:16px;">
  <div style="flex:2;">
    <div>
      <input placeholder="Search files..." bind:value={search} style="margin-bottom:8px;width:70%;" />
      <button on:click={contextCreateFile}>New File</button>
      <button on:click={contextCreateFolder}>New Folder</button>
    </div>
    {#if error}
      <div class="error">{error}</div>
    {/if}
    <ul>
      {#each tree.filter(filterTree) as item}
        <li
          draggable={!item.isDir}
          on:dragstart={e => onDragStart(e, item)}
          on:dragover={e => onDragOver(e, item)}
          on:dragleave={e => onDragLeave(e, item)}
          on:drop={e => onDrop(e, item)}
          on:dragend={onDragEnd}
          class:selected={dropTarget === item.name}
          on:contextmenu={e => showContextMenu(e, item)}
          style="background: {dropTarget === item.name ? '#e0e0ff' : 'transparent'}"
          on:mouseenter={() => !item.isDir && showPreview(item.name)}
        >
          {#if item.isDir}
            <Tooltip content={folderPreviewLoading ? 'Loading...' : folderPreviewContent} placement="right" allowHTML={true}>
              <span on:mouseenter={() => showFolderPreview(item.name)} on:click={() => toggle(item.name)}>{expanded[item.name] ? '▼' : '▶'} {item.name}</span>
            </Tooltip>
          {:else}
            <Tooltip content={`<pre style='margin:0;max-width:400px;max-height:300px;overflow:auto;'>${previewContent}</pre>`} placement="right" allowHTML={true}>
              <span on:click={() => handleOpen(item.name)}>{item.name}</span>
            </Tooltip>
            {#if gitBadge(gitFiles[item.name])}
              <span style="color:{gitBadgeColor(gitFiles[item.name])};margin-left:6px;font-size:1.1em;">{gitBadge(gitFiles[item.name])}</span>
            {/if}
          {/if}
        </li>
      {/each}
    </ul>
    <ContextMenu x={contextMenuX} y={contextMenuY} visible={contextMenuVisible} on:action={handleContextAction} />
  </div>
  <div style="flex:1;min-width:250px;max-width:350px;background:#fafbfc;border-left:1px solid #eee;padding:8px;">
    <div style="font-size:0.9em;color:#888;margin-bottom:4px;">Preview: {previewPath}</div>
    {#if loadingPreview}
      <div>Loading...</div>
    {:else if previewPath}
      <MonacoEditor filePath={previewPath} language={previewPath.split('.').pop()} baseContent={previewContent} modifiedContent={previewContent} theme="vs-dark" />
    {/if}
  </div>
</div>

<style>
  .context-menu > div {
    padding: 6px 16px;
    cursor: pointer;
  }
  .context-menu > div:hover {
    background: #f0f0f0;
  }
  .selected {
    outline: 2px solid #4a90e2;
  }
</style> 