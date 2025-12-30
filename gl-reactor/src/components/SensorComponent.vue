<template>
    <q-page class="q-pa-md">
        <div class="q-mb-md">
            <div class="row q-gutter-md q-wrap items-center">
                <q-select
                outlined
                v-model="sensorType"
                :options="sensorOptions"
                label="Sensor"
                :rules="[val => !!val || 'Please select a value']"
                dense
                class="col-12 col-md-2"
                />
                <q-select
                v-if="sensorType === 'RTD'"
                outlined
                v-model="rtdQty"
                :options="rtdQtyOptions"
                label="Quantity"
                :rules="[val => !!val || 'Please select a value']"
                dense
                class="col-12 col-md-2"
                />
                <q-space/>
                <q-chip v-if="rtdItemCodeOne || rtdItemCodeTwo || dialThermoItemCode" icon="check" square color="green-5" text-color="white" clickable @click="saveToJsonFile()">
                    {{ "Save To File "}}
                </q-chip>
                <!-- <q-space/>
                <q-btn outline color="primary" rounded icon="search" label="Search" @click="searchRtdData"/> -->
            </div>
        </div>   
        <div v-if="sensorType === 'RTD'" class="q-mb-md">
            <div  v-if="rtdQty === '1' || rtdQty === '2'" class="q-mb-lg">
                <div class="row text-h6 q-mb-md">RTD Sensor One</div>
                <div class="row q-gutter-md items-center no-wrap" style="min-height: 56px;">
                    <q-select
                    outlined
                    v-model="rtdMakeOne"
                    :options="rtdMakeOneOptions"
                    label="Make"
                    :rules="[val => !!val || 'Please select a value']"
                    dense
                    class="col-12 col-md-2"
                    />
                    <q-select
                    outlined
                    v-model="rtdTypeOne"
                    :options="rtdTypeOneOptions"
                    label="Type"
                    :rules="[val => !!val || 'Please select a value']"
                    dense
                    class="col-12 col-md-2"
                    />
                    <q-input
                    outlined
                    v-model="rtdLengthOne"
                    type="text"
                    label="Length"
                    :rules="[val => !!val || 'This field is required']"
                    dense
                    class="col-12 col-md-2"
                    />
                    <q-btn
                    outline
                    round
                    color="primary"
                    icon="search"
                    @click="searchSensorData('one')"
                    dense
                    class="self-center"
                    />
                </div>
                <div v-if="rtdDrawingNumberOne || rtdItemCodeOne" class="row q-gutter-md items-center q-mt-sm">

                    <q-chip
                    v-if="rtdDrawingNumberOne"
                    color="primary"
                    outline
                    square
                    text-color="white"
                    label
                    class="col-12 col-md-2"
                    >
                    Drawing #: {{ rtdDrawingNumberOne }}
                    </q-chip>

                    <q-chip
                    v-if="rtdItemCodeOne"
                    color="primary"
                    outline
                    square
                    text-color="white"
                    label
                    class="col-12 col-md-2"
                    >
                    Item Code: {{ rtdItemCodeOne }}
                    </q-chip>
                </div>
            </div>
            <div  v-if="rtdQty === '2'" class="q-mb-lg">
                <div class="text-h6 q-mb-md">RTD Sensor Two
                    <q-btn
                        label="Remove"
                        icon="remove"
                        color="negative"
                        @click="removeRtd"
                        flat
                    />
                </div>
                <div class="row q-gutter-md items-center no-wrap" style="min-height: 56px;">
                    <q-select
                    outlined
                    v-model="rtdMakeTwo"
                    :options="rtdMakeTwoOptions"
                    label="Make"
                    :rules="[val => !!val || 'Please select a value']"
                    dense
                    class="col-12 col-md-2"
                    />
                    <q-select
                    outlined
                    v-model="rtdTypeTwo"
                    :options="rtdTypeTwoOptions"
                    label="Type"
                    :rules="[val => !!val || 'Please select a value']"
                    dense
                    class="col-12 col-md-2"
                    />
                    <q-input
                    outlined
                    v-model="rtdLengthTwo"
                    type="text"
                    label="Length"
                    :rules="[val => !!val || 'This field is required']"
                    dense
                    class="col-12 col-md-2"
                    />
                    <q-btn
                    outline
                    round
                    color="primary"
                    icon="search"
                    @click="searchSensorData('two')"
                    dense
                    class="self-center"
                    />
                </div>
                <div v-if="rtdDrawingNumberTwo || rtdItemCodeTwo" class="row q-gutter-md items-center q-mt-sm">

                    <q-chip
                    v-if="rtdDrawingNumberTwo"
                    color="primary"
                    outline
                    square
                    text-color="white"
                    label
                    class="col-12 col-md-2"
                    >
                    Drawing Number: {{ rtdDrawingNumberTwo }}
                    </q-chip>

                    <q-chip
                    v-if="rtdItemCodeTwo"
                    color="primary"
                    outline
                    square
                    text-color="white"
                    label
                    class="col-12 col-md-2"
                    >
                    Item Code: {{ rtdItemCodeTwo }}
                    </q-chip>
                </div>
            </div>
        </div>
        <div v-if="sensorType === 'Dial Thermometer'" class="q-mb-md">
            <div class="row q-gutter-md q-wrap">
                <q-input
                outlined
                v-model="dialThermoLength"
                type="text"
                label="Length"
                :rules="[val => !!val || 'This field is required']"
                dense
                class="col-12 col-md-2"
                />
                <q-btn
                outline
                round
                color="primary"
                icon="search"
                @click="searchSensorData('dialThermo')"
                dense
                class="self-center"
                />
            </div>
            <div v-if="dialThermoDrawingNumber || dialThermoItemCode" class="row q-gutter-md items-center q-mt-sm">

                    <q-chip
                    v-if="dialThermoDrawingNumber"
                    color="primary"
                    outline
                    square
                    text-color="white"
                    label
                    class="col-12 col-md-2"
                    >
                    Drawing Number: {{ dialThermoDrawingNumber }}
                    </q-chip>

                    <q-chip
                    v-if="dialThermoItemCode"
                    color="primary"
                    outline
                    square
                    text-color="white"
                    label
                    class="col-12 col-md-2"
                    >
                    Item Code: {{ dialThermoItemCode }}
                    </q-chip>
                </div>
        </div>    
    </q-page>   
