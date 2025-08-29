<script>
	// @ts-nocheck
	import { goto } from "$app/navigation";
	import ToolStatusHeader from "$lib/components/ToolStatusHeader.svelte";
	import {page} from "$app/state";
	import {onMount} from "svelte";

	let config = {
		TargetURL: "",
		WordList: [],
		TopLevelDirectory: "",
		HideStatusCode: "",
		ShowOnlyStatusCode: "",
		FilterContentLength: "",
	};

	let backendUrl
	let fileName = "";
	let startEnabled = false;
	let errors = {};
	const projectID = page.params.id
	function validate() {
		errors = {};
		if (!config.TargetURL) errors.TargetURL = "Target URL is required.";
		if (config.WordList.length === 0) errors.WordList = "Please upload a wordlist.";
		startEnabled = Object.keys(errors).length === 0;
	}

	function handleFileUpload(event) {
		const file = event.target.files[0];
		fileName = file.name;
		const reader = new FileReader();
		reader.onload = () => {
			config.WordList = reader.result.split(/\r?\n/).filter(Boolean);
			validate();
		};
		reader.readAsText(file);
	}
	onMount(()=>{
		backendUrl = sessionStorage.getItem("backendUrl") || "http://localhost";
	})
	async function startBruteForce() {
		validate();
		if (!startEnabled) return;

		const payload = {
			TargetURL: config.TargetURL,
			TopLevelDirectory: config.TopLevelDirectory,
			HideStatusCode: config.HideStatusCode
					? config.HideStatusCode.split(",").map(x => x.trim()).filter(Boolean)
					: [],
			ShowOnlyStatusCode: config.ShowOnlyStatusCode
					? config.ShowOnlyStatusCode.split(",").map(x => x.trim()).filter(Boolean)
					: [],
			FilterContentLength: parseInt(config.FilterContentLength || "0"),
			WordList: config.WordList
		};

		try {
			const res = await fetch(`${backendUrl}:8000/${projectID}/bruteForce`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify(payload)
			});

			if (!res.ok) throw new Error("Brute force scan failed");
			goto(`/project/${projectID}/tools/brute-forcer/run`);
		} catch (err) {
			console.error(err);
		}
	}
</script>

<ToolStatusHeader active={["Configuration"]}/>

<form class="brute-form" on:submit|preventDefault={startBruteForce}>
	<input
		type="url"
		placeholder="Enter target URL"
		title="Enter the target URL to scan"
		bind:value={config.TargetURL}
		class:error={errors.TargetURL}
		autocomplete="url"
		name="targetURL"
	/>
	{#if errors.TargetURL}<span class="error-msg">{errors.TargetURL}</span>{/if}

	<input
		type="text"
		placeholder="Upload Wordlist"
		readonly
		value={fileName}
	/>
	<input type="file" accept=".txt" on:change={handleFileUpload} title="Upload wordlist" />
	{#if errors.WordList}<span class="error-msg">{errors.WordList}</span>{/if}


	<input
		type="text"
		placeholder="Top-Level Directory"
		title="Specify base directory"
		bind:value={config.TopLevelDirectory}
	/>
	<input
		type="text"
		placeholder="Hide Status Codes"
		title="Comma-separated codes to hide"
		bind:value={config.HideStatusCode}
	/>
	<input
		type="text"
		placeholder="Show Only Status Codes"
		title="Comma-separated codes to show"
		bind:value={config.ShowOnlyStatusCode}
	/>
	<input
		type="text"
		placeholder="Content Length"
		title="Filter by content length"
		bind:value={config.FilterContentLength}
	/>

	<button type="submit" disabled={!startEnabled}>Start</button>
</form>

<style>
	.brute-form {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		width: 60%;
		max-width: 700px;
		margin: auto;
	}

	input[type="file"] {
		width: 100%;
		display: block;
	}
	input[type="file"]::-webkit-file-upload-button {
		background: #90cdd2;
		border: none;
		padding: 0.75rem;
		border-radius: 6px;
		cursor: pointer;
		font-weight: bold;
	}
	input[type="text"],
	input[type="url"] {
		padding: 0.5rem;
		border: 1px solid #ccc;
		border-radius: 6px;
		font-size: 1rem;
	}
	input.error {
		border-color: red;
	}
	.error-msg {
		color: red;
		font-size: 0.9rem;
	}
	button[type="submit"] {
		background: #90cdd2;
		border: none;
		padding: 0.75rem;
		border-radius: 6px;
		cursor: pointer;
		font-weight: bold;
	}
	@media (prefers-color-scheme: dark) {
		input[type="text"],
		input[type="url"] {
			background: #1f2937;
			color: #bebebe;
		}
	}
</style>
