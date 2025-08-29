<script>
    import { onMount } from 'svelte';
    import {draw} from 'svelte/transition'

</script>

<div
        class="background-svg-container"
>
    <svg
            viewBox="0 0 1920 1080"
            version="1.1"
            id="svg1"
            xmlns="http://www.w3.org/2000/svg"
            xmlns:svg="http://www.w3.org/2000/svg"
            preserveAspectRatio="xMidYMid slice"

    >
        <defs id="defs1" />
        <g id="layer1" >
            <g id="right-lines" >
                <path d="M 1918.7041,695.27857 H 1312.3418 L 1126.5212,862.56549 824.73712,866.9295" id="path2-2" transition:draw={{ duration: 1000 }}/>
                <path d="m 1921.1402,643.58225 -600.0614,2.90209 -199.5205,174.12514 -294.02995,5.80418" id="path3-3" transition:draw={{ duration: 1000 }}/>
                <path d="m 1921.1417,601.95638 -630.1263,2.80924 -192.0384,175.57729 -270.05412,2.80924" id="path4-2" transition:draw={{ duration: 1000 }}/>
                <path d="m 1922.0335,461.68013 -634.2556,3.95175 -94.842,-114.6007" id="path4-9" transition:draw={{ duration: 1000 }}/>
                <path d="m 1914.622,416.90943 h -594.7381 l -73.1074,-88.91434" id="path5" transition:draw={{ duration: 1000 }}/>
            </g>
            <g id="left-lines" >
                <path d="M 3.8172735,424.89182 H 610.17957 l 185.8206,-167.28692 301.78403,-4.36401" id="path2-2-8" transition:draw={{ duration: 1000 }}/>
                <path d="M 1.3811735,476.58814 601.44257,473.68605 800.96307,299.56091 1094.993,293.75673" id="path3-3-5" transition:draw={{ duration: 1000 }}/>
                <path d="M 1.3796735,518.21401 631.50597,515.40477 823.54437,339.82748 1093.5985,337.01824" id="path4-2-7" transition:draw={{ duration: 1000 }}/>
                <path d="M -1.9758741,624.3762 632.2797,620.42445 727.12165,735.02515" id="path4" transition:draw={{ duration: 1000 }}/>
                <path d="M 0.94823284,668.90769 H 595.68633 l 73.1074,88.91434" id="path5-5" transition:draw={{ duration: 1000 }}/>
            </g>
        </g>
    </svg>
</div>

<style>
    .background-svg-container {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        overflow: hidden;
        pointer-events: none;
    }

    .background-svg-container svg {
        display: block;
        width: 100%;
        height: 100%;
        opacity: 0.5;
    }

    /* Combined styling and transition setup only for path */
    .background-svg-container svg path {
        stroke: #949393; /* Use your desired color */
        stroke-width: 1.5px;
        fill: none;
        transition: stroke-dashoffset 0.8s cubic-bezier(0.6, 0, 0.4, 1);
        /* stroke-dasharray and initial stroke-dashoffset are set by JS */
    }
    @media (prefers-color-scheme: dark){
        .background-svg-container svg path{
            stroke: #7bdcdc;
        }
    }
</style>