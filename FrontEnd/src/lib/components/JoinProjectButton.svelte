<script lang="ts">
  // @ts-nocheck
  import { createEventDispatcher, onMount } from 'svelte';
  export let projectId: string;
  export let userInitials: string;
  const dispatch = createEventDispatcher();

  // Define a Status type for response feedback
  type Status = {
    success: boolean;
    message: string;
  };

  let status: Status | null = null;
  let backendUrl: string;

  onMount(() => {
    backendUrl = sessionStorage.getItem("backendUrl") || "http://localhost";
  });

  /**
   * Sends a join request to the backend and updates status.
   */
  async function handleJoin(): Promise<void> {
    status = null;
    try {
      const url = `${backendUrl}:8000/project/${projectId}/join?user_initials=${encodeURIComponent(
        userInitials
      )}`;
      const res = await fetch(url, { method: 'POST' });
      if (!res.ok) {
        const err = await res.json().catch(() => null);
        throw new Error(err?.detail || res.statusText);
      }
      const body = (await res.json()) as { message: string };
      status = { success: true, message: body.message };
      dispatch('joined');
    } catch (e) {
      status = { success: false, message: e instanceof Error ? e.message : String(e) };
    }
  }
</script>

<style>
  .join-button {
    background-color: #4ea8b2;
    color: #fff;
    padding: 0.4rem 0.8rem;
    border: none;
    border-radius: 0.5rem;
    font-size: 0.95rem;
    cursor: pointer;
  }
  .join-button:hover {
    background-color: #407d99;
  }

  .status {
    margin-top: 0.5em;
  }
  .success {
    color: green;
  }
  .error {
    color: red;
  }
</style>

<div>
  <button class="join-button" on:click={handleJoin}>
    Join Project
  </button>

  {#if status}
    <div class="status {status.success ? 'success' : 'error'}">
      {status.message}
    </div>
  {/if}
</div>
