<template>
    <q-page class="q-pa-md">
        <!-- First Row -->
        <div class="q-mb-md">
            <div class="row q-gutter-md q-wrap">
                <q-select
                outlined
                v-model="bovType"
                :options="bovTypeOptions"
                @update:model-value="onUpdateType"
                label="Type"
                dense
                class="col-12 col-md-2"
                />
                <q-select
                outlined
                v-model="bovModel"
                :options="bovModelOptions"
                @update:model-value="onUpdateModel"
                label="Model"
                dense
                class="col-12 col-md-2"
                />

                <q-space/>
                <q-btn outline rounded color="primary" icon="search" label="Search" @click="searchBovData"/>
            </div>
        </div>
        <!-- Second Row -->
        <div class="q-mb-md">
            <div class="row q-gutter-md q-wrap">
                <q-select
                outlined
                v-model="bovGasket"
                :options="bovGasketOptions"
                label="Gasket"
                dense
                class="col-12 col-md-2"
                />
                <q-select
                outlined
                v-model="bovFastenerMaterial"
                :options="bovFastenerMaterialOptions"
                label="Fasteners Material"
                dense
                class="col-12 col-md-2"
                />
            </div>
        </div>
        <div class="q-mb-md">
            <div class="row q-gutter-md q-wrap">
                <q-select
                outlined
                v-model="bovActuatorType"
                :options="bovActuatorTypeOptions"
                label="Actuator Type/Make"
                dense
                class="col-12 col-md-2"
                />
                <q-select
                outlined
                v-model="bovSplitFlangeMaterial"
                :options="bovSplitFlangeMaterialOptions"
                label="Split Flange Material"
                dense
                class="col-12 col-md-2"
                />
                
            </div>
        </div>
        <div class="q-mb-md">
            <div class="row q-gutter-md q-wrap">
                <q-input
                outlined
                v-model="bovProximityLimitSwitch"
                label="Proximity/Limit Switch"
                dense
                class="col-12 col-md-2"
                />
                <q-input
                outlined
                v-model="bovSovType"
                label="SOV Type/Make"
                dense
                class="col-12 col-md-2"
                />
            </div>
        </div>
        <!-- Third Row -->
        <div class="q-mb-md">
            <div class="row q-gutter-md q-wrap">
                <q-input
                outlined
                v-model="bovAFRType"
                label="AFR Type/Make"
                dense
                class="col-12 col-md-2"
                />
                <q-input
                outlined
                v-model="bovRTDType"
                label="RTD Type/Make"
                dense
                class="col-12 col-md-2"
                />
            </div>
        </div>
        <div class="q-mb-md">
            <div class="row q-gutter-md q-wrap">
                <q-input
                outlined
                v-model="bovOther"
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
  name: 'BottomOutletValve',
  props: {
    bov: Object,
    bovMasters: Object
  },
  emits: ['search-data', 'get-bov-masters'],
  setup (props, { emit }) {

    const bovType = ref(null)
    const bovTypeOptions = ref(['-', 'Gland', 'Bellow'])
    const bovModelTypeSize = ref([{model: '201', type: 'Gland', size: '100', actuator: null},
        {model: '201', type: 'Gland', size: '100', actuator: null},
        {model: '202', type: 'Gland', size: '80', actuator: null},
        {model: '203', type: 'Gland', size: '50', actuator: null},
        {model: '204', type: 'Gland', size: '150', actuator: null},
        {model: '901', type: 'Gland', size: '100', actuator: ['VKE']},
        {model: '902', type: 'Gland', size: '80', actuator: ['VKE']},
        {model: '903', type: 'Gland', size: '50', actuator: ['VKE']},
        {model: '904', type: 'Gland', size: '150', actuator: ['VKE']},
        {model: '2801', type: 'Gland', size: '100', actuator: null},
        {model: '2802', type: 'Gland', size: '80', actuator: null},
        {model: '2803', type: 'Gland', size: '50', actuator: null},
        {model: '2804', type: 'Gland', size: '150', actuator: null},
        {model: '701', type: 'Gland', size: '100', actuator: null},
        {model: '702', type: 'Gland', size: '80', actuator: null},
        {model: '703', type: 'Gland', size: '50', actuator: null},
        {model: '704', type: 'Gland', size: '150', actuator: null},
        {model: '1701', type: 'Gland', size: '100', actuator: ['VKE']},
        {model: '1702', type: 'Gland', size: '80', actuator: ['VKE']},
        {model: '1703', type: 'Gland', size: '50', actuator: ['VKE']},
        {model: '1704', type: 'Gland', size: '150', actuator: ['VKE']},
        {model: '801', type: 'Gland', size: '100', actuator: null},
        {model: '802', type: 'Gland', size: '80', actuator: null},
        {model: '803', type: 'Gland', size: '50', actuator: null},
        {model: '804', type: 'Gland', size: '150', actuator: null},
        {model: '1901', type: 'Gland', size: '100', actuator: ['VKE']},
        {model: '1902', type: 'Gland', size: '80', actuator: ['VKE']},
        {model: '1903', type: 'Gland', size: '50', actuator: ['VKE']},
        {model: '1904', type: 'Gland', size: '150', actuator: ['VKE']},
        {model: '301', type: 'Bellow', size: '100', actuator: null},
        {model: '302', type: 'Bellow', size: '80', actuator: null},
        {model: '303', type: 'Bellow', size: '50', actuator: null},
        {model: '304', type: 'Bellow', size: '150', actuator: null},
        {model: '401', type: 'Bellow', size: '100', actuator: ['VKE']},
        {model: '402', type: 'Bellow', size: '80', actuator: ['VKE']},
        {model: '403', type: 'Bellow', size: '50', actuator: ['VKE']},
        {model: '404', type: 'Bellow', size: '150', actuator: ['VKE']},
        {model: '1801', type: 'Bellow', size: '100', actuator: ['Demble', 'Aira']},
        {model: '1802', type: 'Bellow', size: '80', actuator: ['Demble', 'Aira']},
        {model: '1803', type: 'Bellow', size: '50', actuator: ['Demble', 'Aira']},
        {model: '1804', type: 'Bellow', size: '150', actuator: ['Demble', 'Aira']},
        {model: '601', type: 'Bellow', size: '100', actuator: null},
        {model: '602', type: 'Bellow', size: '80', actuator: null},
        {model: '603', type: 'Bellow', size: '50', actuator: null},
        {model: '604', type: 'Bellow', size: '150', actuator: null},
        {model: '501', type: 'Bellow', size: '100', actuator: ['VKE']},
        {model: '502', type: 'Bellow', size: '80', actuator: ['VKE']},
        {model: '503', type: 'Bellow', size: '50', actuator: ['VKE']},
        {model: '504', type: 'Bellow', size: '150', actuator: ['VKE']},
        {model: '2701', type: 'Bellow', size: '100', actuator: ['Demble', 'Aira']},
        {model: '2702', type: 'Bellow', size: '80', actuator: ['Demble', 'Aira']},
        {model: '2703', type: 'Bellow', size: '50', actuator: ['Demble', 'Aira']},
        {model: '2704', type: 'Bellow', size: '150', actuator: ['Demble', 'Aira']},
    ])
    const bovModel = ref(null)
    const bovModelOptions = ref([])
    const bovGasket = ref(null)
    const bovGasketOptions = ref([])
    const bovFastenerMaterial = ref(null)
    const bovFastenerMaterialOptions = ref([])
    const bovSplitFlangeMaterial = ref(null)
    const bovSplitFlangeMaterialOptions = ref([])
    const bovActuatorType = ref(null)
    const bovActuatorTypeOptions = ref([])
    const bovProximityLimitSwitch = ref(null)
    const bovSovType = ref(null)
    const bovAFRType = ref(null)
    const bovRTDType = ref(null)
    const bovOther = ref(null)
    const nozzleLSize = ref(null)

    onMounted(() => {
        getMastrers()
    })

    const getMastrers = () => {
        const bovMasters = {
            component: 'bov',
            master_material_gasket: null,
            master_material_fasteners_pressure: null,
            master_material_split: null
        }
        emit('get-bov-masters', bovMasters)
    }

    const searchBovData = () => {
        const data = prepareBovData()
        emit('search-data', data)
    }

    const prepareBovData = () => {
        const bovData = {
            component:'BOV',
            bovType: bovType.value? bovType.value: null,
            bovModel: bovModel.value? bovModel.value: null,
            bovGasket: bovGasket.value? bovGasket.value: null,
            bovFastenerMaterial: bovFastenerMaterial.value? bovFastenerMaterial.value: null,
            bovSplitFlangeMaterial: bovSplitFlangeMaterial.value? bovSplitFlangeMaterial.value: null,
            bovActuatorType:  bovActuatorType.value? bovActuatorType.value: null,
            bovProximityLimitSwitch: bovProximityLimitSwitch.value? bovProximityLimitSwitch.value: null,
            bovSovType: bovSovType.value? bovSovType.value: null,
            bovAFRType:  bovAFRType.value? bovAFRType.value: null,
            bovRTDType: bovRTDType.value? bovRTDType.value: null,
            bovOther: bovOther.value? bovOther.value: null
        }
        return bovData
    }

    const populateInitialData = (data) => {
        const nozzle_names = JSON.parse(data.nozzle_names)
        const nozzle_sizes = JSON.parse(data.nozzle_sizes)
        for (let i = 0; i < nozzle_names.length; i++) {
            if(nozzle_names[i] === 'L'){
                nozzleLSize.value = nozzle_sizes[i]
            }
        }
        bovGasket.value = data.gasket
        bovFastenerMaterial.value = data.fastener
        bovSplitFlangeMaterial.value = data.split_flange
    }

    const onUpdateType = (val) => {
        const results = filterByTypeAndSize(val, nozzleLSize.value)
        const models = results.map(item => item.model)
        bovModelOptions.value.splice(0, bovModelOptions.value.length)
        bovModelOptions.value.push('-')
        bovModelOptions.value.push(...models)
    }

    const onUpdateModel = (val) => {
        const modelObj = bovModelTypeSize.value.filter(item => item.model === val);
        if(modelObj.length === 1){
            if(modelObj[0].actuator !== null && modelObj[0].actuator.length === 1){
                bovActuatorTypeOptions.value.splice(0, bovActuatorTypeOptions.value.length)
                bovActuatorTypeOptions.value.push('-')
                bovActuatorTypeOptions.value.push(...modelObj[0].actuator)
                bovActuatorType.value = bovActuatorTypeOptions.value[1]
            }
            else if(modelObj[0].actuator !== null && modelObj[0].actuator.length === 2){
                bovActuatorTypeOptions.value.splice(0, bovActuatorTypeOptions.value.length)
                bovActuatorType.value = null
                bovActuatorTypeOptions.value.push('-')
                bovActuatorTypeOptions.value.push(...modelObj[0].actuator)
            }
            else if(modelObj[0].actuator === null){
                bovActuatorTypeOptions.value.splice(0, bovActuatorTypeOptions.value.length)
                bovActuatorTypeOptions.value.push('-')
                bovActuatorType.value = bovActuatorTypeOptions.value[0]
            }
        }
        else{
            bovActuatorTypeOptions.value.splice(0, bovActuatorTypeOptions.value)
            bovActuatorTypeOptions.value.push('-')
            bovActuatorType.value = bovActuatorTypeOptions.value[0]
        }
    }

    const populateMasterData = (masters) => {
        const gasket = masters.master_material_gasket.map(item => item.name)
        bovGasketOptions.value.splice(0, bovGasketOptions.value.length)
        bovGasketOptions.value.push('-')
        bovGasketOptions.value.push(...gasket)

        const fasteners = masters.master_material_fasteners_pressure.map(item => item.name)
        bovFastenerMaterialOptions.value.splice(0, bovFastenerMaterialOptions.value.length)
        bovFastenerMaterialOptions.value.push('-')
        bovFastenerMaterialOptions.value.push(...fasteners)

        const splits = masters.master_material_split.map(item => item.name)
        bovSplitFlangeMaterialOptions.value.splice(0, bovSplitFlangeMaterialOptions.value.length)
        bovSplitFlangeMaterialOptions.value.push('-')
        bovSplitFlangeMaterialOptions.value.push(...splits)

    }

    function filterByTypeAndSize(type, size) {
        return bovModelTypeSize.value.filter(item => item.type === type && item.size === size);
    }

    return {
      bovModelTypeSize,
      bovType,
      bovTypeOptions,
      bovModel,
      bovModelOptions,
      bovGasket,
      bovGasketOptions,
      bovFastenerMaterial,
      bovFastenerMaterialOptions,
      bovSplitFlangeMaterial,
      bovSplitFlangeMaterialOptions,
      bovActuatorType,
      bovActuatorTypeOptions,
      bovProximityLimitSwitch,
      bovSovType,
      bovAFRType,
      bovRTDType,
      bovOther,
      nozzleLSize,

    //   Methods
      getMastrers,
      searchBovData,
      filterByTypeAndSize,
      populateMasterData,
      populateInitialData,
      onUpdateType,
      onUpdateModel

    }

  },
  watch: {
    bovMasters: {
      handler(newVal) {
        if (newVal !== null) {
          this.populateMasterData(newVal);
        }
      },
      immediate: true
    },
    bov: {
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