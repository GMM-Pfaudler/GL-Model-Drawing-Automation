<template>
    <q-page class="q-pa-md">
        <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap">
            <q-select
            outlined
            v-model="mhCoverBalanceAssembly"
            :options="mhCoverBalanceAssemblyOptions"
            @update:model-value="onUpdateAssembly"
            label="Balance Assembly"
            dense
            class="col-12 col-md-2"
            />

            <q-space/>
            <q-btn outline rounded color="primary" icon="search" label="Search" @click="searchSpringbalanceassemblyData"/>
        </div>
    </div>
     <!-- First Row -->
    <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap">
            <q-input
            outlined
            v-model="springbalanceassemblySize"
            label="Size"
            type="=text"
            dense
            class="col-12 col-md-2"
            />
        </div>
    </div>
    <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap">
            <q-select
            outlined
            v-model="springbalanceassemblyType"
            :options="springbalanceassemblyTypeOptions"
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
            v-model="springbalanceassemblyMaterial"
            :options="springbalanceassemblyMaterialOptions"
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
  name: 'SpringBalanceAssembly',
  props: {
    springbalanceassembly: Object
  },
  emits: ['search-data'],
//   props, { emit }
  setup (props, { emit }) {
    const springbalanceassemblySize = ref(null)
    const springbalanceassemblyType = ref(null)
    const springbalanceassemblyTypeOptions = ref(['-', 'Suit To PTFE Bush', 'Standard'])
    const springbalanceassemblyMaterial = ref(null)
    const springbalanceassemblyMaterialOptions = ref(null)
    const mhCoverBalanceAssembly = ref(null)
    const mhCoverBalanceAssemblyOptions = ref(['-', 'Spring Balance Assembly', 'Cap Balancer Assembly'])

    onMounted(() => {
        const springbalanceassembly = localStorage.getItem('springbalanceassembly')
        const data = JSON.parse(springbalanceassembly)
        if(data !== null){
            mhCoverBalanceAssembly.value = data.mhCoverBalanceAssembly
            springbalanceassemblySize.value = data.springbalanceassemblySize
            springbalanceassemblyType.value = data.springbalanceassemblyType
            springbalanceassemblyMaterial.value = data.springbalanceassemblyMaterial
        }
    })

    const searchSpringbalanceassemblyData = () => {
        const springbalanceassembly = prepareSpringBalanceAssemblyData()
        localStorage.setItem('springbalanceassembly', JSON.stringify(springbalanceassembly))
        emit('search-data', springbalanceassembly)
    }

    const prepareSpringBalanceAssemblyData = () => {
        const data = {
            component: 'SpringBalanceAssembly',
            
            mhCoverBalanceAssembly: mhCoverBalanceAssembly.value? mhCoverBalanceAssembly.value: null,
            springbalanceassemblySize: springbalanceassemblySize.value? springbalanceassemblySize.value: null,
            springbalanceassemblyType: springbalanceassemblyType.value? springbalanceassemblyType.value: null,
            springbalanceassemblyMaterial: springbalanceassemblyMaterial.value? springbalanceassemblyMaterial.value: null
        }
        return data
    }

    const onUpdateAssembly = (val) => {
        if(val === 'Cap Balancer Assembly'){
            springbalanceassemblyMaterialOptions.value = ['-', 'MS-Hard Chrome Plated']
            springbalanceassemblyMaterial.value = springbalanceassemblyMaterialOptions.value[0]
            springbalanceassemblyType.value = springbalanceassemblyTypeOptions.value[2]
        }else if(val === 'Spring Balance Assembly'){
            springbalanceassemblyMaterialOptions.value = ['-', 'MS', 'SS304', 'SS316']
            springbalanceassemblyMaterial.value = null
        }
    }

    const populateInitialData = (data) => {
      const nozzle_services = JSON.parse(data.nozzle_services)
        const nozzle_sizes = JSON.parse(data.nozzle_sizes)
        for (let i = 0; i < nozzle_services.length; i++) {
            if(nozzle_services[i] === 'Manhole'){
                springbalanceassemblySize.value = nozzle_sizes[i]
            }
        }
    }

    return {
        springbalanceassemblySize,
        springbalanceassemblyType,
        springbalanceassemblyTypeOptions,
        springbalanceassemblyMaterial,
        springbalanceassemblyMaterialOptions,
        mhCoverBalanceAssembly,
        mhCoverBalanceAssemblyOptions,

        // Methods
        searchSpringbalanceassemblyData,
        populateInitialData,
        onUpdateAssembly

    }

  },
  watch: {
    springbalanceassembly: {
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