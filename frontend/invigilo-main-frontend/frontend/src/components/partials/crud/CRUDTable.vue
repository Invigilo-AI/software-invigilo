<script setup lang="ts">
import "simple-datatables/src/style.css";
import { computed, ref, onMounted, watch, reactive } from "vue";
import { useApi } from "/@src/composable/useApi";
import { useNotyf } from "/@src/composable/useNotyf";
import _cloneDeep from "lodash/cloneDeep";
import dayjs from "dayjs";
import utc from "dayjs/plugin/utc";

dayjs.extend(utc);

export type CRUDCellType =
  | "string"
  | "number"
  | "action"
  | "status"
  | "datetime";
export type CRUDColumn = {
  label?: string;
  field: string | number;
  sortable?: string | boolean;
  searchable?: boolean | string;
  render?: Function;
  type?: CRUDCellType;
  hidden?: boolean;
};
export type Paginate = {
  limit: number;
  offset: number;
  more: boolean;
};
export type CRUDSort = { [field: string]: "asc" | "desc" | undefined };
export type CRUDAction = {
  key: string;
  global?: boolean;
  action: Function;
  label?: string;
  title?: string;
  icon?: string;
  buttonProps?: any;
};
export interface CRUDTableEmits {
  (e: "update:modelValue", value: (string | number)[]): void;
}
export type Searchable = boolean | Record<string, string>;
export type CRUDTableFilter = {
  key: string;
  type: "checkbox" | "date" | "datetime" | "date-range" | "datetime-range";
  label: string;
};
export interface CRUDTable {
  path?: string;
  params?: Record<string, any>;
  columns: CRUDColumn[];
  options?: any;
  data?: any[];
  perPage?: number;
  actions?: CRUDAction[];
  updateTimestamp?: number;
  searchable?: Searchable;
  filterBy?: Record<string, any>;
  filters?: CRUDTableFilter[];
}

const emit = defineEmits<CRUDTableEmits>();
const props = withDefaults(defineProps<CRUDTable>(), {
  perPage: 10,
  searchable: undefined,
  filters: undefined,
  options: {
    perPageSelect: [5, 10, 20, 25, 50, 100],
  },
});

const renderType =
  ({ type }: CRUDColumn) =>
  (data: any, cell: any, row: any) => {
    const template = {
      avatar: `
          <div class="v-avatar">
              <img class="avatar" src="${data}" alt="">
          </div>
      `,
      name: `<span class="has-dark-text dark-inverted is-font-alt is-weight-600 rem-90">${data}</span>`,
      light: `<span class="light-text">${data}</span>`,
      action: `<div class="has-text-right"><button class="button v-button is-dark-outlined" data-row="${row.dataIndex}">Manage</button></div>`,
    };
    if (type === "status") {
      const status = data ? "online" : "offline";
      return `<div class="status is-${status}">
              <i aria-hidden="true" class="iconify" data-icon="carbon:dot-mark"></i>
              <span class="is-capitalize">${status}</span>
          </div>`;
    }
    return data;
  };

const actions = ref([...(props?.actions || [])]);

const globalActions = computed(() =>
  actions.value.filter(({ global = false }) => global)
);

const rowActions = computed(() =>
  actions.value.filter(({ global = false }) => !global)
);

const columns = computed<CRUDColumn[]>(() =>
  props.columns.map((column, idx: number) => {
    const {
      label,
      field = String(idx),
      sortable = false,
      searchable = false,
      render = renderType(column),
      type = "string",
      hidden = false,
      ...opts
    } = column;

    return {
      label,
      field,
      render,
      sortable,
      searchable,
      type,
      hidden,
      ...opts,
    };
  })
);

const visibleColumns = computed(() =>
  columns.value.filter(({ hidden }) => !hidden)
);

const headings = computed(() =>
  visibleColumns.value.map((column) => {
    if (typeof column === "string") return column;
    return column.label !== undefined ? column.label : column.field;
  })
);

