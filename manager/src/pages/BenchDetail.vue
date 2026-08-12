<template>
  <div class="max-w-7xl mx-auto py-8 px-4 space-y-6">
    <!-- Back Button -->
    <div>
      <Button variant="ghost" icon-left="arrow-left" @click="router.push('/')">
        Back to Benches Overview
      </Button>
    </div>

    <!-- Loading State -->
    <div v-if="benchResource.loading" class="p-12 text-center">
      <Spinner class="w-8 h-8 mx-auto text-blue-500" />
      <p class="text-sm text-gray-500 mt-2">Loading bench details...</p>
    </div>

    <!-- Error State -->
    <Alert
      v-else-if="benchResource.error"
      theme="danger"
      title="Error Loading Bench"
      :message="benchResource.error.message"
    />

    <!-- Bench Header -->
    <div v-else-if="bench" class="space-y-6">
      <Card class="p-6">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div class="space-y-1">
            <div class="flex items-center space-x-3">
              <h1 class="text-2xl font-bold text-gray-900">{{ bench.name }}</h1>
              <Badge :theme="bench.status === 'Running' ? 'green' : 'gray'" variant="subtle">
                {{ bench.status }}
              </Badge>
            </div>
            <p class="text-sm text-gray-500 font-mono">{{ bench.path }}</p>
            <div class="flex items-center space-x-4 pt-2">
              <Badge theme="purple" variant="outline">Frappe v{{ bench.frappe_version }}</Badge>
              <Badge theme="blue" variant="outline">{{ bench.python_version }}</Badge>
              <Badge theme="gray" variant="outline">{{ bench.sites_count }} Installed Sites</Badge>
            </div>
          </div>

          <div class="flex items-center space-x-3">
            <Button
              theme="blue"
              variant="solid"
              icon-left="plus"
              @click="showCreateSiteModal = true"
            >
              Create New Site
            </Button>
          </div>
        </div>
      </Card>

      <!-- Navigation Tabs -->
      <Card class="p-4">
        <Tabs
          v-model="activeTabIndex"
          :tabs="[
            { label: 'Sites List', icon: 'globe' },
            { label: 'Installed Apps', icon: 'package' }
          ]"
        />

        <div class="pt-6">
          <!-- TAB 1: SITES LIST -->
          <div v-if="activeTabIndex === 0">
            <div v-if="!bench.sites_detailed || bench.sites_detailed.length === 0" class="p-8 text-center space-y-3">
              <FeatherIcon name="globe" class="w-10 h-10 mx-auto text-gray-300" />
              <p class="text-sm text-gray-500">No sites created in this bench yet.</p>
              <Button theme="blue" variant="solid" icon-left="plus" @click="showCreateSiteModal = true">
                Create First Site
              </Button>
            </div>

            <ListView
              v-else
              :rows="bench.sites_detailed"
              :columns="siteColumns"
              :options="{ selectable: false }"
            >
              <template #cell="{ column, row, value }">
                <template v-if="column.key === 'name'">
                  <div class="font-semibold text-gray-900 flex items-center gap-2">
                    <FeatherIcon name="globe" class="w-4 h-4 text-blue-500" />
                    {{ row.name }}
                  </div>
                </template>

                <template v-else-if="column.key === 'db_name'">
                  <span class="text-xs font-mono text-gray-600">{{ value }}</span>
                </template>

                <template v-else-if="column.key === 'actions'">
                  <Dropdown
                    :button="{ label: 'Actions', variant: 'ghost', iconRight: 'chevron-down' }"
                    :options="[
                      {
                        label: 'Open Site in Browser',
                        icon: 'external-link',
                        onClick: () => window.open(`http://${row.name}:8000`, '_blank')
                      }
                    ]"
                  />
                </template>
              </template>
            </ListView>
          </div>

          <!-- TAB 2: INSTALLED APPS -->
          <div v-else-if="activeTabIndex === 1">
            <ListView
              :rows="bench.apps_list || []"
              :columns="appColumns"
              :options="{ selectable: false }"
            >
              <template #cell="{ column, row, value }">
                <template v-if="column.key === 'name'">
                  <div class="font-semibold text-gray-900 flex items-center gap-2">
                    <FeatherIcon name="box" class="w-4 h-4 text-purple-500" />
                    {{ row.name }}
                  </div>
                </template>

                <template v-else-if="column.key === 'branch'">
                  <Badge theme="gray" variant="subtle">{{ value }}</Badge>
                </template>

                <template v-else-if="column.key === 'path'">
                  <span class="text-xs font-mono text-gray-500 truncate">{{ value }}</span>
                </template>
              </template>
            </ListView>
          </div>
        </div>
      </Card>
    </div>

    <!-- Create Site Dialog Modal -->
    <Dialog
      v-model="showCreateSiteModal"
      :options="{ title: `Create New Site in ${benchName}`, size: 'lg' }"
    >
      <template #body-content>
        <div class="space-y-4 text-start">
          <Alert
            v-if="siteErrorMessage"
            theme="danger"
            :title="siteErrorMessage"
          />

          <FormControl label="Site Name (Domain)" required description="Must end with .localhost or valid domain name">
            <TextInput
              v-model="siteForm.siteName"
              placeholder="e.g. site1.localhost"
            />
          </FormControl>

          <FormControl label="Administrator Password" required description="Initial password for Administrator login">
            <TextInput
              type="password"
              v-model="siteForm.adminPassword"
              placeholder="admin"
            />
          </FormControl>
        </div>
      </template>

      <template #actions="{ close }">
        <div class="flex justify-end space-x-2">
          <Button variant="subtle" @click="close">Cancel</Button>
          <Button
            theme="blue"
            variant="solid"
            :loading="isCreatingSite"
            @click="submitCreateSite(close)"
          >
            Create Site
          </Button>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createResource, toast } from 'frappe-ui'

