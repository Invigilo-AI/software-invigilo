<script setup lang="ts">
import { boolean } from "yup/lib/locale";

export interface EmptyGridProps {
    hide?: boolean;
}
const props = withDefaults(defineProps<EmptyGridProps>(), {
    hide: false
})
</script>
<template>
    <VPlaceholderPage
        :class="{'is-hidden': hide}"
        title="We couldn't find any matching results."
        subtitle="Too bad. Looks like we couldn't find any matching results for the
          search terms you've entered. Please try different search terms or
          criteria."
        larger
      >
        <template #image>
          <img
            class="light-image"
            src="/@src/assets/illustrations/placeholders/search-3.svg"
            alt=""
          />
          <img
            class="dark-image"
            src="/@src/assets/illustrations/placeholders/search-3-dark.svg"
            alt=""
          />
        </template>
      </VPlaceholderPage>
</template>