const searchOptions = computed(() => {
  const searchColumns = columns.value
    .filter((column: CRUDColumn) => column.searchable)
    .reduce(
      (acc, { label, field, searchable }: CRUDColumn) => ({
        ...acc,
        [String(typeof searchable === "boolean" ? field : searchable)]:
          label || field,
      }),
      {}
    );

  if (["boolean", "undefined"].includes(typeof props.searchable)) {
    if (props.searchable !== false) {
      if (Object.keys(searchColumns).length) {
        return searchColumns;
      } else {
        return { q: "Query" };
      }
    } else {
      return {};
    }
  } else {
    return props.searchable;
  }
});

const isSearchable = computed(() =>
  Boolean(props.searchable || Object.keys(searchOptions.value).length)
);

const sortableBy = computed(() =>
  columns.value
    .map(({ sortable, field }: CRUDColumn) => sortable && field)
    .filter(Boolean)
);

const data = ref<any[]>(props.data || []);

const getData = (row: any, column: CRUDColumn | string, idx: number) => {
  let data = null;

  if (typeof column === "string") {
    data = row[idx];
  } else if (typeof column.field === "string") {
    data = column.field
      .split(".")
      .reduce((obj: any, path: string) => obj && obj[path], row);
  } else {
    data = row[column.field || idx];
  }

  if (typeof column === "object") {
    const { type } = column;
    if (type === "status") {
      data = data ? "online" : "offline";
    } else if (type === "datetime") {
      data = dayjs.utc(data).local();
    }
  }

  return data;
};

const loading = ref(false);
const paginate = ref<Paginate>({
  limit: props.perPage,
  offset: 0,
  more: true,
});
const orderBy = reactive<CRUDSort>({});
const searchBy = ref({});
const filterBy = reactive({ ..._cloneDeep(props.filterBy) });

const loadNext = () => {
  if (paginate.value.more) {
    if (data.value.length) paginate.value.offset += paginate.value.limit;
    apiLoad();
  }
};

const loadPrev = () => {
  if (paginate.value.offset > 0) {
    paginate.value.offset -= paginate.value.limit;
    apiLoad();
  }
};

watch(
  () => props.updateTimestamp,
  () => {
    apiLoad();
  }
);

watch(
  () => props.params,
  () => {
    apiLoad(true);
  }
);

watch(
  () => searchBy.value,
  () => {
    apiLoad(true);
  }
);

watch(
  () => orderBy,
  () => {
    apiLoad(true);
  },
  { deep: true }
);

watch(
  () => paginate.value.limit,
  () => {
    apiLoad(true);
  }
);

const notif = useNotyf();
const api = useApi();
const order_by = computed(
  () =>
    Object.keys(orderBy)
      .map((key) => `${orderBy[key] === "asc" ? "" : "-"}${key}`)
      .join(",") || undefined
);

const apiLoad = async (reload = false) => {
  if (!props.path) return;
  loading.value = true;
  if (reload) {
    paginate.value.offset = 0;
    paginate.value.more = true;
  }
  const params = {
    ...props.params,
    ...searchBy.value,
    ...filterBy,
    order_by: order_by.value,
    limit: paginate.value.limit,
    skip: paginate.value.offset,
  };

  await api
    .get(props.path, { params })
    .then((response) => {
      const items = response.data;

      paginate.value.more = items.length === paginate.value.limit;

      if (!items.length && paginate.value.offset >= paginate.value.limit) {
        paginate.value.offset -= paginate.value.limit;
      }

      if (items.length) {
        data.value = items;
      } else if (reload) {
        data.value = [];
      }
    })
    .catch(({ error = {} }) => {
      if (reload) data.value = [];
      if (typeof error.detail === "string") notif.error(error.detail);
    });
  loading.value = false;
};

onMounted(() => {
  apiLoad(true);
});

const eventHandling = (event: any) => {
  console.dir("eventHandling", event);
};

const sortField = (column: CRUDColumn) =>
  String(
    ["boolean", "undefined"].includes(typeof column.sortable)
      ? column.field
      : column.sortable
  );
