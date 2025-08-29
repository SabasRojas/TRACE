<script>
    import { page } from '$app/state';
</script>

<div class="error-container">
    <div class="status-container">
        <p class="status">{page.status}</p>
        <p class="subtext">Page not found</p>
    </div>

    <div class="divider"></div>

    <div class="message-container">
        {#if page.status === 404}
            <p class="error-message">The page you’re looking for doesn’t exist.</p>
        {:else}
            <p class="error-message">{page.error?.message ?? 'An unexpected error occurred.'}</p>
        {/if}
        <a class="home-link" href="/">Go back home</a>
    </div>
</div>

<style>
    .error-container {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 90vh;
        padding: 2rem;
        background-color: #f9f9f9;
        color: #333;
    }

    .status-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 0 3rem;
    }

    .status {
        font-size: 15rem;
        font-weight: bold;
        margin: 0;
    }

    .subtext {
        font-size: 1.5rem;
        margin-top: 1rem;
        color: #666;
    }

    .divider {
        height: 60%;
        width: 2px;
        background-color: #ddd;
        margin: 0 2rem;
    }

    .message-container {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        max-width: 300px;
    }

    .error-message {
        font-size: 1.25rem;
        line-height: 1.5;
    }

    .home-link {
        color: #4aa6b0;
        text-decoration: none;
        font-weight: 500;
        transition: color 0.3s ease;
    }

    .home-link:hover {
        color: #ffffff;
    }
    @media (prefers-color-scheme: dark){
        .error-container{
            background:#12181b;
            color: #e0e0e0;
        }
        .subtext {
            color: #bebebe;
        }
        .divider{
            background: #4aa6b0;
        }
    }
</style>
