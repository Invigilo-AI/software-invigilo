<script setup lang="ts">
import { useHead } from "@vueuse/head";

import { useViewWrapper } from "/@src/stores/viewWrapper";

const viewWrapper = useViewWrapper();
viewWrapper.setPageTitle("Companies");

useHead({
  title: "Companies",
});
</script>

<template>
  <div class="page-content-inner">
    <CompaniesAdministration />
  </div>
</template>
