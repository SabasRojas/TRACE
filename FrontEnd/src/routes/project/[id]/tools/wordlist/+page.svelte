<script>
    // @ts-ignore
    import WordlistForm from "$lib/components/WordListForm.svelte";
</script>

<h1 class="page-header">AI Generator</h1>
<div class="page-content">
    <WordlistForm />
</div>

<style>
    .page-header {
        margin-left: 2.5vw;
    }

    .page-content {
        display: flex;
        justify-content: center;
        flex-direction: column;
        align-items: center;
    }
</style>