</template>

<script>
import { onMounted, ref } from 'vue'
export default {
  name: 'SensorComponent',
  props: {
    sensor: Object
  },
  emits: ['search-data', 'save-sensor'],
  setup (props, { emit }) {
    const sensorResponses = ref([])
    const sensorType = ref(null)
    const sensorOptions = ref(['-', 'RTD', 'Dial Thermometer'])
    const dialThermoLength = ref(null)
    const dialThermoDrawingNumber = ref(null)
    const dialThermoItemCode = ref(null)

    const rtdQty = ref(null)
    const rtdQtyOptions = ref(['-', '1', '2'])
    const rtdMakeOne = ref(null)
    const rtdMakeOneOptions = ref(['-', 'NASA', 'Radix', 'E&H'])
    const rtdTypeOne = ref(null)
    const rtdTypeOneOptions = ref(['-', 'Type 1', 'Type 2'])
    const rtdLengthOne = ref(null)
    const rtdDrawingNumberOne = ref(null)
    const rtdItemCodeOne = ref(null)

    const rtdMakeTwo = ref(null)
    const rtdMakeTwoOptions = ref(['-', 'NASA', 'Radix', 'E&H'])
    const rtdTypeTwo = ref(null)
    const rtdTypeTwoOptions = ref(['-', 'Type 1', 'Type 2'])
    const rtdLengthTwo = ref(null)
    const rtdDrawingNumberTwo = ref(null)
    const rtdItemCodeTwo = ref(null)


    // onMounted(() => {
    //     const draftOne = localStorage.getItem('rtdDraftOne');
    //     if (draftOne) {
    //         const data = JSON.parse(draftOne)
    //         rtdMakeOne.value = data.rtdMake
    //         rtdTypeOne.value = data.rtdType
    //         rtdLengthOne.value = data.rtdLength
    //         rtdDrawingNumberOne.value = data.model_info.drawingNumber
    //         rtdItemCodeOne.value = data.model_info.itemCode
    //     }

    //     const draftTwo = localStorage.getItem('rtdDraftTwo');
    //     if (draftTwo) {
    //         const data = JSON.parse(draftTwo);
    //         rtdMakeTwo.value = data.rtdMake
    //         rtdTypeTwo.value = data.rtdType
    //         rtdLengthTwo.value = data.rtdLength
    //         rtdDrawingNumberTwo.value = data.model_info.drawingNumber
    //         rtdItemCodeTwo.value = data.model_info.itemCode
    //     }

    //     const dialDraft = localStorage.getItem('dialThermoDraft')
    //     if (dialDraft) {
    //         const data = JSON.parse(dialDraft);
    //         dialThermoLength.value = data.dialThermoLength
    //         dialThermoDrawingNumber.value = data.model_info.drawingNumber
    //         dialThermoItemCode.value = data.model_info.itemCode
    //     }
    // });

    const loadDrafts = () => {
    let rtdCount = 0;

    const draftOne = localStorage.getItem('rtdDraftOne');
    if (draftOne) {
        const data = JSON.parse(draftOne)
        rtdMakeOne.value = data.rtdMake
        rtdTypeOne.value = data.rtdType
        rtdLengthOne.value = data.rtdLength
        rtdDrawingNumberOne.value = data.model_info.drawingNumber
        rtdItemCodeOne.value = data.model_info.itemCode
        rtdCount++
    }

    const draftTwo = localStorage.getItem('rtdDraftTwo');
    if (draftTwo) {
        const data = JSON.parse(draftTwo)
        rtdMakeTwo.value = data.rtdMake
        rtdTypeTwo.value = data.rtdType
        rtdLengthTwo.value = data.rtdLength
        rtdDrawingNumberTwo.value = data.model_info.drawingNumber
        rtdItemCodeTwo.value = data.model_info.itemCode
        rtdCount++
    }

    const dialDraft = localStorage.getItem('dialThermoDraft');
    if (dialDraft) {
        const data = JSON.parse(dialDraft)
        dialThermoLength.value = data.dialThermoLength
        dialThermoDrawingNumber.value = data.model_info.drawingNumber
        dialThermoItemCode.value = data.model_info.itemCode
    }

    if (rtdCount > 0) {
        sensorType.value = 'RTD'
        rtdQty.value = rtdCount.toString()
    } else if (dialDraft) {
        sensorType.value = 'Dial Thermometer'
    }

    const uiState = localStorage.getItem('sensorUIState')
    if (uiState) {
        const state = JSON.parse(uiState)
        if (!sensorType.value && state.sensorType) {
        sensorType.value = state.sensorType
        }
        if (!rtdQty.value && state.rtdQty) {
        rtdQty.value = state.rtdQty
        }
    }
}

    onMounted(() => {
    loadDrafts()
});



    const searchSensorData = (sensorNumber) => {
        const sensorData = prepareSensorData(sensorNumber)
        emit('search-data', sensorData)
    }

    const prepareSensorData = (sensorNumber) => {
        let data = null
        if(sensorNumber === 'one'){
            data = {
                    component: 'Sensor',
                    sensorNo: sensorNumber,
                    sensorType: sensorType.value?sensorType.value:null,
                    dialThermoLength: null,
                    rtdMake: rtdMakeOne.value?rtdMakeOne.value:null,
                    rtdType: rtdTypeOne.value?rtdTypeOne.value:null,
                    rtdLength: rtdLengthOne.value?rtdLengthOne.value.toString():null,
            }
            
        }
        else if(sensorNumber === 'two'){
            data = {
                        component: 'Sensor',
                        sensorNo: sensorNumber,        
                        sensorType: sensorType.value?sensorType.value:null,
                        dialThermoLength: null,
                        rtdMake: rtdMakeTwo.value?rtdMakeTwo.value:null,
                        rtdType: rtdTypeTwo.value?rtdTypeTwo.value:null,
                        rtdLength: rtdLengthTwo.value?rtdLengthTwo.value.toString():null,
            }
        }
        else if(sensorNumber === 'dialThermo'){
            data = {
                    component: 'Sensor',
                    sensorNo: sensorNumber,        
                    sensorType: sensorType.value?sensorType.value:null,
                    dialThermoLength: dialThermoLength.value?dialThermoLength.value.toString():null,
                    rtdMake: null,
                    rtdType: null,
                    rtdLength: null,
                }
        }

        return data
    }

    const saveToJsonFile = () => {
        let allSensorData = null
        if (sensorType.value === 'RTD') {
            if (rtdQty.value === '1'){
                allSensorData =  {
                    component: 'Sensor',
                    'one':{
                        sensorType: sensorType.value?sensorType.value:null,
                        rtdMakeOne: rtdMakeOne.value?rtdMakeOne.value:null,
                        rtdTypeOne: rtdTypeOne.value?rtdTypeOne.value:null,
                        rtdLengthOne: rtdLengthOne.value?rtdLengthOne.value:null,
                        rtdDrawingNumberOne: rtdDrawingNumberOne.value?rtdDrawingNumberOne.value:null,
                        rtdItemCodeOne: rtdItemCodeOne.value?rtdItemCodeOne.value:null,
                    }
                }
            }
            else if(rtdQty.value === '2'){
                allSensorData =  {
                    component: 'Sensor',
                    'one':{
                        sensorType: sensorType.value?sensorType.value:null,
                        rtdMakeOne: rtdMakeOne.value?rtdMakeOne.value:null,
                        rtdTypeOne: rtdTypeOne.value?rtdTypeOne.value:null,
                        rtdLengthOne: rtdLengthOne.value?rtdLengthOne.value:null,
                        rtdDrawingNumberOne: rtdDrawingNumberOne.value?rtdDrawingNumberOne.value:null,
                        rtdItemCodeOne: rtdItemCodeOne.value?rtdItemCodeOne.value:null,
                    },
                    'two': {
                        sensorType: sensorType.value?sensorType.value:null,
                        rtdMakeTwo: rtdMakeTwo.value?rtdMakeTwo.value:null,
                        rtdTypeTwo: rtdTypeTwo.value?rtdTypeTwo.value:null,
                        rtdLengthTwo: rtdLengthTwo.value?rtdLengthTwo.value:null,
                        rtdDrawingNumberTwo: rtdDrawingNumberTwo.value?rtdDrawingNumberTwo.value:null,
                        rtdItemCodeTwo: rtdItemCodeTwo.value?rtdItemCodeTwo.value:null
                    }
                }
            }  
        }
        else if (sensorType.value === 'Dial Thermometer') {
            allSensorData =  {
                component: 'Sensor',
                'dialThermo':{
                    sensorType: sensorType.value?sensorType.value:null,
                    dialThermoLength: dialThermoLength.value?dialThermoLength.value:null,
                    dialThermoDrawingNumber: dialThermoDrawingNumber.value?dialThermoDrawingNumber.value:null,
                    dialThermoItemCode: dialThermoItemCode.value?dialThermoItemCode.value:null
                }
            }
        }
        emit('save-sensor', allSensorData)
    }

    const saveUIState = () => {
    const uiState = {
        sensorType: sensorType.value,
        rtdQty: rtdQty.value,
    }
    localStorage.setItem('sensorUIState', JSON.stringify(uiState))
    }


    const assignResponse = (data) => {
    if (data?.sensorType === 'RTD' && data?.sensorNo === 'one') {
        rtdDrawingNumberOne.value = data.model_info.drawingNumber
        rtdItemCodeOne.value = data.model_info.itemCode
        localStorage.setItem('rtdDraftOne', JSON.stringify(data))
    }
    else if (data.sensorType === 'RTD' && data.sensorNo === 'two') {
        rtdDrawingNumberTwo.value = data.model_info.drawingNumber
        rtdItemCodeTwo.value = data.model_info.itemCode
        localStorage.setItem('rtdDraftTwo', JSON.stringify(data))
    }
    else if (data.sensorType === 'Dial Thermometer') {
        dialThermoDrawingNumber.value = data.model_info.drawingNumber
        dialThermoItemCode.value = data.model_info.itemCode
        localStorage.setItem('dialThermoDraft', JSON.stringify(data))
    }

    saveUIState()

    // ✅ Refresh UI
    loadDrafts()
    }


    const removeRtd = () => {
        rtdQty.value = '1'
        rtdDrawingNumberTwo.value = null
        rtdItemCodeTwo.value = null
        rtdMakeTwo.value = null
        rtdTypeTwo.value = null
        rtdLengthTwo.value = null
    }

    return {
        sensorResponses,
        sensorType,
        sensorOptions,
        dialThermoLength,
        dialThermoDrawingNumber,
        dialThermoItemCode,
        rtdQty,
        rtdQtyOptions,
        rtdMakeOne,
        rtdMakeOneOptions,
        rtdTypeOne,
        rtdTypeOneOptions,
        rtdLengthOne,
        rtdDrawingNumberOne,
        rtdItemCodeOne,
        rtdMakeTwo,
        rtdMakeTwoOptions,
        rtdTypeTwo,
        rtdTypeTwoOptions,
        rtdLengthTwo,
        rtdDrawingNumberTwo,
        rtdItemCodeTwo,

        // Methods
        searchSensorData,
        prepareSensorData,
        assignResponse,
        saveToJsonFile,
        removeRtd
    }
  },
  watch: {
    sensor: {
        handler(newVal) {
        if (newVal !== null) {
            this.assignResponse(newVal)
        }
      },
      immediate: true
    }
  }
}
</script>