<script lang="ts">
  import { page } from '$app/state'; 
  import { responseStore } from '$lib/stores/responseStore';
  import ToolStatusHeader from '$lib/components/ToolStatusHeader.svelte';
  import ResponseManager from "$lib/ResponseManager.svelte";
  import { getApiBase } from '../../../../../config';
  import { onMount } from 'svelte';

  // Local state for the request inputs
  let url: string = "";
  const steps = ["Configuration", "Running", "Results"];
  let activeSteps: string[] = [steps[0]];

  // Use a config object for the radio group HTTP method selection.
  let HTTPMethod = "GET";
  let headers: string = '{"Content-Type": "application/json"}';
  let payload: string = "";
  let projectID = page.params.id;

  // Additional input fields
  let cookies: string = "{}";
  let proxy: string = "";
  let hideStatusCodes: string = "";      // Comma-separated list (e.g., "404,500")
  let showOnlyStatusCodes: string = "";    // Comma-separated list (e.g., "200")
  let backendUrl: string;

  onMount(() => {
    backendUrl = sessionStorage.getItem("backendUrl") || "http://localhost";

    const saved = sessionStorage.getItem(`httpResponse-${projectID}`);
   if (saved) {
     responseStore.set(JSON.parse(saved));
     activeSteps = [...steps];
   }
  });

  async function sendRequest() {
    activeSteps = [steps[0], steps[1]];

    console.log("=== Sending HTTP Request ===");
    console.log("URL:", url);
    console.log("HTTP Method:", HTTPMethod);
    console.log("Raw Headers:", headers);
    console.log("Raw Payload:", payload);
    console.log("Raw Cookies:", cookies);
    console.log("Proxy:", proxy);
    console.log("Hide Status Codes:", hideStatusCodes);
    console.log("Show Only Status Codes:", showOnlyStatusCodes);

    // Parse headers from JSON string
    let headersObj = {};
    try {
      headersObj = JSON.parse(headers);
      console.log("Parsed Headers:", headersObj);
    } catch (error) {
      console.error("Invalid JSON for headers", error);
      alert("Invalid JSON for headers");
      return;
    }

    // Parse payload from JSON string if provided
    let payloadObj = null;
    if (payload) {
      try {
        payloadObj = JSON.parse(payload);
        console.log("Parsed Payload:", payloadObj);
      } catch (error) {
        console.error("Invalid JSON for payload", error);
        alert("Invalid JSON for payload");
        return;
      }
    }

    // Parse cookies from JSON string
    let cookiesObj = {};
    try {
      cookiesObj = JSON.parse(cookies);
      console.log("Parsed Cookies:", cookiesObj);
    } catch (error) {
      console.error("Invalid JSON for cookies", error);
      alert("Invalid JSON for cookies");
      return;
    }

    // Convert comma-separated status codes into arrays of numbers
    const hideCodesArray: number[] = hideStatusCodes
      ? hideStatusCodes.split(",")
          .map(code => parseInt(code.trim()))
          .filter(code => !isNaN(code))
      : [];

    const showOnlyCodesArray: number[] = showOnlyStatusCodes
      ? showOnlyStatusCodes.split(",")
          .map(code => parseInt(code.trim()))
          .filter(code => !isNaN(code))
      : [];

    const requestData = {
      url,
      method: HTTPMethod,
      headers: headersObj,
      payload: payloadObj,
      cookies: cookiesObj,
      proxy: proxy || null,
      hide_status_codes: hideCodesArray,
      show_only_status_codes: showOnlyCodesArray
    };
    console.log("Final requestData to send:", requestData);

    try {
      console.log("Sending HTTP request to", `${backendUrl}:8000/tools/send`);
      const res = await fetch(`${backendUrl}:8000/tools/send?project_id=${projectID}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestData)
      });

      console.log("HTTP response status:", res.status);

      if (!res.ok) {
        const errorData = await res.json();
        console.error("Error response from backend:", errorData);
        alert("Error: " + errorData.detail);
        return;
      }

      const data = await res.json();
      console.log("Received data from backend:", data);
      // Update the response store so that the Response Manager displays it.
      responseStore.set(data);

      sessionStorage.setItem(
       `httpResponse-${projectID}`,
       JSON.stringify(data)
     );

      activeSteps = [...steps];

    } catch (error) {
      console.error("Request failed", error);
      alert("Request failed: " + error);
    }
  }
</script>

<!-- Main page container (centered) -->
<div class="page-container">
  {#key JSON.stringify(activeSteps)}
    <ToolStatusHeader active={activeSteps} />
  {/key}

  <!-- HTTP form container -->
  <div class="httprequest-container">
    <div class="config-panel">
      <h2>HTTP Tester</h2>
      <form class="httprequest-form">
        <div class="form-group">
          <label for="url">URL</label>
          <input
            id="url"
            type="text"
            bind:value={url}
            placeholder="https://example.com/api"
          />
        </div>
        
        <div class="form-group">
          <label>Method</label>
          <!-- Radio group configured for GET, PUT, and POST -->
          <div class="radio-group">
            <label>
              <input type="radio" bind:group={HTTPMethod} value="GET" /> GET
            </label>
            <label>
              <input type="radio" bind:group={HTTPMethod} value="PUT" /> PUT
            </label>
            <label>
              <input type="radio" bind:group={HTTPMethod} value="POST" /> POST
            </label>
          </div>
        </div>
        
        <div class="form-group">
          <label for="headers">Headers (JSON)</label>
          <textarea
            id="headers"
            rows="4"
            bind:value={headers}
            placeholder={'{"Content-Type": "application/json"}'}
          ></textarea>
        </div>
        
        <div class="form-group">
          <label for="payload">Payload (JSON)</label>
          <textarea
            id="payload"
            rows="4"
            bind:value={payload}
            placeholder={'{"key": "value"}'}
          ></textarea>
        </div>
        
        <div class="form-group">
          <label for="cookies">Cookies (JSON)</label>
          <textarea
            id="cookies"
            rows="2"
            bind:value={cookies}
            placeholder={'{"session_id": "ABC123"}'}
          ></textarea>
        </div>
        
        <div class="form-group">
          <label for="proxy">Proxy URL</label>
          <input
            id="proxy"
            type="text"
            bind:value={proxy}
            placeholder="http://proxy.example.com:3128"
          />
        </div>
        
        <div class="form-group">
          <label for="hideStatusCodes">Hide Status Codes (comma separated)</label>
          <input
            id="hideStatusCodes"
            type="text"
            bind:value={hideStatusCodes}
            placeholder="e.g., 404,500"
          />
        </div>
        
        <div class="form-group">
          <label for="showOnlyStatusCodes">Show Only Status Codes (comma separated)</label>
          <input
            id="showOnlyStatusCodes"
            type="text"
            bind:value={showOnlyStatusCodes}
            placeholder="e.g., 200"
          />
        </div>
        
        <!-- Only the Start button is included -->
        <button type="button" class="action-btn" on:click={sendRequest}>Start</button>
      </form>
    </div>

    <div class="panel">
      <h2>Results</h2>

      <ResponseManager />
    </div>
  </div>
</div>

<style>
  /* Centered page container */
  .page-container {
    width: 90%;
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2rem;
  }
  
  /* Container for the HTTP request form and results, side-by-side */
  .httprequest-container {
    display: flex;
    flex-direction: row;
    gap: 2rem;
    width: 150%;
    padding: 2rem;
    border-radius: 12px;
    background: #fdfdfd;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }

  /* Ensure both panels share available space */
  .config-panel,
  .panel {
    flex: 1;
  }

  .httprequest-form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  .form-group {
    display: flex;
    flex-direction: column;
  }
  
  label {
    font-size: 0.9rem;
    margin-bottom: 0.25rem;
    color: #333;
  }
  
  input,
  textarea {
    padding: 0.6rem;
    font-size: 1rem;
    border: 1px solid #ccc;
    border-radius: 6px;
    background-color: #1f2937;
    color: #fff;
  }
  
  .radio-group {
    display: flex;
    gap: 1rem;
  }
  
  .action-btn {
    background-color: rgba(74, 166, 176, 0.6);
    color: #000;
    border: none;
    padding: 0.75rem;
    border-radius: 6px;
    font-size: 1rem;
    cursor: pointer;
    width: 100%;
    transition: ease-in-out 0.25s;
  }
  
  .action-btn:hover {
    background: #4aa6b0;
    transform: scale(1.05);
  }
  @media (prefers-color-scheme: dark) {
    .httprequest-container{
      background: #1f2937;
      color: #e5e7eb;
    }
    label{
      color: #e5e7eb;
    }
  }
</style>
