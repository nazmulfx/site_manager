<template>
  <div class="h-screen w-full flex bg-surface-base text-ink-gray-9 overflow-hidden">
    <!-- Sidebar Navigation -->
    <Sidebar width="16rem" class="border-r border-outline-gray-2 bg-surface-modal flex flex-col shrink-0">
      <!-- Sidebar Header -->
      <SidebarHeader
        title="Bench Manager"
        subtitle="Local Host Environment"
        logo="https://frappe.io/files/Frappe-black.png"
        :menu-items="[
          { label: 'Refresh System Data', icon: 'refresh-cw', onClick: () => benchesResource.fetch() },
          { label: 'System Terminal', icon: 'terminal', onClick: () => copyPath(sysInfo.data?.default_parent_dir || '') }
        ]"
      />

      <!-- Scrollable Navigation Items -->
      <div class="flex-1 overflow-y-auto px-2 pt-3 space-y-4">
        <!-- Main Navigation Section -->
        <SidebarSection title="MAIN">
          <SidebarItem
            v-for="item in mainNav"
            :key="item.label"
            :active="activeNav === item.label"
            @click="handleNavClick(item)"
          >
            <template #prefix>
              <FeatherIcon :name="item.icon" class="w-4 h-4 text-ink-gray-6" />
            </template>
            <span class="flex-1 truncate text-sm font-medium">{{ item.label }}</span>
            <template #suffix>
              <Badge
                v-if="item.count !== undefined"
                :theme="item.theme || 'gray'"
                variant="ghost"
                :label="String(item.count)"
              />
            </template>
          </SidebarItem>
        </SidebarSection>

        <!-- System & Tools Section -->
        <SidebarSection title="SYSTEM & TOOLS">
          <SidebarItem
            v-for="item in toolsNav"
            :key="item.label"
            :active="activeNav === item.label"
            @click="handleNavClick(item)"
          >
            <template #prefix>
              <FeatherIcon :name="item.icon" class="w-4 h-4 text-ink-gray-5" />
            </template>
            <span class="flex-1 truncate text-sm font-medium">{{ item.label }}</span>
            <template #suffix>
              <Badge
                v-if="item.badge"
                theme="blue"
                variant="subtle"
                :label="item.badge"
              />
            </template>
          </SidebarItem>
        </SidebarSection>

        <!-- Environment Card -->
        <SidebarSection title="HOST ENVIRONMENT">
          <div class="p-3 bg-surface-gray-2 rounded-xl space-y-2 border border-outline-gray-1 text-xs">
            <div class="flex items-center justify-between">
              <span class="text-ink-gray-5">Node Engine:</span>
              <Badge theme="gray" variant="outline" :label="sysInfo.data?.node_version || 'v20'" />
            </div>
            <div class="flex items-center justify-between">
              <span class="text-ink-gray-5">Python Binaries:</span>
              <Badge theme="purple" variant="outline" :label="`${sysInfo.data?.python_executables?.length || 1} Pythons`" />
            </div>
            <div class="pt-2 border-t border-outline-gray-2 flex flex-col gap-1">
              <span class="text-ink-gray-5">Workspace Root:</span>
              <span class="font-mono text-ink-gray-8 truncate text-[11px]" :title="sysInfo.data?.default_parent_dir">
                {{ sysInfo.data?.default_parent_dir || '/home/nazmul' }}
              </span>
            </div>
          </div>
        </SidebarSection>
      </div>

      <!-- Sidebar User / Action Footer -->
      <div class="p-3 border-t border-outline-gray-2 bg-surface-gray-1 flex items-center justify-between shrink-0">
        <div class="flex items-center space-x-2.5 min-w-0">
          <Avatar title="Administrator" size="sm" shape="circle" />
          <div class="min-w-0">
            <div class="text-xs font-semibold text-ink-gray-9 truncate">Administrator</div>
            <div class="text-[11px] text-ink-gray-5 truncate">Local Admin</div>
          </div>
        </div>

        <Button
          variant="ghost"
          icon="plus"
          tooltip="New Bench"
          @click="showCreateModal = true"
        />
      </div>
    </Sidebar>

    <!-- Main Content Shell -->
    <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
      <!-- Top Page Header -->
      <div class="h-14 px-6 border-b border-outline-gray-2 bg-surface-modal flex items-center justify-between shrink-0">
        <div class="flex items-center gap-3">
          <h1 class="text-lg font-bold text-ink-gray-9">{{ activeNav }}</h1>
          <Badge theme="blue" variant="subtle" :label="`${filteredBenches.length} Benches`" />
        </div>

        <div class="flex items-center gap-3">
          <TabButtons
            v-model="filterTab"
            :options="[{ label: 'All' }, { label: 'Running' }, { label: 'Stopped' }]"
          />

          <div class="w-64">
            <TextInput
              v-model="searchQuery"
              placeholder="Search benches..."
              variant="subtle"
            >
              <template #prefix>
                <FeatherIcon name="search" class="w-4 h-4 text-ink-gray-4" />
              </template>
            </TextInput>
          </div>

          <Button
            variant="outline"
            icon="refresh-cw"
            :loading="benchesResource.loading"
            @click="benchesResource.fetch"
          />

          <Button
            variant="solid"
            theme="blue"
            label="New Bench"
            icon-left="plus"
            @click="showCreateModal = true"
          />
        </div>
      </div>

      <!-- List Content Area -->
      <div class="flex-1 overflow-y-auto p-6">
        <!-- Loading State -->
        <div v-if="benchesResource.loading" class="p-16 text-center">
          <Spinner class="w-8 h-8 mx-auto text-blue-500" />
          <p class="text-sm text-ink-gray-5 mt-2">Discovering system benches...</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="filteredBenches.length === 0" class="p-16 text-center space-y-3 bg-surface-modal rounded-xl border border-outline-gray-2">
          <FeatherIcon name="folder-off" class="w-12 h-12 mx-auto text-ink-gray-4" />
          <h3 class="font-semibold text-ink-gray-8">No Benches Found</h3>
          <p class="text-sm text-ink-gray-5 max-w-sm mx-auto">
            No matching benches found. Initialize a new bench to get started.
          </p>
          <Button theme="blue" variant="solid" icon-left="plus" @click="showCreateModal = true">
            Create New Bench
          </Button>
        </div>

        <!-- List View -->
        <ListView
          v-else
          :rows="filteredBenches"
          row-key="name"
          :columns="columns"
          :options="{ selectable: false, rowHeight: 56 }"
          class="bg-surface-modal rounded-xl border border-outline-gray-2 overflow-hidden"
        >
          <template #cell="{ column, row, value }">
            <template v-if="column.key === 'name'">
              <div class="min-w-0 flex items-center gap-3">
                <div class="w-8 h-8 rounded-lg bg-surface-blue-2 flex items-center justify-center shrink-0">
                  <FeatherIcon name="box" class="w-4 h-4 text-ink-blue-3" />
                </div>
                <div class="min-w-0">
                  <router-link :to="`/bench/${row.name}`" class="font-semibold text-base text-ink-gray-9 hover:text-blue-600 truncate block">
                    {{ row.name }}
                  </router-link>
                  <div class="truncate text-xs text-ink-gray-5 font-mono">
                    {{ row.path }}
                  </div>
                </div>
              </div>
            </template>

            <template v-else-if="column.key === 'frappe_version'">
              <Badge theme="purple" variant="subtle" :label="`v${value}`" />
            </template>

            <template v-else-if="column.key === 'python_version'">
              <span class="text-xs font-mono text-ink-gray-7 truncate">{{ value }}</span>
            </template>

            <template v-else-if="column.key === 'sites_count'">
              <Badge theme="gray" variant="outline" :label="`${value} sites`" />
            </template>

            <template v-else-if="column.key === 'status'">
              <Badge
                :theme="statusTheme[value] || 'gray'"
                variant="subtle"
                :label="value"
              />
            </template>

            <template v-else-if="column.key === 'actions'">
              <Dropdown
                :button="{ label: 'Actions', variant: 'ghost', iconRight: 'chevron-down' }"
                :options="[
                  { label: 'View Details', icon: 'eye', onClick: () => router.push(`/bench/${row.name}`) },
                  { label: 'Copy Path', icon: 'copy', onClick: () => copyPath(row.path) }
                ]"
              />
            </template>
          </template>
        </ListView>
      </div>
    </div>

    <!-- Create Bench Modal -->
    <CreateBenchModal
      v-model:open="showCreateModal"
      @created="benchesResource.fetch"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  Avatar,
  Badge,
  Button,
  Dropdown,
  ListView,
  Sidebar,
  SidebarHeader,
  SidebarItem,
  SidebarSection,
  Spinner,
  TabButtons,
  TextInput,
  createResource,
  toast
} from 'frappe-ui'
import CreateBenchModal from '../components/CreateBenchModal.vue'

