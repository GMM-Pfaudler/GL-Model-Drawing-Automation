<template>
    <q-page class="q-pa-md">
    <div>
      <div class="row justify-end q-mb-md">
        <q-space/>
        <q-chip  icon="check" square color="green-5" text-color="white" clickable @click="saveToJsonFile()">
                {{ "Save To File "}}
        </q-chip>
        <!-- <q-btn outline rounded color="primary" icon="search" label="Search" @click="searchAvcpData"/> -->
      </div>
      
      <!-- <q-separator spaced /> -->
      <!-- Table Header -->
      <div class="row q-col-gutter-sm items-center q-pb-sm">
        <div class="col"><strong>Nozzle</strong></div>
        <div class="col"><strong>Type</strong></div>
        <div class="col"><strong>Location</strong></div>
        <div class="col"><strong>Length</strong></div>
        <div class="col"><strong>Size</strong></div>
        <div class="col"><strong>Material</strong></div>
      </div>

      <!-- Table Rows -->
      <div
        v-for="(row, index) in nozzleTable"
        :key="index"
        class="q-mb-sm"
      >
        <div class="row q-col-gutter-sm items-center">
          <div class="col">
            <q-input v-model="row.nozzle" label="Nozzle" outlined dense clearable/>
          </div>
          <div class="col">
              <q-select
                  v-model="row.type"
                  :options="avcpTypeOptions"
                  outlined
                  dense
                  emit-value
                  map-options
                  label="Type"
              />
          </div>
          <div class="col">
            <q-input v-model.number="row.location" label="Location" outlined dense clearable/>
          </div>
          <div class="col">
            <q-input v-model.number="row.length" type="text" label="Length" outlined dense clearable/>
          </div>
          <div class="col">
            <q-input v-model="row.size" type="text" label="Size" outlined dense clearable/>
          </div>
          <div class="col">
              <q-select
                  v-model="row.material"
                  :options="avcpMaterialOptions"
                  outlined
                  dense
                  emit-value
                  map-options
                  label="Material"
              />
          </div>
          <div class="col-auto">
              <q-btn
                outline
                round
                color="primary"
                icon="search"
                @click="searchNozzle(row)"
                dense
                class="self-center"
              />
          </div>
        </div>
        
        <div class="row q-mt-xs">
          <q-chip
            v-if="row.drawingNumber"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Drawing Number: {{ row.drawingNumber }}
            </q-chip>

            <q-chip
            v-if="row.itemCode"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Item Code: {{ row.itemCode }}
            </q-chip>
        </div>
        
      </div>

      <div class="row q-col-gutter-sm q-mt-md">
        <q-btn
            label="Add Nozzle"
            icon="add"
            color="primary"
            @click="addNozzleRow"
            flat
        />
        <q-btn
            label="Remove Last Nozzle"
            icon="remove"
            color="negative"
            @click="removeLastNozzleRow"
            :disable="nozzleTable.length === 0"
            flat
        />
      </div>
    </div>
  </q-page>
