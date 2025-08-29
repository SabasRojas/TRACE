<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { get } from 'svelte/store';
	import { writable } from 'svelte/store';

	const { id: projectId } = get(page).params;
	//const progress = writable(0);
	const logs = writable<string[]>([]);

	interface ScanResult {
		id: number;
		parameter: string;
		method: string;
		type: string;
		payload: string;
		status: number;
		length: number;
		vulnerable: boolean;
	}

	let progress = 0;
	let scanCompleted = false;
	let scanPaused = false;
	let scanResults: ScanResult[] = [];
	let interval: ReturnType<typeof setInterval> | null = null;
	let testingType = 'Basic SQL Injection';
	let terminal: string[] = [];
	let showTerminal = false;
	let lastResultCount = 0;
	let backendUrl;

	const fetchTerminal = async () => {
		const res = await fetch(`${backendUrl}:8000/tools/sql-injection/terminal-log`);
		const data = await res.json();
		terminal = data.log;
	};

	async function fetchProgress() {
		try {
			const res = await fetch(`${backendUrl}:8000/tools/sql-injection/progress`);
			const data = await res.json();
			progress = +data.progress;
		} catch (err) {
			console.error('Failed to fetch progress:', err);
		}
	}

	async function fetchResults() {
		try {
			const res = await fetch(`${backendUrl}:8000/tools/sql-injection/results`);
			const data = await res.json();
			const newResults = data.results ?? [];

			// Append only new, non-duplicate results
			for (const result of newResults) {
				const alreadyExists = scanResults.some((r) => r.id === result.id);
				if (!alreadyExists) {
					scanResults = [...scanResults, result];
					localStorage.setItem('sqlResults', JSON.stringify(scanResults));
				}
			}
		} catch (err) {
			console.error('Failed to fetch results:', err);
		}
	}

	function startPolling() {
		if (interval) clearInterval(interval);
		interval = setInterval(async () => {
			await fetchProgress();
			await fetchResults();
			await fetchTerminal();
			if (progress >= 100 && interval) {
				clearInterval(interval!);
				interval = null;
				scanCompleted = true;
			}
		}, 2000);
	}

	function togglePauseResume() {
		if (scanPaused) {
			startPolling();
			scanPaused = false;
		} else {
			if (interval) clearInterval(interval);
			scanPaused = true;
		}
	}

	async function stopScan() {
		if (interval) clearInterval(interval);
		scanPaused = true;
		progress = 0;
		scanResults = [];

		try {
			await fetch(`${backendUrl}:8000/tools/sql-injection/stop`, {
				method: 'POST'
			});
		} catch (error) {
			console.error('Failed to stop scan:', error);
		}
	}

	function restartScan() {
		scanCompleted = false;
		scanPaused = true;
		progress = 0;
		scanResults = [];
		goto(`/project/${projectId}/tools/sql-injection/`);
	}

	onMount(() => {
		backendUrl = sessionStorage.getItem("backendUrl") || "http://localhost";
		const storedType = localStorage.getItem('testingType');
		if (storedType) {
			testingType = storedType;
		}

		startPolling();

		return () => {
			if (interval) clearInterval(interval);
		};
	});
</script>

