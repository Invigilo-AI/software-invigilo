<script setup lang="ts">
import { useHead } from "@vueuse/head";

import { useViewWrapper } from "/@src/stores/viewWrapper";

const viewWrapper = useViewWrapper();
viewWrapper.setPageTitle("Servers");

useHead({
  title: "Servers",
});
</script>

<template>
  <div class="page-content-inner">
    <ServersAdministration />
  </div>
</template>
