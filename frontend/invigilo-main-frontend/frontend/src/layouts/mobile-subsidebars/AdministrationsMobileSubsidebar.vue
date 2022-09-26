<template>
  <div class="mobile-subsidebar">
    <div class="inner">
      <div class="sidebar-title">
        <h3>Administrations</h3>
      </div>

      <ul class="submenu" data-simplebar>
        <VCollapseLinks>
          <template #header>
            Administration
            <i
              aria-hidden="true"
              class="iconify"
              data-icon="feather:chevron-right"
            />
          </template>

          <RouterLink :to="{ name: 'administration-companies' }" class="is-submenu">
            <i
              class="iconify"
              data-icon="carbon:enterprise"
              aria-hidden="true"
            ></i>
            <span>Companies</span>
          </RouterLink>
          <RouterLink :to="{ name: 'administration-users' }" class="is-submenu">
             <i
              class="iconify"
              data-icon="carbon:user"
              aria-hidden="true"
            ></i>
            <span>Users</span>
          </RouterLink>
          <RouterLink :to="{ name: 'administration-servers' }" class="is-submenu">
            <i
              class="iconify"
              data-icon="carbon:bare-metal-server"
              aria-hidden="true"
            ></i>
            <span>Servers</span>
          </RouterLink>
          <RouterLink :to="{ name: 'administration-ai-servers' }" class="is-submenu">
            <i
              class="iconify"
              data-icon="carbon:bare-metal-server-02"
              aria-hidden="true"
            ></i>
            <span>AI Servers</span>
          </RouterLink>
          <RouterLink :to="{ name: 'administration-ai-sequences' }" class="is-submenu">
            <i
              class="iconify"
              data-icon="carbon:machine-learning-model"
              aria-hidden="true"
            ></i>
            <span>AI Sequences</span>
          </RouterLink>
          <RouterLink :to="{ name: 'administration-ai-types' }" class="is-submenu">
            <i
              class="iconify"
              data-icon="carbon:model-alt"
              aria-hidden="true"
            ></i>
            <span>AI Models</span>
          </RouterLink>
        </VCollapseLinks>
      </ul>
    </div>
  </div>
</template>
