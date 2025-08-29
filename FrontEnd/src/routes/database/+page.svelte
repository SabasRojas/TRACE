<script lang="ts">
    import {onMount} from "svelte";

    let query: string = "";
    let results: any[] = [];
    let tables: string[] = [];
    let features: string[] = [];
    let backendUrl: string

    onMount(()=>{
        backendUrl = sessionStorage.getItem("backendUrl") || "http://localhost";
    })
    async function openConnection() {
        await fetch(`${backendUrl}:8000/open_connection`, { method: "POST" });
        alert("Database connection opened!");
    }

    async function closeConnection() {
        await fetch(`${backendUrl}:8000/close_connection`, { method: "POST" });
        alert("Database connection closed!");
    }

    async function initializeQuery() {
        await fetch(`${backendUrl}:8000/initialize_enumeration`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query })
        });
        alert("Query initialized!");
    }

    async function executeQuery() {
        await fetch(`${backendUrl}:8000/execute_query`, { method: "POST" });
        alert("Query executed!");
    }

    async function fetchResults() {
        let res = await fetch(`${backendUrl}:8000/get_query_results`);
        results = await res.json();
    }

    async function storeTable(tableName: string) {
        await fetch(`${backendUrl}:8000/store_table`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ table_name: tableName })
        });
        alert(`Table ${tableName} stored!`);
    }

    async function fetchTables() {
        let res = await fetch(`${backendUrl}:8000/get_table_names`);
        tables = await res.json();
    }

    async function fetchTableFeatures(tableName: string) {
        let res = await fetch(`${backendUrl}:8000/get_table_features?table_name=${tableName}`);
        features = (await res.json()).features;
    }
</script>

<h1>SQL Query Executor</h1>
<button on:click={openConnection}>Open Connection</button>
<button on:click={closeConnection}>Close Connection</button>

<input type="text" bind:value={query} placeholder="Enter SQL query" />
<button on:click={initializeQuery}>Initialize Query</button>
<button on:click={executeQuery}>Execute Query</button>
<button on:click={fetchResults}>Get Results</button>

<h2>Results</h2>
<ul>
    {#each results as row}
        <li>{JSON.stringify(row)}</li>
    {/each}
</ul>

<h2>Stored Tables</h2>
<button on:click={fetchTables}>Fetch Tables</button>
<ul>
    {#each tables as table}
        <li>
            {table}
            <button on:click={() => fetchTableFeatures(table)}>View Features</button>
        </li>
    {/each}
</ul>

<h2>Table Features</h2>
<ul>
    {#each features as feature}
        <li>{feature}</li>
    {/each}
</ul>
