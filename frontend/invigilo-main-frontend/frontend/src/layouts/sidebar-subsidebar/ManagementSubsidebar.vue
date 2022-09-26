<script setup lang="ts">
const emit = defineEmits(["close"]);
</script>

<template>
  <div class="sidebar-panel is-generic">
    <div class="subpanel-header">
      <h3 class="no-mb">Management</h3>
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
          <RouterLink :to="{ name: 'management-cameras' }">
            <i
              class="iconify"
              data-icon="carbon:video"
              aria-hidden="true"
            ></i>
            Cameras
          </RouterLink>
        </li>
        <li>
          <RouterLink :to="{ name: 'management-users' }">
            <i
              class="iconify"
              data-icon="carbon:user"
              aria-hidden="true"
            ></i>
            Users
          </RouterLink>
        </li>
      </ul>
    </div>
  </div>
</template>

<style lang="scss">
@import "../../scss/layout/sidebar-panel";
</style>
