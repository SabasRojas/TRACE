<script>
    let {networkLinks = []} = $props();

    import { slide } from "svelte/transition";
</script>

<table class="running-results-table">
    <thead>
        <tr>
            <th class="running-results-table-header">ID</th>
            <th class="running-results-table-header">Response</th>
            <th class="running-results-table-header">Lines</th>
            <th class="running-results-table-header">Word</th>
            <th class="running-results-table-header">Chars</th>
            <th class="running-results-table-header">Payload</th>
            <th class="running-results-table-header">Error</th>
        </tr>
    </thead>
    <tbody>
    {#each Object.entries(networkLinks) as [link, values], i}
        {#if values.filtered !== "True"}
        <tr class="running-result">
            <td class="running-result-ID">{i}</td>
            <td class="running-result-response">{values.status}</td>
            <td class="running-result-lines"></td>
            <td class="running-result-word-count">{values.word_count}</td>
            <td class="running-result-character-count">{values.char}</td>
            <td class="running-result-payload">{values.payload}</td>
            <td class="running-result-character-error">{values.status.toString().startsWith("4")}</td>
        </tr>
            {/if}
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
