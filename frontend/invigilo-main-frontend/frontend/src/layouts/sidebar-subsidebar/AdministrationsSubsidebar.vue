<script setup lang="ts">
const emit = defineEmits(["close"]);
</script>

<template>
  <div class="sidebar-panel is-generic">
    <div class="subpanel-header">
      <h3 class="no-mb">Administrations</h3>
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
          <RouterLink :to="{ name: 'administration-companies' }">
            <i
              class="iconify"
              data-icon="carbon:enterprise"
              aria-hidden="true"
            ></i>
            Companies
          </RouterLink>
        </li>
        <li>
          <RouterLink :to="{ name: 'administration-users' }">
            <i
              class="iconify"
              data-icon="carbon:user"
              aria-hidden="true"
            ></i>
            Users
          </RouterLink>
        </li>
        <li>
          <RouterLink :to="{ name: 'administration-servers' }">
            <i
              class="iconify"
              data-icon="carbon:bare-metal-server"
              aria-hidden="true"
            ></i>
            Servers
          </RouterLink>
        </li>
        <li>
          <RouterLink :to="{ name: 'administration-ai-servers' }">
            <i
              class="iconify"
              data-icon="carbon:bare-metal-server-02"
              aria-hidden="true"
            ></i>
            AI Servers
          </RouterLink>
        </li>
        <li>
          <RouterLink :to="{ name: 'administration-ai-sequences' }">
            <i
              class="iconify"
              data-icon="carbon:machine-learning-model"
              aria-hidden="true"
            ></i>
            AI Sequences
          </RouterLink>
        </li>
        <li>
          <RouterLink :to="{ name: 'administration-ai-types' }">
            <i
              class="iconify"
              data-icon="carbon:model-alt"
              aria-hidden="true"
            ></i>
            AI Models
          </RouterLink>
        </li>
      </ul>
    </div>
  </div>
</template>

<style lang="scss">
@import "../../scss/layout/sidebar-panel";
</style>
