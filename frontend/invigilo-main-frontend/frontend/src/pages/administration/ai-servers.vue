<script setup lang="ts">
import { useHead } from "@vueuse/head";

import { useViewWrapper } from "/@src/stores/viewWrapper";

const viewWrapper = useViewWrapper();
viewWrapper.setPageTitle("AI Servers");

useHead({
  title: "AI Servers",
});
</script>

<template>
  <div class="page-content-inner">
    <AIServersAdministration />
  </div>
</template>
