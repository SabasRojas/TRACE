<script>
    import {page} from '$app/state'
    let { children } = $props();
    let projectID = page.params.id;
</script>

<nav class="side-bar">
    <div class="side-bar-section top">
        <a class="side-bar-logo-link" href="/" aria-label="Home link">
            <img class="side-bar-logo" src="/fontawesome-free-6.7.2-desktop/svgs/solid/microchip.svg" alt="TRACE logo">
        </a>
    </div>
    <div class="side-bar-section mid">
        <button class="side-bar-button" aria-label="Project selection button" type="button">
            <a class="side-bar-logo-link" href="/project" aria-label="Project selection button">
                <img class="side-bar-button-logo" src="/fontawesome-free-6.7.2-desktop/svgs/solid/folder-open.svg" alt="Project selection logo">
            </a>
        </button>
        <button class="side-bar-button" aria-label="Project folders button">
            <a class="side-bar-logo-link" href="/project">
                <img class="side-bar-button-logo" src="/fontawesome-free-6.7.2-desktop/svgs/solid/folder.svg" alt="Project folders logo">
            </a>
        </button>
        <button class="side-bar-button" aria-label="Deleted projects button">
            <a class="side-bar-logo-link" href="/project-delete">
                <img class="side-bar-button-logo" src="/fontawesome-free-6.7.2-desktop/svgs/solid/trash-can.svg" alt="Deleted projects logo">
            </a>
        </button>
    </div>
    <div class="side-bar-section bottom">
        <button class="side-bar-button" aria-label="config-button">
            <a class="side-bar-logo-link" href="/config">
                <img class="side-bar-button-logo" src="/fontawesome-free-6.7.2-desktop/svgs/solid/gear.svg" alt="Config logo">
            </a>
        </button>
    </div>
</nav>
<div class="container">
    {@render children?.()}
</div>

<style>

    .side-bar {
        position: fixed;
        top: 0;
        left: 0;
        height: 100%;
        width: 4%;
        background: #e1e1e1;
        display: flex;
        flex-direction: column;
        border-radius: 3%;
    }
    .side-bar-button{
        border-radius: 50%;
        width: 6vh;
        height: 6vh;
        background: #cfcfcf;
        border: none;
        padding: 0;
    }
    .side-bar-button-logo{
        width: 60%;
    }
    .side-bar-button:hover{
        border: #7e7d7d;
        background: #4aa6b0;
        transform: scale(1.2);
    }
    .side-bar-section{
        display: flex;
        flex-direction: column;
        width: 100%;
        height: 100%;
        align-items: center;
    }
    .side-bar-section.mid{
        justify-content: center;
    }
    .side-bar-section.mid button{
        margin: 1vh
    }
    .side-bar-section.bottom{
        justify-content: flex-end;
    }
    .side-bar-section.bottom button{
        margin: 3vh;
    }
    .side-bar-logo-link{
        border-radius: 50%;
        width: 8vh;
        height: 8vh;
    }
    .side-bar-logo{
        height: 6vh;
        width: auto;
    }
    .container{
        width: 96%;
        margin-left: 4%;
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    @media (prefers-color-scheme: dark){
        .side-bar{
            background: #12181b;
        }
        .side-bar-button:hover{
            border: #7e7d7d;
            background: white;
            transform: scale(1.2);
        }
        .side-bar-button{
            background: #4aa6b0;
        }
    }
</style>