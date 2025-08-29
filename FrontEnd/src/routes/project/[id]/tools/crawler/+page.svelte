<script>
    import CrawlerForm from "$lib/components/CrawlerForm.svelte";
</script>

<h1 class="page-header">Crawler</h1>
<div class="page-content">
    <CrawlerForm></CrawlerForm>
</div>
<style>
    .page-header {
        margin-left: 2.5vw;
        margin-bottom: 0;
    }
    .page-content{
        display: flex;
        justify-content: center;
        flex-direction: column;
        align-items: center;
        max-height: 87vh;
    }

</style>