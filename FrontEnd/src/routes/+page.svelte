<script>
  import { goto } from '$app/navigation';
  import BackgroundLines from "$lib/components/BackgroundLines.svelte";
  import {slide} from 'svelte/transition'
  import {onMount} from "svelte";
  import LoadingSpinner from "$lib/components/LoadingSpinner.svelte";
  let startClicked = false;
  let buttonDisabled = $state(true)
  function goToRoleSelector() {
      goto('./role-selector');
  }
  onMount(()=>{
    let backendUrl = ""
    backendUrl = sessionStorage.getItem("backendUrl") || "http://localhost";
    console.log(backendUrl)
    buttonDisabled = true
    fetch(`${backendUrl}:8000/status`)
            .then(res => {
              if (!res.ok) throw new Error();

              buttonDisabled = false
              sessionStorage.setItem("backendUrl", backendUrl);
              currState = "Backend found. Ready to start TRACE"
            })
            .catch(() => {
              currState = "Could not connect to localhost. Please go to settings and adjust backend IP address:";
              sessionStorage.clear()
            });
  })
  let currState = $state("Attempting connection to backend");
</script>

<style>
  /* Basic Reset + Global Font */
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  /* Overall page container */
  .page {
    position: relative;
    height: 100vh;
    display: flex;
    flex-direction: column;
  }

  /* Top Navigation Bar */
  .top-nav {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    padding: 1rem 2rem;
    background: transparent;
  }

  .top-nav a {
    margin-left: 1.5rem;
    text-decoration: none;
    color: #333;
    font-weight: 500;
  }

  /* Hero Section */
  .hero {
    flex: 1;
    position: relative;
    padding: 3rem 2rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    overflow: hidden;
  }

  .hero h1 {
    font-size: 3rem;
    margin-bottom: 1rem;
    font-weight: bold;
  }

  .hero p {
    max-width: 600px;
    font-size: 1rem;
    color: #555;
    margin-bottom: 2rem;
    line-height: 1.5;
  }

  .hero button {
    background-color: #4ea8b2; /* START button color */
    color: #fff;
    border: none;
    padding: 0.8rem 1.5rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
  }

  .hero button:hover{
    background-color: #3b8991;
  }
   .loader {
     border: 4px solid #f3f3f3;
     border-top: 4px solid #4aa6b0;
     border-radius: 50%;
     width: 40px;
     height: 40px;
     animation: spin 1s linear infinite;
     margin: 20px auto;
   }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  @media (prefers-color-scheme: dark){
    .hero p, .top-nav a{
      color: #bebebe;
    }
  }
</style>

<div class="page">
  <BackgroundLines />
  <!-- Top Navigation -->
  <nav class="top-nav">
    <a href="/config">Settings</a>
  </nav>

  <!-- Hero Section -->
  <section class="hero" transition:slide={{duration:1500}}>
    <h1>Elevate Your Security Strategy with TRACE</h1>
    <p>
      A Cybersecurity Platform to Protect Your Digital Assets. Detect Vulnerabilities,
      Strengthen Defense, and Secure Your Network Seamlessly. Gain Real-Time Insights
      and Proactive Protection.
    </p>
    <div class="button-container">
      {#if buttonDisabled}
        <p>{currState}</p>
        <div class="loader">
    </div>
        {:else}
    <button onclick={goToRoleSelector}>START</button>
      {/if}
    </div>
  </section>
</div>