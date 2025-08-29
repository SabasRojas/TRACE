<script>
    import Tree from "$lib/components/Tree.svelte";
    import {onDestroy, onMount} from "svelte";
    import {goto} from "$app/navigation";
    import SiteMapList from "$lib/components/SiteMapList.svelte";
    import {fade} from 'svelte/transition';
    import {page} from "$app/state";
    import LoadingSpinner from "$lib/components/LoadingSpinner.svelte";
    import ToolButton from "$lib/components/ToolButton.svelte";

    // let networkMap = [
    //     {
    //         ip: "192.168.1.34:8080",
    //         path: "www.google.com",
    //         children: [
    //             {
    //                 ip: "192.168.1.34:8080",
    //                 path: "www.google.com/search",
    //                 children: [
    //                     {
    //                         ip: "192.168.1.34:8080",
    //                         path: "www.google.com/search/search",
    //                         children: [
    //                             {
    //                                 ip: "192.168.1.34:8080",
    //                                 path: "www.google.com/search/search/s",
    //                                 children:[]
    //                             },
    //                             {
    //                                 ip: "192.168.1.34:8080",
    //                                 path: "www.google.com/search/search/search/s",
    //                                 children: []
    //                             }
    //                         ]
    //                     }
    //                 ]
    //             },
    //             {
    //                 ip: "192.168.1.34:8080",
    //                 path: "www.google.com/gmail",
    //                 children: []
    //             }
    //         ]
    //     }
    // ];
    let projectID = page.params.id
    let networkMap = $state([]);
    let chosenTool = $state('crawler')
    let intervalId
    let progress = $state(0);
    let delay = 1000


    let displayZoneElement = $state(); // To bind the container element
    let isDragging = false;
    let startX, startY;
    let startScrollLeft, startScrollTop;
    let noContent = $state(false)
    function handleMouseDown(event) {
        // Only drag with primary mouse button (usually left)
        if (event.button !== 0) return;
        isDragging = true;
        // Get mouse position relative to viewport
        startX = event.clientX;
        startY = event.clientY;
        // Get current scroll position of the container
        startScrollLeft = displayZoneElement.scrollLeft;
        startScrollTop = displayZoneElement.scrollTop;
        // Change cursor and prevent text selection during drag
        displayZoneElement.style.cursor = 'grabbing';
        displayZoneElement.style.userSelect = 'none';
        // Prevent default image dragging behavior
        event.preventDefault();
    }

    function handleMouseMove(event) {
        if (!isDragging) return;
        // Calculate distance mouse has moved
        const dx = event.clientX - startX;
        const dy = event.clientY - startY;
        // Update scroll position based on starting scroll and mouse delta
        // Subtract delta because dragging mouse right should move scroll left
        displayZoneElement.scrollLeft = startScrollLeft - dx*1.3;
        displayZoneElement.scrollTop = startScrollTop - dy*1.3;
    }

    function stopDragging() {
        if (!isDragging) return;
        isDragging = false;
        // Restore cursor and text selection
        displayZoneElement.style.cursor = 'grab';
        displayZoneElement.style.userSelect = '';
    }

    function handleWheelZoom(event) {
        event.preventDefault();
        if (event.deltaY < 0) {
            zoomIn();
        } else if (event.deltaY > 0) {
            zoomOut();
        }
    }

    if (page.url.searchParams.get('delay')){
        delay = page.url.searchParams.get('delay')
    }
    onMount(async () => {
        let backendUrl = sessionStorage.getItem("backendUrl") || "http://localhost";
        if (displayZoneElement) {
            displayZoneElement.style.cursor = 'grab';
            displayZoneElement.addEventListener('mousedown', handleMouseDown);
            window.addEventListener('mousemove', handleMouseMove);
            window.addEventListener('mouseup', stopDragging);
            document.addEventListener('mouseleave', stopDragging);
            displayZoneElement.addEventListener('wheel', handleWheelZoom, { passive: false });
        }
        intervalId = setInterval(async () => {
            const response = await fetch(`${backendUrl}:8000/${projectID}/${chosenTool}/status`);
            if (response.status !== 200) {
                throw Error(response.statusText);
            }
            const status = await response.json();
            progress = status.progress;
            if(status.status === "No running"){
                clearInterval(intervalId);

                noContent = true
            }
            if (status.status === "Failed") {
                clearInterval(intervalId);
                await goto(`/project/${projectID}/tools/error?message=Internal+${chosenTool}+Failure`);
            } else {
                if(progress!==0) {
                    let data = await fetch(`${backendUrl}:8000/${projectID}/${chosenTool}/data`);
                    data = await data.json();
                    networkMap = data;
                    if (status.status === "Complete") {
                        clearInterval(intervalId);
                    }
                }
            }
        }, delay *1.5);
    });


    async function generateWordlist() {
        await goto(`/tools/webScraper`);
    }
    let treeMode = $state(true)


    let scale = $state(1);
    let isZoomedOut = $state(false);
    let isZoomedIn = $state(false);
    function zoomOut() {
        scale = Math.max(0.5, scale - 0.025);
        console.log("scale" + scale+ "isZoomedOut" + isZoomedOut)
        if(scale<=0.5) isZoomedOut = true;
    }

    function zoomIn(){
        scale = Math.min(scale + 0.025, 1.5);
        if(scale<=1.5)
        isZoomedIn = true;
    }
    function resetZoom() {
        scale = 1;
        isZoomedOut = false;
        console.log(scale);
    }

    function countNodes(networkMap) {
        let count = 0;

        function traverse(nodes) {
            for (const node of nodes) {
                count++;
                if (node.children && node.children.length > 0) {
                    traverse(node.children);
                }
            }
        }

        traverse(networkMap);
        return count;
    }


    onDestroy(() => {
        if (typeof window !== 'undefined' && typeof document !== 'undefined') {
            if (displayZoneElement) {
                displayZoneElement.removeEventListener('mousedown', handleMouseDown);
                displayZoneElement.removeEventListener('wheel', handleWheelZoom);
            }

            window.removeEventListener('mousemove', handleMouseMove);
            window.removeEventListener('mouseup', stopDragging);
            document.removeEventListener('mouseleave', stopDragging);
        }});
</script>

<div class="tree-graph">
    {#if treeMode}

        <h1 class="page-header">Tree graph</h1>
        {#if !noContent}
        <div class="display-zone" bind:this={displayZoneElement}>
            {#if !networkMap || networkMap.length === 0}
                <LoadingSpinner></LoadingSpinner>
                {:else}
                {#key progress}
        <Tree networkMap={networkMap} scale={scale}></Tree>
                    {/key}
                {/if}
        </div>
            {:else}
            <h1>No Content To Display</h1>
            {/if}
        <div>progress {progress}%</div>
    {/if}
    {#if treeMode}
    <ToolButton callback={()=>{zoomOut()}}
                content={"Zoom Out"}>
    </ToolButton>
    <ToolButton callback={()=>{zoomIn()}}
                content={"Zoom In"}>
    </ToolButton>
    <ToolButton callback={()=>{resetZoom()}} content={"Reset Zoom"}></ToolButton>
        {/if}
</div>
<style>
    .page-header {
        margin-left: 2vw;
        margin-top: 0;
    }
    .display-zone{
        display: flex;
        justify-content: center;
        overflow: scroll;
        width: 100%;
        height: 80vh;
        scrollbar-width: none;  /* Firefox */
        -ms-overflow-style: none;
    }
    .display-zone::-webkit-scrollbar {
        display: none;  /* Chrome, Safari */
    }
    .display-zone.is-dragging {
        cursor: grabbing;
        user-select: none;
    }
</style>