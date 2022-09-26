<script setup lang="ts">
import { useHead } from "@vueuse/head";

import { useViewWrapper } from "/@src/stores/viewWrapper";

const viewWrapper = useViewWrapper();
viewWrapper.setPageTitle("Users");

useHead({
  title: "Users",
});
</script>

<template>
  <div class="page-content-inner">
    <UsersManagement />
  </div>
</template>
