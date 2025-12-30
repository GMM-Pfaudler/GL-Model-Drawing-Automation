<template>
  <q-page class="q-pa-md">

    <!-- Quantity Select -->
    <div class="q-mb-md">
      <div class="row q-gutter-md q-wrap items-center">
        <q-select
          outlined
          v-model="thermowellQty"
          :options="thermowellQtyOptions"
          label="Quantity"
          :rules="[val => !!val || 'Please select a value']"
          dense
          class="col-12 col-md-2"
        />
        <q-space/>
        <q-chip v-if="itemCodeOne !== null || itemCodeTwo !== null" icon="check" square color="green-5" text-color="white" clickable @click="saveToJsonFile()">
            {{ "Save To File "}}
        </q-chip>
      </div>
    </div>

    <q-separator spaced />

    <!-- Baffle One Section -->
    <div v-if="thermowellQty === '1' || thermowellQty === '2'" class="q-mb-lg">
      <div class="text-h6 q-mb-md">Thermowell One</div>

      <div class="row q-gutter-md items-center no-wrap" style="min-height: 56px;">
        <q-select
          outlined
          v-model="thermowellTypeOne"
          :options="thermowellTypeOneOptions"
          label="Type"
          :rules="[val => !!val || 'Please select a value']"
          dense
          class="col-12 col-md-2"
        />

        <q-select
          outlined
          v-model="thermowellTipTypeOne"
          :options="thermowellTipTypeOneOptions"
          label="Tip Type"
          :rules="[val => !!val || 'Please select a value']"
          dense
          class="col-12 col-md-2"
        />

        <q-input
          outlined
          v-model="mountingNozzleOne"
          type="text"
          label="Mounting Nozzle"
          :rules="[val => !!val || 'This field is required']"
          dense
          class="col-12 col-md-2"
        />

        <q-input
          outlined
          v-model="immersionLengthOne"
          type="text"
          label="Immersion Length"
          :rules="[val => !!val || 'This field is required']"
          dense
          class="col-12 col-md-2"
        />

        <q-btn
          outline
          round
          color="primary"
          icon="search"
          @click="searchThermowellData('one')"
          dense
          class="self-center"
        />
      </div>

      <!-- Chips and Save button -->
      <div v-if="drawingNumberOne || itemCodeOne" class="row q-gutter-md items-center q-mt-sm">

        <q-chip
          v-if="drawingNumberOne"
          color="primary"
          outline
          square
          text-color="white"
          label
          class="col-12 col-md-2"
        >
          Drawing Number: <span style="font-weight: bold;">&nbsp; {{ drawingNumberOne }} </span>
        </q-chip>

        <q-chip
          v-if="itemCodeOne"
          color="primary"
          outline
          square
          text-color="white"
          label
          class="col-12 col-md-2"
        >
          Item Code: <span style="font-weight: bold;">&nbsp; {{ itemCodeOne }} </span>
        </q-chip>
      </div>
    </div>

    <q-separator spaced />

    <!-- Baffle Two Section -->
    <div v-if="thermowellQty === '2'" class="q-mb-lg">

      <div class="row q-col-gutter-sm q-mt-md text-h6 q-mb-md">Thermowell Two
        <q-btn
            label="Remove"
            icon="remove"
            color="negative"
            @click="removeThermowell"
            flat
        />
      </div>
      <!-- <div class="row q-col-gutter-sm q-mt-md">
        
        </div> -->
      <div class="row q-gutter-md items-center no-wrap" style="min-height: 56px;">
        <q-select
          outlined
          v-model="thermowellTypeTwo"
          :options="thermowellTypeTwoOptions"
          label="Type"
          :rules="[val => !!val || 'Please select a value']"
          dense
          class="col-12 col-md-2"
        />

        <q-select
          outlined
          v-model="thermowellTipTypeTwo"
          :options="thermowellTipTypeTwoOptions"
          label="Tip Type"
          :rules="[val => !!val || 'Please select a value']"
          dense
          class="col-12 col-md-2"
        />

        <q-input
          outlined
          v-model="mountingNozzleTwo"
          type="text"
          label="Mounting Nozzle"
          :rules="[val => !!val || 'This field is required']"
          dense
          class="col-12 col-md-2"
        />

        <q-input
          outlined
          v-model="immersionLengthTwo"
          type="text"
          label="Immersion Length"
          :rules="[val => !!val || 'This field is required']"
          dense
          class="col-12 col-md-2"
        />


        <q-btn
          outline
          round
          color="primary"
          icon="search"
          @click="searchThermowellData('two')"
          dense
          class="self-center"
        />
      </div>

      <!-- Chips and Save button -->
      <div v-if="drawingNumberTwo || itemCodeTwo" class="row q-gutter-md items-center q-mt-sm">

        <q-chip
          v-if="drawingNumberTwo"
          color="primary"
          outline
          square
          text-color="white"
          label
          class="col-12 col-md-2"
        >
          Drawing Number: <span style="font-weight: bold;">&nbsp; {{ drawingNumberTwo }} </span>
        </q-chip>

        <q-chip
          v-if="itemCodeTwo"
          color="primary"
          outline
          square
          text-color="white"
          label
          class="col-12 col-md-2"
        >
          Item Code: <span style="font-weight: bold;">&nbsp; {{ itemCodeTwo }} </span>
        </q-chip>
      </div>
    </div>

  </q-page>
