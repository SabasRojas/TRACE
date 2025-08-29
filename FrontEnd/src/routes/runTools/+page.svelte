<script lang="ts">
import { responseStore } from '$lib/stores/responseStore.js';
import { goto } from '$app/navigation';
import { getApiBase } from '../../config';

  // Adjust the API base URL if necessary
  //const API_BASE_URL = 'http://localhost:8000';

  // Variables to hold the user-entered URLs
  let urlInput = '';
  let bruteInput = '';

  async function runCrawler() {
    if (!urlInput) {
      alert("Please enter a URL to crawl.");
      return;
    }
    try {
      const res = await fetch(
        `${getApiBase()}/tools/run-crawler?url=${encodeURIComponent(urlInput)}`, 
        {
          method: 'POST'
        }
      );
      if (!res.ok) {
        console.error('Error calling crawler endpoint:', res.status, res.statusText);
        alert('Failed to run crawler. Check console for details.');
        return;
      }
      const data = await res.json();
      console.log('Crawler response:', data);
      if (data.success) {
        goto(`/webtree?projectId=1`);
      } else {
        alert('Crawler encountered an error: ' + data.error);
      }
    } catch (error) {
      console.error('Network or fetch error:', error);
      alert('Failed to run crawler. Check console for error details.');
    }
  }

  async function runBruteforcer() {
    if (!bruteInput) {
      alert("Please enter a URL to bruteforce.");
      return;
    }
    // Placeholder for your actual brute forcing logic
    try {
      const res = await fetch(
        `${getApiBase()}/tools/run-bruteforce?url=${encodeURIComponent(bruteInput)}`, 
        {
          method: 'POST'
        }
      );
      if (!res.ok) {
        console.error('Error calling bruteforce endpoint:', res.status, res.statusText);
        alert('Failed to run brute forcer. Check console for details.');
        return;
      }
      const data = await res.json();
      console.log('Brute forcer response:', data);
      if (data.success) {
        alert('Brute forcer executed successfully. Check server console for details.');
      } else {
        alert('Brute forcer encountered an error: ' + data.error);
      }
    } catch (error) {
      console.error('Network or fetch error:', error);
      alert('Failed to run brute forcer. Check console for error details.');
    }
  }

  async function runHttpTester() {
    try {
      const response = await fetch('https://httpbin.org/get');
      const data = await response.json();
      console.log('HTTP Tester Response:', data);
      
      // Update the response store with the fetched data
      responseStore.set(data);
      
      // Redirect to the Response Manager page (assumes route is '/response-manager')
      goto('/tools/HTTPRequests');
      } catch (error) {
      console.error('Error executing HTTP Tester:', error);
      alert('Error executing HTTP Tester.');
      }
  }
</script>

<style>
  main {
    max-width: 800px;
    margin: 2rem auto;
    padding: 1rem;
    border-radius: 8px;
    background-color: #fff;
    font-family: Arial, sans-serif;
    color: #333;
  }

  h1 {
    margin-bottom: 1.5rem;
    font-size: 1.75rem;
  }

  .tool-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border: 1px solid #ddd;
    border-radius: 6px;
    padding: 1rem;
    background-color: #fafafa;
    margin-bottom: 1rem;
    position: relative;
  }

  /* Left side: status icon + tool name + progress text */
  .tool-left {
    display: flex;
    align-items: center;
  }
  .status-icon {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    margin-right: 1rem;
  }
  /* Example status-icon color states */
  .completed {
    background-color: #28a745; /* Green */
  }
  .error {
    background-color: #dc3545; /* Red */
  }
  .scanning {
    background-color: #ffc107; /* Yellow */
  }
  .ready {
    background-color: #6c757d; /* Gray */
  }

  .tool-info {
    display: flex;
    flex-direction: column;
  }
  .tool-name {
    font-weight: bold;
    margin-bottom: 0.25rem;
  }
  .tool-progress {
    font-size: 0.9rem;
    color: #555;
  }

  /* Right side: Info/Set Up buttons and optional inputs */
  .tool-right {
    display: flex;
    align-items: center;
  }

  .tool-right button {
    margin-left: 0.5rem;
  }

  /* Setup input + button container */
  .setup-section {
    display: flex;
    align-items: center;
    margin-left: 0.5rem;
  }

  .setup-section input {
    width: 180px;
    padding: 0.4rem 0.5rem;
    font-size: 0.9rem;
    margin-right: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 4px;
  }

  button {
    padding: 0.5rem 0.75rem;
    background-color: #4ea8b2;
    color: #fff;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
  }

  button:hover {
    background-color: #4ea8b2;
  }

  /* Example tooltip styling for the crawler row */
  .tooltip {
    display: none;
    position: absolute;
    left: 60px;
    top: 50px;
    background-color: #333;
    color: #fff;
    padding: 0.6rem;
    border-radius: 4px;
    font-size: 0.8rem;
    max-width: 250px;
  }

  .tool-row:hover .tooltip {
    display: block;
  }
