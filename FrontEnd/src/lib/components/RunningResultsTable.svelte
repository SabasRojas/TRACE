<script>
    import SiteMapList from "$lib/components/SiteMapList.svelte";
    let props = $props()
    let networkMap = $state([])
    networkMap = props.networkMap
    let networkNodeList = $state([])
    function traverse(nodes) {
        for (const node of nodes) {
            networkNodeList.push(node)
            if (node.children && node.children.length > 0) {
                traverse(node.children);
            }
        }
    }
    $effect(()=>{
        networkNodeList.length = 0
        traverse(networkMap);})

</script>

<table class="running-results-table">
        <thead>
            <tr>
                <th class="running-results-table-header">ID</th>
                <th class="running-results-table-header">URL</th>
                <th class="running-results-table-header">Title</th>
                <th class="running-results-table-header">Word Count</th>
                <th class="running-results-table-header">Character Count</th>
                <th class="running-results-table-header">Links Found</th>
                <th class="running-results-table-header">Error</th>
            </tr>
        </thead>
        <tbody>
        {#each networkNodeList as node, i}
            <tr class="running-result">
                <td class="running-result-ID">{i}</td>
                <td class="running-result-URL">{node.ip}</td>
                <td class="running-result-title">{node.path}</td>
                <td class="running-result-word-count">120</td>
                <td class="running-result-character-count">120234</td>
                <td class="running-result-links-found">123</td>
                <td class="running-result-character-error">False</td>
            </tr>
            {/each}
        </tbody>
    </table>

<style>
    thead{
        background: rgba(74, 166, 176, 0.6);
    }
    table {
        margin-top: 1.5vh;
        border-collapse: collapse;
        font-size: 0.8rem;
        letter-spacing: 1px;
        width: 85%;
    }
    th:first-child, td:first-child {
        border-top-left-radius: 7px;
        border-bottom-left-radius: 7px;
    }

    th:last-child, td:last-child {
        border-top-right-radius: 7px;
        border-bottom-right-radius: 7px;
    }
    td{
        text-align: justify;
    }
    th{
        text-align: justify;
    }
    tbody tr:nth-child(even) {
        background-color: #f2f2f2;
    }

    tbody tr:nth-child(odd) {
        background-color: #ffffff;
    }
</style>