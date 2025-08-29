<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	export let data: any; // You can replace `any` with an interface if you want strict typing

	let actionMessage = '';
	let actionError = '';
	let backendUrl: string = 'http://localhost'; // default fallback

	onMount(() => {
		const stored = sessionStorage.getItem('backendUrl');
		if (stored) backendUrl = stored;
	});

	async function toggleLock(lockState: boolean): Promise<void> {
		actionMessage = '';
		actionError = '';

		if (!data.project || !data.requesterId || !data.initials || !data.projectId) {
			actionError = '❌ Cannot toggle lock: Missing required data.';
			return;
		}

		try {
			const res = await fetch(`${backendUrl}/project/${data.projectId}/lock-toggle`, {
				method: 'PUT',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					user_id: parseInt(data.requesterId || '0'),
					initials: data.initials,
					lock: lockState
				})
			});

			const result = await res.json();

			if (res.ok) {
				actionMessage = `✅ ${result.message}`;
				data.project.isLocked = lockState;
			} else {
				console.error('❌ Lock API error:', result.detail);
				actionError = `❌ ${result.detail || 'Failed to toggle lock.'}`;
			}
		} catch (err: unknown) {
			const errorMessage = err instanceof Error ? err.message : String(err);
			console.error('❌ Lock toggle failed:', errorMessage);
			actionError = `❌ Failed to update lock state: ${errorMessage}`;
		}
	}

	function goBack(): void {
		goto('/project');
	}
</script>

<div class="project-container">
	<h1>Project Dashboard</h1>
	<button on:click={goBack} style="margin-bottom: 1rem;">⬅️ Back to Projects</button>

	{#if data.error}
		<p class="error">Error loading project: {data.error}</p>
	{:else if !data.project && !data.error}
		<p>Loading project data...</p>
	{:else if data.project}
		<div class="project-info">
			<h2>{data.project.name}</h2>
			<p><strong>Project ID:</strong> {data.project.id}</p>
			<p><strong>Owner:</strong> {data.project.owner}</p>
			<p><strong>Locked:</strong> {data.project.isLocked ? 'Locked' : 'Unlocked'}</p>
			<p>
				<strong>Files:</strong>
				{data.project.files?.length > 0 ? data.project.files.join(', ') : 'No files'}
			</p>
			<p><strong>IP List:</strong></p>
			{#if data.project.IPList && data.project.IPList.length > 0}
				<ul>
					{#each data.project.IPList as [ip, port] (ip + ':' + port)}
						<li>{ip}:{port}</li>
					{/each}
				</ul>
			{:else}
				<p>No IP addresses listed.</p>
			{/if}

			{#if actionMessage}
				<p class="message">{actionMessage}</p>
			{/if}
			{#if actionError}
				<p class="error">{actionError}</p>
			{/if}

			<div style="margin-top: 1rem;">
				<button
					on:click={() => {
						if (!data.requesterId || !data.initials) {
							actionError = '❌ Cannot continue: missing user credentials.';
							return;
						}
						goto(
							`/project/${data.projectId}/tools` +
								(data.requesterId && data.initials
									? `?requester_id=${data.requesterId}&initials=${data.initials}`
									: '')
						);
					}}
				>
					Run Tools for This Project
				</button>
			</div>
		</div>
	{/if}
</div>

<style>
	.project-container {
		padding: 2rem;
	}

	.project-info {
		background: #f5f5f5;
		padding: 1rem;
		border-radius: 0.5rem;
	}

	.lock-toggle {
		margin-top: 1rem;
	}

	.error {
		color: red;
		font-weight: bold;
		margin-top: 1rem;
	}

	.message {
		color: green;
		font-weight: bold;
		margin-top: 1rem;
	}
	@media (prefers-color-scheme: dark) {
		.project-info {
			background: #12181b;
			color: #e0e0e0;
		}
	}
</style>