</style>

<main>
  <h1>Tools</h1>

  <!-- HTTP Tester row -->
  <div class="tool-row">
    <div class="tool-left">
      <div class="status-icon completed"></div>
      <div class="tool-info">
        <div class="tool-name">HTTP Tester</div>
      </div>
    </div>
    <div class="tool-right">
      <button>Info</button>
      <button on:click={runHttpTester}>Set Up</button>
    </div>
  </div>

  <!-- SQL Injection row -->
  <div class="tool-row">
    <div class="tool-left">
      <div class="status-icon error"></div>
      <div class="tool-info">
        <div class="tool-name">SQL Injection</div>
      </div>
    </div>
    <div class="tool-right">
      <button>Info</button>
      <a href="/tools/sql-injection"><button>Set Up</button></a>
    </div>
  </div>

  <!-- Parameter Fuzzing row -->
  <div class="tool-row">
    <div class="tool-left">
      <div class="status-icon scanning"></div>
      <div class="tool-info">
        <div class="tool-name">Parameter Fuzzing</div>
      </div>
    </div>
    <div class="tool-right">
      <button>Info</button>
      <button>Set Up</button>
    </div>
  </div>

  <!-- Brute Force Tester row -->
  <div class="tool-row">
    <div class="tool-left">
      <div class="status-icon ready"></div>
      <div class="tool-info">
        <div class="tool-name">Brute Force Tester</div>
      </div>
    </div>
    <div class="tool-right">
      <button>Info</button>
      <div class="setup-section">
        <input
          type="text"
          placeholder="Enter URL to bruteforce"
          bind:value={bruteInput}
        />
        <button on:click={runBruteforcer}>Set Up</button>
      </div>
    </div>
  </div>

  <!-- Intruder row -->
  <div class="tool-row">
    <div class="tool-left">
      <div class="status-icon ready"></div>
      <div class="tool-info">
        <div class="tool-name">Intruder</div>
      
      </div>
    </div>
    <div class="tool-right">
      <button>Info</button>
      <button>Set Up</button>
    </div>
  </div>

  <!-- DB Enumerator row -->
  <div class="tool-row">
    <div class="tool-left">
      <div class="status-icon ready"></div>
      <div class="tool-info">
        <div class="tool-name">DB Enumerator</div>
        <div class="tooltip">
          Enumerates the structure and metadata of the backend database.
        </div>
      </div>
    </div>
    <div class="tool-right">
      <button>Info</button>
      <button on:click={() => goto("/tools/dbEnumerator")}>Set Up</button>
    </div>
  </div>


  <!-- Crawler row -->
  <div class="tool-row">
    <div class="tool-left">
      <div class="status-icon ready"></div>
      <div class="tool-info">
        <div class="tool-name">Crawler</div>

        <!-- Tooltip example -->
        <div class="tooltip">
          Scans the application to map out directories, endpoints, and publicly 
          accessible resources.
        </div>
      </div>
    </div>
    <div class="tool-right">
      <button>Info</button>
      <div class="setup-section">
        <input
          type="text"
          placeholder="Enter URL to crawl"
          bind:value={urlInput}
        />
        <button on:click={runCrawler}>Set Up</button>
      </div>
    </div>
  </div>
</main>
