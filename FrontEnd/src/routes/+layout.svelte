<script>
    let { children } = $props();
</script>

<main>
{@render children?.()}
</main>

<style>
    :root  {
        font-family: 'Poppins', sans-serif;
    }
    main{
        margin-top: 0;
        background: #f1f1f1;
        min-height: 100vh;
        box-sizing: border-box;
        padding: 1px;
    }
    :global(body){
        margin: 0;
    }
    @media (prefers-color-scheme: dark){
        main{
            background:#12181b;
            color: #e0e0e0;
        }
    }
</style>
