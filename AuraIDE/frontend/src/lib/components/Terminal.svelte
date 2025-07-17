<script lang="ts">
  import { onMount } from 'svelte';
  export let session: string;
  let term;
  let socket: WebSocket;
  let container: HTMLDivElement;
  let error = '';

  onMount(async () => {
    const { Terminal } = await import('xterm');
    term = new Terminal();
    term.open(container);
    try {
      socket = new WebSocket(`ws://localhost:8000/ws/terminal?session=${encodeURIComponent(session)}`);
      socket.onmessage = (event) => {
        term.write(event.data);
      };
      socket.onerror = (e) => {
        error = 'Terminal connection error';
      };
      term.onData(data => {
        if (socket.readyState === WebSocket.OPEN) {
          socket.send(data);
        }
      });
    } catch (e) {
      error = 'Failed to connect to terminal: ' + e.message;
    }
  });
</script>

<div>
  {#if error}
    <div class="error">{error}</div>
  {/if}
  <div bind:this={container} style="height:400px;width:100%;background:#111;"></div>
</div>

<style>
  .error { color: red; margin-bottom: 8px; }
</style> 