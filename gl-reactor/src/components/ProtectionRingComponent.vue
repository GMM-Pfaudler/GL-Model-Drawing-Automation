<template>
    <q-page class="q-pa-md">
     <!-- First Row -->
    <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap">
            <q-input
            outlined
            v-model="protectionRingSize"
            label="Size"
            dense
            class="col-12 col-md-2"
            />

            <q-space/>
            <q-btn outline rounded color="primary" icon="search" label="Search" @click="searchProtectionRingData"/>
        </div>
    </div>
    <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap">
            <q-select
            outlined
            v-model="protectionRingType"
            :options="protectionRingTypeOptions"
            @update:model-value="onUpdateType"
            label="Type"
            dense
            class="col-12 col-md-2"
            />
        </div>
    </div>
    <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap">
            <q-select
            outlined
            v-model="protectionRingMaterial"
            :options="protectionRingMaterialOptions"
            label="Material"
            dense
            class="col-12 col-md-2"
            />
        </div>
    </div>
  </q-page>
</template>
<script>
import { onMounted, ref } from 'vue'
export default {
  name: 'ProtectionRing',
  props: {
    protectionRing: Object
  },
  emits: ['search-data'],
  setup (props, { emit }) {
    const protectionRingSize = ref(null)
    const protectionRingType = ref(null)
    const protectionRingTypeOptions = ref(['-', 'Glass Lined', 'PTFE BUSH TYPE', 'PFA Lined'])
    const protectionRingMaterial = ref(null)
    const protectionRingMaterialOptions = ref(null)

    onMounted(() => {
        const protectionring = localStorage.getItem('protectionring')
        const data = JSON.parse(protectionring)
        if(data !== null){
            protectionRingSize.value = data.protectionRingSize
            protectionRingType.value = data.protectionRingType
            protectionRingMaterial.value = data.protectionRingMaterial
        }
    })

    const searchProtectionRingData = () => {
        const data = prepareProtectionRingData()
        emit('search-data', data)
    }

    const prepareProtectionRingData = () => {
        const protectionRing = {
            component: 'ProtectionRing',
            protectionRingSize: protectionRingSize.value?protectionRingSize.value:null,
            protectionRingType: protectionRingType.value?protectionRingType.value:null,
            protectionRingMaterial: protectionRingMaterial.value?protectionRingMaterial.value:null
        }
        localStorage.setItem('protectionring', JSON.stringify(protectionRing))
        return protectionRing
    }

    const onUpdateType = (val) => {
        if(val === 'Glass Lined'){
            protectionRingMaterial.value = null
            protectionRingMaterialOptions.value = ['-', 'MS', 'SS316L']
        }
        else if(val === 'PFA Lined'){
            protectionRingMaterialOptions.value = ['-', 'MS', 'SS304', 'SS316', 'SS316L']
            protectionRingMaterial.value = null
        }
        else if(val === 'PTFE BUSH TYPE'){
            protectionRingMaterialOptions.value = ['-', '100% PTFE']
            protectionRingMaterial.value = protectionRingMaterialOptions.value[0]
        }
    }

    const populateInitialData = (data) => {
      const nozzle_services = JSON.parse(data.nozzle_services)
        const nozzle_sizes = JSON.parse(data.nozzle_sizes)
        for (let i = 0; i < nozzle_services.length; i++) {
            if(nozzle_services[i] === 'Manhole'){
                protectionRingSize.value = nozzle_sizes[i]
            }
        }
    }

    return {
        protectionRingSize,
        protectionRingType,
        protectionRingTypeOptions,
        protectionRingMaterial,
        protectionRingMaterialOptions,

        // Methods
        onUpdateType,
        searchProtectionRingData,
        populateInitialData
    }
  },
  watch: {
    protectionRing: {
      handler(newVal) {
        if (newVal !== null) {
          this.populateInitialData(newVal);
        }
      },
      immediate: true
    }
  }
}
</script>