<div class="page">
	<!-- Header and Steps -->
	<!-- Header and Steps -->
	<div class="header">
		<h1 class="title">SQL Injection</h1>

		<div class="steps">
			<div class="step">Configuration</div>
			<div class="line"></div>
			<div class="step active">Running</div>
			<div class="line"></div>
			<div class="step">Results</div>
		</div>
	</div>

	<!-- Subtext -->
	<!-- Subtext -->
	<p class="sub-title">Running</p>

	<!-- Progress Bar and Scan Text Section -->
	<!-- Progress Bar and Scan Text Section -->
	<div class="progress-container">
		<div class="scan-status">
			{#if scanCompleted}
				<div class="percentage">100%</div>
				<div class="status-text">Complete</div>
			{:else}
				<div class="percentage">{progress}%</div>
				<div class="status-text">Scanning...</div>
			{/if}
		</div>

		<div class="progress-bar">
			<div class="progress" style="width: {progress}%"></div>
		</div>
	</div>

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

	<!-- Table -->
	<!-- Table -->
	<div class="table-container">
		<table class="w-full">
			<thead>
				<tr>
					<th>#</th>
					<th>Parameter</th>
					<th>Method</th>
					<th>Type</th>
					<th>Payload</th>
					<th>Status</th>
					<th>Length</th>
					<th>Vulnerable</th>
				</tr>
			</thead>
			<tbody>
				{#each scanResults as result}
					<tr>
						<td>{result.id}</td>
						<td>{result.parameter}</td>
						<td>{result.method}</td>
						<td>{result.type}</td>
						<td>{result.payload}</td>
						<td>{result.status}</td>
						<td>{result.length}</td>
						<td>{result.vulnerable ? 'True' : 'False'}</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>

	<div class="buttons">
		<button on:click={togglePauseResume} class="btn">
			{scanPaused ? 'Resume' : 'Pause'}
		</button>
		<button on:click={stopScan} class="btn">Stop</button>
		<button on:click={restartScan} class="btn">Restart</button>
		<button
			class="btn secondary"
			on:click={() => (showTerminal = !showTerminal)}
			title="Show raw log output of scan"
		>
			{showTerminal ? 'Hide Terminal' : 'Show Terminal'}
		</button>
		{#if scanCompleted}
			<button
				on:click={() => goto(`/project/${projectId}/tools/sql-injection/results`)}
				class="btn"
			>
				View Results
			</button>
		{/if}
	</div>

	{#if showTerminal}
		<div class="terminal-container">
			<h2 class="text-lg font-semibold text-white">Terminal Output</h2>
			<div class="terminal-output">
				{#each terminal as line}
					<pre>{line}</pre>
				{/each}
			</div>
		</div>
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

	.progress-container {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.5rem;
		margin-bottom: 2rem;
	}

	.scan-status {
		color: rgb(133, 127, 127);
		font-weight: bold;
		font-size: 1rem;
		text-align: left;
		width: 80%;
	}

	.progress-bar {
		width: 80%;
		height: 8px;
		background: #d1d5db;
		border-radius: 9999px;
		overflow: hidden;
		margin: 0 auto;
	}

	.progress {
		height: 100%;
		background: #3b82f6;
		width: 0%;
		transition: width 0.2s ease;
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

	.table-container {
		overflow-x: auto;
		background: white;
		padding: 1rem;
		border-radius: 0.75rem;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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

	.buttons {
		display: flex;
		justify-content: center;
		gap: 1rem;
		margin-top: 2rem;
	}

	.btn {
		background: #3b82f6;
		color: white;
		padding: 0.5rem 1.5rem;
		border-radius: 0.5rem;
		font-weight: bold;
		transition: background 0.3s;
	}

	.btn:hover {
		background: #2563eb;
	}

	.btn.secondary {
		background: #6b7280;
	}

	.btn.secondary:hover {
		background: #4b5563;
	}
	.percentage {
		font-size: 2rem;
		font-weight: bold;
		color: rgb(133, 127, 127);
		text-align: left;
		width: 100%;
	}

	.status-text {
		font-size: 1rem;
		color: rgb(133, 127, 127);
		text-align: left;
		width: 100%;
	}

	.terminal-container {
		margin-top: 2rem;
		background: #1e1e1e;
		border-radius: 8px;
		padding: 1rem;
		color: #e5e5e5;
		max-height: 300px;
		overflow-y: auto;
	}

	.terminal-output {
		font-family: monospace;
		white-space: pre-wrap;
		background-color: #121212;
		padding: 1rem;
		border-radius: 4px;
		overflow-y: auto;
	}

	.terminal-output pre {
		margin: 0;
		line-height: 1.5;
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
