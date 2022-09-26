<script setup lang="ts">
import { ref, watchPostEffect, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'

import type { SidebarTheme } from '/@src/components/navigation/desktop/Sidebar.vue'
import { useViewWrapper } from '/@src/stores/viewWrapper'
import { useUserSession } from '/@src/stores/userSession';

const props = withDefaults(
  defineProps<{
    theme?: SidebarTheme
    defaultSidebar?: string
    closeOnChange?: boolean
    openOnMounted?: boolean
    nowrap?: boolean
  }>(),
  {
    defaultSidebar: 'dashboard',
    theme: 'default',
  }
)

const viewWrapper = useViewWrapper()
const route = useRoute()
const {user, viewAsCompany, isSuperuser, hasPermission} = useUserSession()
const isMobileSidebarOpen = ref(false)
const isDesktopSidebarOpen = ref(props.openOnMounted)
const activeMobileSubsidebar = ref(props.defaultSidebar)

function switchSidebar(id: string) {
  if (id === activeMobileSubsidebar.value) {
    isDesktopSidebarOpen.value = !isDesktopSidebarOpen.value
  } else {
    isDesktopSidebarOpen.value = true
    activeMobileSubsidebar.value = id
  }
}

/**
 * watchPostEffect callback will be executed each time dependent reactive values has changed
 */
watchPostEffect(() => {
  viewWrapper.setPushed(isDesktopSidebarOpen.value ?? false)
})
watch(
  () => route.fullPath,
  () => {
    isMobileSidebarOpen.value = false

    if (props.closeOnChange && isDesktopSidebarOpen.value) {
      isDesktopSidebarOpen.value = false
    }
  }
)
onMounted(()=>{
  const [parent, ...kids] = String(route.name || '').split('-')
  if (parent && kids.length) switchSidebar(parent)
})
</script>

<template>
  <div class="sidebar-layout">
    <div class="app-overlay"></div>

    <!-- Mobile navigation -->
    <MobileNavbar
      :is-open="isMobileSidebarOpen"
      @toggle="isMobileSidebarOpen = !isMobileSidebarOpen"
    >
      <template #brand>
        <RouterLink :to="{ name: 'index' }" class="navbar-item is-brand">
          <AnimatedLogo width="38px" height="38px" />
        </RouterLink>

        <div class="brand-end">
          <!-- <NotificationsMobileDropdown /> -->
          <UserProfileDropdown />
        </div>
      </template>
    </MobileNavbar>

    <!-- Mobile sidebar links -->
    <MobileSidebar
      :is-open="isMobileSidebarOpen"
      @toggle="isMobileSidebarOpen = !isMobileSidebarOpen"
    >
      <template #links>
        <li>
          <RouterLink :to="{ name: 'app' }">
            <i aria-hidden="true" class="iconify" data-icon="carbon:dashboard"></i>
          </RouterLink>
        </li>
        <li>
          <RouterLink :to="{ name: 'incident' }">
            <i aria-hidden="true" class="iconify" data-icon="carbon:warning-square"></i>
          </RouterLink>
        </li>
        <li v-if="hasPermission('admin')">
          <RouterLink :to="{ name: 'management' }">
            <i aria-hidden="true" class="iconify" data-icon="carbon:task-settings"></i>
          </RouterLink>
        </li>
        <li v-if="isSuperuser">
          <RouterLink :to="{ name: 'administration' }">
            <i aria-hidden="true" class="iconify" data-icon="carbon:task-tools"></i>
          </RouterLink>
        </li>
      </template>

      <template #bottom-links></template>
    </MobileSidebar>

    <!-- Mobile subsidebar links -->
    <Transition name="slide-x">
      <DashboardsMobileSubsidebar
        v-if="isMobileSidebarOpen && activeMobileSubsidebar === 'dashboard'"
      />
    </Transition>
    <Transition name="slide-x">
      <IncidentMobileSubsidebar
        v-if="isMobileSidebarOpen && activeMobileSubsidebar === 'incident'"
      />
    </Transition>
    <Transition name="slide-x">
      <ManagementMobileSubsidebar
        v-if="isMobileSidebarOpen && activeMobileSubsidebar === 'management'"
      />
    </Transition>
    <Transition name="slide-x">
      <AdministrationsMobileSubsidebar
        v-if="isMobileSidebarOpen && activeMobileSubsidebar === 'administration'"
      />
    </Transition>

    <Sidebar :theme="props.theme" :is-open="isDesktopSidebarOpen">
      <template #links>
        <!-- Dashboards -->
        <li>
          <a
            :class="[activeMobileSubsidebar === 'dashboard' && 'is-active']"
            data-content="Dashboards"
            tabindex="0"
            @keydown.space.prevent="switchSidebar('dashboard')"
            @click="switchSidebar('dashboard')"
          >
            <i
              aria-hidden="true"
              class="iconify sidebar-svg"
              data-icon="carbon:dashboard"
            ></i>
          </a>
        </li>
        <!-- Incident -->
        <li>
          <a
            :class="[activeMobileSubsidebar === 'incident' && 'is-active']"
            data-content="Incident"
            tabindex="0"
            @keydown.space.prevent="switchSidebar('incident')"
            @click="switchSidebar('incident')"
          >
            <i
              aria-hidden="true"
              class="iconify sidebar-svg"
              data-icon="carbon:warning-square"
            ></i>
          </a>
        </li>
        <!-- Management -->
        <li v-if="hasPermission('admin')">
          <a
            :class="[
              activeMobileSubsidebar === 'management' && 'is-active',
            ]"
            data-content="Management"
            tabindex="0"
            @keydown.space.prevent="switchSidebar('management')"
            @click="switchSidebar('management')"
          >
            <i class="iconify sidebar-svg" data-icon="carbon:task-settings" aria-hidden="true"></i>
          </a>
        </li>
        <!-- Administrations -->
        <li v-if="isSuperuser">
          <a
            :class="[
              activeMobileSubsidebar === 'administration' && 'is-active',
            ]"
            data-content="Administrations"
            tabindex="0"
            @keydown.space.prevent="switchSidebar('administration')"
            @click="switchSidebar('administration')"
          >
            <i class="iconify sidebar-svg" data-icon="carbon:task-tools" aria-hidden="true"></i>
          </a>
        </li>
      </template>
      <template #bottom-links>
        <li>
          <UserProfileDropdown up />
        </li>
      </template>
    </Sidebar>

    <Transition name="slide-x">
      <DashboardsSubsidebar
        v-if="isDesktopSidebarOpen && activeMobileSubsidebar === 'dashboard'"
        @close="isDesktopSidebarOpen = false"
      />
    </Transition>
    <Transition name="slide-x">
      <IncidentSubsidebar
        v-if="isDesktopSidebarOpen && activeMobileSubsidebar === 'incident'"
        @close="isDesktopSidebarOpen = false"
      />
    </Transition>
    <Transition name="slide-x">
      <ManagementSubsidebar
        v-if="isDesktopSidebarOpen && activeMobileSubsidebar === 'management'"
        @close="isDesktopSidebarOpen = false"
      />
    </Transition>
    <Transition name="slide-x">
      <AdministrationsSubsidebar
        v-if="isDesktopSidebarOpen && activeMobileSubsidebar === 'administration'"
        @close="isDesktopSidebarOpen = false"
      />
    </Transition>

    <!-- <LanguagesPanel /> -->

    <VViewWrapper>
      <VPageContentWrapper>
        <template v-if="props.nowrap">
          <slot></slot>
        </template>
        <VPageContent v-else class="is-relative">
          <div class="page-title has-text-centered">
            <!-- Sidebar Trigger -->
            <div
              class="vuero-hamburger nav-trigger push-resize"
              tabindex="0"
              @keydown.space.prevent="
                isDesktopSidebarOpen = !isDesktopSidebarOpen
              "
              @click="isDesktopSidebarOpen = !isDesktopSidebarOpen"
            >
              <span class="menu-toggle has-chevron">
                <span
                  :class="[isDesktopSidebarOpen && 'active']"
                  class="icon-box-toggle"
                >
                  <span class="rotate">
                    <i aria-hidden="true" class="icon-line-top"></i>
                    <i aria-hidden="true" class="icon-line-center"></i>
                    <i aria-hidden="true" class="icon-line-bottom"></i>
                  </span>
                </span>
              </span>
            </div>

            <div class="title-wrap">
              <h1 class="title is-4">{{ viewWrapper.pageTitle }}</h1>
            </div>

            <Toolbar class="desktop-toolbar" />
          </div>

          <slot></slot>
        </VPageContent>
      </VPageContentWrapper>
    </VViewWrapper>
  </div>
</template>