const route = useRoute()
const router = useRouter()

const benchName = route.params.benchName
const activeTabIndex = ref(0)
const showCreateSiteModal = ref(false)
const isCreatingSite = ref(false)
const siteErrorMessage = ref('')

const siteForm = reactive({
  siteName: '',
  adminPassword: 'admin'
})

const siteColumns = [
  { key: 'name', label: 'Site Domain' },
  { key: 'db_name', label: 'Database Name' },
  { key: 'actions', label: '' }
]

const appColumns = [
  { key: 'name', label: 'App Name' },
  { key: 'branch', label: 'Git Branch' },
  { key: 'path', label: 'Repository Path' }
]

const sysInfo = createResource({
  url: 'site_manager.api.get_system_info',
  auto: true
})

const targetBenchPath = computed(() => {
  const parentDir = sysInfo.data?.default_parent_dir || '/home/nazmul'
  return `${parentDir}/${benchName}`
})

const benchResource = createResource({
  url: 'site_manager.api.get_bench_details',
  auto: true,
  makeParams() {
    return { bench_path: targetBenchPath.value }
  }
})

const bench = computed(() => benchResource.data)

const createSiteRes = createResource({
  url: 'site_manager.api.create_site',
  onSuccess(data) {
    isCreatingSite.value = false
    toast({ title: 'Site Created', text: data.message, appearance: 'success' })
    benchResource.fetch()
    showCreateSiteModal.value = false
  },
  onError(err) {
    isCreatingSite.value = false
    siteErrorMessage.value = err.message || 'Failed to create site'
  }
})

const submitCreateSite = (closeModal) => {
  if (!siteForm.siteName.trim()) {
    siteErrorMessage.value = 'Site name is required'
    return
  }
  siteErrorMessage.value = ''
  isCreatingSite.value = true
  createSiteRes.submit({
    bench_path: targetBenchPath.value,
    site_name: siteForm.siteName.trim(),
    admin_password: siteForm.adminPassword
  })
}
</script>
