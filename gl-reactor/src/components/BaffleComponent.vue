<template>
  <q-page class="q-pa-md">

    <!-- Quantity Select -->
    <div class="q-mb-md">
      <div class="row q-gutter-md q-wrap items-center">
        <q-select
          outlined
          v-model="baffleQty"
          :options="baffleQtyOptions"
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
    <div v-if="baffleQty === '1' || baffleQty === '2'" class="q-mb-lg">
      <div class="text-h6 q-mb-md">Baffle One</div>

      <div class="row q-gutter-md items-center no-wrap" style="min-height: 56px;">
        <q-select
          outlined
          v-model="baffleTypeOne"
          :options="baffleTypeOneOptions"
          label="Type"
          :rules="[val => !!val || 'Please select a value']"
          dense
          class="col-12 col-md-2"
        />

        <q-select
          outlined
          v-model="baffleTipTypeOne"
          :options="baffleTipTypeOneOptions"
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
          clearable
        />

        <q-input
          outlined
          v-model="immersionLengthOne"
          type="text"
          label="Immersion Length"
          :rules="[val => !!val || 'This field is required']"
          dense
          class="col-12 col-md-2"
          clearable
        />

        <q-btn
          outline
          round
          color="primary"
          icon="search"
          @click="searchBaffleData('one')"
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
          Drawing Number: {{ drawingNumberOne }}
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
          Item Code: {{ itemCodeOne }}
        </q-chip>
      </div>
    </div>

    <q-separator spaced />

    <!-- Baffle Two Section -->
    <div v-if="baffleQty === '2'" class="q-mb-lg">

      <div class="row q-col-gutter-sm q-mt-md text-h6 q-mb-md">Baffle Two
        <q-btn
            label="Remove"
            icon="remove"
            color="negative"
            @click="removeBaffle"
            flat
        />
      </div>
      <!-- <div class="row q-col-gutter-sm q-mt-md">
        
        </div> -->
      <div class="row q-gutter-md items-center no-wrap" style="min-height: 56px;">
        <q-select
          outlined
          v-model="baffleTypeTwo"
          :options="baffleTypeTwoOptions"
          label="Type"
          :rules="[val => !!val || 'Please select a value']"
          dense
          class="col-12 col-md-2"
        />

        <q-select
          outlined
          v-model="baffleTipTypeTwo"
          :options="baffleTipTypeTwoOptions"
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
          clearable
        />

        <q-input
          outlined
          v-model="immersionLengthTwo"
          type="text"
          label="Immersion Length"
          :rules="[val => !!val || 'This field is required']"
          dense
          class="col-12 col-md-2"
          clearable
        />


        <q-btn
          outline
          round
          color="primary"
          icon="search"
          @click="searchBaffleData('two')"
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
          Drawing #: {{ drawingNumberTwo }}
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
          Item Code: {{ itemCodeTwo }}
        </q-chip>
      </div>
    </div>

  </q-page>
</template>


