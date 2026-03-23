<template>
  <router-view />
</template>

<script setup>
// Use Vue Router to manage page navigation
</script>

<style>
/* Global style reset */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'JetBrains Mono', 'Space Grotesk', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #F3F4F6;
  background-color: #121317;
}

/* Scrollbar styles */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #16181D;
}

::-webkit-scrollbar-thumb {
  background: #23272E;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #3C83F6;
}
</style>
