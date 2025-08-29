<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { get } from 'svelte/store';

	let targetUrl = 'https://juice-shop.herokuapp.com/';
	let port = '80';
	let username = '';
	let password = '';
	let enumerationLevel = 'Basic';
	let timeout = 2;
	let additionalParams = '';
	let databaseEnumeration = false;
	let errorMessage = '';
	let backendUrl;
	const { id: projectId } = get(page).params;

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
	let active = true;

	let terminal: string[] = [];
	let showTerminal = false;
	let showPayloadModal = false;
	let payloadText = '';

	async function submitPayloads() {
		const payloads = payloadText
			.split('\n')
			.map((p) => p.trim())
			.filter(Boolean);
		try {
			const res = await fetch(`${backendUrl}:8000/tools/sql-injection/configure-payloads`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(payloads)
			});
			const data = await res.json();
			alert(`Payloads updated (${data.payload_count})`);
			showPayloadModal = false;
		} catch (err) {
			alert('Error updating payloads');
		}
	}

	let showParamModal = false;
	let paramText = '';

	async function submitParameters() {
		const params = paramText
			.split('\n')
			.map((p) => p.trim())
			.filter(Boolean);
		try {
			const res = await fetch(`${backendUrl}:8000/tools/sql-injection/configure-parameters`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(params)
			});
			const data = await res.json();
			alert(`Parameters updated (${data.parameter_count})`);
			showParamModal = false;
		} catch (err) {
			alert('Error updating parameters');
		}
	}

	function validateInputs() {
		return targetUrl && port && enumerationLevel && timeout !== null;
	}

	async function startScan() {
		if (!validateInputs()) {
			errorMessage = '❌ Please complete all required fields.';
			return;
		}

		try {
			const res = await fetch(`${backendUrl}:8000/tools/sql-injection/start`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					projectId,
					targetUrl,
					port,
					username,
					password,
					enumerationLevel,
					timeout,
					additionalParams,
					databaseEnumeration
				})
			});

			if (!res.ok) {
				errorMessage = '❌ Failed to start scan.';
				return;
			}

			goto(`/project/${projectId}/tools/sql-injection/running`);
		} catch (error) {
			errorMessage = '❌ Network error while starting scan.';
			console.error(error);
		}
	}

	async function fetchProgress() {
		const res = await fetch(`${backendUrl}:8000/tools/sql-injection/progress`);
		const data = await res.json();
		progress = data.progress;
	}

	async function fetchResults() {
		const res = await fetch(`${backendUrl}:8000/tools/sql-injection/results`);
		const data = await res.json();
		scanResults = data.results;
	}

	async function fetchTerminal() {
		const res = await fetch(`${backendUrl}:8000/tools/sql-injection/terminal-log`);
		const data = await res.json();
		terminal = data.log;
	}

	function startPolling() {
		if (interval) clearInterval(interval);
		interval = setInterval(async () => {
			if (!active) return;

			await fetchProgress();
			await fetchResults();
			await fetchTerminal();

			if (progress >= 100) {
				clearInterval(interval!);
				scanCompleted = true;
			}
		}, 1000);
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

	function stopScan() {
		if (interval) clearInterval(interval);
		scanPaused = false;
		progress = 0;
		scanResults = [];
	}

	function restartScan() {
		scanCompleted = false;
		scanPaused = false;
		progress = 0;
		scanResults = [];
		startPolling();
	}

	onMount(() => {
		backendUrl = sessionStorage.getItem("backendUrl") || "http://localhost";
		startPolling();
		const storedType = localStorage.getItem('testingType');
		if (storedType) {
			testingType = storedType;
		}
	});
	onDestroy(() => {
		active = false;
		if (interval) clearInterval(interval);
		interval = null;

		progress = 0;
		scanResults = [];
		terminal = [];
		scanCompleted = false;
		scanPaused = false;
	});
</script>

<div class="page">
	<div class="header">
		<h1 class="title">SQL Injection</h1>
		<div class="steps">
			<div class="step active">Configuration</div>
			<div class="line"></div>
			<div class="step">Running</div>
			<div class="line"></div>
			<div class="step">Results</div>
		</div>
	</div>

	<div class="form-container">
		<p class="section-title">Configuration</p>

		<div class="toggle-container">
			<label class="switch">
				<input type="checkbox" bind:checked={databaseEnumeration} />
				<span class="slider round"></span>
			</label>
			<span class="toggle-label">Database Enumeration</span>
		</div>

		<div class="form-grid">
			<div class="form-group">
				<label for="targetUrl">Target URL <span class="required">*</span></label>
				<input
					id="targetUrl"
					type="text"
					placeholder="Enter Target URL"
					bind:value={targetUrl}
					class="input"
				/>
			</div>

			<div class="form-group">
				<label for="port">Port <span class="required">*</span></label>
				<input id="port" type="text" placeholder="Enter Port" bind:value={port} class="input" />
			</div>

			<div class="form-group">
				<label for="username">Database Username</label>
				<input id="username" type="text" placeholder="admin" bind:value={username} class="input" />
			</div>

			<div class="form-group">
				<label for="password">Database Password</label>
				<input
					id="password"
					type="password"
					placeholder="password"
					bind:value={password}
					class="input"
				/>
			</div>

			<div class="form-group">
				<label for="enumerationLevel">Enumeration Level</label>
				<input
					id="enumerationLevel"
					type="text"
					placeholder="Basic"
					bind:value={enumerationLevel}
					class="input"
				/>
			</div>

			<div class="form-group">
				<label for="timeout">Time Out</label>
				<input
					id="timeout"
					type="number"
					placeholder="30 seconds"
					bind:value={timeout}
					class="input"
				/>
			</div>

			<div class="form-group">
				<label for="additionalParams">Additional Parameters (if applicable)</label>
				<input
					id="additionalParams"
					type="text"
					placeholder="NULL"
					bind:value={additionalParams}
					class="input"
				/>
			</div>
		</div>

		{#if errorMessage}
			<p class="text-red-500 mt-4">{errorMessage}</p>
		{/if}
		<div style="margin-top: 1rem; display: flex; gap: 1rem;">
			<button class="btn btn-secondary" on:click={() => (showPayloadModal = true)}>
				Configure Payloads
			</button>
			<button class="btn btn-secondary" on:click={() => (showParamModal = true)}>
				Configure Parameters
			</button>
		</div>
		{#if showPayloadModal}
			<div class="modal">
				<div class="modal-content">
					<h3>Configure SQL Payloads</h3>
					<textarea
						bind:value={payloadText}
						rows="10"
						cols="50"
						placeholder="Paste one payload per line..."
					></textarea>
					<br />
					<button on:click={submitPayloads}>Save</button>
					<button on:click={() => (showPayloadModal = false)}>Cancel</button>
				</div>
			</div>
		{/if}
		{#if showParamModal}
			<div class="modal">
				<div class="modal-content">
					<h3>Paste Parameters</h3>
					<textarea
						bind:value={paramText}
						rows="10"
						cols="50"
						placeholder="One parameter per line (e.g., id, email, user_id)..."
					></textarea>
					<div class="modal-actions">
						<button on:click={submitParameters}>Save</button>
						<button on:click={() => (showParamModal = false)}>Cancel</button>
					</div>
				</div>
			</div>
		{/if}
		<button
			on:click={startScan}
			class="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 mt-6 rounded"
		>
			Start
		</button>
	</div>
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

	.form-container {
		margin-top: 3rem;
		max-width: 600px;
		width: 100%;
		margin-left: auto;
		margin-right: auto;
		background: transparent;
		padding: 2rem;
		border-radius: 1rem;
	}

	.form-group {
		display: flex;
		flex-direction: column;
		margin-bottom: 1.5rem;
	}

	label {
		color: rgb(133, 127, 127);
		font-weight: 600;
		margin-bottom: 0.5rem;
	}

	.input {
		border: 1px solid #ccc;
		padding: 0.5rem;
		border-radius: 0.375rem;
		background: transparent;
		color: rgb(75, 71, 71);
	}

	.input::placeholder {
		color: #aaa;
	}

	.section-title {
		font-weight: bold;
		color: rgb(133, 127, 127);
		margin-bottom: 1rem;
		font-size: 1.25rem;
	}

	.required {
		color: red;
	}

	.toggle-container {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		margin-bottom: 2rem;
	}

	.toggle-label {
		font-weight: 600;
		color: rgb(133, 127, 127);
		line-height: 1;
	}

	.switch {
		position: relative;
		display: inline-block;
		width: 40px;
		height: 20px;
	}

	.switch input {
		opacity: 0;
		width: 0;
		height: 0;
	}

	.slider {
		position: absolute;
		cursor: pointer;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background-color: #ccc;
		transition: 0.4s;
		border-radius: 34px;
	}

	.slider:before {
		position: absolute;
		content: '';
		height: 16px;
		width: 16px;
		left: 2px;
		bottom: 2px;
		background-color: white;
		transition: 0.4s;
		border-radius: 50%;
	}

	input:checked + .slider {
		background-color: #06b12b;
	}

	input:checked + .slider:before {
		transform: translateX(20px);
	}

	@media (prefers-color-scheme: dark) {
	.page {
		background-color: #111;
	}

	label,
	.title,
	.section-title,
	.toggle-label,
	.step,
	.input,
	.required {
		color: white;
	}

	.input {
		background-color: #222;
		border-color: #444;
	}

	.step.active {
		background: #2563eb; /* Optional: Adjust blue for contrast */
		color: white;
	}

	.line {
		background: #444;
	}
}
</style>
