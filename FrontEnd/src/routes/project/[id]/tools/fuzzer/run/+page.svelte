<script>
    import ToolStatusHeader from "$lib/components/ToolStatusHeader.svelte";
    import RunningResultsTable from "$lib/components/RunningResultsTableCrawler.svelte";
    import ToolButton from "$lib/components/ToolButton.svelte";
    import {page} from "$app/state";
    import {onDestroy, onMount} from "svelte";
    import {goto} from "$app/navigation";
    import ProgressBar from "$lib/components/ProgressBar.svelte";
    import RunningResultsTableFuzzer from "$lib/components/RunningResultsTableFuzzer.svelte";

    let networkLinks = $state([]);
    let { data } = $props();
    let projectID = $derived(data.projectId);
    let progress = $state(0)
    let intervalId
    let delay = 1000
    let currTime = $state(0)
    let requestCount = $state(0)
    let reqSec = $state(0)
    let nonFilteredCount = $state(0)
    let backendUrl
    let noContent = $state(false)
    if (page.url.searchParams.get('delay')){
        delay = page.url.searchParams.get('delay')
    }
    onMount(async () => {
        let startTime = performance.now();
        backendUrl = sessionStorage.getItem("backendUrl") || "http://localhost";
        intervalId = setInterval(async () => {
            const response = await fetch(`${backendUrl}:8000/${projectID}/fuzzer/status`);
            if (response.status !== 200) {
                clearInterval(intervalId)
                throw Error(response.statusText);
            }
            const status = await response.json();
            progress = status.progress;
            if (status.status === "Failed") {
                clearInterval(intervalId);
                await goto(`/project/${projectID}/tools/error?message=Internal+Fuzzer+Failure`);
            }else if(status.status === "No running"){
                clearInterval(intervalId)
                noContent = true
            }
            else {
                if(progress!==0) {
                    let data = await fetch(`${backendUrl}:8000/${projectID}/fuzzer/data`);
                    data = await data.json();
                    requestCount += 1
                    networkLinks = data.fuzzerResults;
                    let results = Object.values(networkLinks);
                    filteredCount = results.filter(r => r.filtered === "True").length;
                    nonFilteredCount = results.filter(r => r.filtered === "False").length;
                    if (status.status === "Complete") {
                        clearInterval(intervalId);
                        done = true
                    }
                }
            }
            if(status && status.status !== "Paused") {
                currTime = performance.now() - startTime;
                reqSec = currTime / requestCount / 1000;
            }
        }, delay *1.5);
    });

    onDestroy(() => {
        clearInterval(intervalId);
    });
    let done = $state(false);
    let filteredCount = $state(0)
</script>



<h1 class="page-header">Fuzzer</h1>
<div class="page-wrapper">
    {#key requestCount}
    <ToolStatusHeader active={["Configuration", "Running",...(done ? ["Results"] : [])]} title="Running"></ToolStatusHeader>
        {/key}
    <div class="metrics">
        <div class="metric">
            <div class="metric-title">Running Time</div>
            <div class="metric-value">{currTime.toFixed(2)} ms</div>
        </div>
        <div class="metric">
            <div class="metric-title">Processed Requests</div>
            <div class="metric-value">{nonFilteredCount}</div>
        </div>
        <div class="metric">
            <div class="metric-title">Filtered Requests</div>
            <div class="metric-value">{filteredCount}</div>
        </div>
        <div class="metric">
            <div class="metric-title">Requests/sec</div>
            <div class="metric-value">{reqSec.toFixed(2)}</div>
        </div>
    </div>
    {#key progress}
        <ProgressBar progress={progress}></ProgressBar>
    {/key}
    {#if noContent}
        <div>No Content, Try Running This Tool Again</div>
    {:else}
    <div class="table-display-area">
    <RunningResultsTableFuzzer networkLinks={networkLinks}></RunningResultsTableFuzzer>

    </div>
        {/if}
</div>
<div class="footer-buttons">
    <div class="left-buttons">
        <ToolButton callback={async ()=>{const response = await fetch(`${backendUrl}:8000/${projectID}/fuzzer/pause`, {method: 'POST'}); const result = await response.json(); console.log(result)}} content="<b>Pause</b>"></ToolButton>
        <ToolButton callback={async ()=>{const response = await fetch(`${backendUrl}:8000/${projectID}/fuzzer/stop`, {method: 'POST'}); const result = await response.json(); console.log(result)}} content="<b>Stop</b>"></ToolButton>
        <ToolButton callback={async ()=>{const response = await fetch(`${backendUrl}:8000/${projectID}/fuzzer/resume`, {method: 'POST'}); const result = await response.json(); console.log(result)}} content="<b>Resume</b>"></ToolButton>
        <ToolButton callback={()=>{goto(`/project/${projectID}/tools/fuzzer`)}} content="<b>Start New Fuzzer</b>"></ToolButton>
    </div>
    <div class="right-button">
        <ToolButton callback={()=>{}} content="<b>Show Terminal</b>"></ToolButton>
    </div>
</div>


<style>
    .page-header {
        margin-left: 2.5vw;
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
    .page-wrapper {
        width: 90%;
        max-height: 100vh;
        margin-left: 2rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        background: transparent;
    }
    .metrics{
        display: flex;
        width: 90%;
        justify-content: space-evenly;
        align-items: center;
        margin-bottom: 10px;
    }
    .metric{
        display: flex;
        flex-direction: column;
        justify-content: space-evenly;
    }
    .metric-value{
        font-weight: bold;
    }
    .footer-buttons{
        position: absolute;
        display: flex;
        margin-bottom: 1vh;
        bottom: 1vh;
        width: 90%;
        justify-content: space-between;
    }


</style>