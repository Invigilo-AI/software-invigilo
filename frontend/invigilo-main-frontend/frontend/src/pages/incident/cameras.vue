<script setup lang="ts">
import { useHead } from "@vueuse/head";

import { useViewWrapper } from "/@src/stores/viewWrapper";

const viewWrapper = useViewWrapper();
viewWrapper.setPageTitle("Cameras");

useHead({
  title: "Cameras",
});
</script>

<template>
  <div class="page-content-inner">
    <CamerasIncident />
  </div>
</template>