const sortColumn = (column: CRUDColumn) => {
  const field = sortField(column);
  const currentSort = orderBy[field];

  if (currentSort === undefined) {
    orderBy[field] = "asc";
  } else if (currentSort === "asc") {
    orderBy[field] = "desc";
  } else {
    delete orderBy[field];
  }
};
const hasActiveFilters = computed(() => Boolean(Object.keys(filterBy).length));
const filterModalOpen = ref(false);

const clearFilters = () => {
  filterModalOpen.value = false;
  Object.keys(filterBy).forEach((key) => delete filterBy[key]);
  reloadData();
};
const applyFilters = () => {
  filterModalOpen.value = false;
  reloadData();
};

const reloadData = async () => await apiLoad(true);

const handleGlobalAction = async (key: string) => {
  const actionIndex = actions.value.findIndex((action) => action.key === key);

  if (actionIndex === -1) return;

  let action = actions.value[actionIndex];

  if (!action.buttonProps) action.buttonProps = {};

  action.buttonProps.loading = true;

  const updateAction = await action.action(
    {
      ...searchBy.value,
      ...filterBy,
      order_by: order_by.value,
    },
    action
  );

  action.buttonProps.loading = false;

  if (updateAction) {
    actions.value.splice(actionIndex, 1, updateAction);
  }
};

const prepareActionProps = (action: CRUDAction, data: any, index: number) =>
  Object.keys(action.buttonProps)
    .map((key) => {
      const prop = action.buttonProps[key];
      return {
        key,
        value: typeof prop === "function" ? prop(data, index) : prop,
      };
    })
    .reduce((acc, elm) => ({ ...acc, [elm.key]: elm.value }), {});
</script>

