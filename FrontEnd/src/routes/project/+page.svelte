v<script lang="ts">
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { currentUser } from "$lib/stores/user";
  import { get } from "svelte/store";
  import "$lib/styles/trace.css";

  const user = get(currentUser);

  let message = "";
  let showDialog = false;
  let backendUrl;
  let projects: { id: string; name: string; owner: string; isLocked: boolean; files: string[] }[] = [];
  let recentProjects: { id: string; name: string }[] = [];

  // Project creation fields
  let newProjectId = "";
  let newProjectName = "";
  let startDate = "";
  let endDate = ""; // ✅ NEW FIELD
  let leadAnalyst = "";
  let projectDescription = "";
  let uploadedFiles: File[] = [];

  function handleFileUpload(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files) uploadedFiles = Array.from(input.files);
  }

  function removeFile(index: number) {
    uploadedFiles.splice(index, 1);
  }

  async function createProject() {
    // ✅ Updated validation
    if (!newProjectName || !startDate || !endDate || !leadAnalyst) {
      message = "Please fill all required fields.";
      return;
    }

    const payload = {
      name: newProjectName,
      owner: leadAnalyst,
      dateRange: [startDate, endDate], // ✅ Updated range
      description: projectDescription,
      files: uploadedFiles.map(f => f.name),
      IPList: [],
      isLocked: false,
      id: newProjectId || Math.random().toString(36).substring(2, 8)
    };

    try {
      const res = await fetch(`${backendUrl}:8000/project/create`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      if (res.ok) {
        projects.push(payload);
        showDialog = false;
        message = `${data.message}`;
        resetCreateForm();
        loadProjects();
      } else {
        message = `${data.detail || "Failed to create project."}`;
      }
    } catch {
      message = "Failed to connect to server.";
    }
  }

  function resetCreateForm() {
    newProjectId = "";
    newProjectName = "";
    startDate = "";
    endDate = ""; // ✅ Reset new field
    leadAnalyst = "";
    projectDescription = "";
    uploadedFiles = [];
  }

  async function loadProjects() {
    const res = await fetch(`${backendUrl}:8000/project`);
    const data = await res.json();
    if (Array.isArray(data)) projects = data;
  }

  async function openProject(projectId: string) {
    if (!user || !user.id) {
      message = "Please log in first.";
      return;
    }

    try {
      await fetch(`${backendUrl}:8000/project/${projectId}/access`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: user.id })
      });
    } catch {
      console.warn("Access logging failed.");
    }

    goto(`/project/${projectId}?requester_id=${user.id}&initials=${user.name}`);
  }

  async function loadRecentProjects() {
    if (!user?.id) return;
    try {
      const res = await fetch(`${backendUrl}:8000/project/recent?user_id=${user.id}`);
      const data = await res.json();
      if (Array.isArray(data)) recentProjects = data;
    } catch (e) {
      console.error("Failed to load recent projects.");
    }
  }

  interface ImportedData {
    name: string;
    id: string;
    files: any;
    IPList: any;
    isLocked: boolean;
    owner: string;
  }

  async function importProject(importedData: ImportedData) {
    const payload = {
      name: importedData.name,
      owner: importedData.owner,
      dateRange: ["", ""],
      description: "",
      files: importedData.files,
      IPList: importedData.IPList,
      isLocked: importedData.isLocked,
      id: importedData.id
    };

    try {
      const res = await fetch(`${backendUrl}:8000/project/create`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      if (res.ok) {
        projects.push(payload);
        showDialog = false;
        message = `${data.message}`;
      } else {
        message = `${data.detail || "Failed to create project."}`;
      }
    } catch {
      message = "Failed to connect to server.";
    }
  }

  async function toggleLock(projectId: string) {
  const currentProject = projects.find(p => p.id === projectId);
  if (!currentProject) {
    message = "Project not found.";
    return;
  }

  try {
    const res = await fetch(`${backendUrl}:8000/project/${projectId}/lock-toggle`, {
      method: "PUT", // ✅ Correct HTTP method
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: user.id,
        initials: user.name,
        lock: !currentProject.isLocked
      })
    });

    if (res.ok) {
      currentProject.isLocked = !currentProject.isLocked;
      await loadProjects();
    } else {
      const data = await res.json();
      message = data.detail || "Failed to toggle lock.";
    }
  } catch {
    message = "Failed to connect to server.";
  }
}


  onMount(() => {
    backendUrl = sessionStorage.getItem("backendUrl") || "http://localhost";
    loadProjects();
    loadRecentProjects();
  });