</template>
<script>
import { onMounted, ref } from 'vue'
import { useQuasar } from 'quasar'
export default {
  name: 'AirVentCouplingPlug',
  props: {
    avcp: Object
  },
  emits: ['search-data', 'save-airvent'],
  setup (props, { emit }) {
    const $q = useQuasar()
    const avcpMaterialOptions = ref(['-', 'SA 105', 'SS304', 'SS316'])
    const avcpTypeOptions = ref(['-', 'Coupling', 'Plug', 'Bend Coupling', 'Nozzle'])
    const nozzleTable = ref([{ nozzle: null, type:null, location: null, length: null, size: null, material: null, drawingNumber: null, itemCode: null }]);
    const searchedNozzleName = ref(null)

    const LOCAL_STORAGE_KEY = 'airVentCouplingPlug'
    
    onMounted(() => {
        console.log('AirVentCouplingPlug')

        // ✅ Load from localStorage if exists
      const stored = localStorage.getItem(LOCAL_STORAGE_KEY)
      if (stored) {
        try {
          const parsed = JSON.parse(stored)
          if (Array.isArray(parsed.nozzles)) {
            nozzleTable.value = parsed.nozzles
          }
        } catch (err) {
          console.error('Failed to parse saved AVCP data:', err)
        }
      }
    })

    const addNozzleRow = () => {
        nozzleTable.value.push({ nozzle: null, type: null, location: null, length: null, size: null, material: null, drawingNumber: null, itemCode: null});
    }

    const removeLastNozzleRow = () => {
        if (nozzleTable.value.length > 0) {
            nozzleTable.value.pop();
        }
    }

    // const searchAvcpData = () => {
    //     // const data = prepareAvcpData()
    //     const isNull = hasNull(nozzleTable.value)
    //     if(!isNull){
    //       emit('search-data', data)
    //     }
    //     else{
    //       $q.dialog({
    //             title: '<span class="text-red">Alert</span>',
    //             message: `<span style="font-weight: bold">Some required data fields are missing.</span>`,
    //             color: 'red-5',
    //             html: true
    //         });
    //     }
    // }

    const saveToJsonFile = () => {
      const nozzleData = {nozzles: nozzleTable.value}
      emit('save-airvent', nozzleData)
    }

    const searchNozzle = (row) => {
      const isNull = hasNull(row)
      if(isNull){
        $q.dialog({
            title: '<span class="text-red">Alert</span>',
            message: `Please enter missing value.`,
            color: 'red-5',
            html: true
        });
      }
      else{
        searchedNozzleName.value = row.nozzle
        const nozzle = {
          component: 'AirVentCouplingPlug',
          type: row.type,
          length: row.length,
          size: row.size,
          material: row.material
        }

        
        // Save to localStorage on search
        const toStore = {
          nozzles: nozzleTable.value
        }
        localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(toStore))

        emit('search-data', nozzle)
      }
    }

    // const prepareAvcpData = () => {
    //     const avcpData = {
    //         component: 'AirVentCouplingPlug',
    //         nozzleTable: nozzleTable.value? nozzleTable.value : null
    //     }
    //     const result = flattenForExcel(avcpData)
    //     return result
    // }

    const flattenForExcel = (obj) => {
        const output = {};

        // Copy top-level properties except 'nozzles'
        for (const key in obj) {
            if (key !== 'nozzleTable') {
            output[key] = obj[key];
            }
        }

        // Ensure nozzles is plain JS (unwrap Proxy if needed)
        const rawNozzles = JSON.parse(JSON.stringify(obj.nozzleTable || []));

        // Flatten each nozzle into its own stringified JSON field
        rawNozzles.forEach((nozzle, index) => {
            output[`nozzle_${index}`] = JSON.stringify(nozzle);
        });

        return output;
    }

    const hasNull = (obj) => {
      return Object.entries(obj).some(
        ([key, value]) =>
          !['drawingNumber', 'itemCode'].includes(key) && (value === null || value === '')
      );
    }

    const assignValues = (data) => {
      if(data?.component === 'AirVentCouplingPlug'){
        const foundNozzle = nozzleTable.value.find(row => row.nozzle === searchedNozzleName.value);
        if(foundNozzle){
          foundNozzle.drawingNumber = data.model_info.drawingNumber
          foundNozzle.itemCode = data.model_info.itemCode
        }
      }
    }

    return {
        nozzleTable,
        avcpMaterialOptions,
        avcpTypeOptions,
        searchedNozzleName,

        // Methods
        addNozzleRow,
        removeLastNozzleRow,
        // searchAvcpData,
        searchNozzle,
        saveToJsonFile,
        flattenForExcel,
        assignValues
    }
  },
  watch: {
    avcp: {
      handler(newVal) {
        if (newVal?.model_info) {
          this.assignValues(newVal);
        }
      },
      immediate: true
    }
  }
}
</script>