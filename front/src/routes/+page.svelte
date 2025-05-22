<script>
  // Microinteraction state for button hover
  let isHovered = false;

  // Accessibility: Focus management for keyboard users
  function handleFocus() {
    isHovered = true;
  }

  function handleBlur() {
    isHovered = false;
  }
</script>

<section class="relative flex flex-col items-center justify-center min-h-screen px-4 py-8 text-center overflow-hidden">
  <!-- Repetitive Geometric Patterns -->
  <div class="absolute inset-0 z-0 overflow-hidden">
    {#each Array(10) as _, i}
      <div
        class="absolute w-20 h-20 bg-gradient-to-br from-pink-500 to-red-500 rounded-full opacity-30 animate-float"
        style={`top: ${Math.random() * 100}%; left: ${Math.random() * 100}%; animation-delay: ${i * 0.5}s`}
      ></div>
    {/each}
  </div>

  <!-- Abstract SVG Shape with Parallax Effect -->
  <svg
    class="absolute top-[-10%] left-[-10%] w-[120%] h-[120%] opacity-30 animate-float-parallax"
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 1000 1000"
    fill="currentColor"
    aria-hidden="true"
  >
    <path d="M500 0C223.9 0 0 223.9 0 500s223.9 500 500 500 500-223.9 500-500S776.1 0 500 0zm0 950c-246.6 0-450-203.4-450-450S253.4 50 500 50s450 203.4 450 450-203.4 450-450 450z" />
  </svg>

  <!-- Background Gradient Overlay -->
  <div class="absolute inset-0 bg-gradient-to-br from-blue-900 via-indigo-800 to-purple-900 opacity-90 blur-sm"></div>

  <!-- Glassmorphism Card -->
  <div class="relative z-10 p-8 bg-white/10 backdrop-blur-lg rounded-3xl shadow-lg border border-white/20 max-w-md text-center">
    <h1 class="text-4xl font-bold text-white md:text-5xl">Discover Luxury Properties</h1>
    <p class="mt-4 text-lg text-gray-200 leading-relaxed md:text-xl">
      Bid on exclusive estates and unlock unparalleled opportunities in the world of real estate.
    </p>

    <!-- Bold CTA Button -->
    <button
      class="mt-6 px-6 py-3 text-base font-semibold text-white bg-gradient-to-r from-pink-500 to-red-500 rounded-full shadow-lg transition-transform duration-200 ease-in-out hover:scale-105 focus:outline-none focus:ring-2 focus:ring-pink-500 focus:ring-offset-2 focus:ring-offset-gray-900"
      on:mouseenter={() => (isHovered = true)}
      on:mouseleave={() => (isHovered = false)}
      on:focus={handleFocus}
      on:blur={handleBlur}
      aria-label="Start Bidding Now"
    >
      {isHovered ? 'Bid Now →' : 'Get Started'}
    </button>
  </div>
</section>

<style>
  /* Keyframes for SVG floating animation */
  @keyframes float {
    0% {
      transform: translateY(0) rotate(0deg);
    }
    50% {
      transform: translateY(-10px) rotate(5deg);
    }
    100% {
      transform: translateY(0) rotate(0deg);
    }
  }

  @keyframes float-parallax {
    0% {
      transform: translateY(0) scale(1);
    }
    50% {
      transform: translateY(-20px) scale(1.05);
    }
    100% {
      transform: translateY(0) scale(1);
    }
  }

  .animate-float {
    animation: float 10s infinite ease-in-out;
  }

  .animate-float-parallax {
    animation: float-parallax 15s infinite ease-in-out;
  }
</style>