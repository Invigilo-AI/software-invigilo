<script setup lang="ts">
const emit = defineEmits(["close"]);
</script>

<template>
  <div class="sidebar-panel is-generic">
    <div class="subpanel-header">
      <h3 class="no-mb">Incidents</h3>
      <div
        class="panel-close"
        tabindex="0"
        @keydown.space.prevent="emit('close')"
        @click="emit('close')"
      >
        <i aria-hidden="true" class="iconify" data-icon="feather:x"></i>
      </div>
    </div>
    <div class="inner" data-simplebar>
      <ul>
        <li>
          <RouterLink :to="{ name: 'incident-last' }">
            <i class="iconify" data-icon="carbon:activity" aria-hidden="true"></i>
            Incident gallery
          </RouterLink>
        </li>
        <li>
          <RouterLink :to="{ name: 'incident-report' }">
            <i class="iconify" data-icon="carbon:report" aria-hidden="true"></i>
            Incidents &amp; Reports
          </RouterLink>
        </li>
        <li>
          <RouterLink :to="{ name: 'incident-cameras' }">
            <i class="iconify" data-icon="carbon:grid" aria-hidden="true"></i>
            Cameras
          </RouterLink>
        </li>
      </ul>
    </div>
  </div>
</template>

<style lang="scss">
@import "../../scss/layout/sidebar-panel";
</style>
