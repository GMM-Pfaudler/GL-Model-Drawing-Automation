<template>
    <q-page class="q-pa-md">
        <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap">
            <q-select
            outlined
            v-model="mhCClampMaterial"
            :options="mhCClampMaterialOptions"
            @update:model-value="onUpdateAssembly"
            label="Material"
            dense
            class="col-12 col-md-2"
            />

            <q-space/>
            <q-btn outline rounded color="primary" icon="search" label="Search" @click="searchManholeCClampData"/>
        </div>
    </div>
     <!-- First Row -->
    <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap">
            <q-input
            outlined
            v-model="mhCClampSize"
            label="Size"
            dense
            class="col-12 col-md-2"
            />
        </div>
    </div>
    <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap">
            <q-input
            outlined
            v-model="mhCClampQty"
            label="Quantity"
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
  name: 'ManholeCClamp',
  props: {
    manholeCClamp: Object,
    manholeCClampMasters: Object
  },
  emits: ['search-data', 'get-mh-masters'],
  setup (props, { emit }) {
    const mhCClampMaterial = ref(null)
    const mhCClampMaterialOptions = ref([])
    const mhCClampSize = ref(null)
    const mhCClampQty = ref(null)

    onMounted(() => {
        getMasters()
        const manholecclamp = localStorage.getItem('manholecclamp')
        const data = JSON.parse(manholecclamp)
        if(data !== null){
          mhCClampMaterial.value = data.mhCClampMaterial
          mhCClampQty.value = data.mhCClampQty
          mhCClampSize.value = data.mhCClampSize
        }
    })

    const getMasters = () => {
        const masters = {
            component: 'manholecclamp',
            master_material_hclamp: null
        }
        emit('get-mh-masters', masters)
    }


    const searchManholeCClampData = () => {
        const data = prepareManholeCClampData()
        emit('search-data', data)
    }

    const prepareManholeCClampData = () => {
        const manholeCClamp = {
            component: 'ManholeCClamp',
            mhCClampMaterial: mhCClampMaterial.value?mhCClampMaterial.value:null,
            mhCClampSize: mhCClampSize.value?mhCClampSize.value:null,
            // mhCClampQty: mhCClampQty.value?mhCClampQty.value:null,
        }
        const manholeCClamp_storing_data = {
            component: 'ManholeCClamp',
            mhCClampMaterial: mhCClampMaterial.value?mhCClampMaterial.value:null,
            mhCClampSize: mhCClampSize.value?mhCClampSize.value:null,
            mhCClampQty: mhCClampQty.value?mhCClampQty.value:null,
        }
        localStorage.setItem('manholecclamp', JSON.stringify(manholeCClamp_storing_data))
        return manholeCClamp
    }

    const populateInitialData = (masters) => {
        const material = masters.master_material_hclamp.map(item => item.name)
        mhCClampMaterialOptions.value.splice(0, mhCClampMaterialOptions.value.length)
        mhCClampMaterialOptions.value.push(...material)
    }

    return {
        mhCClampMaterial,
        mhCClampMaterialOptions,
        mhCClampSize,
        mhCClampQty,

        // Methods
        getMasters,
        populateInitialData,
        searchManholeCClampData,
    }
  },
  watch: {
    manholeCClampMasters: {
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