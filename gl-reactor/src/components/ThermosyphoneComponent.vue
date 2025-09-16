<template>
    <q-page class="q-pa-md">
        <div class="q-mb-md">
            <div class="row q-gutter-md q-wrap">
                <q-select
                outlined
                v-model="thermosyphoneMake"
                :options="thermosyphoneMakeOptions"
                label="Make"
                dense
                class="col-12 col-md-2"
                />
                <q-space/>
                <q-btn outline rounded color="primary" icon="search" label="Search" @click="searchThermosyphoneData"/>
            </div>
        </div>
        <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap">

            <q-select
            outlined
            v-model="thermosyphoneMaterial"
            :options="thermosyphoneMaterialOptions"
            label="Material"
            dense
            class="col-12 col-md-2"
            />
        </div>
    </div>
    <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap">

            <q-select
            outlined
            v-model="cleatType"
            :options="cleatTypeOptions"
            label="Cleat Type"
            dense
            class="col-12 col-md-2"
            />
        </div>
    </div>
    <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap">

            <q-select
            outlined
            v-model="cleatMaterial"
            :options="cleatMaterialOptions"
            label="Cleat Material"
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
  name: 'ThermosyphoneComponent',
  props: {
    thermosyphone: Object,
    thermosyphoneMasters: Object
  },
  emits: ['search-data', 'get-thermosyphone-masters'],
  setup (props, { emit }) {
    const thermosyphonestemp = ref(null)
    const thermosyphoneMake = ref(null)
    const thermosyphoneMakeOptions = ref([])
    const thermosyphoneMaterial = ref(null)
    const thermosyphoneMaterialOptions = ref([])
    const cleatType = ref(null)
    const cleatTypeOptions = ref(['-', 'Suit to Hi-fab', 'EBIPL'])
    const cleatMaterial = ref(null)
    const cleatMaterialOptions = ref([])

    onMounted(() => {
        getMaters()
        const data = localStorage.getItem('thermosyphoneData')
        const thermosyphoneData = JSON.parse(data)
        if(thermosyphoneData !== null){
            thermosyphoneMake.value = thermosyphoneData.thermosyphoneMake
            thermosyphoneMaterial.value = thermosyphoneData.thermosyphoneMaterial
            cleatType.value = thermosyphoneData.cleatType
            cleatMaterial.value = thermosyphoneData.cleatMaterial
        }
    })

    const searchThermosyphoneData = () => {
        const data = prepareThermosyphoneData()
        localStorage.setItem('thermosyphoneData', JSON.stringify(data))
        emit('search-data', data)
    }

    const prepareThermosyphoneData = () => {
        const thermosyphoneData = {
            component: 'Thermosyphone',
            thermosyphoneMake: thermosyphoneMake.value?thermosyphoneMake.value:null,
            thermosyphoneMaterial: thermosyphoneMaterial.value?thermosyphoneMaterial.value:null,
            cleatType: cleatType.value?cleatType.value:null,
            cleatMaterial: cleatMaterial.value?cleatMaterial.value:null
        }
        return thermosyphoneData
    }

    const getMaters = () => {
        const thermosyphoneMasters = {
            component: 'thermosyphone',
            master_drive_thermo_make: null,
            master_drive_thermo_material: null
        }
        emit('get-thermosyphone-masters', thermosyphoneMasters)
    }

    const populateInitialData = (masters) =>{
        const material = masters.master_drive_thermo_material.map(item => item.name)
        thermosyphoneMaterialOptions.value.splice(0, thermosyphoneMaterialOptions.value.length)
        thermosyphoneMaterialOptions.value.push(...material)
        cleatMaterialOptions.value.splice(0, cleatMaterialOptions.value.length)
        cleatMaterialOptions.value.push(...material)

        const make = masters.master_drive_thermo_make.map(item => item.name)
        thermosyphoneMakeOptions.value.splice(0, thermosyphoneMakeOptions.value.length)
        thermosyphoneMakeOptions.value.push(...make)
    }

    return {
        thermosyphonestemp,
        thermosyphoneMake,
        thermosyphoneMakeOptions,
        thermosyphoneMaterial,
        thermosyphoneMaterialOptions,
        cleatType,
        cleatTypeOptions,
        cleatMaterial,
        cleatMaterialOptions,

        // Methods
        getMaters,
        searchThermosyphoneData,
        populateInitialData
    }
  },
  watch: {
    thermosyphoneMasters: {
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