<template>
  <div
    class="dataTable-wrapper dataTable-loading no-footer fixed-columns"
    :class="{ sortable: sortableBy.length, searchable: isSearchable }"
  >
    <div class="dataTable-top">
      <SearchBy
        v-if="isSearchable"
        v-model="searchBy"
        :options="searchOptions"
        class="dataTable-search"
      />

      <div class="dataTable-filters">
        <template v-if="(filters && filters.length) || $slots.filters">
          <VButton
            v-if="hasActiveFilters"
            icon="carbon:filter-edit"
            outlined
            @click="filterModalOpen = true"
          >
            Edit filters
          </VButton>
          <VButton
            v-else
            icon="carbon:filter"
            outlined
            @click="filterModalOpen = true"
          >
            Add filters
          </VButton>
          <VModal
            :open="filterModalOpen"
            actions="right"
            noscroll
            class="modal-filters"
            @close="filterModalOpen = false"
            title="Filters"
          >
            <template #content>
              <slot
                name="filters"
                v-bind="{ data: filterBy, reload: reloadData }"
              ></slot>
            </template>
            <template #cancel>
              <VButton color="danger" outlined @click="clearFilters"
                >Clear all</VButton
              >
            </template>
            <template #action>
              <VButton color="primary" raised @click="applyFilters"
                >Apply</VButton
              >
            </template>
          </VModal>
        </template>
      </div>
      <div v-if="$slots.extraActions" class="dataTable-extra dataTable-actions">
        <slot
          name="extraActions"
          v-bind="{ data: filterBy, reload: reloadData }"
        ></slot>
      </div>
      <div
        v-if="globalActions.length || $slots.actions"
        class="dataTable-actions"
      >
        <slot name="actions" :actions="globalActions">
          <VButton
            v-for="action in globalActions"
            :key="action.key"
            :icon="action.icon"
            v-tooltip.left="action.title"
            v-bind="action.buttonProps"
            @click.prevent.stop="handleGlobalAction(action.key)"
            >{{ action.label }}</VButton
          >
        </slot>
      </div>
    </div>
    <div class="dataTable-container">
      <table class="dataTable-table">
        <thead>
          <tr>
            <th
              :key="idx"
              v-for="(column, idx) in visibleColumns"
              :data-sortable="column.sortable"
              :class="orderBy[sortField(column)]"
            >
              <a
                v-if="column.sortable"
                href="#"
                @click.stop.prevent="sortColumn(column)"
                class="dataTable-sorter"
                >{{ headings[idx] }}</a
              >
              <span v-else>{{ headings[idx] }}</span>
            </th>
            <th v-if="rowActions.length">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!data.length">
            <td :colspan="columns.length + (rowActions.length && 1)">
              <!--Empty Placeholder-->
              <VPlaceholderSection
                title="No data to show"
                subtitle="There is currently no data to show in this list."
              >
                <template #image>
                  <img
                    class="light-image"
                    src="/@src/assets/illustrations/placeholders/search-4.svg"
                    alt=""
                  />
                  <img
                    class="dark-image"
                    src="/@src/assets/illustrations/placeholders/search-4-dark.svg"
                    alt=""
                  />
                </template>
              </VPlaceholderSection>
            </td>
          </tr>
          <tr v-else :key="idy" v-for="(row, idy) in data">
            <td :key="idx" v-for="(column, idx) in visibleColumns">
              <span v-if="typeof column.type === 'function'">{{
                column.type(getData(row, column, idx), row, idx)
              }}</span>
              <div
                v-else-if="column.type === 'status'"
                :class="`status is-${getData(row, column, idx)}`"
                :title="getData(row, column, idx)"
              >
                <i
                  aria-hidden="true"
                  class="iconify"
                  data-icon="carbon:dot-mark"
                ></i>
              </div>
              <div v-else-if="column.type === 'image'" class="image">
                <img :src="getData(row, column, idx)" />
              </div>
              <span
                v-else-if="column.type === 'datetime'"
                v-tooltip="
                  getData(row, column, idx).format(
                    'dddd, MMMM D YYYY, HH:mm:ss'
                  )
                "
                >{{
                  getData(row, column, idx).format("DD/MM/YYYY HH:mm")
                }}</span
              >
              <VCheckbox
                v-else-if="column.type === 'boolean'"
                :checked="getData(row, column, idx)"
                solid
                disabled
              />
              <span v-else>{{ getData(row, column, idx) }}</span>
            </td>
            <td v-if="rowActions.length" class="row-action">
              <template v-for="action in rowActions" :key="action.key">
                <VButton
                  v-if="action.label"
                  :icon="action.icon"
                  v-tooltip.left="action.title"
                  v-bind="prepareActionProps(action, data[idy])"
                  @click.prevent.stop="action.action(data[idy])"
                  >{{ action.label }}</VButton
                >
                <VIconButton
                  v-else
                  :icon="action.icon"
                  v-tooltip.left="action.title"
                  v-bind="prepareActionProps(action, data[idy])"
                  @click.prevent.stop="action.action(data[idy])"
                />
              </template>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="dataTable-bottom">
      <div class="dataTable-dropdown">
        <label>
          <select class="dataTable-selector" v-model="paginate.limit">
            <option
              :value="option"
              :key="option"
              v-for="option in options.perPageSelect"
            >
              {{ option }}
            </option>
          </select>
        </label>
      </div>
      <nav class="dataTable-pagination">
        <ul class="dataTable-pagination-list">
          <li :class="{ disabled: paginate.offset === 0 }" class="pager">
            <a
              href="#"
              :disabled="paginate.offset === 0"
              @click.prevent.stop="loadPrev"
            >
              <i class="iconify" data-icon="carbon:chevron-left" />
            </a>
          </li>
          <li :class="{ disabled: !paginate.more }" class="pager">
            <a
              href="#"
              :disabled="!paginate.more"
              @click.prevent.stop="loadNext"
            >
              <i class="iconify" data-icon="carbon:chevron-right" />
            </a>
          </li>
        </ul>
      </nav>
    </div>
  </div>
</template>

<style lang="scss">
.v-modal.modal-filters {
  .modal-content,
  .modal-card {
    overflow: visible;
  }
}
.is-navbar {
  .datatable-toolbar {
    padding-top: 30px;
  }
}

