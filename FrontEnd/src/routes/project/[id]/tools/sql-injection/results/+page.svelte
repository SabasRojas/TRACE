<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { get } from 'svelte/store';

	const { id: projectId } = get(page).params;

	let scanResults: any[] = [];
	let testingType = '';
	let activeTab = 'scan';

	let dbStructure: Record<
		string,
		{ column: string; type: string; nullable: boolean; key: string }[]
	> = {};

	let expandedTables: Set<string> = new Set();

	function toggleTable(table: string) {
		if (expandedTables.has(table)) {
			expandedTables.delete(table);
		} else {
			expandedTables.add(table);
		}
		expandedTables = new Set(expandedTables);
	}

	function getBackendUrl(): string {
		if (typeof window !== 'undefined') {
			return sessionStorage.getItem('backendUrl') || 'http://localhost:8000';
		}
		return 'http://localhost:8000';
	}

	async function fetchResults() {
		try {
			const res = await fetch(`${getBackendUrl()}/tools/sql-injection/results`);
			const data = await res.json();
			scanResults = data.results;
			if (data.structure) dbStructure = data.structure;
		} catch (err) {
			console.error('❌ Failed to fetch results:', err);
		}
	}

	onMount(() => {
		const stored = localStorage.getItem('sqlResults');
		if (stored) {
			scanResults = JSON.parse(stored);
		}
	});
</script>

<div class="page">
	<div class="header">
		<h1 class="title">SQL Injection</h1>
		<div class="steps">
			<div class="step">Configuration</div>
			<div class="line"></div>
			<div class="step">Running</div>
			<div class="line"></div>
			<div class="step active">Results</div>
		</div>
	</div>

	<p class="sub-title">Results</p>

	<div class="metrics-grid">
		<div class="metric">
			<p class="metric-label">Testing Type</p>
			<p class="metric-value">{testingType}</p>
		</div>
		<div class="metric">
			<p class="metric-label">Processed Requests</p>
			<p class="metric-value">{scanResults.length}</p>
		</div>
		<div class="metric">
			<p class="metric-label">Effective Payloads</p>
			<p class="metric-value">{scanResults.filter((r) => r.vulnerable).length}</p>
		</div>
		<div class="metric">
			<p class="metric-label">Response Time</p>
			<p class="metric-value">~0.5s</p>
		</div>
	</div>

	<div class="tab-buttons">
		<button class:active={activeTab === 'scan'} on:click={() => (activeTab = 'scan')}>
			Scan Results
		</button>
		<button class:active={activeTab === 'db'} on:click={() => (activeTab = 'db')}>
			Database Structure
		</button>
	</div>

	{#if activeTab === 'scan'}
		<div class="table-container">
			<table>
				<thead>
					<tr>
						<th>#</th>
						<th>Parameter</th>
						<th>Payload</th>
						<th>Status</th>
						<th>Length</th>
						<th>Vulnerable</th>
					</tr>
				</thead>
				<tbody>
					{#each scanResults as result, i}
						<tr class={result.vulnerable ? 'vulnerable' : ''}>
							<td>{i + 1}</td>
							<td>{result.parameter}</td>
							<td>{result.payload}</td>
							<td>{result.status}</td>
							<td>{result.length}</td>
							<td>{result.vulnerable ? 'True' : 'False'}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{:else if activeTab === 'db'}
		{#if Object.keys(dbStructure).length === 0}
			<p class="text-white">No database structure found.</p>
		{:else}
			{#each Object.entries(dbStructure) as [tableName, columns]}
				<div class="table-container">
					<h3 on:click={() => toggleTable(tableName)} class="table-title">
						{expandedTables.has(tableName) ? '▾' : '▸'}
						{tableName}
					</h3>
					{#if expandedTables.has(tableName)}
						<table>
							<thead>
								<tr>
									<th>Column</th>
									<th>Type</th>
									<th>Nullable</th>
									<th>Key</th>
								</tr>
							</thead>
							<tbody>
								{#each columns as col}
									<tr>
										<td>{col.column}</td>
										<td>{col.type}</td>
										<td>{col.nullable ? 'Yes' : 'No'}</td>
										<td>{col.key || '-'}</td>
									</tr>
								{/each}
							</tbody>
						</table>
					{/if}
				</div>
			{/each}
		{/if}
	{/if}
</div>

<style>
	.page {
		display: flex;
		flex-direction: column;
		padding: 2rem;
		min-height: 100vh;
	}

	.header {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.title {
		font-size: 2rem;
		font-weight: bold;
		color: rgb(133, 127, 127);
	}

	.steps {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.step {
		padding: 0.5rem 1rem;
		border-radius: 9999px;
		background: #d1d5db;
		font-weight: bold;
		font-size: 0.9rem;
	}

	.step.active {
		background: #3b82f6;
		color: white;
	}

	.line {
		height: 2px;
		width: 40px;
		background: #d1d5db;
	}

	.sub-title {
		color: rgb(133, 127, 127);
		font-weight: bold;
		font-size: 1.2rem;
		margin-top: 1rem;
		margin-bottom: 5rem;
	}

	.metrics-grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 1rem;
		text-align: center;
		margin: 2rem 0;
	}

	.metric-label {
		color: #9ca3af;
		font-weight: 600;
		font-size: 0.9rem;
	}

	.metric-value {
		color: rgb(133, 127, 127);
		font-size: 1.5rem;
		font-weight: bold;
	}

	.tab-buttons {
		display: flex;
		gap: 1rem;
		margin-bottom: 2rem;
	}

	.tab-buttons button {
		padding: 0.5rem 1rem;
		border-radius: 0.375rem;
		border: none;
		cursor: pointer;
		font-weight: bold;
		background: #6b7280;
		color: white;
	}

	.tab-buttons button.active {
		background: #3b82f6;
	}

	.table-container {
		overflow-x: auto;
		background: white;
		padding: 1rem;
		border-radius: 0.75rem;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		margin-bottom: 2rem;
	}

	.table-title {
		cursor: pointer;
		margin-bottom: 0.5rem;
		font-size: 1.1rem;
		font-weight: bold;
		color: #111827;
	}

	table {
		width: 100%;
		border-collapse: collapse;
	}

	th {
		background: #3b82f6;
		color: white;
		text-align: left;
		padding: 0.75rem;
	}

	td {
		padding: 0.75rem;
		border-top: 1px solid #d1d5db;
		color: black;
	}

	tr:nth-child(even) {
		background: #f9fafb;
	}

	tr.vulnerable {
		background-color: #f4f4f4;
	}
	@media (prefers-color-scheme: dark) {
	.page {
		background-color: #111;
	}

	.title,
	.percentage,
	.scan-status,
	.step,
	.status-text,
	.metric-value,
	.required {
		color: white;
	}

	.input {
		background-color: #222;
		border-color: #444;
	}

	.step.active {
		background: #2563eb; /* Optional: Adjust blue for contrast */
	}

	.line {
		background: #444;
	}
}
</style>
