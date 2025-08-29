<script>
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import TreeGraph from '$lib/TreeGraph.svelte';

  let treeData = null;
  let loading = true;
  let error = null;

  $: projectId = $page.url.searchParams.get('projectId');

  onMount(async () => {
    let backendUrl = sessionStorage.getItem("backendUrl") || "http://localhost";
    try {
      const res = await fetch(`${backendUrl}:8000/webtree/?projectId=${projectId}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const result = await res.json();

      console.log("Crawler response:", result);

      if (Array.isArray(result)) {
        treeData = {
          name: 'ROOT',
          children: result
        };
      } else {
        treeData = null;
      }

      console.log("Final treeData:", treeData);
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  });
</script>

<style>
  .webtree-container {
    padding: 2rem;
    max-width: 100%;
    min-height: 100vh;
    background-color: #f9fafb;
    font-family: 'Segoe UI', sans-serif;
  }

  h1 {
    font-size: 2rem;
    margin-bottom: 1rem;
    color: #1f2937;
    text-align: center;
  }

  .status-message {
    text-align: center;
    color: #6b7280;
    font-size: 1.2rem;
  }

  .error {
    color: red;
  }
</style>

<div class="webtree-container">
  <h1>WebTree</h1>

  {#if loading}
    <p class="status-message">Loading tree data...</p>
  {:else if error}
    <p class="status-message error">Error: {error}</p>
  {:else if treeData && Array.isArray(treeData.children) && treeData.children.length > 0}
    <TreeGraph data={treeData} />
  {:else}
    <p class="status-message">No tree data to display.</p>
  {/if}
</div>
