<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { browser } from '$app/environment'; // Remove if not using SvelteKit

  const dispatch = createEventDispatcher();

  let {containerRadius = 100, stickRadius = 50} = $props();

  let container;
  let stick;
  let isDragging = $state(false);
  let touchIdentifier = null;
  let x = $state(0);
  let y = $state(0);

  function handleStart(event) {
    if (isDragging) return;
    if (event.type === 'touchstart') event.preventDefault();

    isDragging = true;
    touchIdentifier = event.type.startsWith('touch') 
      ? event.touches[0].identifier 
      : null;

    window.addEventListener('mousemove', handleMove);
    window.addEventListener('mouseup', handleEnd);
    window.addEventListener('touchmove', handleMove, { passive: false });
    window.addEventListener('touchend', handleEnd);

    handleMove(event);
  }

  function handleMove(event) {
    if (!isDragging) return;

    const client = event.type.startsWith('touch')
      ? Array.from(event.touches).find(t => t.identifier === touchIdentifier)
      : event;

    if (!client) return;

    const rect = container.getBoundingClientRect();
    const stickWidth = stick.offsetWidth;
    const maxDistance = (rect.width - stickWidth) / 2;
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;

    let deltaX = client.clientX - centerX;
    let deltaY = client.clientY - centerY;
    const distance = Math.sqrt(deltaX ** 2 + deltaY ** 2);

    if (distance > maxDistance) {
      deltaX = (deltaX / distance) * maxDistance;
      deltaY = (deltaY / distance) * maxDistance;
    }

    x = deltaX;
    y = deltaY;

    dispatch('move', {
      x: deltaX / maxDistance,
      y: -deltaY / maxDistance // Invert Y axis for natural up=positive
    });
  }

  function handleEnd() {
    isDragging = false;
    x = y = 0;
    dispatch('move', { x: 0, y: 0 });
    removeListeners();
  }

  function removeListeners() {
    window.removeEventListener('mousemove', handleMove);
    window.removeEventListener('mouseup', handleEnd);
    window.removeEventListener('touchmove', handleMove);
    window.removeEventListener('touchend', handleEnd);
  }
// Cleanup
  onMount(() => {
    return () => {
      if (browser) removeListeners();
    };
  });
</script>

<div class="container" 
     style="width: {containerRadius}px; height: {containerRadius}px;"
     bind:this={container}
     onmousedown={handleStart}
     ontouchstart={handleStart}>
  <div class="stick" 
      bind:this={stick}
        style="width: {stickRadius}px; height: {stickRadius}px;
              transform: translate(-50%, -50%) translate({x}px, {y}px);
              transition: {isDragging ? 'none' : 'transform 0.2s ease-out'}">
  </div>
</div>

<style>
  .container {
    border-radius: 50%;
    background: #3333;
    position: relative;
    touch-action: none;
  }

  .stick {
    background: #6666;
    border-radius: 50%;
    position: absolute;
    left: 50%;
    top: 50%;
    user-select: none;
  }
</style>
