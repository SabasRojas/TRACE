<script lang="ts">
  import { responseStore } from '$lib/stores/responseStore';
  let parsedResponse: any = null;

  function isJson(str: string): boolean {
    try {
      JSON.parse(str);
      return true;
    } catch {
      return false;
    }
  }

  $: responseStore.subscribe(data => {
    parsedResponse = data ? parseResponse(data) : null;
  });

  function parseResponse(response: string | object) {
    if (typeof response === 'string') {
      try {
        return JSON.parse(response);
      } catch {
        return response;
      }
    } else if (typeof response === 'object') {
      return response;
    }
    return null;
  }
</script>

<style>
.response-container {
  padding: 1rem;
  background-color: #1f2937;
  color: #e5e7eb;
  border-radius: 0.5rem;
  width: 50vw;        /* responsive width based on viewport */
  height: 70vh;       /* responsive height based on viewport */
  max-width: 80vw;    /* optional cap to avoid overly wide */
  max-height: 80vh;   /* optional cap to avoid overly tall */
  overflow: auto;     /* enable both x & y scrolling */
  box-sizing: border-box;
}

.response-header {
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.response-body {
  white-space: pre;   /* preserve formatting and allow horizontal scroll */
  font-family: monospace;
  color: #f1f5f9;
}

ul {
  padding-left: 1rem;
}
li {
  margin-bottom: 0.25rem;
}
</style>

<div class="response-container">
  <div class="response-header">HTTP Response</div>
  {#if parsedResponse}
    {#if parsedResponse.filtered}
      <p>{parsedResponse.message}</p>
    {:else if parsedResponse.status}
      <div>
        <div><strong>Status:</strong> {parsedResponse.status}</div>
        <div><strong>Headers:</strong></div>
        <ul>
          {#each Object.entries(parsedResponse.headers) as [key, value]}
            <li>{key}: {value}</li>
          {/each}
        </ul>
        <div class="response-body">
          <strong>Body:</strong>
          {#if typeof parsedResponse.body === 'string' && isJson(parsedResponse.body)}
            {JSON.stringify(JSON.parse(parsedResponse.body), null, 2)}
          {:else}
            {parsedResponse.body}
          {/if}
        </div>
      </div>
    {:else}
      <p>No valid response to display.</p>
    {/if}
  {:else}
    <p>No valid response to display.</p>
  {/if}
</div>
