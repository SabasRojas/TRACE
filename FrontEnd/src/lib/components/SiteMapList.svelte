<script>
    import SiteMapList from './SiteMapList.svelte';
    let props = $props()
    let networkMap = props.networkMap
</script>

<div class="SiteMapList">
    <ul class="site-map-list">
    {#each networkMap as site}
        <li class="site-map-list-item">{site.path}</li>
        {#if site.children && site.children.length > 0}
            <ul>
                <SiteMapList networkMap ={site.children}></SiteMapList>
            </ul>
            {/if}
    {/each}
        </ul>
</div>