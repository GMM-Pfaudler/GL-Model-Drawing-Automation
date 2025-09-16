<template>
  <q-page class="q-pa-md">
     <!-- First Row for Additional Jacket Fields -->
    <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap">
            <q-select
            outlined
            v-model="shaftclosureDia"
            :options="shaftclosureDiaTypeOptions"
            label="Shaft Dia @ Sealing"
            dense
            class="col-12 col-md-2"
            />
            <q-select
            outlined
            v-model="shaftclosureType"
            :options="shaftclosureTypeOptions"
            label="Type"
            dense
            class="col-12 col-md-2"
            />

            <q-select
            v-if="shaftclosureType !== 'Stuffing Box'"
            outlined
            v-model="shaftclosureMake"
            :options="shaftclosureMakeOptions"
            label="Make"
            dense
            class="col-12 col-md-2"
            />

            <q-select
            v-if="shaftclosureType !== 'Stuffing Box'"
            outlined
            v-model="shaftclosureSealing"
            :options="shaftclosureSealingOptions"
            label="Sealing"
            dense
            class="col-12 col-md-2"
            />

            <q-space/>
            <q-btn outline rounded color="primary" icon="search" label="Search" @click="searchShaftClosureData"/>
        </div>
    </div>

    <!-- Second Row for Additional Jacket Fields -->
    <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap">

            <q-select
            v-if="shaftclosureType !== 'Stuffing Box'"
            outlined
            v-model="shaftclosureHousing"
            :options="shaftclosureHousingOptions"
            label="Housing"
            dense
            class="col-12 col-md-2"
            />

            <q-select
            v-if="shaftclosureType !== 'Stuffing Box'"
            outlined
            v-model="shaftclosureInboardFace"
            :options="shaftclosureInboardFaceOptions"
            label="Inboard Face"
            dense
            class="col-12 col-md-2"
            />

            <q-select
            v-if="(shaftclosureType !== 'Single Mechanical Seal') && (shaftclosureType !== 'Stuffing Box')"
            outlined
            v-model="shaftclosureOutboardFace"
            :options="shaftclosureOutboardFaceOptions"
            label="Outboard Face"
            dense
            class="col-12 col-md-2"
            />
            <q-input
            v-if="shaftclosureType !== 'Stuffing Box'"
            outlined
            v-model="shaftclosureOther"
            type="text"
            label="Other"
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
  name: 'ShaftClosureComponent',
  props: {
    shaftclosure: Object,
    shaftclosureMasters: Object
  },
  emits: ['search-data', 'get-shaftclosure-masters'],

  setup (props, { emit }) {
    const shaftclosureDia = ref(null)
    const shaftclosureDiaTypeOptions = ref([])
    const shaftclosureType = ref(null)
    const shaftclosureTypeOptions = ref([])
    const shaftclosureMake = ref(null)
    const shaftclosureMakeOptions = ref([])
    const shaftclosureSealing = ref(null)
    const shaftclosureSealingOptions = ref([])
    const shaftclosureHousing = ref(null)
    const shaftclosureHousingOptions = ref([])
    const shaftclosureInboardFace = ref(null)
    const shaftclosureInboardFaceOptions = ref([])
    const shaftclosureOutboardFace = ref(null)
    const shaftclosureOutboardFaceOptions = ref([])
    const shaftclosureOther = ref(null)

    onMounted(() => {
        getMasters()
        const data = localStorage.getItem('shaftClosureData')
        const shaftClosureData = JSON.parse(data);
        if(shaftClosureData !== null){
          shaftclosureDia.value = shaftClosureData.shaftclosureDia
          shaftclosureType.value = shaftClosureData.shaftclosureType
          shaftclosureMake.value = shaftClosureData.shaftclosureMake
          shaftclosureSealing.value = shaftClosureData.shaftclosureSealing
          shaftclosureHousing.value = shaftClosureData.shaftclosureHousing
          shaftclosureInboardFace.value = shaftClosureData.shaftclosureInboardFace
          shaftclosureOutboardFace.value = shaftClosureData.shaftclosureOutboardFace
          shaftclosureOther.value = shaftClosureData.shaftclosureOther
        }
    })

    const searchShaftClosureData = () => {
        const shaftClosureData = prepareShaftClosureData()
        localStorage.setItem('shaftClosureData', JSON.stringify(shaftClosureData))
        emit('search-data', shaftClosureData)

    }

    const prepareShaftClosureData = () => {
      if(shaftclosureType.value === 'Single Mechanical Seal'){
        shaftclosureOutboardFace.value = null
      }
      else if(shaftclosureType.value === 'Stuffing Box'){
        shaftclosureHousing.value = null
        shaftclosureSealing.value = null
        shaftclosureMake.value = null
        shaftclosureInboardFace.value = null
        shaftclosureOutboardFace.value = null
        shaftclosureOther.value = null
      }
      const shaftClosureData = {
        component: 'Shaftclosure',
        shaftclosureDia: shaftclosureDia.value?shaftclosureDia.value:null,
        shaftclosureType: shaftclosureType.value?shaftclosureType.value:null,
        shaftclosureMake: shaftclosureMake.value?shaftclosureMake.value:null,
        shaftclosureSealing: shaftclosureSealing.value?shaftclosureSealing.value:null,
        shaftclosureHousing: shaftclosureHousing.value?shaftclosureHousing.value:null,
        shaftclosureInboardFace: shaftclosureInboardFace.value?shaftclosureInboardFace.value:null,
        shaftclosureOutboardFace: shaftclosureOutboardFace.value?shaftclosureOutboardFace.value:null,
        shaftclosureOther: shaftclosureOther.value?shaftclosureOther.value:null
      }
      return shaftClosureData
    }

    const getMasters = () => {
        const shaftclosureMasters = {
            component: 'shftclosure',
            master_drive_shaft_type: null,
            master_drive_shaft_make: null,
            master_drive_shaft_sealing: null,
            master_drive_shaft_housing: null,
            master_drive_shaft_inborad: null,
            master_drive_shaft_outborad: null
        }
        emit('get-shaftclosure-masters', shaftclosureMasters)
    }

    const populateInitialData = (data, masters) => {
        const type = masters.master_drive_shaft_type.map(item => item.name)
        shaftclosureTypeOptions.value.splice(0, shaftclosureTypeOptions.value.length)
        shaftclosureTypeOptions.value.push(...type)

        const make = masters.master_drive_shaft_make.map(item => item.name)
        shaftclosureMakeOptions.value.splice(0, shaftclosureMakeOptions.value.length)
        shaftclosureMakeOptions.value.push(...make)

        const sealing = masters.master_drive_shaft_sealing.map(item => item.name)
        shaftclosureSealingOptions.value.splice(0, shaftclosureSealingOptions.value.length)
        shaftclosureSealingOptions.value.push(...sealing)

        const housing = masters.master_drive_shaft_housing.map(item => item.name)
        shaftclosureHousingOptions.value.splice(0, shaftclosureHousingOptions.value.length)
        shaftclosureHousingOptions.value.push(...housing)

        const inboard = masters.master_drive_shaft_inborad.map(item => item.name)
        shaftclosureInboardFaceOptions.value.splice(0, shaftclosureInboardFaceOptions.value.length)
        shaftclosureInboardFaceOptions.value.push(...inboard)

        const outboard = masters.master_drive_shaft_outborad.map(item => item.name)
        shaftclosureOutboardFaceOptions.value.splice(0, shaftclosureOutboardFaceOptions.value.length)
        shaftclosureOutboardFaceOptions.value.push(...outboard)

        // Shaft Closure initial data
        shaftclosureDia.value = data.shaft_dia
        shaftclosureType.value = data.shaft_type
        shaftclosureMake.value = data.shaft_make
        shaftclosureSealing.value = data.shaft_sealing
        shaftclosureHousing.value = data.shaft_housing
        shaftclosureInboardFace.value = data.shaft_inboard
        shaftclosureOutboardFace.value = data.shaft_outboard
        shaftclosureOther.value = data.shaft_other
    }

    return {
        shaftclosureDia,
        shaftclosureDiaTypeOptions,
        shaftclosureType,
        shaftclosureTypeOptions,
        shaftclosureMake,
        shaftclosureMakeOptions,
        shaftclosureSealing,
        shaftclosureSealingOptions,
        shaftclosureHousing,
        shaftclosureHousingOptions,
        shaftclosureInboardFace,
        shaftclosureInboardFaceOptions,
        shaftclosureOutboardFace,
        shaftclosureOutboardFaceOptions,
        shaftclosureOther,

        // Methods
        searchShaftClosureData,
        getMasters,
        populateInitialData
    }
  },
  watch: {
    shaftclosureMasters: {
      handler(newVal) {
        if (newVal !== null && this.shaftclosure != null) {
          this.populateInitialData(this.shaftclosure, newVal);
        }
      },
      immediate: true
    }
  }
}
</script>