</template>


<script>
import { onMounted, ref } from 'vue'
export default {
  name: 'ThermowellComponent',
  props: {
    thermowell: Object,
    thermowellMasters: Object
  },
  emits: ['search-data', 'get-thermowell-masters', 'save-thermowell'],
  mounted() {
    this.getThermowellMasters()
  },

  setup (props, { emit }) {
    const thermowellQty = ref(null)
    const thermowellQtyOptions = ref(['-', '1', '2'])
    const thermowellTypeOne = ref(null)
    const thermowellTypeOneOptions = ref([])
    const thermowellTipTypeOne = ref(null)
    const thermowellTipTypeOneOptions = ref(['-', 'Tantalum Tip', 'Hastalloy Tip', 'Glass Tip', 'Without Tip'])
    const mountingNozzleOne = ref(null)
    const immersionLengthOne = ref(null)
    const drawingNumberOne = ref(null)
    const itemCodeOne = ref(null)
    const thermowellTypeTwo = ref(null)
    const thermowellTypeTwoOptions = ref([])
    const thermowellTipTypeTwo = ref(null)
    const thermowellTipTypeTwoOptions = ref(['-', 'Tantalum Tip', 'Hastalloy Tip', 'Glass Tip', 'Without Tip'])
    const mountingNozzleTwo = ref(null)
    const immersionLengthTwo = ref(null)
    const drawingNumberTwo = ref(null)
    const itemCodeTwo = ref(null)


    onMounted(() => {
        const draftOne = localStorage.getItem('thermowellDraftOne');
        if (draftOne) {
            const data = JSON.parse(draftOne);
            thermowellQty.value = data.thermowellQty
            mountingNozzleOne.value = data.mountingNozzleOne;
            immersionLengthOne.value = data.immersionLengthOne;
            thermowellTypeOne.value = data.thermowellTypeOne;
            thermowellTipTypeOne.value = data.thermowellTipTypeOne;
            drawingNumberOne.value = data.drawingNumberOne
            itemCodeOne.value = data.itemCodeOne
        }

        const draftTwo = localStorage.getItem('thermowellDraftTwo');
        if (draftTwo) {
            const data = JSON.parse(draftTwo);
            thermowellQty.value = data.thermowellQty
            mountingNozzleTwo.value = data.mountingNozzleTwo;
            immersionLengthTwo.value = data.immersionLengthTwo;
            thermowellTypeTwo.value = data.thermowellTypeTwo;
            thermowellTipTypeTwo.value = data.thermowellTipTypeTwo;
            drawingNumberTwo.value = data.drawingNumberTwo
            itemCodeTwo.value = data.itemCodeTwo
        }
    });

    const removeThermowell = () => {
        thermowellQty.value = '1'
        thermowellTypeTwo.value = null
        thermowellTipTypeTwo.value = null
        mountingNozzleTwo.value = null
        immersionLengthTwo.value = null
        drawingNumberTwo.value = null
        itemCodeTwo.value = null
        localStorage.removeItem('thermowellDraftTwo')
    }

    const getThermowellMasters = () => {
        const thermowellMasters = {
            component: 'thermowell',
            master_baffle_type: null
        }
        emit('get-thermowell-masters', thermowellMasters)
    }

    const searchThermowellData = (thermowellNumber) => {
        const thermowellData = prepareThermowellData(thermowellNumber)
        const hasNoNullValues = Object.values(thermowellData).every(val => val !== null && val !== undefined);
        if(hasNoNullValues){
            emit('search-data', thermowellData)
        }
    }

    const prepareThermowellData = (thermowellNumber) => {
        let data = null;

        if (thermowellNumber === 'one') {
            data = {
            component: 'Thermowell',
            thermowellNo: thermowellNumber,
            mountingNozzle: mountingNozzleOne.value ? mountingNozzleOne.value.toString() : null,
            immersionLength: immersionLengthOne.value ? immersionLengthOne.value.toString() : null,
            thermowellType: thermowellTypeOne.value ? thermowellTypeOne.value : null,
            thermowellTipType: thermowellTipTypeOne.value ? thermowellTipTypeOne.value : null
            }; 

            // console.log(data)
        }

        if (thermowellNumber === 'two') {
            data = {
            component: 'Thermowell',
            thermowellNo: thermowellNumber,
            mountingNozzle: mountingNozzleTwo.value ? mountingNozzleTwo.value.toString() : null,
            immersionLength: immersionLengthTwo.value ? immersionLengthTwo.value.toString() : null,
            thermowellType: thermowellTypeTwo.value ? thermowellTypeTwo.value : null,
            thermowellTipType: thermowellTipTypeTwo.value ? thermowellTipTypeTwo.value : null
            };
        }

        return data;
    }

    const populateInitialData = (data) => {
        const thermowellTypeOptionsTemp = data.master_baffle_type.map(item => item.name)
        thermowellTypeOneOptions.value.splice(0, thermowellTypeOneOptions.value.length)
        thermowellTypeOneOptions.value.push(...thermowellTypeOptionsTemp)
        thermowellTypeTwoOptions.value.splice(0, thermowellTypeTwoOptions.value.length)
        thermowellTypeTwoOptions.value.push(...thermowellTypeOptionsTemp)
    }

    const assignData = (data) => {
        if(data?.thermowellNo){
            const no = data?.thermowellNo
            if(no === 'one'){
                // console.log('model_info:', data.model_info)
                drawingNumberOne.value = data?.model_info.drawingNumber
                itemCodeOne.value = data?.model_info.itemCode
                const thermowellDraftOne = {
                    thermowellQty: '1',
                    thermowellTypeOne: data.thermowellType,
                    thermowellTipTypeOne: data.thermowellTipType,
                    mountingNozzleOne: parseInt(data.mountingNozzle),
                    immersionLengthOne: parseInt(data.immersionLength),
                    drawingNumberOne: drawingNumberOne.value?drawingNumberOne.value:null,
                    itemCodeOne: itemCodeOne.value?itemCodeOne.value:null
                }
                localStorage.setItem('thermowellDraftOne', JSON.stringify(thermowellDraftOne))
            }else if(no === 'two'){
                drawingNumberTwo.value = data?.model_info.drawingNumber
                itemCodeTwo.value = data?.model_info.itemCode
                const thermowellDraftTwo = {
                    thermowellQty: '2',
                    thermowellTypeTwo: data.thermowellType,
                    thermowellTipTypeTwo: data.thermowellTipType,
                    mountingNozzleTwo: parseInt(data.mountingNozzle),
                    immersionLengthTwo: parseInt(data.immersionLength),
                    drawingNumberTwo: drawingNumberTwo.value?drawingNumberTwo.value:null,
                    itemCodeTwo: itemCodeTwo.value?itemCodeTwo.value:null
                }
                localStorage.setItem('thermowellDraftTwo', JSON.stringify(thermowellDraftTwo))
            }
            // console.log('Received assignData for thermowell TWO:', data)
            // console.log('model_info:', data?.model_info)
        }
    }

    const saveToJsonFile = () => {
        const allThermowellData = {
            component: 'Thermowell',
            'one':{
                mountingNozzleOne: mountingNozzleOne.value?mountingNozzleOne.value.toString():null,
                immersionLengthOne: immersionLengthOne.value?immersionLengthOne.value.toString():null,
                thermowellTypeOne: thermowellTypeOne.value?thermowellTypeOne.value:null,
                thermowellTipTypeOne: thermowellTipTypeOne.value?thermowellTipTypeOne.value:null,
                drawingNumberOne: drawingNumberOne.value && thermowellTypeOne.value !== null?drawingNumberOne.value:null,
                itemCodeOne: itemCodeOne.value && thermowellTypeOne.value !== null?itemCodeOne.value:null,
            },
            'two': {
                mountingNozzleTwo: mountingNozzleTwo.value?mountingNozzleTwo.value.toString():null,
                immersionLengthTwo: immersionLengthTwo.value?immersionLengthTwo.value.toString():null,
                thermowellTypeTwo: thermowellTypeTwo.value?thermowellTypeTwo.value:null,
                thermowellTipTypeTwo: thermowellTipTypeTwo.value?thermowellTipTypeTwo.value:null,
                drawingNumberTwo: drawingNumberTwo.value && thermowellTypeTwo.value !== null?drawingNumberTwo.value:null,
                itemCodeTwo: itemCodeTwo.value && thermowellTypeTwo.value !== null?itemCodeTwo.value:null
            }
        }
        emit('save-thermowell', allThermowellData)
        // localStorage.removeItem('thermowellDraftOne')
        // localStorage.removeItem('thermowellDraftTwo')
    }

    return {
        thermowellQty,
        thermowellQtyOptions,
        thermowellTypeOne,
        thermowellTypeOneOptions,
        thermowellTipTypeOne,
        thermowellTipTypeOneOptions,
        mountingNozzleOne,
        immersionLengthOne,
        drawingNumberOne,
        itemCodeOne,
        thermowellTypeTwo,
        thermowellTypeTwoOptions,
        thermowellTipTypeTwo,
        thermowellTipTypeTwoOptions,
        mountingNozzleTwo,
        immersionLengthTwo,
        drawingNumberTwo,
        itemCodeTwo,

        // Methods
        removeThermowell,
        getThermowellMasters,
        searchThermowellData,
        prepareThermowellData,
        populateInitialData,
        assignData,
        saveToJsonFile
    }
  },
  watch: {
    thermowellMasters: {
      handler(newVal) {
        if (newVal !== null) {
          this.populateInitialData(newVal)
        }
      },
      immediate: true
    },
    thermowell: {
        handler(newVal) {
        if (newVal !== null) {
          this.assignData(newVal)
        }
      },
      immediate: true
    }
  }
}
</script>