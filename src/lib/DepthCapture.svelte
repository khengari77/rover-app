<script>
    import { onMount } from 'svelte';
    import { Client } from '@gradio/client';

    let depthImage = null; // To store the depth map result
    let loading = false;
    let error = null;

    // Function to capture frame and send to Depth Anything V2
    const captureAndProcess = async () => {
        try {
            loading = true;
            error = null;

            // Fetch the latest frame from /api/stream as a blob
            const streamResponse = await fetch('/api/stream');
            if (!streamResponse.ok) throw new Error('Failed to fetch stream');
            const imageBlob = await streamResponse.blob();

            const hf_token = import.meta.env.VITE_HF_TOKEN;
            // Connect to Depth Anything V2 API
            const client = await Client.connect('khengari77/Depth-Anything-V2', {hf_token});
            const result = await client.predict('/on_submit', {
                image: imageBlob,
            });

            // Assuming result.data[0] is the depth map (adjust based on API response)
            depthImage = URL.createObjectURL(result.data[0]); // Convert blob to URL for display
        } catch (err) {
            error = err.message;
            console.error('Depth processing error:', err);
        } finally {
            loading = false;
        }
    };

    // Cleanup the object URL when component is destroyed
    onMount(() => {
        return () => {
            if (depthImage) URL.revokeObjectURL(depthImage);
        };
    });
</script>

<div class="depth-capture" on:click={captureAndProcess}>
    {#if loading}
        <p>Loading...</p>
    {:else if error}
        <p>Error: {error}</p>
    {:else if depthImage}
        <img src={depthImage} alt="Depth Map" />
    {:else}
        <p>Click to capture and process depth</p>
    {/if}
</div>

<style>
    .depth-capture {
        width: 100%;
        height: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        cursor: pointer;
        background: #f0f0f0;
        border: 1px solid #ccc;
    }
    img {
        max-width: 100%;
        max-height: 100%;
    }
</style>
