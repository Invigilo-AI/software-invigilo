<script setup lang="ts">
import { useThemeColors } from "/@src/composable/useThemeColors";
import { useApi } from "/@src/composable/useApi";
import { computed, onMounted, reactive, ref, watch } from "vue";
import _merge from "lodash/merge";
import dayjs from "dayjs";
import utc from "dayjs/plugin/utc";
import duration from "dayjs/plugin/duration";
import weekday from "dayjs/plugin/weekday";
import isBetween from "dayjs/plugin/isBetween";
import type { Duration } from "dayjs/plugin/duration";
import type { Dayjs } from "dayjs";
import { useUserSession } from "/@src/stores/userSession";

dayjs.extend(utc);
dayjs.extend(duration);
dayjs.extend(weekday);
dayjs.extend(isBetween);

const themeColors = useThemeColors();
const api = useApi();
const userSession = useUserSession();

const graphCommonOptions = {
  height: 450,
};

// ==== line chart
const formatTick = computed(() =>
  period.value === "today" ? "HH:mm" : "DD MMM"
);

const lineApex = ref<ApexCharts | null>(null);
const lineSeries = ref<number[]>([]);
const lineOptions = reactive<ApexCharts.ApexOptions>({
  chart: {
    height: graphCommonOptions.height / 2,
    type: "line",
    toolbar: { show: false },
  },
  tooltip: {
    x: {
      show: true,
      formatter: (x) => dayjs(x).format(formatTick.value),
    },
  },
  series: [],
  xaxis: {
    type: "datetime",
    labels: {
      trim: true,
    },
    tooltip: {
      formatter: (x) => dayjs(x).format(formatTick.value),
    },
  },
});
// ==== gauge chart
const gaugeApexFormatter = (
  x: string | number | { config: { series: number[] } }
) => {
  let value = 0;
  if (typeof x === "object") {
    const { series } = x.config;
    value = series.reduce((p, c) => p + c, 0) / series.length;
  } else {
    value = Number(x);
  }
  return `${Number.isInteger(value) ? value : value.toFixed(2)}%`;
};
const gaugeApex = ref<ApexCharts | null>(null);
const gaugeSeries = ref<number[]>([]);
const gaugeOptions = reactive<ApexCharts.ApexOptions>({
  chart: {
    height: graphCommonOptions.height,
    type: "radialBar",
    offsetY: -50,
  },
  plotOptions: {
    radialBar: {
      startAngle: -90,
      endAngle: 90,
      inverseOrder: true,
      dataLabels: {
        show: true,
        name: {
          show: true,
          fontSize: "14px",
          fontWeight: 500,
          offsetY: -10,
        },
        value: {
          show: true,
          fontWeight: 600,
          color: themeColors.lightText,
          fontSize: "16px",
          offsetY: -5,
          formatter: gaugeApexFormatter,
        },
        total: {
          show: true,
          fontSize: "14px",
          fontWeight: 500,
          color: themeColors.lightText,
          formatter: gaugeApexFormatter,
        },
      },
      hollow: {
        margin: 15,
        size: "40%",
      },
      track: {
        strokeWidth: "100%",
      },
    },
  },
  stroke: {
    lineCap: "round",
  },
  labels: [],
});
// ==== radar graph
const radarApex = ref<ApexCharts | null>(null);
const radarSeries = ref<number[]>([]);
const radarOptions = reactive<ApexCharts.ApexOptions>({
  chart: {
    height: graphCommonOptions.height,
    type: "radar",
    toolbar: { show: false },
  },
  series: [],
  xaxis: {
    type: "category",
    labels: {
      trim: true,
    },
  },
  yaxis: {
    show: false,
  },
});
// ===== pie chart
const countApex = ref<ApexCharts | null>(null);
const countSeries = ref<number[]>([]);
const countOptions = reactive<ApexCharts.ApexOptions>({
  chart: {
    height: graphCommonOptions.height,
    type: "pie",
  },
  series: [],
  labels: [],
  legend: {
    position: "bottom",
  },
});

