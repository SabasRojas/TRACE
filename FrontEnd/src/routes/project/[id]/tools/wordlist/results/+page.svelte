<script>
    import ToolStatusHeader from "$lib/components/ToolStatusHeader.svelte";
    import ToolButton from "$lib/components/ToolButton.svelte";
    import ResultsTableAIGenerator from "$lib/components/ResultsTableAIGenerator.svelte";
    import { onMount, onDestroy } from "svelte";
import {goto} from "$app/navigation";
import {page} from "$app/state";
import ProgressBar from "$lib/components/ProgressBar.svelte";
  
    let credentials = $state([]);
    let startTime;
    let runningTime = $state(0);
    let usernamesCount = $state(0);
    let passwordsCount = $state(0);
    let projectId = page.params.id
    let intervalId;
    let backendUrl
    let progress = $state(0)
    let noContent = $state(false)

onMount(async () => {
  startTime = performance.now();
  backendUrl = sessionStorage.getItem("backendUrl") || "http://localhost";
  intervalId = setInterval(async () => {
    const response = await fetch(`${backendUrl}:8000/${projectId}/aiGenerator/status`);
    if (response.status !== 200) {
      clearInterval(intervalId)
      await goto(`/project/${projectID}/tools/error?message=Internal+ai_Generator+Failure`);
      throw Error(response.statusText);
    }
    runningTime = (performance.now() - startTime) / 1000;
    const status = await response.json();
    progress = status.progress;
    if (status.status === "Failed") {
      clearInterval(intervalId);
      await goto(`/project/${projectID}/tools/error?message=Internal+ai+Generator+Failure`);
    }
    else if(status.status === "No running"){
      progress = status.progress;
      let data = await fetch(`${backendUrl}:8000/${projectId}/aiGenerator/data`);
      data = await data.json();
      if(!data){
        noContent = true
      }
      clearInterval(intervalId)
    }
    else {
      if (status.status === "Complete" ) {
        let data = await fetch(`${backendUrl}:8000/${projectId}/aiGenerator/data`);
        data = await data.json();
        progress = status.progress;
        console.log(progress)
        credentials = data;
        usernamesCount = credentials.length;
        passwordsCount = credentials.length;
        clearInterval(intervalId);
      }
    }
  },1000)})

  
    onDestroy(() => {
      clearInterval(intervalId);
    });
  
    function regenerate() {
      location.reload();
    }
  
    function saveWordlist() {
      alert("Word list saved successfully!");
    }
  </script>
  
  <h1 class="page-header">AI Generator</h1>
<div class="page-wrapper">
  <ToolStatusHeader active={["Configuration", "Running", "Results"]} title="Results" />
  
  <div class="metrics">
    <div class="metric">
      <div class="metric-title">Running Time</div>
      <div class="metric-value">{runningTime.toFixed(2)}</div>
    </div>
    <div class="metric">
      <div class="metric-title">Generated Usernames</div>
      <div class="metric-value">{usernamesCount}</div>
    </div>
    <div class="metric">
      <div class="metric-title">Generated Passwords</div>
      <div class="metric-value">{passwordsCount}</div>
    </div>
  </div>
  {#key progress}
    <ProgressBar progress={progress}></ProgressBar>
  {/key}
  {#if noContent}
    <div>No Content, Try Running This Tool Again</div>
    {:else}
  <div class="table-display-area">
  <ResultsTableAIGenerator credentials={credentials} />
  </div>
    {/if}
  <div class="footer-buttons">
    <div class="left">
      <ToolButton callback={regenerate} content="<b>Re-Generate</b>" />
    </div>
    <div class="right">
      <ToolButton callback={saveWordlist} content="<b>Save Word List</b>" />
    </div>
  </div>
</div>
  <style>
    .page-wrapper {
      width: 90%;
      max-height: 100vh;
      margin-left: 2rem;
      display: flex;
      flex-direction: column;
      align-items: center;
      background: transparent;
    }
    .table-display-area{
      width: 100%;
      display: flex;
      justify-content: center;
      overflow: scroll;
      scrollbar-width: none;  /* Firefox */
      -ms-overflow-style: none;
      max-height: 50vh;
    }
    .table-display-area::-webkit-scrollbar {
      display: none;  /* Chrome, Safari */
    }
    .page-header {
      margin-left: 2.5vw;
    }
    .metrics{
      display: flex;
      width: 90%;
      justify-content: space-evenly;
      align-items: center;
      margin-bottom: 10px;
    }
    .metric {
      text-align: center;
    }
    .metric-title {
      font-size: 0.9rem;
      color: #666;
    }
    .metric-value {
      font-weight: bold;
      font-size: 1.1rem;
    }
    .footer-buttons {
      margin: 2rem;
      display: flex;
      justify-content: space-between;
    }
  </style>
  