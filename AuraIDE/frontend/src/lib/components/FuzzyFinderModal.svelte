<script lang="ts">
  import Modal from './common/Modal.svelte';
  import MonacoEditor from './MonacoEditor.svelte';
  import { readFile, listDir } from '../apis/files/index';
  import { onMount } from 'svelte';
  import Tooltip from '../../../src/lib/components/common/Tooltip.svelte';
  import ContextMenu from './common/ContextMenu.svelte';
  let open = false;
  let search = '';
  let allFiles: Array<{path: string, isDir: boolean}> = [];
  let filtered: Array<{path: string, isDir: boolean}> = [];
  let selectedIdx = 0;
  let previewContent = '';
  let previewPath = '';
  let loadingPreview = false;
  let contextMenuX = 0;
  let contextMenuY = 0;
  let contextMenuVisible = false;
  let contextMenuItem = null;
  let recentFiles: Array<{path: string, isDir: boolean}> = [];
  let showMonacoPreview = true;
  let previewLines = 40;
  let filterType = 'all'; // 'all', 'file', 'folder'
  let filterExt = '';

  // Recursively gather all files and folders in the workspace
  async function gatherFiles(path = ''): Promise<Array<{path: string, isDir: boolean}>> {
    const entries = await listDir(path);
    let files: Array<{path: string, isDir: boolean}> = [];
    for (const entry of entries) {
      const fullPath = path ? `${path}/${entry.name}` : entry.name;
      if (entry.isDir) {
        files.push({ path: fullPath, isDir: true });
        files = files.concat(await gatherFiles(fullPath));
      } else {
        files.push({ path: fullPath, isDir: false });
      }
    }
    return files;
  }

  function fuzzyMatch(files: Array<{path: string, isDir: boolean}>, query: string): Array<{path: string, isDir: boolean}> {
    if (!query) return files.slice(0, 50);
    const q = query.toLowerCase();
    return files
      .map(f => ({ ...f, score: f.path.toLowerCase().indexOf(q) }))
      .filter(x => x.score !== -1)
      .sort((a, b) => a.score - b.score)
      .slice(0, 50);
  }

  async function showPreview(path: string, limit: number = previewLines) {
    loadingPreview = true;
    previewPath = path;
    try {
      let content = await readFile(path);
      previewContent = content.split('\n').slice(0, limit).join('\n');
      if (content.split('\n').length > limit) previewContent += '\n...';
    } catch (e) {
      previewContent = 'Error loading preview.';
    } finally {
      loadingPreview = false;
    }
  }

  function select(idx: number) {
    selectedIdx = idx;
    if (filtered[idx] && !filtered[idx].isDir) showPreview(filtered[idx].path);
  }

  function addRecentFile(item) {
    if (item.isDir) return;
    recentFiles = recentFiles.filter(f => f.path !== item.path);
    recentFiles.unshift(item);
    if (recentFiles.length > 10) recentFiles = recentFiles.slice(0, 10);
    localStorage.setItem('recentFiles', JSON.stringify(recentFiles));
  }

  function fileIcon(item) {
    if (item.isDir) return '📁';
    const ext = item.path.split('.').pop()?.toLowerCase();
    if (['js', 'ts', 'jsx', 'tsx'].includes(ext)) return '📦';
    if (['py'].includes(ext)) return '🐍';
    if (['md'].includes(ext)) return '📘';
    if (['json'].includes(ext)) return '🗄️';
    if (['png', 'jpg', 'jpeg', 'gif', 'svg'].includes(ext)) return '🖼️';
    if (['sh', 'bat', 'cmd'].includes(ext)) return '��';
    return '📄';
  }

  function applyFilters(files) {
    let out = files;
    if (filterType === 'file') out = out.filter(f => !f.isDir);
    if (filterType === 'folder') out = out.filter(f => f.isDir);
    if (filterExt) out = out.filter(f => f.path.endsWith('.' + filterExt));
    return out;
  }

  function openFileOrFolder(item) {
    addRecentFile(item);
    if (item.isDir) {
      // Dispatch event to parent to expand folder in explorer
      const event = new CustomEvent('expand-folder', { detail: { path: item.path } });
      dispatchEvent(event);
      open = false;
    } else {
      const event = new CustomEvent('open', { detail: { path: item.path } });
      dispatchEvent(event);
      open = false;
    }
  }

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
    // Dispatch event to parent for handling
    const event = new CustomEvent('context-action', { detail: { action, item: contextMenuItem } });
    dispatchEvent(event);
    hideContextMenu();
  }

  onMount(async () => {
    allFiles = await gatherFiles('');
    filtered = allFiles;
    if (filtered.length && !filtered[0].isDir) showPreview(filtered[0].path);
    // Load recent files
    try {
      recentFiles = JSON.parse(localStorage.getItem('recentFiles') || '[]');
    } catch {}
  });

  $: filtered = applyFilters(fuzzyMatch(allFiles, search));
  $: if (filtered[selectedIdx] && !filtered[selectedIdx].isDir) showPreview(filtered[selectedIdx].path);
