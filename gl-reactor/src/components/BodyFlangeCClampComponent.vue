<template>
    <q-page class="q-pa-md">
        <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap">
            <q-select
            outlined
            v-model="bfCClampMaterial"
            :options="bfCClampMaterialOptions"
            @update:model-value="onUpdateAssembly"
            label="Material"
            dense
            class="col-12 col-md-2"
            />

            
        </div>
    </div>
     <!-- First Row -->
    <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap">
            <q-input
            outlined
            v-model="bfCClampSize"
            label="Size"
            type="text"
            dense
            class="col-12 col-md-2"
            />

            <q-space/>
            <q-btn outline rounded color="primary" icon="search" label="Search" @click="searchBodyFlangeCClampData"/>
        </div>
    </div>
    <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap">
            <q-select
            outlined
            v-model="bfCClampQty"
            :options="bfCClampQtyOptions"
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
  name: 'BodyFlangeCClamp',
  props: {
    bodyFlangeCClamp: Object,
    bodyFlangeCClampMasters: Object
  },
  emits: ['search-data', 'get-bf-masters'],
  setup (props, { emit }) {
    const bfCClampMaterial = ref(null)
    const bfCClampMaterialOptions = ref([])
    const bfCClampSize = ref(null)
    const bfCClampQty = ref(null)
    const bfCClampQtyOptions = ref(['-', '10', '12', '14', '16'])

    onMounted(() => {
        getMasters()
      const bfcclamp = localStorage.getItem('bfcclamp')
        const data = JSON.parse(bfcclamp)
        if(data !== null){
          bfCClampMaterial.value = data.bfCClampMaterial
          bfCClampQty.value = data.bfCClampQty
          bfCClampSize.value = data.bfCClampSize
        }
    })

    const getMasters = () => {
      const bfMasters = {
        component:'bfcclamp',
        master_material_hclamp: null
      }
      emit('get-bf-masters', bfMasters)
    }

    const searchBodyFlangeCClampData = () => {
        const data = prepareBodyFlangeCClampData()
        emit('search-data', data)
    }

    const prepareBodyFlangeCClampData = () => {
        const bfCClamp = {
            component: 'BodyFlangeCClamp',
            bfCClampMaterial: bfCClampMaterial.value?bfCClampMaterial.value:null,
            bfCClampSize: bfCClampSize.value?bfCClampSize.value:null,
            bfCClampQty: bfCClampQty.value?bfCClampQty.value:null,
        }
        localStorage.setItem('bfcclamp', JSON.stringify(bfCClamp))
        return bfCClamp
    }

    const populateInitialData = (masters) => {
      const material = masters.master_material_hclamp.map(item => item.name)
        bfCClampMaterialOptions.value.splice(0, bfCClampMaterialOptions.value.length)
        bfCClampMaterialOptions.value.push(...material)
    }

    return {
      bfCClampMaterial,
      bfCClampMaterialOptions,
      bfCClampSize,
      bfCClampQty,
      bfCClampQtyOptions,

      // Methods
      getMasters,
      populateInitialData,
      searchBodyFlangeCClampData
    }

  },
  watch: {
    bodyFlangeCClampMasters: {
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