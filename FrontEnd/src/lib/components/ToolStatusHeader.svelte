<script>
    let props = $props()
    let activeStep = props.active
</script>

<div class="form-header">
    <h3>{activeStep[activeStep.length-1]}</h3>
    <div class="stepper">
        <div class="step {activeStep.includes('Configuration') ? 'active' : ''}">
            <div class="circle">{#if activeStep.includes('Configuration')}
                <img class="step-check" src="/fontawesome-free-6.7.2-desktop/svgs/regular/circle-check.svg" alt="Check circle" />
            {/if}
            </div>
            <span>Configuration</span>
        </div>
        <div class="line"></div>
        <div class="step {activeStep.includes('Running') ? 'active' : ''}">
            <div class="circle">
                {#if activeStep.includes('Running')}
                    <img class="step-check" src="/fontawesome-free-6.7.2-desktop/svgs/regular/circle-check.svg" alt="Check circle" />
                {/if}
            </div>
            <span>Running</span>
        </div>
        <div class="line"></div>
        <div class="step {activeStep.includes('Results') ? 'active' : ''}">
            <div class="circle">
                {#if activeStep.includes('Results')}
                    <img class="step-check" src="/fontawesome-free-6.7.2-desktop/svgs/regular/circle-check.svg" alt="Check circle" />
                {/if}
            </div>
            <span>Results</span>
        </div>
    </div>
</div>

<style>
    .form-header {
        display: flex;
        justify-content: space-between;
        width: 100%;
        max-width: 700px;
        margin-bottom: 0.5rem;
        max-height: 100vh;
    }

    .stepper {
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }

    .step {
        display: flex;
        flex-direction: column;
        align-items: center;
        font-size: 0.75rem;
        color: #999;
    }

    .step.active {
        color: #4aa6b0;
        font-weight: bold;
    }

    .circle {
        width: 12px;
        height: 12px;
        border: 2px solid #ccc;
        border-radius: 50%;
        background: white;
        display: flex;
    }

    .step.active .circle {
        border-color: #4aa6b0;
        background: #4aa6b0;
    }

    .line {
        width: 30px;
        height: 2px;
        background: #ccc;
        margin: 0 4px;
        align-self: center;
    }

    .step-check{
        width: 12px;
        height: 12px;
    }
    @media (prefers-color-scheme: dark) {
        .circle{
            background: #020101;
        }
        .line{
            background: #020101;
        }
    }
</style>