<template>
  <div class="mobile-subsidebar">
    <div class="inner">
      <div class="sidebar-title">
        <h3>Dashboards</h3>
      </div>

      <ul class="submenu" data-simplebar>
        <VCollapseLinks>
          <template #header>
            Personal
            <i aria-hidden="true" class="iconify" data-icon="feather:chevron-right" />
          </template>

          <RouterLink :to="{ name: 'app' }" class="is-submenu">
            <i aria-hidden="true" class="lnil lnil-home"></i>
            <span>Home</span>
          </RouterLink>

          <RouterLink :to="{ name: 'app-map' }" class="is-submenu">
            <span class="iconify" data-icon="carbon:heat-map-02" data-inline="false"></span>
            <span>Location map</span>
          </RouterLink>
        </VCollapseLinks>
      </ul>
    </div>
  </div>
</template>
