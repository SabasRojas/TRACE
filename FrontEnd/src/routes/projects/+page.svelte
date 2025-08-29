<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';

  // Example data with additional fields:
  let projects = [
    {
      id: 1,
      name: 'Encrypted Communications Hub',
      lastEdit: 'Nov 4, 2024',
      leadAnalyst: 'S.I.',
      port: 49153
    },
    {
      id: 2,
      name: 'Military Drone Command Interface Scan',
      lastEdit: 'Nov 4, 2024',
      leadAnalyst: 'J.S.',
      port: 49154
    },
    {
      id: 3,
      name: 'Field Intelligence Data Platform',
      lastEdit: 'Nov 4, 2024',
      leadAnalyst: 'R.S.',
      port: 49155
    },
    {
      id: 4,
      name: 'Secure Satellite Control Panel Audit',
      lastEdit: 'Nov 4, 2024',
      leadAnalyst: 'L.T.',
      port: 49156
    }
  ];

  let role = '';
  let isLead = false;
  let openMenu: number | null = null; 

  // Retrieve the 'role' query param from the URL
  $: roleParam = $page.url.searchParams.get('role');

  onMount(() => {
    role = roleParam || 'analyst';
    isLead = (role === 'lead_analyst');
  });
  function runScan(projectId: number): void {
    goto(`/tools-dashboard`);
  }

  function toggleMenu(projectId: number): void {
    openMenu = (openMenu === projectId) ? null : projectId;
  }

  function lockProject(projectId: number): void {
    alert(`Lock Project clicked for project ID: ${projectId}`);
  }

  function unlockProject(projectId: number): void {
    alert(`Unlock Project clicked for project ID: ${projectId}`);
  }

  function createNewProject(): void {
    alert('Create New Project button clicked!');
  }
</script>

<main class="page-container">
  <!-- Main Content (Sidebar Removed) -->
  <div class="main-content">
    <!-- Header -->
    <header class="header">
      <h1>Project Selection</h1>
      {#if isLead}
        <button class="create-btn" on:click={createNewProject}>+ Create new</button>
      {/if}
    </header>

    <!-- Recent Projects -->
    <section class="recent-projects">
      <h2>Recent Projects</h2>
      <div class="recent-projects-cards">
        {#each projects.slice(0, 2) as proj}
          <div class="project-card">
            <h3>{proj.name}</h3>
          </div>
        {/each}
      </div>
    </section>

    <!-- All Projects -->
    <section class="all-projects">
      <h2>All Projects</h2>
      <table>
        <thead>
          <tr>
            <th>Project Name</th>
            <th>Last Edit</th>
            <th>Lead Analyst</th>
          </tr>
        </thead>
        <tbody>
          {#each projects as proj}
            <tr>
              <td>{proj.name}</td>
              <td>{proj.lastEdit}</td>
              <td>{proj.leadAnalyst}</td>
              <td class="actions-cell">
                <button class="run-scan-btn" on:click={() => runScan(proj.id)}>
                  Run Scan
                </button>
                {#if isLead}
                  <div class="dots-menu">
                    <button type="button" class="dots-icon" on:click={() => toggleMenu(proj.id)} aria-label="Toggle menu">
                      <span>...</span>
                    </button>
                    {#if openMenu === proj.id}
                      <div class="submenu">
                        <button on:click={() => lockProject(proj.id)}>
                          Lock Project
                        </button>
                        <button on:click={() => unlockProject(proj.id)}>
                          Unlock Project
                        </button>
                      </div>
                    {/if}
                  </div>
                {/if}
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </section>
  </div>
</main>

<style>
  /* Global Reset & Font */
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  /* PAGE CONTAINER - Adjusted to remove sidebar */
  .page-container {
    display: flex;
    min-height: 100vh;
  }

  /* MAIN CONTENT */
  .main-content {
    flex: 1;
    padding: 2rem;
    background-color: #fff;
  }

  /* HEADER */
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
  }

  .header h1 {
    font-size: 1.5rem;
  }

  .create-btn {
    background-color: #4ea8b2;
    color: #fff;
    border: none;
    padding: 0.6rem 1rem;
    border-radius: 4px;
    cursor: pointer;
  }
  .create-btn:hover {
    background-color: #3b8991;
  }

  /* RECENT PROJECTS */
  .recent-projects {
    margin-bottom: 2rem;
  }
  .recent-projects-cards {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
  }
  .project-card {
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 1rem;
    width: 220px;
    background-color: #fafafa;
  }
  .project-card h3 {
    margin-bottom: 0.5rem;
    font-size: 1rem;
  }

  /* ALL PROJECTS */
  .all-projects {
    margin-bottom: 2rem;
  }
  table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0 8px;
  }
  thead {
    background-color: #ffffff;
    font-size: 10pt;
    color: #63656c;
  }
  th, td {
    border: none;
    text-align: left;
    padding: 0.8rem;
  }
  tbody tr {
    background-color: #e1e1e1;
    border-radius: 12px;
  }
  .actions-cell {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    gap: 1rem;
    position: relative;
  }
  .run-scan-btn {
    background-color: #4ea8b2;
    color: #fff;
    border: none;
    padding: 0.4rem 0.6rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.85rem;
  }
  .run-scan-btn:hover {
    background-color: #3b8991;
  }

  /* DOTS MENU */
  .dots-menu {
    position: relative;
  }
  .dots-icon {
    cursor: pointer;
    padding: 0.4rem;
    border-radius: 4px;
    color: #666;
  }
  .dots-icon:hover {
    background-color: #e9e9e9;
  }
  .submenu {
    position: absolute;
    top: 2rem;
    right: 0;
    background: #fff;
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 0.4rem;
    display: flex;
    flex-direction: column;
    width: 120px;
    z-index: 10;
  }
  .submenu button {
    background: none;
    border: none;
    color: #333;
    text-align: left;
    padding: 0.4rem;
    font-size: 0.85rem;
    cursor: pointer;
    border-radius: 4px;
  }
  .submenu button:hover {
    background-color: #f5f5f5;
  }

  .dots-icon {
    border: none;
    background: transparent; /* or 'none' if you prefer */
    padding: 0.4rem; /* keep existing styling */
    border-radius: 4px;
    cursor: pointer;
    color: inherit; /* inherits the text/icon color */
  }

  .dots-icon:hover {
    background-color: #e9e9e9;
  }
</style>
