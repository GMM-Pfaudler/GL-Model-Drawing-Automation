<template>
    <q-page class="q-pa-md">
        <div class="q-mb-md">
            <div class="row q-gutter-md q-wrap">
                <q-select
                outlined
                v-model="gearboxMake"
                :options="gearboxMakeOptions"
                label="Make"
                dense
                class="col-12 col-md-2"
                />
                <q-space/>
                <q-btn outline rounded color="primary" icon="search" label="Search" @click="searchGearboxData"/>
            </div>
        </div>
        <div class="q-mb-md">
            <div class="row q-gutter-md q-wrap">
                <q-select
                outlined
                v-model="gearboxType"
                :options="gearboxTypeOptions"
                label="Type"
                dense
                class="col-12 col-md-2"
                />
            </div>
        </div>
        <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap">

            <q-input
            outlined
            v-model="gearboxModel"
            label="Model"
            dense
            class="col-12 col-md-2"
            />
        </div>
    </div>
    <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap">

            <q-input
            outlined
            v-model="gearboxRatio"
            label="Ratio"
            dense
            class="col-12 col-md-2"
            />
        </div>
    </div>
    <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap">

            <q-input
            outlined
            v-model="gearboxFrame"
            label="Frame"
            dense
            class="col-12 col-md-2"
            />
        </div>
    </div>
    </q-page>
</template>
<script>
import { onMounted, ref } from 'vue'
import emitter from '../event-bus.js';
export default {
  name: 'GearBoxComponent',
  props: {
    gearbox: Object,
    gearboxMasters: Object
  },
  emits: ['search-data', 'get-gearbox-masters'],
  setup ( props, { emit }) {
    const gear = ref(null)
    const gearboxMake = ref(null)
    const gearboxMakeOptions = ref([])
    const gearboxType = ref(null)
    const gearboxTypeOptions = ref([])
    const gearboxModel = ref(null)
    const gearboxModelOptions = ref(['-', 'Model1', 'Model2', 'Model3'])
    const gearboxRatio = ref(null)
    const gearboxRatioOptions = ref(['-', 'Ratio1', 'Ratio2', 'Ratio3'])
    const gearboxFrame = ref(null)
    const gearboxFrameOptions = ref(['-', 'Frame1', 'Frame2', 'Frame3'])
    
    

    onMounted(() => {
        getMaters()
        const data = localStorage.getItem('gearbox')
        const gearboxData = JSON.parse(data)
        if(gearboxData !== null){
            gearboxMake.value = gearboxData.gearboxMake
            gearboxType.value = gearboxData.gearboxType
            gearboxModel.value = gearboxData.gearboxModel
            gearboxRatio.value = gearboxData.gearboxRatio
            gearboxFrame.value = gearboxData.gearboxFrame
        }
        
    })

    const searchGearboxData = () => {
        const gearbox = prepareGearboxData()
        localStorage.setItem('gearbox', JSON.stringify(gearbox))
        emit('search-data', gearbox)
        emitter.emit('custom-event-gearbox', gearbox);
    }

    const prepareGearboxData = () => {
        const gearboxData = {
            component:'Gearbox',
            gearboxMake: gearboxMake.value?gearboxMake.value:null,
            gearboxType: gearboxType.value?gearboxType.value:null,
            gearboxModel: gearboxModel.value?gearboxModel.value:null,
            gearboxRatio: gearboxRatio.value?gearboxRatio.value:null,
            gearboxFrame: gearboxFrame.value?gearboxFrame.value:null
        }
        return gearboxData
    }

    const getMaters = () => {
        const gearboxMasters = {
            component: 'gearbox',
            master_drive_gear_make: null,
            master_drive_gear_type: null
        }
        emit('get-gearbox-masters', gearboxMasters)
    }

    const populateInitialData = (data, masters) => {
        const make = masters.master_drive_gear_make.map(item => item.name)
        gearboxMakeOptions.value.splice(0, gearboxMakeOptions.value.length)
        gearboxMakeOptions.value.push(...make)
        gearboxMake.value = data.gear_make

        const type = masters.master_drive_gear_type.map(item => item.name)
        gearboxTypeOptions.value.splice(0, gearboxTypeOptions.value.length)
        gearboxTypeOptions.value.push(...type)
        gearboxType.value = data.gear_type
    }

    return {
        gear,
        gearboxMake,
        gearboxMakeOptions,
        gearboxType,
        gearboxTypeOptions,
        gearboxModel,
        gearboxModelOptions,
        gearboxRatio,
        gearboxRatioOptions,
        gearboxFrame,
        gearboxFrameOptions,

        // Methods
        getMaters,
        populateInitialData,
        searchGearboxData,
        prepareGearboxData
    }
  },
  watch: {
    gearboxMasters: {
      handler(newVal) {
        if (newVal !== null && this.gearbox !== null) {
          this.populateInitialData(this.gearbox, newVal);
        }
      },
      immediate: true
    }
  }
}
</script>