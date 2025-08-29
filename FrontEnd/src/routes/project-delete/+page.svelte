<script lang="ts">
  import { onMount } from "svelte";
  import { currentUser } from "$lib/stores/user";
  import { get } from "svelte/store";
  import { goto } from "$app/navigation";

  let projects: any[] = [];
  let message: string = "";
  let membersByProject: Record<string, { id: string; name: string }[]> = {};
  let backendUrl: string;

  // Initialize backend URL and load projects
  onMount(() => {
    backendUrl = sessionStorage.getItem("backendUrl") || "http://localhost";
    loadProjects();
  });

  // Fetch all projects, then their members
  async function loadProjects() {
    try {
      const res = await fetch(`${backendUrl}:8000/project`);
      const data = await res.json();
      if (Array.isArray(data)) {
        projects = data;
        await Promise.all(projects.map(p => loadMembers(p.id)));
      }
    } catch (err) {
      console.error(err);
      message = "❌ Failed to fetch projects.";
    }
  }

  // Fetch members for a single project
  async function loadMembers(projectId: string) {
    try {
      const res = await fetch(`${backendUrl}:8000/project/${projectId}/members`);
      membersByProject[projectId] = res.ok ? await res.json() : [];
    } catch (err) {
      console.error(`Error loading members for ${projectId}:`, err);
      membersByProject[projectId] = [];
    }
  }

  // Add an analyst to a project (owner only)
  async function addMember(projectId: string, initials: string) {
    if (!initials) return;
    const caller = get(currentUser)?.name;
    try {
      const url = `${backendUrl}:8000/project/${projectId}/add_member` +
          `?user_initials=${encodeURIComponent(initials)}` +
          `&caller_initials=${encodeURIComponent(caller)}`;
      const res = await fetch(url, { method: "POST" });
      const payload = await res.json().catch(() => ({}));
      if (res.ok) {
        await loadMembers(projectId);
        message = `✅ Added ${initials} to ${projectId}`;
      } else {
        console.error("AddMember failed:", payload);
        message = `❌ ${payload.detail || JSON.stringify(payload)}`;
      }
    } catch (err) {
      console.error(err);
      message = "❌ Error adding member.";
    }
  }

  // Remove an analyst from a project (owner only)
  async function removeMember(projectId: string, initials: string) {
    try {
      const url = `${backendUrl}:8000/project/${projectId}/remove_member` +
    `?user_initials=${encodeURIComponent(initials)}`;

      const res = await fetch(url, { method: "DELETE" });
      if (res.ok) {
        await loadMembers(projectId);
        message = `✅ Removed ${initials} from ${projectId}`;
      } else {
        const err = await res.json().catch(() => ({}));
        message = `❌ ${err.detail || res.statusText}`;
      }
    } catch (err) {
      console.error(err);
      message = "❌ Error removing member.";
    }
  }

  // Delete a project (owner only)
  async function deleteProject(id: string) {
    const user = get(currentUser);
    if (!user) {
      message = "❌ You must be logged in to delete a project.";
      return;
    }
    if (!confirm(`Delete project "${id}" permanently?`)) return;
    try {
      const url =
        `${backendUrl}:8000/project-manager/${id}/delete` +
        `?initials=${encodeURIComponent(user.name)}`;
      const res = await fetch(url, { method: "DELETE" });
      const data = await res.json().catch(() => ({}));
      if (res.ok && data.message) {
        message = `✅ ${data.message}`;
        projects = projects.filter(p => p.id !== id);
      } else {
        message = `❌ ${data.detail || 'Failed to delete project.'}`;
      }
    } catch (err) {
      console.error(err);
      message = "❌ Error deleting project.";
    }
  }

  function goBack() {
    goto("/project");
  }
</script>

<style>
  .project-list { padding: 2rem; }
  .project-card {
    padding: 1rem;
    background: var(--card-bg, #f5f5f5);
    border-radius: 0.5rem;
    margin-bottom: 1rem;
  }
  .members { margin-top: 0.5rem; }
  .members li { display: flex; align-items: center; }
  .members button { margin-left: 0.5rem; }

  .add-member {
    display: flex;
    align-items: center;
    margin-top: 0.75rem;
    gap: 0.5rem;
  }
  .add-member input {
    flex: 1;
    padding: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 0.3rem;
    font-size: 0.9rem;
  }
  .add-member button {
    padding: 0.5rem 0.75rem;
    border-radius: 0.3rem;
    border: none;
    background-color: #4ea8b2;
    color: #fff;
    cursor: pointer;
    font-size: 0.9rem;
  }
  .add-member button:hover {
    background-color: #407d99;
  }

  button.delete {
    background-color: #dc2626;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 0.3rem;
    cursor: pointer;
    margin-top: 0.75rem;
  }
  button.delete:hover { background-color: #b91c1c; }

  .message { margin: 1rem 0; font-weight: bold; }

  @media (prefers-color-scheme: dark) {
    .project-card { background: #243136; color: #e0e0e0; }
  }
</style>

<div class="project-list">
  <h1>Manage / Delete Projects</h1>
  <button on:click={goBack} style="margin-bottom:1rem;">⬅️ Back to Projects</button>

  {#if message}
    <div class="message">{message}</div>
  {/if}

  {#each projects as project}
    <div class="project-card">
      <h2>{project.name} <small>({project.id})</small></h2>
      <p>Owner: {project.owner}</p>

      <!-- Current analysts -->
      <ul class="members">
        {#each membersByProject[project.id] ?? [] as m}
          <li>
            {m.name}
            {#if $currentUser.name === project.owner}
              <button on:click={() => removeMember(project.id, m.name)}>Remove</button>
            {/if}
          </li>
        {/each}
        {#if (membersByProject[project.id] ?? []).length === 0}
          <li><em>No analysts assigned.</em></li>
        {/if}
      </ul>

      <!-- Add analyst (owner only) -->
      {#if $currentUser.name === project.owner}
        <div class="add-member">
          <input
            type="text"
            placeholder="Analyst Initials"
            bind:this={project[`input_${project.id}`] as HTMLInputElement}
          />
          <button on:click={() => addMember(project.id, (project[`input_${project.id}`] as HTMLInputElement).value)}>
            Add Analyst
          </button>
        </div>
      {/if}

      <!-- Delete project (owner only) -->
      {#if $currentUser.name === project.owner}
        <button class="delete" on:click={() => deleteProject(project.id)}>
          Delete Project
        </button>
      {/if}
    </div>
  {/each}
</div>
