<script>
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";

    let backendUrl = $state();
    let currBackendIP = $state();
    let connected = $state(false);
    let errorMessage = $state("");

    let saveConfig = async (event) => {
        event.preventDefault();
        const data = new FormData(event.currentTarget);
        const inputValue = data.get("backendUrl");

        if (!inputValue) {
            errorMessage = "Please enter a backend IP address.";
            return;
        }

        const inputUrl = String(inputValue);

        if (!inputUrl.startsWith("http://") && !inputUrl.startsWith("https://")) {
            errorMessage = "Please include 'http://' or 'https://' when adding your IP.";
            return;
        }

        errorMessage = "";
        backendUrl = inputUrl;
        sessionStorage.setItem("backendUrl", backendUrl);
        await goto('/');
    };

    onMount(async () => {
        try {
            backendUrl = sessionStorage.getItem("backendUrl") || "http://localhost";
            const res = await fetch(`${backendUrl}:8000/ip`);
            if (!res.ok) throw new Error();
            connected = true;
            const ip = await res.json();
            currBackendIP = ip.ip;
        } catch {
            connected = false;
            currBackendIP = "Not Found";
        }
    });
</script>
<div class="page-wrapper">
<div class="config-container">
<form class="crawler-form" onsubmit={saveConfig}>
    {#if connected}
        <div class="form-group">
            <label for="TargetURL">Current Backend URL (Use this to connect with another computer)</label>
            <input type="text" id="TargetURL" name="TargetURL" value={currBackendIP} disabled />
        </div>
    {/if}

    <div class="form-group">
        <label for="backendUrl">Backend URL</label>
        <input type="text" id="backendUrl" name="backendUrl" placeholder="http://localhost" required />
        {#if errorMessage}
            <div class="error-message">{errorMessage}</div>
        {/if}
    </div>

    <button type="submit">Save</button>
</form>
</div>
</div>
<style>
    .page-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 90vh;
        background-color: #f4f4f4;
        padding: 2rem;
    }

    .config-container {
        background-color: #fff;
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        max-width: 500px;
        width: 100%;
    }

    .crawler-form {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }

    .form-group {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    label {
        font-weight: 600;
        color: #333;
        font-size: 1rem;
    }

    input[type="text"] {
        padding: 0.75rem 1rem;
        border: 1px solid #ccc;
        border-radius: 0.5rem;
        font-size: 1rem;
        transition: border-color 0.3s ease;
    }

    input[type="text"]:focus {
        border-color: #45a0a7;
        outline: none;
    }

    button {
        padding: 0.75rem;
        background-color: #93dbe9;
        color: #fff;
        font-weight: 600;
        border: none;
        border-radius: 0.5rem;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    .error-message {
        color: #ef4444;
        font-size: 0.9rem;
        margin-top: 0.25rem;
        background: #fee2e2;
        padding: 0.5rem 0.75rem;
        border: 1px solid #fca5a5;
        border-radius: 0.375rem;
    }


    button[type="submit"]:hover {
        background-color: #5cc3d3;
    }
    @media (prefers-color-scheme: dark) {
        .page-wrapper {
            background: #1f2937;
            color: #bebebe;
        }
        .config-container{
            background: #12181b;
        }
        input {
            background: #020101;
            color: #fff;
        }
        label{
            color: #e5e7eb;
        }
    }
</style>

