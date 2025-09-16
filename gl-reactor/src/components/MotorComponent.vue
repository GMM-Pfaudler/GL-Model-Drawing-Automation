<template>
    <q-page class="q-pa-md">
     <!-- First Row -->
    <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap">
            <q-select
            outlined
            v-model="motorMake"
            :options="motorMakeOptions"
            label="Make"
            dense
            class="col-12 col-md-2"
            />
            <q-select
            outlined
            v-model="motorType"
            :options="motorTypeOptions"
            label="Type"
            dense
            class="col-12 col-md-2"
            />

            <q-select
            outlined
            v-model="motorMouting"
            :options="motorMoutingOptions"
            label="Mounting"
            dense
            class="col-12 col-md-2"
            />

            <q-space/>
            <q-btn outline rounded color="primary" icon="search" label="Search" @click="searchMotorData"/>
        </div>
    </div>

    <!-- Second Row -->
    <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap">

            <q-select
            outlined
            v-model="motorHP"
            :options="motorHPOptions"
            label="Motor HP"
            dense
            class="col-12 col-md-2"
            />

            <q-select
            outlined
            v-model="motorStandard"
            :options="motorStandardOptions"
            label="Motor Standards"
            dense
            class="col-12 col-md-2"
            />

            <q-select
            outlined
            v-model="motorFrame"
            :options="motorFrameOptions"
            label="Frame"
            dense
            class="col-12 col-md-2"
            />
        </div>
    </div>
    <!-- Three Row -->
    <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap">

            <q-select
            outlined
            v-model="motorTempClass"
            :options="motorTempClassOptions"
            label="Temperature Class"
            dense
            class="col-12 col-md-2"
            />

            <q-select
            outlined
            v-model="motorGasGroup"
            :options="motorGasGroupOptions"
            label="Gas Group"
            dense
            class="col-12 col-md-2"
            />

            <q-select
            outlined
            v-model="motorProtection"
            :options="motorProtectionOptions"
            label="Protection"
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
  name: 'MotorComponent',
  props: {
    motor: Object,
    motorMasters: Object
  },
  emits: ['search-data', 'get-motor-masters'],
  setup (props, { emit }) {
    const motorMake = ref(null)
    const motorMakeOptions = ref([])
    const motorType = ref(null)
    const motorTypeOptions = ref([])
    const motorMouting = ref(null)
    const motorMoutingOptions = ref([])
    const motorHP = ref(null)
    const motorHPOptions = ref([])
    const motorStandard = ref(null)
    const motorStandardOptions = ref([])
    const motorFrame = ref(null)
    const motorFrameOptions = ref(['-', 'Frame1', 'Frame2', 'Frame3'])
    const motorTempClass = ref(null)
    const motorTempClassOptions = ref(['-', 'TempClass1', 'TempClass2', 'TempClass3'])
    const motorGasGroup = ref(null)
    const motorGasGroupOptions = ref(['-', 'GasGroup1', 'GasGroup2', 'GasGroup3'])
    const motorProtection = ref(null)
    const motorProtectionOptions = ref(['-', 'Protection1', 'Protection2', 'Protection3'])

    onMounted(() => {
        getMasters()
        const data = localStorage.getItem('motor')
        const motorData = JSON.parse(data)
        if(motorData !== null){
            motorMake.value = motorData.motorMake
            motorType.value = motorData.motorType
            motorMouting.value = motorData.motorMouting
            motorHP.value = motorData.motorHP
            motorStandard.value = motorData.motorStandard
            motorFrame.value = motorData.motorFrame
            motorTempClass.value = motorData.motorTempClass
            motorGasGroup.value = motorData.motorGasGroup
            motorProtection.value = motorData.motorProtection
        }
    })

    const getMasters = () => {
        const motorMasters = {
            component: 'motor',
            master_drive_motor_type_1: null,
            master_drive_motor_type_2: null,
            master_drive_motor_make: null,
            master_drive_motor_mounting: null,
            master_drive_hp: null
        }
        emit('get-motor-masters', motorMasters)
    }

    const searchMotorData = () => {
        const data = prepareMotorData()
        emit('search-data', data)
    }

    const prepareMotorData = () => {
        const motor = {
            component: 'Motor',
            motorMake: motorMake.value?motorMake.value:null,
            motorType: motorType.value?motorType.value:null,
            motorMouting: motorMouting.value?motorMouting.value:null,
            motorHP: motorHP.value?motorHP.value:null,
            motorStandard: motorStandard.value?motorStandard.value:null,
            motorFrame: motorFrame.value?motorFrame.value:null,
            motorTempClass: motorTempClass.value?motorTempClass.value:null,
            motorGasGroup: motorGasGroup.value?motorGasGroup.value:null,
            motorProtection: motorProtection.value?motorProtection.value:null
        }
        localStorage.setItem('motor', JSON.stringify(motor))
        return motor
    }

    const populateInitialData = (data, masters) => {
        console.log(masters)
        const standard = masters.master_drive_motor_type_1.map(item => item.name)
        motorStandardOptions.value.splice(0, motorStandardOptions.value.length)
        motorStandardOptions.value.push(...standard)
        motorStandard.value = data.motor_standard

        const type = masters.master_drive_motor_type_2.map(item => item.name)
        motorTypeOptions.value.splice(0, motorTypeOptions.value.length)
        motorTypeOptions.value.push(...type)
        motorType.value = data.motor_type

        const make = masters.master_drive_motor_make.map(item => item.name)
        motorMakeOptions.value.splice(0, motorMakeOptions.value.length)
        motorMakeOptions.value.push(...make)
        motorMake.value = data.motor_make

        const mouting = masters.master_drive_motor_mounting.map(item => item.name)
        motorMoutingOptions.value.splice(0, motorMoutingOptions.value.length)
        motorMoutingOptions.value.push(...mouting)
        motorMouting.value = data.motor_mounting

        const hp = masters.master_drive_hp.map(item => item.name)
        motorHPOptions.value.splice(0, motorHPOptions.value.length)
        motorHPOptions.value.push(...hp)
        motorHP.value = data.motor_hp
    }

    return {
        motorMake,
        motorMakeOptions,
        motorType,
        motorTypeOptions,
        motorMouting,
        motorMoutingOptions,
        motorHP,
        motorHPOptions,
        motorStandard,
        motorStandardOptions,
        motorFrame,
        motorFrameOptions,
        motorTempClass,
        motorTempClassOptions,
        motorGasGroup,
        motorGasGroupOptions,
        motorProtection,
        motorProtectionOptions,

        // Methods
        getMasters,
        populateInitialData,
        searchMotorData
    }
  },
  watch: {
    motorMasters: {
      handler(newVal) {
        if (newVal !== null && this.motor !== null) {
          this.populateInitialData(this.motor, newVal);
        }
      },
      immediate: true
    }
  }
}
</script>