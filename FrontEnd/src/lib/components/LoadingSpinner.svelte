<div class="loading-spinner-container">
    <div class="loading-spinner" aria-label="loading spinner"></div>
</div>
<style>
    .loading-spinner-container{
        height: 100%;
        width: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .loading-spinner{
        position: absolute;
        border: 16px solid #ffffff;
        border-top: 16px solid #4aa6b0;
        border-radius: 50%;
        width: 120px;
        height: 120px;

        animation: spin 2s linear infinite;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
</style>