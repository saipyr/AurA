<script lang="ts">
  import { onMount, createEventDispatcher, afterUpdate } from 'svelte';
  import { readFile, saveFile } from '../apis/files/index';
  let container: HTMLDivElement;
  export let filePath: string;
  export let language: string = 'javascript';
  export let theme: string = 'vs-dark';
  export let customTheme: string | null = null; // Name of custom Monaco theme
  export let baseContent: string | null = null;
  export let modifiedContent: string | null = null;
  /**
   * If true, show side-by-side diff. If false, show inline diff.
   */
  export let renderSideBySide: boolean = true;
  /**
   * If true, hide unchanged regions in large diffs.
   */
  export let hideUnchangedRegions: boolean = true;
  /**
   * If true, highlight moved code blocks (Monaco experimental).
   */
  export let showMoves: boolean = true;
  /**
   * If true, enable word wrap in diff view.
   */
  export let wordWrap: boolean = false;
  let editor: any;
  let monaco: any;
  let error = '';
  let saving = false;
  const dispatch = createEventDispatcher();
  let lspClient: any = null;
  let lspSocket: WebSocket | null = null;
  let originalModel: any = null;
  let modifiedModel: any = null;

  // Navigation state
  let changeIndex = 0;
  let lineChanges: any[] = [];

  async function loadContent() {
    try {
      error = '';
      const content = await readFile(filePath);
      editor.setValue(content);
    } catch (e) {
      error = e.message;
    }
  }

  async function save() {
    saving = true;
    error = '';
    try {
      await saveFile(filePath, editor.getValue());
    } catch (e) {
      error = e.message;
    } finally {
      saving = false;
    }
  }

  async function setupLsp(monaco, editor, language) {
    if (lspClient && lspClient.stop) lspClient.stop();
    if (lspSocket) lspSocket.close();
    try {
      const { MonacoLanguageClient, CloseAction, ErrorAction, createConnection } = await import('monaco-languageclient');
      const { listen } = await import('@codingame/monaco-jsonrpc');
      const url = `ws://localhost:8000/ws/lsp?language=${encodeURIComponent(language)}`;
      lspSocket = new WebSocket(url);
      listen({
        webSocket: lspSocket,
        onConnection: (connection) => {
          lspClient = new MonacoLanguageClient({
            name: `${language} LSP`,
            clientOptions: {
              documentSelector: [language],
              errorHandler: {
                error: () => ErrorAction.Continue,
                closed: () => CloseAction.Restart,
              },
            },
            connectionProvider: {
              get: () => Promise.resolve(createConnection(connection)),
            },
          });
          lspClient.start();
          connection.onClose(() => lspClient.stop());
        },
      });
    } catch (e) {
      error = 'Failed to set up LSP: ' + e.message;
    }
  }

  function defineCustomTheme() {
    if (monaco && customTheme) {
      monaco.editor.defineTheme(customTheme, {
        base: 'vs-dark',
        inherit: true,
        rules: [
          { token: '', background: '1e1e1e' },
          { token: 'deleted', foreground: 'ff5555' },
          { token: 'inserted', foreground: '50fa7b' },
        ],
        colors: {
          'diffEditor.insertedTextBackground': '#14421255',
          'diffEditor.removedTextBackground': '#60000055',
          'editor.background': '#1e1e1e',
        }
      });
    }
  }

  function createDiffOptions() {
    return {
      theme: customTheme || theme,
      automaticLayout: true,
      renderSideBySide,
      ignoreTrimWhitespace: false,
      renderIndicators: true,
      diffWordWrap: wordWrap ? 'on' : 'off',
      hideUnchangedRegions,
      experimental: { showMoves },
    };
  }

  function updateNavigation() {
    if (editor && editor.getLineChanges) {
      lineChanges = editor.getLineChanges() || [];
      changeIndex = 0;
    }
  }

  function goToChange(idx: number) {
    if (!lineChanges.length) return;
    changeIndex = (idx + lineChanges.length) % lineChanges.length;
    const change = lineChanges[changeIndex];
    if (change && editor && editor.modifiedEditor) {
      editor.modifiedEditor.revealLineInCenter(change.modifiedStartLineNumber);
    }
  }

  function goToNextChange() {
    goToChange(changeIndex + 1);
  }
  function goToPrevChange() {
    goToChange(changeIndex - 1);
  }

  // Expose navigation for parent
  export { goToNextChange, goToPrevChange };

  onMount(async () => {
    try {
      monaco = await import('monaco-editor');
      if (customTheme) defineCustomTheme();
      if (baseContent !== null && modifiedContent !== null) {
        // Diff editor
        editor = monaco.editor.createDiffEditor(container, createDiffOptions());
        originalModel = monaco.editor.createModel(baseContent, language);
        modifiedModel = monaco.editor.createModel(modifiedContent, language);
        editor.setModel({ original: originalModel, modified: modifiedModel });
        setTimeout(updateNavigation, 500);
      } else {
        // Regular editor
        editor = monaco.editor.create(container, {
          value: '',
          language,
          theme,
          automaticLayout: true
        });
        await loadContent();
        editor.onDidChangeModelContent(() => {
          dispatch('change', { value: editor.getValue() });
        });
        await setupLsp(monaco, editor, language);
      }
    } catch (e) {
      error = 'Failed to load Monaco Editor: ' + e.message;
    }
  });

  afterUpdate(() => {
    if (editor && monaco && baseContent !== null && modifiedContent !== null) {
      if (originalModel) originalModel.dispose();
      if (modifiedModel) modifiedModel.dispose();
      originalModel = monaco.editor.createModel(baseContent, language);
      modifiedModel = monaco.editor.createModel(modifiedContent, language);
      editor.setModel({ original: originalModel, modified: modifiedModel });
      editor.updateOptions(createDiffOptions());
      setTimeout(updateNavigation, 500);
    }
  });

  // Expose editor instance for plugins/extensibility
  export { editor };
</script>

<div>
  {#if error}
    <div class="error">{error}</div>
  {/if}
  <div bind:this={container} style="height:500px;"></div>
  {#if !baseContent && !modifiedContent}
    <button on:click={save} disabled={saving}>{saving ? 'Saving...' : 'Save'}</button>
  {/if}
</div> 