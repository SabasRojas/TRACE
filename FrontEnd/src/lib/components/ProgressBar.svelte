<script>
    import {onMount} from "svelte";

    let props = $props()
    let currentCount = props.currentCount
    let total = props.total
    let progress = $state()
    progress = props.progress

</script>
<div class="progress-bar-wrapper">
<div class="progress-bar-header">
    {progress}% {progress === 100? 'Complete': 'running'}
</div>
<div class="progress-container">
    <div class="progress-bar" style="width: {progress}%;"></div>
</div>
</div>
<style>
    .progress-container {
        width: 80%;
        height: 10px;
        background: #ddd;
        border-radius: 5px;
        overflow: hidden;
        margin-top: 10px;
        margin-bottom: 10px;
    }

    .progress-bar {
        height: 100%;
        background: #4aa6b0;
        width: 0;
        transition: width 0.7s ease-in-out;
    }
    .progress-bar-header{
        display: flex;
        width: 80%;
    }
    .progress-bar-wrapper{
        display: flex;
        flex-direction: column;
        width: 100%;
        align-items: center;
    }
</style>