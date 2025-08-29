<script>
    let { ip, scale = 1, path, root } = $props();
    const baseFontSizePx = 14;
    let adjustedFontSize = $derived(baseFontSizePx / Math.max(0.1, scale));
</script>

<div class="tree-node {root ? 'root' : ''}" style="font-size: {adjustedFontSize}px;">
    {#if scale > 0.95}
    <div class="tree-node-title">
        {ip}
    </div>
    <div class="dividing-line">
    </div>
        {/if}
    <div class="tree-node-content">
        {path}
    </div>
</div>

<style>
    .tree-node {
        display: flex;
        flex-direction: column;
        background: white;
        border: 2px solid #006699;
        border-radius: 10px;
        padding: 5px;
        margin: 10px auto;
        text-align: center;
        min-height: 70px;
        width: fit-content;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
        position: relative;
        justify-content: space-around;
    }
    .dividing-line{
        width: 100%;
        height: 1px;
        background: darkgrey;
    }
    @media (prefers-color-scheme: dark) {
        .dividing-line{
            background: #006699;
        }
        .tree-node{
            background: #1f2937;
        }
    }


</style>