// AI model/indices
const ai_types = ref([]);

// === filters
const period = ref("this_week");
const periodOptions = [
  { value: "today", label: "Today" },
  { value: "this_week", label: "This week" },
  { value: "this_month", label: "This month" },
  { value: "last_week", label: "Last week" },
  { value: "last_month", label: "Last month" },
];

const graph_filters = computed(() => {
  let start: Dayjs = dayjs().startOf("hour");
  let end: Dayjs = dayjs().startOf("hour");
  let interval: Duration = dayjs.duration(1, "weeks");

  if (
    ["this_week", "last_week", "this_month", "last_month"].includes(
      period.value
    )
  ) {
    interval = dayjs.duration(1, "day");
  } else if (["today"].includes(period.value)) {
    interval = dayjs.duration(1, "hour");
  }

  if (period.value === "this_month") {
    start = start.clone().startOf("month");
    end = end.clone().endOf("month");
  } else if (period.value === "last_week") {
    start = start.clone().subtract(1, "week");
  } else if (period.value === "last_month") {
    start = start.clone().subtract(1, "month");
  } else if (period.value === "today") {
    start = start.clone().startOf("day");
    end = end.clone().endOf("day");
  } else {
    // if (period.value === "this_week")
    start = start.clone().startOf("week");
    end = end.clone().endOf("week");
  }
  return {
    start,
    end,
    interval,
  };
});

const resetGraphs = () => {
  if (userSession.isSuperuser && !userSession.viewAsCompany) return;

  get_activity_reports();
  get_gauge_reports();
  get_count_reports();
  get_by_type_count_reports();
};

watch(
  () => graph_filters.value,
  () => {
    resetGraphs();
  }
);

watch(
  () => userSession.viewAsCompany,
  () => {
    resetGraphs();
  }
);

onMounted(async () => {
  await get_ai_types();
  resetGraphs();
});

const asCompany = computed(
  () => (userSession.isSuperuser && userSession.viewAsCompany) || undefined
);

// ==== request graphs

const get_ai_types = async () =>
  api.get("ai/types").then(({ data }) => {
    ai_types.value = data;
    const ai_type_column = ai_types.value.map(({ name }) => name);

    radarOptions.labels = ai_type_column;

    if (radarApex.value) {
      radarApex.value.updateOptions(radarOptions);
    }
  });

const get_activity_reports = () => {
  api
    .get("reports/activity", {
      params: {
        company_id: asCompany.value,
        start: graph_filters.value.start.format(),
        end: graph_filters.value.end.format(),
        interval: graph_filters.value.interval.asSeconds(),
      },
    })
    .then(({ data }) => {
      const timeline: (string | Dayjs)[] = [];
      let start = graph_filters.value.start;
      let end = graph_filters.value.end;

      while (start <= end) {
        timeline.push(start.clone());
        start = start.add(graph_filters.value.interval);
      }

      lineOptions.labels = timeline.map((d) => d.valueOf().toString());
      lineSeries.value = data.map(({ cam_server, timeline }: any) => ({
        name: cam_server.name,
        data: timeline.map((x: number | null) => x),
      }));
      lineOptions.series = lineSeries.value;

      if (lineApex.value) {
        lineApex.value.updateOptions(lineOptions);
      }
    });
};

const get_gauge_reports = () => {
  api
    .get("reports/gauge", {
      params: {
        company_id: asCompany.value,
        start: graph_filters.value.start.format(),
        end: graph_filters.value.end.format(),
        interval: graph_filters.value.interval.asSeconds(),
      },
    })
    .then(({ data }) => {
      const server_locations = data.reduce(
        (acc: any, { cam_server }: any) => ({
          ...acc,
          [cam_server.id]: cam_server.location,
        }),
        {}
      );

      const zeroData = data.map(({ cam_server, value }: any) => [
        cam_server.id,
        value,
      ]);

      gaugeSeries.value = data.map(({ value }: any) => value);
      gaugeOptions.labels = data.map(
        ({ cam_server }: any) => cam_server.location
      );

      if (gaugeApex.value) gaugeApex.value.updateOptions(gaugeOptions);
    });
};

