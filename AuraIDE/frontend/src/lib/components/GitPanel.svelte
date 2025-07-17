<script lang="ts">
  import { onMount } from 'svelte';
  import { gitStatus, gitCommit, gitPush, gitPull, gitBranches, gitCheckout, gitStage, gitUnstage, gitDiff, gitFileContent } from '../apis/git/index';
  import MonacoEditor from './MonacoEditor.svelte';
  let files: any[] = [];
  let commitMsg = '';
  let output = '';
  let error = '';
  let loading = false;
  let branches: string[] = [];
  let currentBranch = '';
  let selectedFile: any = null;
  let selectedDiff: string = '';
  let selectedStaged: boolean = false;
  let baseContent: string | null = null;
  let modifiedContent: string | null = null;
  let sideBySide = true;
  let hideUnchanged = true;
  let showMoves = true;
  let wordWrap = false;
  let customTheme = '';
  let monacoEditorRef;
  function goToNextChange() {
    monacoEditorRef?.goToNextChange?.();
  }
  function goToPrevChange() {
    monacoEditorRef?.goToPrevChange?.();
  }

  async function loadStatus() {
    loading = true;
    try {
      files = await gitStatus();
      error = '';
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }
  async function doCommit() {
    loading = true;
    try {
      output = await gitCommit(commitMsg);
      commitMsg = '';
      await loadStatus();
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }
  async function doPush() {
    loading = true;
    try {
      output = await gitPush();
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }
  async function doPull() {
    loading = true;
    try {
      output = await gitPull();
      await loadStatus();
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }
  async function loadBranches() {
    try {
      const raw = await gitBranches();
      branches = raw.split('\n').map(b => b.trim()).filter(Boolean);
      const current = branches.find(b => b.startsWith('*'));
      currentBranch = current ? current.replace('*', '').trim() : '';
    } catch (e) {
      error = e.message;
    }
  }
  async function switchBranch(branch: string) {
    if (branch === currentBranch) return;
    loading = true;
    try {
      output = await gitCheckout(branch);
      await loadBranches();
      await loadStatus();
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }
  async function stageFile(file: string) {
    loading = true;
    try {
      await gitStage(file);
      await loadStatus();
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }
  async function unstageFile(file: string) {
    loading = true;
    try {
      await gitUnstage(file);
      await loadStatus();
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }
  async function showDiff(file: any, staged: boolean) {
    selectedFile = file;
    selectedStaged = staged;
    selectedDiff = '';
    baseContent = null;
    modifiedContent = null;
    try {
      baseContent = await gitFileContent(file.path, 'HEAD');
      if (staged) {
        modifiedContent = await gitFileContent(file.path, 'index');
      } else {
        modifiedContent = await gitFileContent(file.path, 'working');
      }
    } catch (e) {
      error = e.message;
    }
  }
  function groupFiles(status: string) {
    return files.filter(f => f.status === status);
  }
  onMount(() => { loadStatus(); loadBranches(); });
</script>

<div style="border:1px solid #ccc; padding:16px; background:#fafbfc;">
  <h3>Git Status</h3>
  {#if loading}
    <div>Loading...</div>
  {/if}
  {#if error}
    <div class="error">{error}</div>
  {/if}
  <div style="display:flex; gap:32px;">
    <div style="flex:1;">
      <h4>Staged</h4>
      <ul>
        {#each groupFiles('staged') as file}
          <li>
            <span style="cursor:pointer;" on:click={() => showDiff(file, true)}>{file.path}</span>
            <button on:click={() => unstageFile(file.path)} disabled={loading}>Unstage</button>
          </li>
        {/each}
      </ul>
      <h4>Unstaged</h4>
      <ul>
        {#each groupFiles('unstaged') as file}
          <li>
            <span style="cursor:pointer;" on:click={() => showDiff(file, false)}>{file.path}</span>
            <button on:click={() => stageFile(file.path)} disabled={loading}>Stage</button>
          </li>
        {/each}
      </ul>
      <h4>Untracked</h4>
      <ul>
        {#each groupFiles('untracked') as file}
          <li>
            <span style="cursor:pointer;" on:click={() => showDiff(file, false)}>{file.path}</span>
            <button on:click={() => stageFile(file.path)} disabled={loading}>Stage</button>
          </li>
        {/each}
      </ul>
    </div>
    <div style="flex:2;">
      {#if selectedFile}
        <h4>Diff: {selectedFile.path} ({selectedStaged ? 'staged' : 'unstaged'})</h4>
        <div style="margin-bottom:8px;">
          <button on:click={() => sideBySide = !sideBySide}>
            {sideBySide ? 'Switch to Inline Diff' : 'Switch to Side-by-Side Diff'}
          </button>
          <label style="margin-left:12px;">
            <input type="checkbox" bind:checked={hideUnchanged} /> Hide Unchanged Regions
          </label>
          <label style="margin-left:12px;">
            <input type="checkbox" bind:checked={showMoves} /> Highlight Moved Code
          </label>
          <label style="margin-left:12px;">
            <input type="checkbox" bind:checked={wordWrap} /> Word Wrap
          </label>
          <label style="margin-left:12px;">
            Custom Theme: <input type="text" bind:value={customTheme} placeholder="(optional)" style="width:120px;" />
          </label>
          <button style="margin-left:12px;" on:click={goToPrevChange}>Previous Change</button>
          <button on:click={goToNextChange}>Next Change</button>
        </div>
        {#if baseContent !== null && modifiedContent !== null}
          <MonacoEditor
            bind:this={monacoEditorRef}
            filePath={selectedFile.path}
            language={selectedFile.path.split('.').pop()}
            theme="vs-dark"
            baseContent={baseContent}
            modifiedContent={modifiedContent}
            renderSideBySide={sideBySide}
            hideUnchangedRegions={hideUnchanged}
            showMoves={showMoves}
            wordWrap={wordWrap}
            customTheme={customTheme || null}
          />
        {:else}
          <div>Loading diff...</div>
        {/if}
      {/if}
    </div>
  </div>
  <div style="margin-top:16px;">
    <input placeholder="Commit message" bind:value={commitMsg} style="width:60%;" />
    <button on:click={doCommit} disabled={loading || !commitMsg}>Commit</button>
    <button on:click={doPush} disabled={loading}>Push</button>
    <button on:click={doPull} disabled={loading}>Pull</button>
  </div>
  <div style="margin-top:24px;">
    <h4>Branches</h4>
    <ul style="list-style:none; padding:0;">
      {#each branches as b}
        <li>
          <button
            style="background:{b.startsWith('*') ? '#4a90e2' : '#eee'};color:{b.startsWith('*') ? '#fff' : '#222'};border:none;padding:4px 12px;margin:2px 0;cursor:pointer;"
            on:click={() => switchBranch(b.replace('*', '').trim())}
            disabled={b.startsWith('*') || loading}
          >
            {b.replace('*', '').trim()}
            {#if b.startsWith('*')} <span style="font-weight:bold;"> (current)</span>{/if}
          </button>
        </li>
      {/each}
    </ul>
  </div>
  {#if output}
    <pre style="margin-top:16px;">{output}</pre>
  {/if}
</div>

<style>
  .error { color: red; margin-bottom: 8px; }
</style> 