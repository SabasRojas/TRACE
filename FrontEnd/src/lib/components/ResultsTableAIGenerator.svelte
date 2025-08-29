<script>
// @ts-nocheck

let {credentials = []} = $props();
  </script>
  
  <div class="table-wrapper">
    <table class="results-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Usernames</th>
          <th>Passwords</th>
        </tr>
      </thead>
      <tbody>
        {#each credentials as row, index}
          <tr>
            <td>{index + 1}</td>
            <td>{row[0]}</td>
            <td>{row[1]}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
  
  <style>
    .table-wrapper {
      overflow-x: auto;
      padding: 0 2rem;
      scrollbar-width: none;  /* Firefox */
      -ms-overflow-style: none;
      width: 100%;
    }
    .table-wrapper::-webkit-scrollbar {
      display: none;  /* Chrome, Safari */
    }
    .results-table {
      width: 100%;
      border-collapse: collapse;
      margin: auto;
    }
  
    th, td {
      text-align: left;
      padding: 0.5rem 1rem;
      font-size: 0.8rem;
    }
  
    thead {
      background-color: rgba(74, 166, 176, 0.6);
    }

    tbody tr:nth-child(even) {
      background-color: #f0f0f1;
    }

    tbody tr:nth-child(odd) {
      background-color: #e0dfe0;
    }
    @media (prefers-color-scheme: dark) {
      tbody tr:nth-child(even) {
        background-color: #1a2024;
      }
      tbody tr:nth-child(odd) {
        background-color:#171d21;
      }
    }
  </style>
  