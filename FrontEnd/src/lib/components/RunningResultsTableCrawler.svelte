<script>
    let {networkNodeList = []} = $props();



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
    {#each networkNodeList as node, i (node.id || i)}
        <tr class="running-result">
            <td class="running-result-ID">{i}</td>
            <td class="running-result-URL">{node.ip}</td>
            <td class="running-result-title">{node.path}</td>
            <td class="running-result-word-count">{node.word_count ?? 'N/A'}</td>
            <td class="running-result-character-count">{node.char_count ?? 'N/A'}</td>
            <td class="running-result-links-found">{node.links_found ?? 0}</td>
            <td class="running-result-character-error">{node.status_code === 200 ? "False" : "True"}</td>
        </tr>
    {/each}
    </tbody>
</table>

<style>
    thead {
        background: rgba(74, 166, 176, 0.6);
    }

    table {
        margin-top: 1.5vh;
        border-collapse: collapse;
        font-size: 0.8rem;
        letter-spacing: 1px;
        width: 85%;
    }

    th:first-child {
        border-top-left-radius: 7px;
    }

    th:last-child{
        border-top-right-radius: 7px;
    }

    td, th {
        max-width: 30vw;
        text-align: justify;
        padding: 8px 4px;
        overflow: scroll;
        scrollbar-width: none;  /* Firefox */
        -ms-overflow-style: none;
    }

    tbody tr:nth-child(even) {
        background-color: #f0f0f1;
    }

    tbody tr:nth-child(odd) {
        background-color: #e0dfe0;
    }
    table::-webkit-scrollbar {
        display: none;  /* Chrome, Safari */
    }
    @media (prefers-color-scheme: dark) {
        tbody tr:nth-child(even) {
            background-color: #1a2024;
        }
        tbody tr:nth-child(odd) {
            background-color:#171d21;
        }
        thead{
            color: #e5e7eb;
        }
    }
</style>