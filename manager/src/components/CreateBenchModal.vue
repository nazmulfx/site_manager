<template>
  <Dialog
    :modelValue="open"
    @update:modelValue="$emit('update:open', $event)"
    :options="{ title: 'Initialize New Frappe Bench', size: '2xl' }"
  >
    <template #body-content>
      <div class="space-y-4 text-start">
        <Alert
          v-if="errorMessage"
          theme="danger"
          :title="errorMessage"
        />

        <FormControl label="Bench Directory Name" required description="Name of the directory created in your bench workspace">
          <TextInput
            v-model="form.benchName"
            placeholder="e.g. frappe-bench-v16"
          />
        </FormControl>

        <div class="grid grid-cols-2 gap-4">
          <FormControl label="Frappe Framework Branch / Version" required>
            <Select
              v-model="form.frappeBranch"
              :options="branchOptions"
            />
          </FormControl>

          <FormControl label="Python Executable Environment" required>
            <Select
              v-model="form.pythonPath"
              :options="pythonOptions"
            />
          </FormControl>
        </div>

        <FormControl label="Pre-install Frappe Apps">
          <MultiSelect
            v-model="form.selectedApps"
            :options="appOptions"
            placeholder="Select apps to install..."
          />
        </FormControl>

        <div class="grid grid-cols-2 gap-4 pt-2">
          <Switch
            v-model="form.useRedis"
            label="Enable Redis Services"
          />
          <Switch
            v-model="form.autoStart"
            label="Start bench immediately"
          />
        </div>
      </div>
    </template>

    <template #actions="{ close }">
      <div class="flex justify-end space-x-2">
        <Button variant="subtle" @click="close">Cancel</Button>
        <Button
          theme="blue"
          variant="solid"
          :loading="isSubmitting"
          @click="submitCreate(close)"
        >
          Initialize Bench
        </Button>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { createResource, toast } from 'frappe-ui'

const props = defineProps({
  open: { type: Boolean, default: false }
})

const emit = defineEmits(['update:open', 'created'])

const isSubmitting = ref(false)
const errorMessage = ref('')

const form = reactive({
  benchName: '',
  frappeBranch: 'version-16',
  pythonPath: 'python3',
  selectedApps: [],
  useRedis: true,
  autoStart: false
})

const branchOptions = [
  { label: 'Version 16 (v16.x - Next)', value: 'version-16' },
  { label: 'Version 15 (v15.x - Stable)', value: 'version-15' },
  { label: 'Develop Branch (Latest)', value: 'develop' }
]

const appOptions = [
  { label: 'ERPNext (Enterprise Resource Planning)', value: 'erpnext' },
  { label: 'HRMS (Human Resource Management)', value: 'hrms' },
  { label: 'Frappe Builder', value: 'builder' },
  { label: 'Frappe Helpdesk', value: 'helpdesk' },
  { label: 'Site Manager', value: 'site_manager' }
]

const systemInfo = createResource({
  url: 'site_manager.api.get_system_info',
  auto: true
})

const pythonOptions = computed(() => {
  if (!systemInfo.data?.python_executables?.length) {
    return [{ label: 'python3 (System Default)', value: 'python3' }]
  }
  return systemInfo.data.python_executables.map(p => ({
    label: `${p.version} (${p.path})`,
    value: p.path
  }))
})

const createBenchRes = createResource({
  url: 'site_manager.api.create_bench',
  onSuccess(data) {
    isSubmitting.value = false
    toast({
      title: 'Bench Initialization Started',
      text: data.message,
      appearance: 'success'
    })
    emit('created')
    emit('update:open', false)
  },
  onError(err) {
    isSubmitting.value = false
    errorMessage.value = err.message || 'Failed to create bench'
  }
})

const submitCreate = (closeModal) => {
  if (!form.benchName.trim()) {
    errorMessage.value = 'Bench directory name is required'
    return
  }
  errorMessage.value = ''
  isSubmitting.value = true
  createBenchRes.submit({
    bench_name: form.benchName.trim(),
    frappe_branch: form.frappeBranch,
    python_path: form.pythonPath,
    apps: form.selectedApps
  })
}
</script>
