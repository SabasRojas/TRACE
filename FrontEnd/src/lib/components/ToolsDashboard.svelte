<script>
	import {goto} from "$app/navigation";
	import {page} from "$app/state";
	import DashboardProgressBar from "$lib/components/DashboardProgressBar.svelte";
	import ToolButton from "$lib/components/ToolButton.svelte";
	import {onMount} from "svelte";
	let props = $props()
	let projectName = props.projectName;
	let projectID = page.params.id;
	let backendUrl

	onMount(()=>{
		backendUrl = backendUrl = sessionStorage.getItem("backendUrl") || "http://localhost";
	})
	let tools = $state([
		{
			name: "HTTP Tester",
			pathName: "http-requests",
			progress: 0,
			status: "Ready to Go!",
			color: "#ccc",
			tooltip: "Tests HTTP methods and headers for unexpected behavior",
			action: "Set Up",
			enabled: true, 
			callback: ()=>{goto(`/project/${projectID}/tools/HTTP-requests`)},
			results: ()=>{goto(`/project/${projectID}/tools/HTTP-requests`)}
		},
		{
			name: "SQL Injection",
			progress: 0,
			status: "Ready to Go!",
			color: "#ccc",
			tooltip: "Tests input fields and parameters for SQL injection vulnerabilities by sending crafted queries.",
			action: "Set Up",
			enabled: true,
			callback: ()=>{ goto(`/project/${projectID}/tools/sql-injection`)},
			//results: ()=>{goto(`/project/${projectID}/tools/sql-injection/results`)}
		},
		{
			name: "Parameter Fuzzing",
			pathName: "fuzzer",
			progress: 0,
			status: "Ready to Go!",
			color: "#ccc",
			tooltip: "Tries random values for fuzzing parameters",
			action: "Set Up",
			enabled: true,
			callback: ()=>{goto(`/project/${projectID}/tools/fuzzer`)},
			results: ()=>{goto(`/project/${projectID}/tools/fuzzer/run`)}
		},
		{
			name: "Brute Force Tester",
			pathName: "bruteForce",
			progress: 0,
			status: "Ready to Go!",
			color: "#ccc",
			tooltip: "Attempts brute force attacks",
			action: "Set Up",
			enabled: true,
			callback: ()=>{goto(`/project/${projectID}/tools/brute-forcer`)},
			results: ()=>{goto(`/project/${projectID}/tools/brute-forcer/run`)}
		},
		{
			name: "DB Enumeration",
			progress: 0,
			status: "Ready to Go!",
			color: "#ccc",
			tooltip: "Attempts to enumerate database names, tables, and columns using inference techniques.",
			action: "Set Up",
			enabled: true,
			callback: ()=>{goto(`/project/${projectID}/tools/db_enumerator`)},

		},
		{
			name: "Crawler",
			pathName: "crawler",
			progress: 0,
			status: "Ready to Go!",
			color: "#ccc",
			tooltip: "Scan a website to gather links and map its structure.",
			action: "Set Up",
			enabled: true,
			callback: ()=>{goto(`/project/${projectID}/tools/crawler`)},
			results: ()=>{goto(`/project/${projectID}/tools/crawler/run`)}
		}
	]);
</script>

<h2 class="project-name">{projectName}</h2>

<div class="tools-list">
	{#each tools as tool}
		<div class="tool-row">
			<div class="tool-name">{tool.name}</div>
			<DashboardProgressBar tool={tool.name} projectID = {projectID} results={tool.results} callback={tool.callback} tooltip={tool.tooltip} toolName={tool.pathName}></DashboardProgressBar>

		</div>
	{/each}
</div>

<ToolButton callback={async ()=>{await fetch(`${backendUrl}:8000/${projectID}/bruteForce/stop`, {method: 'POST'});
												await fetch(`${backendUrl}:8000/${projectID}/crawler/stop`, {method: 'POST'});
												await fetch(`${backendUrl}:8000/${projectID}/fuzzer/stop`, {method: 'POST'})}} content="<b>Stop Project</b>"></ToolButton>

<style>
	.project-name {
		margin-left: 2.5vw;
		color: #666;
		font-size: 1.2rem;
		margin-bottom: 2rem;
	}

	.tools-list {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		align-items: center;
		width: 60%;
	}

	.tool-row {
		display: flex;
		align-items: center;
		justify-content: space-between;
		width: 85%;
		padding: 0.7rem;
		border-radius: 12px;
		background: #e0dfe0;
	}

	.tool-name {
		width: 20%;
		font-weight: 500;
	}



	.stop-btn {
		margin: 2rem auto;
		display: block;
		background: #d8f3dc;
		border: none;
		padding: 0.75rem 2rem;
		border-radius: 6px;
		cursor: pointer;
		font-weight: bold;
		color: #000;
	}
	@media (prefers-color-scheme: dark) {
		.project-name{
			color: #e5e7eb;
		}
		.tool-row{
			background: #1f2937;
		}
		.stop-btn{
			background: #273949;
			color: #bebebe;
		}
	}
</style>

