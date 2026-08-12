<template>
  <div class="max-w-7xl mx-auto py-8 px-4 space-y-6">
    <!-- Top Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <FeatherIcon name="box" class="w-7 h-7 text-blue-600" />
          Frappe & Bench Manager
        </h1>
        <p class="text-sm text-gray-500 mt-1">
          Discover, monitor, create, and manage Frappe benches and sites on this computer.
        </p>
      </div>

      <div class="flex items-center space-x-3">
        <Button
          variant="outline"
          icon="refresh-cw"
          :loading="benchesResource.loading"
          @click="benchesResource.fetch"
        >
          Refresh
        </Button>

        <Button
          theme="blue"
          variant="solid"
          icon-left="plus"
          @click="showCreateModal = true"
        >
          New Bench
        </Button>
      </div>
    </div>

    <!-- Stats Overview Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <Card class="p-4 space-y-2">
        <div class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Total Benches</div>
        <div class="text-3xl font-bold text-gray-900">
          {{ benchesList.length }}
        </div>
        <div class="text-xs text-gray-400">Detected in workspace directory</div>
      </Card>

      <Card class="p-4 space-y-2">
        <div class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Running Services</div>
        <div class="text-3xl font-bold text-green-600">
          {{ runningCount }}
        </div>
        <div class="text-xs text-gray-400">Active bench start processes</div>
      </Card>

      <Card class="p-4 space-y-2">
        <div class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Total Sites</div>
        <div class="text-3xl font-bold text-blue-600">
          {{ totalSitesCount }}
        </div>
        <div class="text-xs text-gray-400">Installed sites across benches</div>
      </Card>

      <Card class="p-4 space-y-2">
        <div class="text-xs font-semibold text-gray-500 uppercase tracking-wider">System Environment</div>
        <div class="text-sm font-semibold text-gray-800 truncate">
          {{ sysInfo.data?.node_version || 'Node.js' }}
        </div>
        <div class="text-xs text-gray-400 truncate">
          {{ sysInfo.data?.python_executables?.[0]?.version || 'Python 3' }}
        </div>
      </Card>
    </div>

    <!-- Search & Filter Controls -->
    <div class="flex items-center justify-between gap-4">
      <div class="w-72">
        <TextInput
          v-model="searchFilter"
          placeholder="Filter bench by name..."
          variant="subtle"
        >
          <template #prefix>
            <FeatherIcon name="search" class="w-4 h-4 text-gray-400" />
          </template>
        </TextInput>
      </div>

      <Badge theme="blue" variant="subtle">
        Path: {{ sysInfo.data?.default_parent_dir || 'Local Host' }}
      </Badge>
    </div>

    <!-- Benches ListView -->
    <Card class="overflow-hidden">
      <div v-if="benchesResource.loading" class="p-12 text-center">
        <Spinner class="w-8 h-8 mx-auto text-blue-500" />
        <p class="text-sm text-gray-500 mt-2">Scanning workspace for Frappe benches...</p>
      </div>

      <div v-else-if="filteredBenches.length === 0" class="p-12 text-center space-y-3">
        <FeatherIcon name="folder-off" class="w-12 h-12 mx-auto text-gray-300" />
        <h3 class="font-semibold text-gray-700">No Benches Found</h3>
        <p class="text-sm text-gray-500 max-w-sm mx-auto">
          No bench directory detected in search directory. Initialize a new bench to get started.
        </p>
        <Button theme="blue" variant="solid" icon-left="plus" @click="showCreateModal = true">
          Create First Bench
        </Button>
      </div>

      <ListView
        v-else
        :rows="filteredBenches"
        :columns="columns"
        :options="{ selectable: false }"
      >
        <!-- Custom Cell Renderers -->
        <template #cell="{ column, row, value }">
          <template v-if="column.key === 'name'">
            <router-link :to="`/bench/${row.name}`" class="font-semibold text-blue-600 hover:underline flex items-center gap-1.5">
              <FeatherIcon name="folder" class="w-4 h-4 text-blue-500" />
              {{ row.name }}
            </router-link>
          </template>

          <template v-else-if="column.key === 'frappe_version'">
            <Badge theme="purple" variant="subtle">v{{ value }}</Badge>
          </template>

          <template v-else-if="column.key === 'python_version'">
            <span class="text-xs font-mono text-gray-600">{{ value }}</span>
          </template>

          <template v-else-if="column.key === 'sites_count'">
            <Badge theme="gray" variant="outline">{{ value }} sites</Badge>
          </template>

          <template v-else-if="column.key === 'status'">
            <Badge :theme="value === 'Running' ? 'green' : 'gray'" variant="subtle">
              {{ value }}
            </Badge>
          </template>

          <template v-else-if="column.key === 'actions'">
            <Dropdown
              :button="{ label: 'Actions', variant: 'ghost', iconRight: 'chevron-down' }"
              :options="getBenchRowActions(row)"
            />
          </template>
        </template>
      </ListView>
    </Card>

    <!-- Create Bench Modal Component -->
    <CreateBenchModal
      v-model:open="showCreateModal"
      @created="benchesResource.fetch"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { createResource, toast } from 'frappe-ui'
import CreateBenchModal from '../components/CreateBenchModal.vue'

const router = useRouter()
const showCreateModal = ref(false)
const searchFilter = ref('')

const columns = [
  { key: 'name', label: 'Bench Name' },
  { key: 'frappe_version', label: 'Frappe Version' },
  { key: 'python_version', label: 'Python Engine' },
  { key: 'sites_count', label: 'Sites' },
  { key: 'status', label: 'Status' },
  { key: 'actions', label: '' }
]

const sysInfo = createResource({
  url: 'site_manager.api.get_system_info',
  auto: true
})

const benchesResource = createResource({
  url: 'site_manager.api.get_benches',
  auto: true
})

const benchesList = computed(() => benchesResource.data || [])

const filteredBenches = computed(() => {
  if (!searchFilter.value) return benchesList.value
  const query = searchFilter.value.toLowerCase()
  return benchesList.value.filter(b => b.name.toLowerCase().includes(query))
})

const runningCount = computed(() => {
  return benchesList.value.filter(b => b.status === 'Running').length
})

const totalSitesCount = computed(() => {
  return benchesList.value.reduce((acc, b) => acc + (b.sites_count || 0), 0)
})

const getBenchRowActions = (row) => {
  return [
    {
      label: 'View Bench Details',
      icon: 'eye',
      onClick: () => router.push(`/bench/${row.name}`)
    },
    {
      label: 'Open Bench Directory',
      icon: 'folder',
      onClick: () => {
        toast({ title: 'Bench Path', text: row.path, appearance: 'info' })
      }
    }
  ]
}
</script>