const router = useRouter()
const showCreateModal = ref(false)
const searchQuery = ref('')
const filterTab = ref('All')
const activeNav = ref('All Benches')

const columns = [
  { key: 'name', label: 'Bench Name', width: '1.8fr' },
  { key: 'frappe_version', label: 'Frappe Ver', width: '7rem' },
  { key: 'python_version', label: 'Python Engine', width: '10rem' },
  { key: 'sites_count', label: 'Sites', width: '6rem' },
  { key: 'status', label: 'Status', width: '7rem' },
  { key: 'actions', label: 'Actions', width: '6rem', align: 'end' }
]

const statusTheme = {
  Running: 'green',
  Stopped: 'gray',
  Error: 'red'
}

const sysInfo = createResource({
  url: 'site_manager.api.get_system_info',
  auto: true
})

const benchesResource = createResource({
  url: 'site_manager.api.get_benches',
  auto: true
})

const benchesList = computed(() => benchesResource.data || [])

const runningCount = computed(() => {
  return benchesList.value.filter(b => b.status === 'Running').length
})

const stoppedCount = computed(() => {
  return benchesList.value.filter(b => b.status === 'Stopped').length
})

const mainNav = computed(() => [
  { label: 'All Benches', icon: 'grid', count: benchesList.value.length, theme: 'blue' },
  { label: 'Running Services', icon: 'play-circle', count: runningCount.value, theme: 'green' },
  { label: 'Stopped Benches', icon: 'pause-circle', count: stoppedCount.value, theme: 'gray' }
])

const toolsNav = computed(() => [
  { label: 'Python Engines', icon: 'terminal', badge: `${sysInfo.data?.python_executables?.length || 1} Active` },
  { label: 'Node & System', icon: 'cpu', badge: sysInfo.data?.node_version || 'v20' },
  { label: 'Global Settings', icon: 'settings' }
])

const handleNavClick = (item) => {
  activeNav.value = item.label
  if (item.label === 'Running Services') {
    filterTab.value = 'Running'
  } else if (item.label === 'Stopped Benches') {
    filterTab.value = 'Stopped'
  } else if (item.label === 'All Benches') {
    filterTab.value = 'All'
  }
}

const filteredBenches = computed(() => {
  let list = benchesList.value

  if (filterTab.value === 'Running') {
    list = list.filter(b => b.status === 'Running')
  } else if (filterTab.value === 'Stopped') {
    list = list.filter(b => b.status === 'Stopped')
  }

  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    list = list.filter(b => b.name.toLowerCase().includes(query) || b.path.toLowerCase().includes(query))
  }

  return list
})

const copyPath = (path) => {
  navigator.clipboard.writeText(path)
  toast({ title: 'Path Copied', text: path, appearance: 'info' })
}
</script>
