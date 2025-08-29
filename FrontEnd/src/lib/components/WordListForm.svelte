<script>
    // @ts-nocheck
    
        import { goto } from "$app/navigation";
        import { page } from "$app/state";
        import ToolStatusHeader from "$lib/components/ToolStatusHeader.svelte";
    import {onMount} from "svelte";
    
        let wordlistConfig = { file: null };
        let usernameOptions = {
            characters: false,
            numbers: true,
            symbols: true,
            length: 12,
        };
        let passwordOptions = {
            characters: true,
            numbers: false,
            symbols: false,
            length: 12,
        };
    
        let fileName = "";
        let errors = {
            file: "",
            plength: "",
            ulength: ""
        };
        let credentialAmount = 12
    let backendUrl
        function validate() {
            errors = {};
            if (!wordlistConfig.file)
                errors.file = "Please upload a wordlist file.";
            if (passwordOptions.length < 10)
                errors.plength = "Invalid password length";
            if (usernameOptions.length < 5)
                errors.ulength = "Invalid username length";
            if (credentialAmount < 1)
                errors.amount = "Credential amount must be at least 1.";

        }
    onMount(()=>{
        backendUrl = sessionStorage.getItem("backendUrl") || "http://localhost";
    })
    function handleFileUpload(event) {
        const file = event.target.files[0];
        fileName = file.name;
        const reader = new FileReader();
        reader.onload = () => {
            wordlistConfig.file = reader.result.split(/\r?\n/).filter(Boolean);
            validate();
        };
        reader.readAsText(file);
    }
    async function submitWordlist() {
        validate();
        if (Object.keys(errors).length > 0) return;

        const projectID = page.params.id;

        const payload = {
            passchars: passwordOptions.characters,
            userchars: usernameOptions.characters,
            passnums: passwordOptions.numbers,
            usernums: usernameOptions.numbers,
            passsyms: passwordOptions.symbols,
            usersyms: usernameOptions.symbols,
            userlen: usernameOptions.length,
            passle: passwordOptions.length,
            credentialAmount: credentialAmount,
            wordlist: wordlistConfig.file
        };

        try {
            const response = await fetch(`${backendUrl}:8000/${projectID}/webscraper`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error("Server error:", errorData.detail);
                return;
            }
            await goto(`/project/${projectID}/tools/wordlist/results`);
        } catch (error) {
            console.error("Fetch error:", error);
        }
    }
</script>
    
    <div class="container">
        <form class="wordlist-form" on:submit|preventDefault={submitWordlist}>
            <input type="file" accept=".txt" on:change={handleFileUpload} />
            {#if errors.file}<span class="error-msg">{errors.file}</span>{/if}
    
            <div style="display: flex; gap: 20px;">
                <!-- Username -->
                <div class="box" style="flex: 1;">
                    <h4>Username</h4>
                    {#each Object.keys(usernameOptions) as key (key)}
                        {#if key !== "length"}
                            <div style="display: flex; justify-content: space-between; align-items: center; margin: 10px 0;">
                                <span>{key.charAt(0).toUpperCase() + key.slice(1)}</span>
                                <button
                                    type="button"
                                    class="toggle-container {usernameOptions[key] ? 'active' : ''}"
                                    on:click={() => (usernameOptions[key] = !usernameOptions[key])}
                                    aria-label="Toggle {key} for username"
                                >
                                    <div class="toggle"></div>
                                </button>
                            </div>
                        {/if}
                    {/each}
                    <label for="username-length">Length</label>
                    <input type="number" bind:value={usernameOptions.length} class="input-field" min="1" />
                    {#if errors.ulength}<span class="error-msg">{errors.ulength}</span>{/if}
                </div>
    
                <!-- Password -->
                <div class="box" style="flex: 1;">
                    <h4>Password</h4>
                    {#each Object.keys(passwordOptions) as key (key)}
                        {#if key !== "length"}
                            <div style="display: flex; justify-content: space-between; align-items: center; margin: 10px 0;">
                                <span>{key.charAt(0).toUpperCase() + key.slice(1)}</span>
                                <button
                                    type="button"
                                    class="toggle-container {passwordOptions[key] ? 'active' : ''}"
                                    on:click={() => (passwordOptions[key] = !passwordOptions[key])}
                                    aria-label="Toggle {key} for username"
                                >
                                    <div class="toggle"></div>
                                </button>
                            </div>
                        {/if}
                    {/each}
                    <label for="password-length">Length</label>
                    <input type="number" bind:value={passwordOptions.length} class="input-field" min="1" />
                    {#if errors.plength}<span class="error-msg">{errors.plength}</span>{/if}
                </div>
                <div class="box" style="flex: 1;">
                    <h4>Number of Credentials</h4>
                    <input type="number" bind:value={credentialAmount} class="input-field" min="1" />
                    {#if errors.amount}<span class="error-msg">{errors.amount}</span>{/if}
                </div>

            </div>
        </form>
    
        <div class="bottom-left">
            <button type="button" on:click={submitWordlist} class="submit">Generate</button>
        </div>
    </div>
    
    <style>
        .bottom-left {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
        }
    
        .wordlist-form {
            display: flex;
            flex-direction: column;
            gap: 1rem;
            width: 60%;
            max-width: 700px;
            margin: auto;
        }
    
        input,
        textarea {
            padding: 0.5rem;
            border: 1px solid #ccc;
            border-radius: 6px;
            font-size: 1rem;
        }
    
        .error-msg {
            color: red;
            font-size: 0.9rem;
        }
    
        button {
            background: #90cdd2;
            border: none;
            padding: 0.75rem;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
        }
    
        .container {
            display: flex;
            height: 100vh;
            flex: 1;
            padding: 20px;
        }

        input[type="file"] {
             display: block;
             width: 100%;
         }
    
        .box {
            background: white;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 15px;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
        }
    
        .toggle-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            cursor: pointer;
            background: #ddd;
            width: 40px;
            height: 20px;
            border-radius: 20px;
            padding: 3px;
            position: relative;
        }
    
        .toggle {
            width: 16px;
            height: 16px;
            background: white;
            border-radius: 50%;
            transition: 0.3s;
        }
    
        .toggle-container.active {
            background: #64b5f6;
        }
    
        .toggle-container.active .toggle {
            transform: translateX(20px);
        }
    
        .input-field {
            width: 100%;
            padding: 5px;
            border: 1px solid #ccc;
            border-radius: 4px;
            margin-top: 5px;
        }
        input[type="file"]::-webkit-file-upload-button {
            background: #90cdd2;
            border: none;
            padding: 0.75rem;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
        }
        @media (prefers-color-scheme: dark) {
            .input-field {
                background: #1f2937;
                color: #bebebe;
            }
            .box{
                background: #1f2937;
            }
            .toggle{
                background: #1a2024;
            }
        }
    </style>