<script>
import { onMounted, ref } from 'vue'
import { useQuasar } from 'quasar'
export default {
  name: 'BaffleComponent',
  props: {
    baffle: Object,
    baffleMasters: Object
  },
  emits: ['search-data', 'get-baffle-masters', 'save-baffle'],
  mounted() {
    this.getBaffleMasters()
  },

  setup (props, { emit }) {
    const $q = useQuasar()
    const baffleQty = ref(null)
    const baffleQtyOptions = ref(['-', '1', '2'])
    const baffleTypeOne = ref(null)
    const baffleTypeOneOptions = ref([])
    const baffleTipTypeOne = ref(null)
    const baffleTipTypeOneOptions = ref(['-', 'Tantalum Tip', 'Hastalloy Tip', 'Glass Tip', 'Without Tip'])
    const mountingNozzleOne = ref(null)
    const immersionLengthOne = ref(null)
    const drawingNumberOne = ref(null)
    const itemCodeOne = ref(null)
    const baffleTypeTwo = ref(null)
    const baffleTypeTwoOptions = ref([])
    const baffleTipTypeTwo = ref(null)
    const baffleTipTypeTwoOptions = ref(['-', 'Tantalum Tip', 'Hastalloy Tip', 'Glass Tip', 'Without Tip'])
    const mountingNozzleTwo = ref(null)
    const immersionLengthTwo = ref(null)
    const drawingNumberTwo = ref(null)
    const itemCodeTwo = ref(null)


    onMounted(() => {
        const draftOne = localStorage.getItem('baffleDraftOne');
        localStorage.removeItem('baffleDraftOne');
        if (draftOne) {
            const data = JSON.parse(draftOne);
            baffleQty.value = data.baffleQty
            mountingNozzleOne.value = data.mountingNozzleOne;
            immersionLengthOne.value = data.immersionLengthOne;
            baffleTypeOne.value = data.baffleTypeOne;
            baffleTipTypeOne.value = data.baffleTipTypeOne;
            drawingNumberOne.value = data.drawingNumberOne
            itemCodeOne.value = data.itemCodeOne
        }

        const draftTwo = localStorage.getItem('baffleDraftTwo');
        localStorage.removeItem('baffleDraftTwo');
        if (draftTwo) {
            const data = JSON.parse(draftTwo);
            baffleQty.value = data.baffleQty
            mountingNozzleTwo.value = data.mountingNozzleTwo;
            immersionLengthTwo.value = data.immersionLengthTwo;
            baffleTypeTwo.value = data.baffleTypeTwo;
            baffleTipTypeTwo.value = data.baffleTipTypeTwo;
            drawingNumberTwo.value = data.drawingNumberTwo
            itemCodeTwo.value = data.itemCodeTwo
        }
    });

    const removeBaffle = () => {
        baffleQty.value = '1'
        baffleTypeTwo.value = null
        baffleTipTypeTwo.value = null
        mountingNozzleTwo.value = null
        immersionLengthTwo.value = null
        drawingNumberTwo.value = null
        itemCodeTwo.value = null
        localStorage.removeItem('baffleDraftTwo')
    }

    const getBaffleMasters = () => {
        const baffleMasters = {
            component: 'baffle',
            master_baffle_type: null
        }
        emit('get-baffle-masters', baffleMasters)
    }

    const searchBaffleData = (baffleNumber) => {
        const baffleData = prepareBaffleData(baffleNumber)
        const hasNoNullValues = Object.values(baffleData).every(val => val !== null && val !== undefined);
        if(hasNoNullValues){
            emit('search-data', baffleData)
        }else{
          $q.dialog({
                title: '<span class="text-red">Alert</span>',
                message: `<span style="font-weight: bold">Some required data fields are missing.</span>`,
                color: 'red-5',
                html: true
            });
        }
    }

    const prepareBaffleData = (baffleNumber) => {
        let data = null;

        if (baffleNumber === 'one') {
            data = {
            component: 'Baffle',
            baffleNo: baffleNumber,
            mountingNozzle: mountingNozzleOne.value ? mountingNozzleOne.value.toString() : null,
            immersionLength: immersionLengthOne.value ? immersionLengthOne.value.toString() : null,
            baffleType: baffleTypeOne.value ? baffleTypeOne.value : null,
            baffleTipType: baffleTipTypeOne.value ? baffleTipTypeOne.value : null
            };
        }

        if (baffleNumber === 'two') {
            data = {
            component: 'Baffle',
            baffleNo: baffleNumber,
            mountingNozzle: mountingNozzleTwo.value ? mountingNozzleTwo.value.toString() : null,
            immersionLength: immersionLengthTwo.value ? immersionLengthTwo.value.toString() : null,
            baffleType: baffleTypeTwo.value ? baffleTypeTwo.value : null,
            baffleTipType: baffleTipTypeTwo.value ? baffleTipTypeTwo.value : null
            };
        }

        return data;
    }

    const populateInitialData = (data) => {
        const baffleTypeOptionsTemp = data.master_baffle_type.map(item => item.name)
        baffleTypeOneOptions.value.splice(0, baffleTypeOneOptions.value.length)
        baffleTypeOneOptions.value.push(...baffleTypeOptionsTemp)
        baffleTypeTwoOptions.value.splice(0, baffleTypeTwoOptions.value.length)
        baffleTypeTwoOptions.value.push(...baffleTypeOptionsTemp)
    }

    const assignData = (data) => {
        if(data?.baffleNo){
            const no = data?.baffleNo
            if(no === 'one'){
                drawingNumberOne.value = data?.model_info.drawingNumber
                itemCodeOne.value = data?.model_info.itemCode
                const baffleDraftOne = {
                    baffleQty: '1',
                    baffleTypeOne: data.baffleType,
                    baffleTipTypeOne: data.baffleTipType,
                    mountingNozzleOne: parseInt(data.mountingNozzle),
                    immersionLengthOne: parseInt(data.immersionLength),
                    drawingNumberOne: drawingNumberOne.value?drawingNumberOne.value:null,
                    itemCodeOne: itemCodeOne.value?itemCodeOne.value:null
                }
                localStorage.setItem('baffleDraftOne', JSON.stringify(baffleDraftOne))
            }else if(no === 'two'){
                drawingNumberTwo.value = data?.model_info.drawingNumber
                itemCodeTwo.value = data?.model_info.itemCode
                const baffleDraftTwo = {
                    baffleQty: '2',
                    baffleTypeTwo: data.baffleType,
                    baffleTipTypeTwo: data.baffleTipType,
                    mountingNozzleTwo: parseInt(data.mountingNozzle),
                    immersionLengthTwo: parseInt(data.immersionLength),
                    drawingNumberTwo: drawingNumberTwo.value?drawingNumberTwo.value:null,
                    itemCodeTwo: itemCodeTwo.value?itemCodeTwo.value:null
                }
                localStorage.setItem('baffleDraftTwo', JSON.stringify(baffleDraftTwo))
            }
        }
    }

    const saveToJsonFile = () => {
        const allBaffleData = {
            component: 'Baffle',
            'one':{
                mountingNozzleOne: mountingNozzleOne.value?mountingNozzleOne.value.toString():null,
                immersionLengthOne: immersionLengthOne.value?immersionLengthOne.value.toString():null,
                baffleTypeOne: baffleTypeOne.value?baffleTypeOne.value:null,
                baffleTipTypeOne: baffleTipTypeOne.value?baffleTipTypeOne.value:null,
                drawingNumberOne: drawingNumberOne.value && baffleTypeOne.value !== null?drawingNumberOne.value:null,
                itemCodeOne: itemCodeOne.value && baffleTypeOne.value !== null?itemCodeOne.value:null,
            },
            'two': {
                mountingNozzleTwo: mountingNozzleTwo.value?mountingNozzleTwo.value.toString():null,
                immersionLengthTwo: immersionLengthTwo.value?immersionLengthTwo.value.toString():null,
                baffleTypeTwo: baffleTypeTwo.value?baffleTypeTwo.value:null,
                baffleTipTypeTwo: baffleTipTypeTwo.value?baffleTipTypeTwo.value:null,
                drawingNumberTwo: drawingNumberTwo.value && baffleTypeTwo.value !== null?drawingNumberTwo.value:null,
                itemCodeTwo: itemCodeTwo.value && baffleTypeTwo.value !== null?itemCodeTwo.value:null
            }
        }
        emit('save-baffle', allBaffleData)
        localStorage.removeItem('baffleDraftOne')
        localStorage.removeItem('baffleDraftTwo')
    }

    return {
        baffleQty,
        baffleQtyOptions,
        baffleTypeOne,
        baffleTypeOneOptions,
        baffleTipTypeOne,
        baffleTipTypeOneOptions,
        mountingNozzleOne,
        immersionLengthOne,
        drawingNumberOne,
        itemCodeOne,
        baffleTypeTwo,
        baffleTypeTwoOptions,
        baffleTipTypeTwo,
        baffleTipTypeTwoOptions,
        mountingNozzleTwo,
        immersionLengthTwo,
        drawingNumberTwo,
        itemCodeTwo,

        // Methods
        removeBaffle,
        getBaffleMasters,
        searchBaffleData,
        prepareBaffleData,
        populateInitialData,
        assignData,
        saveToJsonFile
    }
  },
  watch: {
    baffleMasters: {
      handler(newVal) {
        if (newVal !== null) {
          this.populateInitialData(newVal)
        }
      },
      immediate: true
    },
    baffle: {
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