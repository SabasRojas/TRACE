<script lang="ts">
	import { page } from '$app/stores';
	import { get } from 'svelte/store';

	const { id: projectId } = get(page).params;

	// ✅ Default Docker-internal values
	let host = 'dvwa-db';
	let port = '3306';
	let username = 'root';
	let password = 'root';

	let loading = false;
	let errorMessage = '';
	let result: any = null;
	let backendUrl;

	async function startEnumeration() {
		errorMessage = '';
		loading = true;
		result = null;

		const formData = new FormData();
		formData.append('host', host);
		formData.append('port', port);
		formData.append('username', username);
		formData.append('password', password);
		formData.append('project_id', projectId);

		try {
			backendUrl = sessionStorage.getItem("backendUrl") || "http://localhost";
			const res = await fetch(`${backendUrl}:8000/tools/db-enumerator/`, {
				method: 'POST',
				body: formData
			});
			const data = await res.json();

			if (data.status === 'success') {
				result = data;
			} else {
				errorMessage = data.message || '❌ Enumeration failed.';
			}
		} catch (err) {
			errorMessage = '❌ Network error.';
			console.error(err);
		} finally {
			loading = false;
		}
	}
</script>

<div class="page">
	<div class="header">
		<h1 class="title">Database Enumeration</h1>
		<div class="steps">
			<div class="step active">Configuration</div>
			<div class="line"></div>
			<div class="step">Results</div>
		</div>
	</div>

	<div class="form-container">
		<p class="section-title">Configured to run against dvwa-db</p>

		<button
			on:click={startEnumeration}
			class="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 mt-4 rounded"
		>
			{loading ? 'Enumerating...' : 'Run Enumeration'}
		</button>

		{#if errorMessage}
			<p class="text-red-500 mt-4">{errorMessage}</p>
		{/if}
	</div>

	{#if result}
		<div class="mt-8">
			<h3 class="section-title">Results</h3>
			<pre class="bg-gray-900 text-white p-4 rounded">{JSON.stringify(result, null, 2)}</pre>
		</div>
	{/if}
</div>

<style>
	.page { padding: 2rem; }
	.header { display: flex; justify-content: space-between; align-items: center; }
	.title { font-size: 2rem; font-weight: bold; color: white; }
	.steps { display: flex; align-items: center; gap: 0.5rem; }
	.step { padding: 0.5rem 1rem; border-radius: 9999px; background: #d1d5db; font-weight: bold; font-size: 0.9rem; }
	.step.active { background: #3b82f6; color: white; }
	.line { height: 2px; width: 40px; background: #d1d5db; }
	.form-container { margin-top: 3rem; max-width: 600px; margin-left: auto; margin-right: auto; padding: 2rem; border-radius: 1rem; }
	.section-title { font-weight: bold; color: white; margin-bottom: 1rem; font-size: 1.25rem; }
	pre { max-height: 500px; overflow-y: auto; white-space: pre-wrap; }
</style>