</script>

{#if open}
  <Modal on:close={() => (open = false)}>
    <div style="width:600px;max-width:90vw;display:flex;gap:16px;">
      <div style="flex:1;">
        <input
          placeholder="Type to search files..."
          bind:value={search}
          style="width:100%;margin-bottom:8px;"
          on:keydown={(e) => {
            if (e.key === 'ArrowDown') select(Math.min(selectedIdx + 1, filtered.length - 1));
            if (e.key === 'ArrowUp') select(Math.max(selectedIdx - 1, 0));
            if (e.key === 'Enter' && filtered[selectedIdx]) openFileOrFolder(filtered[selectedIdx]);
          }}
        />
        <div style="margin-bottom:8px;display:flex;gap:12px;align-items:center;">
          <label>Type:
            <select bind:value={filterType}>
              <option value="all">All</option>
              <option value="file">Files</option>
              <option value="folder">Folders</option>
            </select>
          </label>
          <label>Ext:
            <input type="text" bind:value={filterExt} placeholder="e.g. js, py" style="width:60px;" />
          </label>
          <label>Preview:
            <select bind:value={showMonacoPreview}>
              <option value={true}>Monaco</option>
              <option value={false}>Plain</option>
            </select>
          </label>
          <label>Lines:
            <input type="number" min="5" max="200" bind:value={previewLines} style="width:50px;" />
          </label>
        </div>
        {#if recentFiles.length}
          <div style="margin-bottom:8px;">
            <b>Recent Files:</b>
            <ul style="max-height:120px;overflow:auto;">
              {#each recentFiles as item}
                <li style="cursor:pointer;display:flex;align-items:center;gap:6px;" on:click={() => openFileOrFolder(item)}>
                  <span>{fileIcon(item)}</span> {item.path}
                </li>
              {/each}
            </ul>
          </div>
        {/if}
        <ul style="max-height:400px;overflow:auto;">
          {#each filtered as item, i}
            <li
              style="padding:4px 8px;cursor:pointer;background:{i === selectedIdx ? '#e0e0ff' : 'transparent'};display:flex;align-items:center;gap:6px;"
              on:mouseenter={() => select(i)}
              on:click={() => openFileOrFolder(item)}
              on:contextmenu={e => showContextMenu(e, item)}
            >
              <span>{fileIcon(item)}</span>
              {#if item.isDir}
                {item.path}/
              {:else}
                <Tooltip content={`<pre style='margin:0;max-width:400px;max-height:300px;overflow:auto;'>${previewContent}</pre>`} placement="right" allowHTML={true}>
                  <span>{item.path}</span>
                </Tooltip>
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
        {:else}
          {#if showMonacoPreview}
            <MonacoEditor filePath={previewPath} language={previewPath.split('.').pop()} baseContent={previewContent} modifiedContent={previewContent} theme="vs-dark" />
          {:else}
            <pre style="max-width:100%;max-height:400px;overflow:auto;background:#222;color:#eee;padding:8px;">{previewContent}</pre>
          {/if}
        {/if}
      </div>
    </div>
  </Modal>
{/if} 