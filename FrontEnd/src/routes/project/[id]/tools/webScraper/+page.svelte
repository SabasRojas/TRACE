<script>
    import {onMount} from "svelte";

    let credentials = $state()
    onMount(async () => {
        let backendUrl = sessionStorage.getItem("backendUrl") || "http://localhost";
        try {
            const response = await fetch(`${backendUrl}:8000/webscraper`);
            const data = await response.json();
            if (data.error) {
                console.error("Error:", data.error);
            } else {
                credentials = data;
                console.log(credentials)
            }
        } catch (err) {
            console.error("Failed to fetch web scraper data:", err);
        }
    });
</script>
<div>
    {#key credentials}
    <ul>
    {#each credentials as cred}
         <li>
             {cred}
         </li>
        {/each}
    </ul>
        {/key}
</div>