<template>
    <q-page class="q-pa-md">
     <!-- First Row -->
    <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap">
            <q-select
            outlined
            v-model="ringMaterial"
            :options="ringMaterialOptions"
            label="Material"
            dense
            class="col-12 col-md-2"
            />

            <q-space/>
            <q-btn outline rounded color="primary" icon="search" label="Search" @click="searchRingData"/>
        </div>
    </div>

    <!-- Second Row -->
    <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap">

            <q-input
            outlined
            v-model="nozzleSize"
            label="Bottom Nozzle Size"
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
  name: 'DiaphragmRing',
  props: {
    diaphragmRing: Object
  },
  emits: ['search-data'],
  setup (props, { emit }) {
    const ringMaterial = ref(null)
    const ringMaterialOptions = (['-', 'MS', 'SS304', 'SS316'])
    const nozzleSize = ref(null)

    onMounted(() => {
        const data = localStorage.getItem('ring')
        const ringData = JSON.parse(data)
        if(ringData !== null){
            ringMaterial.value = ringData.ringMaterial
            nozzleSize.value = ringData.nozzleSize
        }
    })

    const searchRingData = () => {
        const ringData = prepareRingData()
        emit('search-data', ringData)
    }

    const prepareRingData = () => {
        const data = {
            component: 'DiaphragmRing',
            ringMaterial: ringMaterial.value?ringMaterial.value:null,
            nozzleSize: nozzleSize.value?nozzleSize.value:null
        }
        localStorage.setItem('ring', JSON.stringify(data))
        // console.log('Saved to localStorage:', data)
        return data
    }

    const populateInitialData = (data) => {
        const nozzle_names = JSON.parse(data.nozzle_names)
        const nozzle_sizes = JSON.parse(data.nozzle_sizes)
        for (let i = 0; i < nozzle_names.length; i++) {
            if(nozzle_names[i] === 'L'){
                nozzleSize.value = nozzle_sizes[i]
            }
        }
    }

    return {
        ringMaterial,
        ringMaterialOptions,
        nozzleSize,

        // Methods
        populateInitialData,
        searchRingData
    }
  },
  watch: {
    diaphragmRing: {
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