.datatable-toolbar {
  display: flex;
  align-items: center;
  margin-bottom: 20px;

  &.is-reversed {
    flex-direction: row-reverse;
  }

  .field {
    margin-bottom: 0;

    .control {
      .button {
        color: var(--light-text);

        &:hover,
        &:focus {
          background: var(--primary);
          border-color: var(--primary);
          color: var(--primary--color-invert);
        }
      }
    }
  }

  .buttons {
    margin-left: auto;
    margin-bottom: 0;

    .v-button {
      margin-bottom: 0;
    }
  }
}

.is-dark {
  .datatable-toolbar {
    .field {
      .control {
        .button {
          background: var(--dark-sidebar) !important;
          color: var(--light-text);

          &:hover,
          &:focus {
            background: var(--primary) !important;
            border-color: var(--primary) !important;
            color: var(--smoke-white) !important;
          }
        }
      }
    }
  }
}

.dataTable-wrapper {
  .dataTable-top {
    padding-left: 0;
    padding-right: 0;
    display: flex;

    &::after {
      display: none;
    }

    .dataTable-search {
      flex: 1 3;
      margin-bottom: 0;
      margin-right: 0.75rem;
    }
    .dataTable-filters {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      flex: 2 3;

      .date-input {
        width: 100px;
      }
      .datetime-input {
        width: 140px;
      }

      .field {
        margin-right: 0.5rem;
      }
    }
    .dataTable-actions {
      flex: 0 3;
      display: flex;
      .button {
        margin-right: 0.5rem;
        &:last-of-type {
          margin-right: 0;
        }
      }
    }
  }

  .dataTable-container {
    background: var(--white);
    border: none !important;
    overflow-x: auto;

    &::-webkit-scrollbar {
      height: 8px !important;
    }

    &::-webkit-scrollbar-thumb {
      border-radius: 10px !important;
      background: rgb(0 0 0 / 20%) !important;
    }

    .dataTable-table {
      border: 1px solid var(--fade-grey);
      border-collapse: collapse;
      border-radius: 0.75rem;

      th {
        padding: 16px 20px;
        font-family: var(--font-alt);
        font-size: 0.8rem;
        color: var(--dark-text);
        text-transform: uppercase;
        border: 1px solid var(--fade-grey);
        font-weight: 600;

        &:last-child {
          text-align: right;
        }

        .dataTable-sorter {
          &::after,
          &::before {
            right: -14px;
          }
        }
      }

      td {
        font-family: var(--font);
        vertical-align: middle;
        padding: 6px;
        border-bottom: 1px solid var(--fade-grey);

        &:last-child {
          text-align: right;
        }

        &.dataTables-empty {
          opacity: 0;
        }
      }

      .light-text {
        color: var(--light-text);
      }

      .flex-media {
        display: flex;
        align-items: center;

        .meta {
          margin-left: 10px;
          line-height: 1.3;

          span {
            display: block;
            font-size: 0.8rem;
            color: var(--light-text);
            font-family: var(--font);

            &:first-child {
              font-family: var(--font-alt);
              color: var(--dark-text);
            }
          }
        }
      }

      .row-action {
        white-space: nowrap;
        .button {
          margin-right: 4px;

          &:last-of-type {
            margin-right: 0;
          }

          &.v-button {
            height: 35px;
            padding: 6px 14px;
          }
        }
      }

      .checkbox {
        padding: 0;
      }

      .product-photo {
        width: 80px;
        height: 80px;
        object-fit: contain;
      }

      .file-icon {
        width: 46px;
        height: 46px;
        object-fit: contain;
      }

      .drinks-icon {
        display: block;
        max-width: 48px;
        border-radius: var(--radius-rounded);
        border: 1px solid var(--fade-grey);
      }

      .negative-icon,
      .positive-icon {
        svg {
          height: 16px;
          width: 16px;
        }
      }

      .positive-icon {
        .iconify {
          color: var(--success);

          * {
            stroke-width: 4px;
          }
        }
      }

      .negative-icon {
        &.is-danger {
          .iconify {
            color: var(--danger) !important;
          }
        }

        .iconify {
          color: var(--light-text);

          * {
            stroke-width: 4px;
          }
        }
      }

      .price {
        color: var(--dark-text);
        font-weight: 500;

        &::before {
          content: "$";
        }

        &.price-free {
          color: var(--light-text);
        }
      }

      .image {
        position: relative;
        z-index: 1;
        overflow: visible;
        img {
          max-width: 40px;
          max-height: 40px;
          transition: all 150ms;
        }

        &:hover {
          border: 1px solid var(--primary);
          position: absolute;
          margin-top: -20px;
          z-index: 2;
          img {
            max-width: initial;
            max-height: 250px;
          }
        }
      }

      .status {
        display: flex;
        align-items: center;

        &.is-online {
          .iconify {
            color: var(--success);
          }
        }

        &.is-busy {
          .iconify {
            color: var(--danger);
          }
        }

        &.is-offline {
          .iconify {
            color: var(--light-text);
          }
        }

        .iconify {
          width: 24px;
          height: 24px;
        }

        span {
          font-family: var(--font);
          font-size: 0.9rem;
          color: var(--light-text);
        }
      }
    }
  }

  .dataTable-bottom {
    padding-left: 0;
    padding-right: 0;
    .dataTable-info {
      font-family: var(--font);
      font-size: 0.9rem;
      color: var(--light-text);
    }

    .dataTable-dropdown {
      label {
        display: block;
        position: relative;
        font-family: var(--font);
        font-weight: 400;
        font-size: 0.9rem;
        color: var(--light-text);

        &::after {
          position: absolute;
          top: 1px;
          right: 4px;
          content: "";
          font-family: "Font Awesome 5 Free";
          font-weight: 900;
          font-size: 0.9rem;
          color: var(--light-text);
          height: 36px;
          width: 36px;
          border-radius: 0.5rem;
          display: flex;
          justify-content: center;
          align-items: center;
          background: var(--white);
        }
      }

      select {
        font-size: 1rem;
        background: var(--white);
        border: 1px solid var(--border);
        color: var(--dark-text);
        border-radius: 0.5rem;
        height: 38px;
        transition: box-shadow 0.3s;
        padding-right: 25px;

        &:focus {
          box-shadow: var(--light-box-shadow);
        }
      }
    }

    .dataTable-pagination {
      li {
        &:not(.active) {
          a:hover {
            background: var(--white);
          }
        }

        &.active {
          a {
            background: var(--primary);
            box-shadow: var(--primary-box-shadow);
            color: var(--primary--color-invert);
          }
        }

        a {
          display: flex;
          justify-content: center;
          align-items: center;
          font-family: var(--font);
          color: var(--light-text);
          border-radius: var(--radius-rounded);
          min-width: 34px;
          min-height: 34px;
          padding: 0;
        }
      }
    }
  }
}

.is-dark {
  .dataTable-wrapper {
    .dataTable-bottom {
      .dataTable-dropdown {
        label {
          &::after {
            background: var(--dark-sidebar-light-6) !important;
          }
        }

        select {
          border-color: var(--dark-sidebar-light-12);
          background: var(--dark-sidebar-light-6);
          color: var(--white);
        }
      }
    }

    .dataTable-container {
      border-color: var(--dark-sidebar-light-12);
      background: var(--dark-sidebar-light-6);

      .dataTable-table {
        border-color: var(--dark-sidebar-light-12);

        th,
        td {
          border-color: var(--dark-sidebar-light-12);
          color: var(--dark-dark-text);
        }

        th {
          .dataTable-sorter {
            &::after,
            &::before {
              right: -14px;
            }
            &::before {
              border-top-color: var(--dark-dark-text);
            }

            &::after {
              border-bottom-color: var(--dark-dark-text);
            }
          }
        }

        .drinks-icon {
          border-color: var(--dark-sidebar-light-12);
        }
      }
    }
  }
}
</style>
