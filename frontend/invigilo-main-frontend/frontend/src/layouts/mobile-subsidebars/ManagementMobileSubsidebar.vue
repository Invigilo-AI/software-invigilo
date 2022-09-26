<template>
  <div class="mobile-subsidebar">
    <div class="inner">
      <div class="sidebar-title">
        <h3>Management</h3>
      </div>

      <ul class="submenu" data-simplebar>
        <VCollapseLinks>
          <template #header>
            Management
            <i
              aria-hidden="true"
              class="iconify"
              data-icon="feather:chevron-right"
            />
          </template>

          <RouterLink :to="{ name: 'management-cameras' }" class="is-submenu">
            <i
              class="iconify"
              data-icon="carbon:video"
              aria-hidden="true"
            ></i>
            <span>Cameras</span>
          </RouterLink>
          <RouterLink :to="{ name: 'management-users' }" class="is-submenu">
             <i
              class="iconify"
              data-icon="carbon:user"
              aria-hidden="true"
            ></i>
            <span>Users</span>
          </RouterLink>
        </VCollapseLinks>
      </ul>
    </div>
  </div>
</template>
