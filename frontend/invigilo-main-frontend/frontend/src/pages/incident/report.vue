<script setup lang="ts">
import { useHead } from "@vueuse/head";

import { useViewWrapper } from "/@src/stores/viewWrapper";

const viewWrapper = useViewWrapper();
viewWrapper.setPageTitle("Incidents & Reports");

useHead({
  title: "Incidents & Reports",
});
</script>

<template>
  <div class="page-content-inner">
    <ReportIncident />
  </div>
</template>
