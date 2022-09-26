<script setup lang="ts">
import { useHead } from "@vueuse/head";

import { useViewWrapper } from "/@src/stores/viewWrapper";

const viewWrapper = useViewWrapper();
viewWrapper.setPageTitle("AI Models");

useHead({
  title: "AI Models",
});
</script>

<template>
  <div class="page-content-inner">
    <AITypesAdministration />
  </div>
</template>
