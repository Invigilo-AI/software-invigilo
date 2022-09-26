<template>
  <div class="mobile-subsidebar">
    <div class="inner">
      <div class="sidebar-title">
        <h3>Incidents</h3>
      </div>

      <ul class="submenu" data-simplebar>
        <VCollapseLinks>
          <template #header>
            Incidents
            <i
              aria-hidden="true"
              class="iconify"
              data-icon="feather:chevron-right"
            />
          </template>

          <RouterLink :to="{ name: 'incident-last' }" class="is-submenu">
            <i class="iconify" data-icon="carbon:activity" aria-hidden="true"></i>
            <span>Incident gallery</span>
          </RouterLink>

          <RouterLink :to="{ name: 'incident-report' }" class="is-submenu">
            <i class="iconify" data-icon="carbon:report" aria-hidden="true"></i>
            <span>Incidents &amp; Reports</span>
          </RouterLink>

          <RouterLink :to="{ name: 'incident-cameras' }" class="is-submenu">
            <i class="iconify" data-icon="carbon:grid" aria-hidden="true"></i>
            <span>Cameras</span>
          </RouterLink>
        </VCollapseLinks>
      </ul>
    </div>
  </div>
</template>
