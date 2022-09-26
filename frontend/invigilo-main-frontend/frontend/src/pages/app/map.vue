<script setup lang="ts">
import { useHead } from '@vueuse/head'

import { useViewWrapper } from '/@src/stores/viewWrapper'

const viewWrapper = useViewWrapper()
viewWrapper.setPageTitle('Location map')

useHead({
  title: 'Location map',
})
</script>

<template>
  <div class="page-content-inner">
    <LocationMap />
  </div>
</template>
