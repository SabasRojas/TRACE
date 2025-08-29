<script>
    import { onMount } from "svelte";
    import TreeNode from './TreeNode.svelte';
    import Tree from './Tree.svelte';

    let { networkMap = [], scale = 1 } = $props();
</script>

<div class="network-tree" style:transform="scale({scale})" style:transform-origin="center">
        {#each networkMap as node}
            <div class="tree-branch">
                <TreeNode ip={node.ip} path={node.path} scale={scale}/>
                {#if node.children && node.children.length > 0}
                    <div class="children">
                        <Tree networkMap={node.children} scale={scale}/>
                    </div>
                {/if}
            </div>
        {/each}
</div>

<style>
    .network-tree {
        display: flex;
        position: relative;
        min-width: 25%;
        min-height: 100%;
        transition: transform 0.2s ease-out;
    }

    .children {
        display: flex;
        justify-content: center;
        align-items: center;
        position: relative;
        margin-top: 2px;
    }
    .tree-branch{
        margin-top: 2px;
        margin-left: 2px;
        margin-right: 2px;
    }


</style>
