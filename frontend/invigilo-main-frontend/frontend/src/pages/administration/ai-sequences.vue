<script setup lang="ts">
import { useHead } from "@vueuse/head";

import { useViewWrapper } from "/@src/stores/viewWrapper";

const viewWrapper = useViewWrapper();
viewWrapper.setPageTitle("AI Sequences");

useHead({
  title: "AI Sequences",
});
</script>

<template>
  <div class="page-content-inner">
    <AISequencesAdministration />
  </div>
</template>