const get_count_reports = () => {
  api
    .get("reports/count", {
      params: {
        company_id: asCompany.value,
        start: graph_filters.value.start.format(),
        end: graph_filters.value.end.format(),
        interval: graph_filters.value.interval.asSeconds(),
      },
    })
    .then(({ data }) => {
      const server_locations = data.reduce(
        (acc: any, { cam_server }: any) => ({
          ...acc,
          [cam_server.id]: cam_server.location,
        }),
        {}
      );

      const zeroData = data.map(({ cam_server, value }: any) => [
        cam_server.id,
        value,
      ]);

      countOptions.labels = data.map(
        ({ cam_server }: any) => cam_server.location
      );
      countSeries.value = data.map(({ value }: any) => value);

      if (countApex.value) {
        countApex.value.updateOptions(countOptions);
        countApex.value.updateSeries(countSeries.value);
      }
    });
};

const get_by_type_count_reports = () => {
  api
    .get("reports/by_type_count", {
      params: {
        company_id: asCompany.value,
        start: graph_filters.value.start.format(),
        end: graph_filters.value.end.format(),
      },
    })
    .then(({ data }) => {
      radarSeries.value = data.map(({ cam_server, values }: any) => ({
        name: cam_server.name,
        data: ai_types.value.map((type: any) => {
          const count = values.find(({ index }: any) => index === type.index);
          return (count && count.count) || 0;
        }),
      }));
      radarOptions.series = radarSeries.value;

      if (radarApex.value) {
        radarApex.value.updateOptions(radarOptions);
      }
    });
};
</script>

<template>
  <EmptyGrid v-if="userSession.isSuperuser && !userSession.viewAsCompany" />
  <template v-else>
    <div class="card-grid-toolbar">
      <div class="buttons">
        <VField class="h-hidden-mobile">
          <VControl>
            <Multiselect
              v-model="period"
              :searchable="false"
              :allow-empty="false"
              :options="periodOptions"
              placeholder="Period"
            />
          </VControl>
        </VField>
      </div>
    </div>
    <div class="columns is-multiline">
      <div class="column is-12">
        <div class="s-card">
          <h4 class="is-font is-weight-500 rem-120">Heartbeat</h4>
          <ApexChart
            id="gauge"
            ref="gaugeApex"
            :height="gaugeOptions.chart.height"
            :type="gaugeOptions.chart.type"
            :series="gaugeSeries"
            :options="gaugeOptions"
          >
          </ApexChart>
        </div>
      </div>
      <div class="column is-12">
        <div class="s-card">
          <h4 class="is-font is-weight-500 rem-120">Incidents in time</h4>
          <ApexChart
            id="line"
            ref="lineApex"
            :height="lineOptions.chart.height"
            :type="lineOptions.chart.type"
            :series="lineSeries"
            :options="lineOptions"
          >
          </ApexChart>
        </div>
      </div>
      <div class="column is-6">
        <div class="s-card">
          <h4 class="is-font is-weight-500 rem-120">Locations</h4>
          <ApexChart
            id="count"
            ref="countApex"
            :height="countOptions.chart.height"
            :type="countOptions.chart.type"
            :series="countSeries"
            :options="countOptions"
          >
          </ApexChart>
        </div>
      </div>
      <div class="column is-6">
        <div class="s-card">
          <h4 class="is-font is-weight-500 rem-120">Incident types</h4>
          <ApexChart
            id="radar"
            ref="radarApex"
            :height="radarOptions.chart.height"
            :type="radarOptions.chart.type"
            :series="radarSeries"
            :options="radarOptions"
          >
          </ApexChart>
        </div>
      </div>
    </div>
  </template>
</template>

<style lang="postcss">
.vue-apexcharts svg {
  overflow: visible;
}
</style>