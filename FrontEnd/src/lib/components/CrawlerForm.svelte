<script>

	import { goto } from "$app/navigation";
	import { fade, slide } from "svelte/transition";
	import ToolStatusHeader from "$lib/components/ToolStatusHeader.svelte";
	import { page } from '$app/state';
	import {onMount} from "svelte";
	let crawling = false;

	let res = null;
	let advancedOptions = $state(false);
	let backendUrl
	onMount(()=>{
		backendUrl = sessionStorage.getItem("backendUrl") || "http://localhost";
	})
	async function startCrawl(event) {
		event.preventDefault();
		crawling = true;
		const projectID = page.params.id;
		const data = new FormData(event.currentTarget);

		let depth = data.get("CrawlDepth") ? data.get("CrawlDepth") : 2
		let pageNumberLimit = data.get("PageNumberLimit") ? data.get("PageNumberLimit") : 50
		sessionStorage.setItem("crawlerPageLimit", pageNumberLimit);
		let userAgent = data.get("UserAgent") ? data.get('UserAgent') : "Mozilla/3.0"
		let delay = data.get("RequestDelay") ? data.get("RequestDelay") : 1000
		let FilterRelative = data.has("FilterRelativePaths");
		sessionStorage.setItem("crawlerDelay", delay);

		const response = await fetch(`${backendUrl}:8000/${projectID}/crawler`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({
				TargetURL: data.get("TargetURL"),
				CrawlDepth:  depth,
				PageNumberLimit: pageNumberLimit,
				UserAgent: userAgent,
				RequestDelay: delay,
				FilterRelative:FilterRelative
			}),
		});
		if (response.status === 409) {
			alreadyRunning = true
		}
		if (!response.ok) {
			crawling = false;

			sessionStorage.removeItem("crawlerPageLimit");
			throw Error(`Server error: ${response.status}`);
		}
		res = await response.json();
		await goto(`/project/${projectID}/tools/crawler/run?pageLimit=${pageNumberLimit}&delay=${delay}`);
	}

	let alreadyRunning = $state(false);
</script>

{#if !crawling}
	<div class="page-wrapper">
		<ToolStatusHeader active={["Configuration"]}></ToolStatusHeader>

		<div class="crawler-container">
			<form class="crawler-form" on:submit={startCrawl}>
				<div class="form-group">
					<label for="TargetURL">Target URL *</label>
					<input type="url" id="TargetURL" name="TargetURL" required />
				</div>
				{#if advancedOptions}
					<div class="advanced-options" transition:slide >
					<div class="form-group">
						<label for="CrawlDepth">Crawl Depth</label>
						<input type="number" id="CrawlDepth" name="CrawlDepth" value="2" 	min="1"
							   max="100"/>
					</div>

					<div class="form-group">
						<label for="PageNumberLimit">Limit on Number of Pages</label>
						<input type="number" id="PageNumberLimit" name="PageNumberLimit" value="50" 	min="1"
							   max="1000" />
					</div>

					<div class="form-group">
						<label for="UserAgent">User-Agent String</label>
						<select id="UserAgent" name="UserAgent">
							<option value="Mozilla/3.0">Mozilla/3.0</option>
							<option value="AppleWebKit/537.36">AppleWebKit/537.36</option>
							<option value="Chrome/112.0.0.0">Chrome/112.0.0.0</option>
							<option value="Mobile Safari/537.36">Mobile Safari/537.36</option>
						</select>
					</div>

					<div class="form-group">
						<label for="RequestDelay">Request Delay (ms)</label>
						<input type="number" id="RequestDelay" name="RequestDelay" value="1000" 	min="250"
							   max="100000000"/>
					</div>
						<div class="form-group">
							<label for="FilterRelative">Filter Relative Paths</label>
							<input type="checkbox" id="FilterRelative" name="FilterRelativePaths" value="true" checked />
						</div>
					</div>
					{/if}

				<button type="submit" class="start-btn">Start</button>
			</form>

			<button class="toggle-btn" on:click={() => (advancedOptions = !advancedOptions)}>
				{advancedOptions ? "Hide Advanced Options ⌃" : "Show Advanced Options ⌵"}
			</button>
		</div>
		{#if alreadyRunning}
		<div>
			<h1 class="error">Crawler Already Running For This Project!</h1>
<!--			TODO: Might add a modal that stops the crawler-->
		</div>
		{/if}
	</div>
	{/if}

<style>
	:global(body) {
		background: white;
	}

	.page-wrapper {
		width: 90%;
		padding: 2rem;
		display: flex;
		flex-direction: column;
		align-items: center;
		background: transparent;
	}


	.crawler-container {
		width: 100%;
		max-width: 700px;
		padding: 2rem;
		border-radius: 12px;
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
		background: #f9f9f9;
	}

	form {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.form-group {
		display: flex;
		flex-direction: column;
	}

	label {
		font-size: 0.9rem;
		margin-bottom: 0.25rem;
		color: #333;
		margin-top: 2px;
	}

	input,
	select {
		padding: 0.6rem;
		font-size: 1rem;
		border-radius: 6px;
		border: 1px solid #ccc;
	}
	input[type="checkbox"] {
		text-align: center;
		height: 25px;
		accent-color: #0d9488;
		cursor: pointer;
	}
	.start-btn {
		background-color: rgba(74, 166, 176, 0.6);
		color: #000;
		border: none;
		border-radius: 6px;
		padding: 0.75rem;
		font-size: 1rem;
		cursor: pointer;
		width: 100%;
		transition: ease-in-out .25s;
	}

	.start-btn:hover{
		background: #4aa6b0;
		transform: scale(1.05);
	}

	.toggle-btn {
		margin-top: 1rem;
		background: none;
		border: none;
		color: #4aa6b0;
		cursor: pointer;
		font-weight: bold;
	}
	.error{
		color: #fa2424;
		margin-top: 5vh;
	}
	@media (prefers-color-scheme: dark) {
		input[type="number"],
		input[type="url"], textarea, select {
			background: #1f2937;
			color: #bebebe;
		}
		.crawler-container{
			background: #1f2937;
			color: #e5e7eb;
		}
		label{
			color: #e5e7eb;
		}
	}
</style>

