<script lang="ts">
  import FileExplorer from './components/FileExplorer.svelte';
  import MonacoEditor from './components/MonacoEditor.svelte';
  import TerminalTabs from './components/TerminalTabs.svelte';
  import GitPanel from './components/GitPanel.svelte';
  let currentFile = 'README.md';
  function handleOpen(e) {
    currentFile = e.detail.path;
  }
</script>

<div style="display: flex; height: 100vh;">
  <div style="width: 300px; border-right: 1px solid #ccc; overflow-y: auto;">
    <FileExplorer on:open={handleOpen} />
    <GitPanel />
  </div>
  <div style="flex: 1; display: flex; flex-direction: column;">
    <MonacoEditor filePath={currentFile} language="markdown" theme="vs-dark" />
    <TerminalTabs />
  </div>
</div> 