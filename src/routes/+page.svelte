<script>
import AnalogStick from '$lib/AnalogStick.svelte'
import DepthCapture from '$lib/DepthCapture.svelte'
import { onMount, onDestroy } from 'svelte'

let jsonData = null;
let loading = false;
let error = null;
let pollInterval = 5000; // 5 seconds




const fetchData = async () => {
    try {
        loading = true;
        error = null;
        const response = await fetch('/api/update');
        if (!response.ok) throw new Error('Failed to fetch');
        jsonData = await response.json();
    } catch (err) {
        error = err.message;
        console.error('Fetch error:', err);
    } finally {
        loading = false;
    }
};

// Setup polling
let intervalId;
onMount(() => {
    fetchData(); // Initial fetch
    intervalId = setInterval(fetchData, pollInterval);
    
    // Cleanup on component destroy
    return () => clearInterval(intervalId);
});

// Optional: Handle component destruction
onDestroy(() => {
    clearInterval(intervalId);
});

const sendCommand = async (command) => {
  let speed = Math.sqrt(command.y ** 2 + command.x ** 2);
  let angle = Math.atan2(command.x, command.y) * 180 / Math.PI;
  if (Math.abs(angle) > 90) {
    angle = (angle % 90) - (Math.sign(angle) * 90)
    speed *= -1
  }
  response = await fetch('/api/command', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      speed: speed,
      angle: angle
    })
  })
}

</script>

<div class="container">
    <!-- Left Panels -->
    <div class="panel left-top">
        <div class="image-holder">
            <img src="api/stream" alt="📷 Camera feed">
        </div>
    </div>
    

    <!-- Right Panels -->
    <div class="panel right-top">
        <div class="stick-container">
            <AnalogStick 
                containerRadius={400} 
                stickRadius={100} 
                on:move={({ detail }) => sendCommand(detail)}
            />
        </div>
    </div>

    <div class="panel left-bottom">
        <div class="image-holder">
            <DepthCapture />
        </div>
    </div>
    
    <div class="panel right-bottom">
        <table>
            <thead>
                <tr>
                    <th style:text-align="center">Key</th>
                    <th style:text-align="center">Value</th>
                </tr>
            </thead>
            <tbody>
                {#if jsonData}
                    {#each Object.entries(jsonData) as [key, value]}
                        <tr>
                            <td style:text-align="center">{key}</td>
                            <td style:text-align="center">{value}</td>
                        </tr>
                    {/each}
                {/if}
            </tbody>
        </table>
    </div>
</div>

<style>
    .container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        grid-template-rows: 1fr 1fr;
        height: 100vh;
        margin: 0;
        padding: 20px;
        gap: 20px;
    }

    .panel {
        border: 2px solid #ccc;
        border-radius: 10px;
        padding: 20px;
    }

    .stick-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
    }

    .image-holder {
        height: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 1.5em;
        background-color: #f0f0f0;
        border-radius: 8px;
    }

    table {
        width: 100%;
        border-collapse: collapse;
    }

    th, td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }

</style>
