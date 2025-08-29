<script>
    import {onMount} from "svelte";
    import {goto} from "$app/navigation";
    import {getApiBase} from "../../config.js";

    let props = $props()
    let toolName = props.toolName;
    let projectID = props.projectID
    let color =  $state("#4aa6b0");
    let results = props.results;
    let callback = props.callback;
    let tooltip = props.tooltip;
    let progress = $state(0);
    let toolStatus = $state("Loading");
    let intervalId;
    onMount(async () => {
        let backendUrl = sessionStorage.getItem("backendUrl") || "http://localhost";
        intervalId = setInterval(async () => {
            const response = await fetch(`${backendUrl}:8000/${projectID}/${toolName}/status`);
            if (response.status !== 200) {
                clearInterval(intervalId)
                throw Error(response.statusText);
            }
            const status = await response.json();
            progress = status.progress;
            toolStatus = status.status;
            if (status.status === "Failed") {
                color = "#fa2424"
                clearInterval(intervalId);
            }else if( status.status === "No running"){
                const response = await fetch(`${backendUrl}:8000/${projectID}/${toolName}/exists`);
                if(response.status !== 200){
                    color = "#fa2424"
                    clearInterval(intervalId)
                }
                const exists = await response.json()
                if(exists.status === "No Content") {
                    color = "#52cecc"
                    toolStatus = "Ready To Run";
                    clearInterval(intervalId);
                }
                else if(exists.status === "Complete"){
                    toolStatus = "Complete"
                    color = "#6fc287"
                }
            }
            else {
                if(progress!==0) {
                    if (status.status === "Complete") {
                        color = "#6fc287"
                        clearInterval(intervalId);
                    }
                }
            }
        }, 1000);
    });

</script>
<div class="tool-progress">
    <div class="progress-bar-wrapper">
        <div class="progress-container">
            <div class="progress-bar" style="width: {progress}%; background: {color};"></div>
        </div>
    </div>
    <div class="progress-label">
        {progress}% <span style="color: {color}">{toolStatus}</span>
    </div>
</div>
<div class="tool-actions">
    <div class="tooltip-wrapper">
        <button class="info-btn" data-tooltip= {tooltip}>
            <img class="info-logo" src="/fontawesome-free-6.7.2-desktop/svgs/regular/circle-question.svg" alt="Info">
        </button>
    </div>
    <button class="action-btn" onclick={progress === 0 ? callback : results}>{progress === 0 ? "Set Up" : "View"}</button>
</div>

<style>
    .progress-container {
        width: 20vw;
        height: 10px;
        background: #ddd;
        border-radius: 5px;
        overflow: hidden;
        margin-top: 10px;
        margin-bottom: 10px;
    }

    .tooltip-wrapper {
        position: relative; /* Needed for absolute positioning of the tooltip */
        display: inline-block; /* Or block, depending on layout */
    }
    .progress-bar {
        height: 100%;
        width: 0;
        transition: width 0.7s ease-in-out;
    }
    .progress-bar-wrapper{
        display: flex;
        flex-direction: column;
        width: 100%;
        align-items: center;
    }

    .tool-actions {
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    .info-btn {
        border: none;
        border-radius: 10%;
        cursor: pointer;
        font-weight: bold;
        height: 6vh;
        background: transparent;
    }

    .info-logo{
        height: 4vh
    }

    .action-btn {
        background: #4aa5af;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        cursor: pointer;
        font-weight: bold;
    }

    .action-btn:disabled {
        background: #ccc;
        cursor: not-allowed;
    }
    .info-btn::after {
        content: attr(data-tooltip); /* Get text from data-tooltip */
        position: absolute;
        background: rgba(51, 51, 51, 0.9); /* Dark background */
        color: white;
        padding: 6px 10px; /* Padding */
        border-radius: 4px;
        font-size: 0.8rem; /* Adjust font size */
        white-space: nowrap; /* Prevent line breaks */
        z-index: 10; /* Ensure it's above other elements */

        /* Positioning (example: above the button) */
        bottom: 110%; /* Position above */
        left: 50%;
        transform: translateX(-50%); /* Center horizontally */

        /* Initially hidden */
        opacity: 0;
        visibility: hidden;
        pointer-events: none; /* Don't interfere with mouse */
        transition: opacity 0.2s ease-in-out, visibility 0.2s ease-in-out; /* Smooth fade */
    }

    /* Optional: Add a small triangle/arrow */
    .info-btn::before {
        content: '';
        position: absolute;
        border-width: 5px;
        border-style: solid;
        border-color: rgba(51, 51, 51, 0.9) transparent transparent transparent; /* Arrow pointing up */
        bottom: 110%; /* Position above */
        margin-bottom: -10px; /* Overlap slightly with ::after */
        left: 50%;
        transform: translateX(-50%);
        z-index: 11;
        opacity: 0;
        visibility: hidden;
        pointer-events: none;
        transition: opacity 0.2s ease-in-out, visibility 0.2s ease-in-out;
    }


    /* Show tooltip on button hover or focus */
    .info-btn:hover::after,
    .info-btn:focus::after,
    .info-btn:hover::before,
    .info-btn:focus::before {
        opacity: 1;
        visibility: visible;
    }
</style>