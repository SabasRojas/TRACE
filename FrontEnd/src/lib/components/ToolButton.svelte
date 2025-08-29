<script>
    let props = $props()
    let content = props.content
    let callback = props.callback
</script>
<button  onclick={callback}>
    {@html content}
</button>
<style>
    button {
        background: rgba(74, 166, 176, 0.6);
        border-radius: 5px;
        margin: 7px;
        padding: 0.7em;
        width: 10em;
        border: none;
        font-size: 0.8em;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
    }
    button:hover{
        background: #4aa6b0;
        cursor: pointer;
    }
</style>