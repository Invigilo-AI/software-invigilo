<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useApi } from "/@src/composable/useApi";
import { useUserSession } from "/@src/stores/userSession";
const serverId = ref();
const levelIdx = ref(0);
const locations = ref<any[]>([]);
const locationLevels = computed(() => {
  const server: any = locations.value.find(({ id }) => id === serverId.value);

  return (server && server?.meta?.levels) || [];
});

const currentLevel = computed(
  () =>
    locationLevels.value &&
    locationLevels.value.length &&
    typeof levelIdx !== "undefined" &&
    locationLevels.value[levelIdx.value]
);

const api = useApi();
const userSession = useUserSession();

const getServers = () =>
  api
    .get("servers/extra", {
      params: {
        company_id: userSession.viewAsCompany || undefined,
      },
    })
    .then(({ data }) => {
      locations.value = data;
      serverId.value = locations.value.length
        ? locations.value[0].id
        : undefined;
    });

watch(() => userSession.viewAsCompany, getServers);
onMounted(getServers);
</script>
<template>
  <EmptyGrid v-if="userSession.isSuperuser && !userSession.viewAsCompany" />
  <div v-else>
    <VField addons v-if="locations.length">
      <VControl :key="idx" v-for="(location, idx) in locations">
        <VButton
          :icon="`ic:twotone-filter-${idx >= 9 ? '9-plus' : idx + 1}`"
          :lower="location.id === serverId"
          :color="(location.id === serverId && 'primary') || undefined"
          @click="(serverId = location.id), (levelIdx = 0)"
          >{{ location.name }}</VButton
        >
      </VControl>
    </VField>
    <VMessage v-else color="warning">This company has no servers</VMessage>
    <br />
    <!-- <code>{{JSON.stringify(locationLevels, null, 2)}}</code> -->
    <VField addons v-if="locationLevels.length">
      <VControl :key="idx" v-for="(level, idx) in locationLevels">
        <VButton
          :icon="`mdi:numeric-${idx >= 9 ? '9-plus' : idx + 1}-box`"
          :lower="idx === levelIdx"
          :color="(idx === levelIdx && 'primary') || undefined"
          @click="levelIdx = idx"
          >{{ level.name }}</VButton
        >
      </VControl>
    </VField>
    <VMessage v-else-if="locations.length" color="warning"
      >This server has no maps configured</VMessage
    >
    <div>
      <EmptyGrid :hide="Boolean(locationLevels)" />
      <BoundaryEditor
        v-if="currentLevel"
        v-model="currentLevel"
        :background="currentLevel.image_url"
        boundaryKey="cameras"
        :exclude-tool="[
          'select',
          'point',
          'rect',
          'ellipse',
          'polygon',
          'path',
          'camera',
        ]"
        responsive
      >
      </BoundaryEditor>
      <!-- <code>{{ JSON.stringify(currentLevel, null, 2) }}</code> -->
    </div>
  </div>
</template>
