<!-- src/lib/components/home/ModernHero.svelte -->
<script>
  import { onMount } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  import { elasticOut, cubicOut } from 'svelte/easing';

  // Animation state management
  let mounted = false;
  let isVisible = false;

  // Control sphere animation variations
  const spheres = [
    { x: 15, y: 20, size: 50, delay: 0, speed: 25, rotate: 8 },
    { x: 85, y: 15, size: 35, delay: 2, speed: 28, rotate: -5 },
    { x: 75, y: 65, size: 60, delay: 1, speed: 22, rotate: 3 },
    { x: 25, y: 70, size: 45, delay: 3, speed: 26, rotate: -10 },
    { x: 50, y: 40, size: 65, delay: 0.5, speed: 30, rotate: 12 }
  ];

  onMount(() => {
    mounted = true;
    
    // Delay to ensure transitions work properly
    setTimeout(() => {
      isVisible = true;
    }, 300);
  });
</script>

<section class="hero-container">
  <!-- Animated background shapes -->
  <div class="wave-container">
    <svg viewBox="0 0 1440 800" preserveAspectRatio="none" class="waves">
      <defs>
        <!-- Primary Blue to Primary Peach Gradient -->
        <linearGradient id="wave-gradient-1" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#b9dcf2" /> <!-- primary-blue -->
          <stop offset="100%" stop-color="#f6cfbe" /> <!-- primary-peach -->
        </linearGradient>
        
        <!-- Secondary Blue to Component Primary Gradient -->
        <linearGradient id="wave-gradient-2" x1="0%" y1="100%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#7c98b6" /> <!-- secondary-blue -->
          <stop offset="100%" stop-color="#0062cc" /> <!-- component-primary -->
        </linearGradient>
        
        <!-- Component Secondary to Secondary Peach Gradient -->
        <linearGradient id="wave-gradient-3" x1="100%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#6c63ff" /> <!-- component-secondary -->
          <stop offset="100%" stop-color="#e5b3a0" /> <!-- secondary-peach -->
        </linearGradient>
        
        <!-- Sphere Gradients -->
        <radialGradient id="sphere-gradient-1" cx="30%" cy="30%" r="70%">
          <stop offset="0%" stop-color="#b9dcf2" stop-opacity="0.9" /> <!-- primary-blue -->
          <stop offset="100%" stop-color="#b9dcf2" stop-opacity="0.4" />
        </radialGradient>
        
        <radialGradient id="sphere-gradient-2" cx="30%" cy="30%" r="70%">
          <stop offset="0%" stop-color="#f6cfbe" stop-opacity="0.9" /> <!-- primary-peach -->
          <stop offset="100%" stop-color="#f6cfbe" stop-opacity="0.4" />
        </radialGradient>
        
        <radialGradient id="sphere-gradient-3" cx="30%" cy="30%" r="70%">
          <stop offset="0%" stop-color="#0062cc" stop-opacity="0.9" /> <!-- component-primary -->
          <stop offset="100%" stop-color="#0062cc" stop-opacity="0.4" />
        </radialGradient>
      </defs>
      
      <!-- Professional curved shapes -->
      <path 
        class="wave wave-1" 
        d="M0,160 C240,120 480,220 720,180 C960,140 1200,200 1440,180 L1440,800 L0,800 Z"
        fill="url(#wave-gradient-1)"
        opacity="0.6"
      />
      
      <path 
        class="wave wave-2" 
        d="M0,340 C360,300 720,380 1080,320 C1260,290 1350,330 1440,320 L1440,800 L0,800 Z"
        fill="url(#wave-gradient-2)"
        opacity="0.5"
      />
      
      <path 
        class="wave wave-3" 
        d="M0,520 C180,480 360,560 540,520 C720,480 900,530 1080,500 C1260,470 1350,510 1440,500 L1440,800 L0,800 Z"
        fill="url(#wave-gradient-3)"
        opacity="0.4"
      />
    </svg>
  </div>
  
  <!-- 3D Sphere Elements -->
  <div class="spheres-container">
    {#each spheres as sphere, i}
      <div 
        class="sphere-wrapper"
        style="
          left: {sphere.x}%; 
          top: {sphere.y}%; 
          --delay: {sphere.delay}s;
          --speed: {sphere.speed}s;
          --rotate: {sphere.rotate}deg;
        "
      >
        <svg 
          viewBox="0 0 100 100" 
          class="sphere"
          style="width: {sphere.size}px; height: {sphere.size}px;"
        >
          <circle 
            cx="50" 
            cy="50" 
            r="48" 
            fill={`url(#sphere-gradient-${(i % 3) + 1})`}
            opacity="0.7"
          />
          <!-- Highlight to enhance 3D effect -->
          <circle 
            cx="35" 
            cy="35" 
            r="15" 
            fill="rgba(255, 255, 255, 0.3)"
          />
        </svg>
      </div>
    {/each}
  </div>
  
  <!-- Content Container with Glassmorphism -->
  <div class="content-container">
    {#if isVisible}
      <div 
        class="glass-card"
        in:fly={{ y: 50, duration: 1000, delay: 300, easing: elasticOut }}
      >
        <h1>GUDIT<br><span>Auction Platform</span></h1>
        
        <p in:fade={{ duration: 800, delay: 700 }}>
          The most trusted platform to bid, win, and acquire unique items with transparent, secure bidding processes
        </p>
        
        <div 
          class="cta-buttons"
          in:fly={{ y: 20, duration: 800, delay: 900, easing: cubicOut }}
        >
          <button class="btn-primary">Start Bidding</button>
          <button class="btn-secondary">Browse Auctions</button>
        </div>
      </div>
    {/if}
  </div>
</section>

<style>
  /* Hero container styles */
  .hero-container {
    position: relative;
    width: 100%;
    height: 100vh;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #fff;
  }
  
  /* Wave animation styles */
  .wave-container {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
  }
  
  .waves {
    position: absolute;
    bottom: 0;
    width: 100%;
    height: 100%;
  }
  
  .wave {
    transform-origin: bottom;
  }
  
  .wave-1 {
    animation: wave-animation-subtle 25s ease-in-out infinite alternate;
  }
  
  .wave-2 {
    animation: wave-animation-subtle 20s ease-in-out -5s infinite alternate-reverse;
  }
  
  .wave-3 {
    animation: wave-animation-subtle 18s ease-in-out -8s infinite alternate;
  }
  
  /* 3D Sphere styles */
  .spheres-container {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
  }
  
  .sphere-wrapper {
    position: absolute;
    transform: translate(-50%, -50%);
    animation: float-animation var(--speed) ease-in-out infinite;
    animation-delay: var(--delay);
    z-index: 10;
  }
  
  .sphere {
    animation: rotate-animation calc(var(--speed) * 2) linear infinite;
    filter: drop-shadow(0 10px 15px rgba(0, 0, 0, 0.2));
  }
  
  /* Content styles */
  .content-container {
    position: relative;
    z-index: 100;
    width: 100%;
    max-width: 1200px;
    padding: 0 20px;
    text-align: center;
  }
  
  .glass-card {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 20px;
    border: 1px solid rgba(185, 220, 242, 0.3);
    padding: 3rem 4rem;
    color: var(--text-dark);
    display: flex;
    flex-direction: column;
    align-items: center;
    max-width: 800px;
    margin: 0 auto;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
  }
  
  h1 {
    font-family: 'Outfit', sans-serif;
    font-size: 4.5rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    line-height: 1.2;
    margin-bottom: 1.5rem;
    background: linear-gradient(135deg, var(--component-primary), var(--component-secondary));
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
  }
  
  h1 span {
    font-weight: 400;
    font-size: 2.8rem;
    display: block;
    color: var(--secondary-blue);
    background: none;
    -webkit-background-clip: initial;
    background-clip: initial;
  }
  
  p {
    font-size: 1.2rem;
    margin-bottom: 2.5rem;
    line-height: 1.6;
    max-width: 540px;
    color: var(--text-medium);
  }
  
  .cta-buttons {
    display: flex;
    gap: 1.5rem;
  }
  
  .btn-primary {
    background: var(--component-primary);
    color: white;
    border: none;
    padding: 1rem 2.5rem;
    border-radius: 12px;
    font-family: 'Outfit', sans-serif;
    font-weight: 600;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 5px 15px rgba(0, 98, 204, 0.2);
  }
  
  .btn-primary:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(0, 98, 204, 0.3);
    background: var(--component-primary);
    opacity: 0.9;
  }
  
  .btn-secondary {
    background: transparent;
    color: var(--component-primary);
    border: 2px solid var(--component-primary);
    padding: 1rem 2.5rem;
    border-radius: 12px;
    font-family: 'Outfit', sans-serif;
    font-weight: 600;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .btn-secondary:hover {
    background: rgba(0, 98, 204, 0.05);
    transform: translateY(-3px);
  }
  
  /* Animations */
  @keyframes wave-animation-subtle {
    0% {
      transform: translateY(0) scaleY(1);
    }
    50% {
      transform: translateY(-10px) scaleY(1.02);
    }
    100% {
      transform: translateY(-5px) scaleY(1);
    }
  }
  
  @keyframes float-animation {
    0% {
      transform: translate(-50%, -50%) translateY(0) rotate(0deg);
    }
    50% {
      transform: translate(-50%, -50%) translateY(-15px) rotate(var(--rotate));
    }
    100% {
      transform: translate(-50%, -50%) translateY(0) rotate(0deg);
    }
  }
  
  @keyframes rotate-animation {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }
  
  /* Responsive adjustments */
  @media (max-width: 768px) {
    .glass-card {
      padding: 2rem;
    }
    
    h1 {
      font-size: 2.5rem;
    }
    
    h1 span {
      font-size: 2rem;
    }
    
    p {
      font-size: 1rem;
    }
    
    .cta-buttons {
      flex-direction: column;
      width: 100%;
    }
    
    .btn-primary, .btn-secondary {
      width: 100%;
    }
  }
</style>