</script>

<div>
  {#if user}
    <p class="message">👤 Logged in as <strong>{user.name}</strong> (Role: {user.role})</p>
  {:else}
    <p class="message">No user found. <a href="/role-selector">Select your role</a></p>
  {/if}

  <div class="header-bar">
    <h1>TRACE System</h1>
    <div class="nav-buttons">

      <button on:click={() => showDialog = true}>+ Create Project</button>
      <button on:click={() => {
        const dataStr = JSON.stringify(projects, null, 2);
        const blob = new Blob([dataStr], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "projects.json";
        a.click();
        URL.revokeObjectURL(url);
      }}>Export</button>
      <label class="file-upload-label">
        Import
        <input type="file" accept="application/json" on:change={(e) => {
          const input = e.target as HTMLInputElement;
          const file = input.files?.[0];
          if (!file) return;

          const reader = new FileReader();
          reader.onload = (e) => {
            try {
              const importedData = JSON.parse(e.target?.result as string);
              const isValid = (typeof importedData.name === "string" &&
                               typeof importedData.id === "string" &&
                               typeof importedData.owner === "string" &&
                               typeof importedData.isLocked === "boolean" &&
                               Array.isArray(importedData.files) &&
                               importedData.files.every(file => typeof file === "string") &&
                               Array.isArray(importedData.IPList) &&
                               importedData.IPList.every(ip => Array.isArray(ip) && ip.length === 2 && typeof ip[0] === "string" && typeof ip[1] === "number")
              );
              if (isValid) {
                importProject(importedData)
                message = "Projects imported successfully.";
              } else {
                message = "Invalid JSON format.";
              }
            } catch {
              message = "Failed to parse JSON.";
            }
          };
          reader.readAsText(file);
        }} />
      </label>
    </div>
  </div>

  {#if message}
    <div class="message">{message}</div>
  {/if}

  {#if recentProjects.length > 0}
    <div class="recent-projects">
      <h2>Recently Accessed Projects</h2>
      <ul>
        {#each recentProjects as proj}
          <li>{proj.name} <button on:click={() => openProject(proj.id)}>Open</button></li>
        {/each}
      </ul>
    </div>
  {/if}

  <div class="all-projects">
    <h2>All Projects</h2>
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>ID</th>
          <th>Lead</th>
          <th>Status</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {#each projects as p}
          <tr>
            <td>{p.name}</td>
            <td>{p.id}</td>
            <td>{p.owner}</td>
            <td>
              <span>{p.isLocked ? "Locked" : "Unlocked"}</span>
              {#if user && (user.role === "admin" || user.name === p.owner)}
                <button on:click={() => toggleLock(p.id)} style="margin-left: 0.5rem;">
                  {p.isLocked ? "Unlock" : "Lock"}
                </button>
              {/if}
            </td>
            <td><button on:click={() => openProject(p.id)}>Open</button></td>
          </tr>
        {/each}
      </tbody>
    </table>
    <a href="/project-delete">
      <button style="background-color: #dc2626; color: white; margin-top: 1rem;">
        Manage/Delete Projects
      </button>
    </a>
  </div>

  {#if showDialog}
    <div class="modal">
      <div class="modal-content">
        <h3>Create Project</h3>
        <button on:click={() => showDialog = false} style="float: right;">✖</button>
        <label>Project Name: <input type="text" bind:value={newProjectName} /></label>
        <label>Start Date: <input type="date" bind:value={startDate} /></label>
        <label>End Date: <input type="date" bind:value={endDate} /></label> <!-- ✅ Updated Input -->
        <label>Lead Analyst Initials: <input type="text" bind:value={leadAnalyst} /></label>
        <label>Description: <textarea bind:value={projectDescription}></textarea></label>
        <label>File Upload: <input type="file" multiple on:change={handleFileUpload} /></label>

        {#if uploadedFiles.length > 0}
          <ul>
            {#each uploadedFiles as file, i}
              <li>{file.name} <button on:click={() => removeFile(i)}>🗑️</button></li>
            {/each}
          </ul>
        {/if}

        <div style="display: flex; justify-content: space-between; margin-top: 1rem;">
          <button on:click={() => showDialog = false}>Cancel</button>
          <button on:click={createProject}>Create</button>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
	@media (prefers-color-scheme: dark) {
		tr,
		.header-bar {
			background: #1d282c;
		}
		p {
			color: white;
		}
		.modal-content {
			background: #243136;
		}
		.modal-content input,
		.modal-content textarea {
			background: #243136;
			color: white;
		}
	}
</style>
