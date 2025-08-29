<script lang="ts">
    import ToolStatusHeader from "$lib/components/ToolStatusHeader.svelte";
    import ResponseManager from "$lib/ResponseManager.svelte";
    import { goto } from "$app/navigation";
  
    // Define the steps to show in the ToolStatusHeader.
    let steps = ["Configuration", "Running", "Results"];
  
    // Modify button function navigates back to the configuration page.
    function modifyTool() {
      goto("/tools/HTTP-requests");
    }
  </script>
  
  <h1 class="page-title">HTTP Tester</h1>
  <div class="page-wrapper">
    <!-- Display the status header with your three steps -->
    <ToolStatusHeader active={steps} title="Running" />
    
    <!-- Main content area: ResponseManager displays the tool's output -->
    <div class="response-display">
      <ResponseManager />
    </div>
    
    <!-- Only the Modify button is included -->
    <div class="footer-buttons">
      <button on:click={modifyTool}>Modify</button>
    </div>
  </div>
  
  <style>
    :global(body) {
      margin: 0;
      padding: 0;
      font-family: sans-serif;
      background-color: #fff;
    }
    
    .page-title {
      margin-left: 2rem;
      margin-top: 1rem;
      font-size: 1.5rem;
    }
    
    .page-wrapper {
      width: 90%;
      max-width: 1200px;
      margin: 1rem auto 2rem auto;
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }
    
    .response-display {
      background: #fdfdfd;
      border-radius: 8px;
      padding: 1rem;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      flex: 1;
      max-height: 50vh;
      overflow: auto;
    }
    
    .footer-buttons {
      display: flex;
      gap: 1rem;
      justify-content: flex-start;
      margin-top: 1rem;
    }
    
    .footer-buttons button {
      background-color: rgba(74, 166, 176, 0.6);
      border: none;
      padding: 0.75rem 1rem;
      border-radius: 6px;
      font-weight: 600;
      cursor: pointer;
      transition: background-color 0.2s ease;
    }
    
    .footer-buttons button:hover {
      background-color: #4aa6;
    }
  </style>
  