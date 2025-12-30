<template>
  <q-page class="q-pa-md">
    <div class="q-pa-md" style="height: 100vh; display: flex; flex-direction: column;">
     <!-- Jacket -->
     <!-- First Row -->
    <div class="q-mb-md">
        <div class="text-h6 q-mb-md ">Jacket</div>
        <div class="row q-gutter-md q-wrap">
            <q-input
            outlined
            v-model="shellThickness"
            type="text"
            label="Shell Thickness"
            dense
            class="col-12 col-md-2"
            />
            <q-input
            outlined
            v-model="dishThickness"
            type="text"
            label="Dish Thickness"
            dense
            class="col-12 col-md-2"
            />
            <q-space/>
            <q-btn outline rounded color="primary" icon="search" label="Search" @click="searchJacketData"/>
            <q-space/>
            <q-chip  icon="check" square color="green-5" text-color="white" clickable :disable="!showSaveToJsonButton" @click="saveToJsonFile()">
                {{ "Save To File "}}
                <q-tooltip v-if="!showSaveToJsonButton">
                  Please complete all required drawing numbers and item codes.
                </q-tooltip>
            </q-chip>

        </div>
    </div>
    <!-- Second Row -->
    <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap">

            <q-select
            outlined
            v-model="jacketType"
            :options="jacketTypeOptions"
            label="Jacket Type"
            dense
            class="col-12 col-md-2"
            />

            <q-select
            outlined
            v-model="jacketTemperature"
            :options="jacketTemperatureOptions"
            label="Temperature"
            dense
            class="col-12 col-md-2"
            />

            <q-select
            outlined
            v-model="jacketPressure"
            :options="jacketPressureOptions"
            label="Pressure"
            dense
            class="col-12 col-md-2"
            />

            <q-select
            outlined
            v-model="suitToInsulation"
            :options="suitToInsulationOptions"
            label="Suit To Insulation"
            dense
            class="col-12 col-md-2"
            />
        </div>
    </div>
    <!-- Third Row -->
    <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap">
            <q-select
            outlined
            v-model="ndt"
            :options="ndtOptions"
            label="NDT"
            dense
            class="col-12 col-md-2"
            />

            <q-select
            outlined
            v-model="jacketOD"
            :options="jacketODOptions"
            label="OD"
            dense
            class="col-12 col-md-2"
            />

            <q-select
            outlined
            v-model="jacketMaterial"
            :options="jacketMaterialOptions"
            label="Jacket Material"
            dense
            class="col-12 col-md-2"
            />

            <q-select
            outlined
            v-model="liftingLug"
            :options="liftingLugOptions"
            label="Lifting Lug"
            dense
            class="col-12 col-md-2"
            />
        </div>
    </div>
    <div class="q-mb-md">
      <div class="row q-gutter-md q-wrap">
        <q-chip  v-if="drawingNumberJacket" outline square color="blue-5" text-color="white">
          {{ "Drawing Number: " + drawingNumberJacket }}
        </q-chip>
        <q-chip  v-if="itemCodeJacket" outline square color="blue-5" text-color="white">
          {{ "Item Code: " + itemCodeJacket }}
        </q-chip>
      </div>
    </div>
    <q-separator spaced />
    <div class="text-h6 q-mb-md ">Diaphragm Ring</div>
    <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap">
            <q-select
            outlined
            v-model="ringMaterial"
            :options="ringMaterialOptions"
            label="Material"
            dense
            class="col-12 col-md-2"
            />

            <q-input
            outlined
            v-model="nozzleSize"
            label="Bottom Nozzle Size"
            dense
            class="col-12 col-md-2"
            />

            <q-space/>
            <q-btn outline rounded color="primary" icon="search" label="Search" @click="searchRingData"/>
        </div>
    </div>
    <div class="q-mb-md">
      <div class="row q-gutter-md q-wrap">
        <q-chip  v-if="drawingNumberJacketEarthing" outline square color="blue-5" text-color="white">
          {{ "Drawing Number: " + drawingNumberJacketEarthing }}
        </q-chip>
        <q-chip  v-if="itemCodeJacketEarthing" outline square color="blue-5" text-color="white">
          {{ "Item Code: " + itemCodeJacketEarthing }}
        </q-chip>
      </div>
    </div>
    <q-separator spaced />
    <div class="text-h6 q-mb-md ">Earthing</div>
    <div class="q-mb-md">
      <div class="row q-gutter-md q-wrap">
        <!-- Always shown based on conditions -->
        <q-select
          outlined
          v-model="jacketEarthingType"
          :options="jacketEarthingTypeOptions"
          label="Type"
          dense
          class="col-12 col-md-2"
        />

        <q-select
          outlined
          v-model="earthingQuantity"
          :options="earthingQuantityOptions"
          label="Quantity"
          dense
          class="col-12 col-md-2"
        />

        <q-select
          outlined
          v-model="earthingMaterial"
          :options="earthingMaterialOptions"
          label="Material"
          dense
          class="col-12 col-md-2"
        />

        <q-input
          outlined
          v-model="earthingOther"
          label="Other"
          dense
          class="col-12 col-md-2"
        />

        <q-space />
        <q-btn
          outline
          rounded
          color="primary"
          icon="search"
          label="Search"
          @click="searchJacketEarthing"
        />
      </div>
    </div>
    <div class="q-mb-md">
      <div class="row q-gutter-md q-wrap">
        <q-chip  v-if="drawingNumberJacketEarthing" outline square color="blue-5" text-color="white">
          {{ "Drawing Number: " + drawingNumberJacketEarthing }}
        </q-chip>
        <q-chip  v-if="itemCodeJacketEarthing" outline square color="blue-5" text-color="white">
          {{ "Item Code: " + itemCodeJacketEarthing }}
        </q-chip>
      </div>
    </div>


    <!-- Jacket Support -->
    <q-separator spaced />
    <div class="text-h6 q-mb-md ">Support</div>
    <div class="q-mb-md">
      <div class="row q-gutter-md q-wrap">
      <!-- Jacket Support Selection -->
        <q-select
          outlined
          v-model="jacketSupport"
          :options="jacketSupportOptions"
          @update:model-value="onUpdateJacketSpport"
          label="Support"
          dense
          class="col-12 col-md-2"
        />
      </div>
    </div>
    <div class="q-mb-md">
      <div class="row q-gutter-md q-wrap">
        <!-- Always shown based on conditions -->
        <q-select
          v-if="showField('material')"
          outlined
          v-model="supportMaterial"
          :options="supportMaterialOptions"
          label="Material"
          dense
          class="col-12 col-md-2"
        />

        <q-select
          v-if="showField('type')"
          outlined
          v-model="supportType"
          :options="supportTypeOptions"
          label="Type"
          dense
          class="col-12 col-md-2"
        />

        <q-select
          v-if="showField('sideBracketSupportType')"
          outlined
          v-model="sideBracketSupportType"
          :options="sideBracketSupportTypeOptions"
          label="Side Bracket Support Type"
          dense
          class="col-12 col-md-2"
        />

        <q-input
          v-if="showField('cToc')"
          outlined
          v-model="cToc"
          label="C To C"
          type="text"
          dense
          class="col-12 col-md-2"
        />

        <q-select
          v-if="showField('legSupportType')"
          outlined
          v-model="legSupportType"
          :options="legSupportTypeOptions"
          label="Leg Support Type"
          dense
          class="col-12 col-md-2"
        />

        <q-input
          v-if="showField('supportHeight')"
          outlined
          v-model="supportHeight"
          label="Height from BTM Nozzle Face"
          type="text"
          dense
          class="col-12 col-md-2"
        />

        <q-input
          v-if="showField('suppportOD')"
          outlined
          v-model="supportOD"
          label="Outside Diameter"
          type="text"
          dense
          class="col-12 col-md-2"
        />

        <q-input
          outlined
          v-model="supportOther"
          label="Other"
          dense
          class="col-12 col-md-2"
        />

        <q-space />
        <q-btn
          outline
          rounded
          color="primary"
          icon="search"
          label="Search"
          @click="searchJacketSupport"
        />
      </div>
    </div>
    <div class="q-mb-md">
      <div class="row q-gutter-md q-wrap">
        <q-chip  v-if="drawingNumberJacketSupport" outline square color="blue-5" text-color="white">
          {{ "Drawing Number: " + drawingNumberJacketSupport }}
        </q-chip>
        <q-chip  v-if="itemCodeJacketSupport" outline square color="blue-5" text-color="white">
          {{ "Item Code: " + itemCodeJacketSupport }}
        </q-chip>
      </div>
    </div>

    <!-- Jacket Nozzle -->
    <q-separator spaced />
    <!-- Jacket Nozzle Table -->
    <div class="q-mt-md" style="flex-grow: 1; display: flex; flex-direction: column; padding-bottom: 300px;">
      <div class="q-mb-md">
          <div class="row q-gutter-md q-wrap">
              <div class="text-h6 q-mb-md ">Jacket Nozzles</div>
                  <q-select
                  outlined
                  v-model="nozzleMaterial"
                  :options="nozzleMaterialOptions"
                  label="Nozzle Material"
                  dense
                  class="col-12 col-md-2"
                  />
          </div>
      </div>
      <!-- Table Header -->
      <div class="row q-col-gutter-sm items-center q-pb-sm">
        <div class="col"><strong>Nozzle</strong></div>
        <div class="col"><strong>length</strong></div>
        <div class="col"><strong>Size</strong></div>
        <div class="col"><strong>Degree</strong></div>
        <div class="col"><strong>Location</strong></div>
      </div>
       <!-- Table Rows -->
      <div v-for="(row, index) in nozzleTable" :key="index" class="q-mb-sm">

        <!-- Row 1: Inputs and Button -->
        <div class="row q-col-gutter-sm items-center">
          <div class="col">
            <q-input v-model="row.nozzle" outlined dense />
          </div>
          <div class="col">
            <q-input v-model="row.length" outlined dense />
          </div>
          <div class="col">
            <q-input v-model.number="row.size" type="text" outlined dense />
          </div>
          <div class="col">
            <q-input v-model.number="row.degree" type="text" outlined dense />
          </div>
          <div class="col">
            <q-input v-model="row.location" outlined dense />
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

        <!-- Row 2: Chips (new line, but part of same v-for) -->
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
  </div>
  </q-page>
</template>

<script>
import { ref } from 'vue'
import { useQuasar } from 'quasar'
export default {
  name: 'JacketComponent',
  props: {
    jacket: Object,
    jacketMasters: Object
  },
  emits: ['search-data', 'get-jacket-masters', 'save-jacket'],
  // mounted() {
  //   this.getJacketMasters()
  //   if (this.jacket?.data) {
  //       this.fillData(this.jacket?.data)
  //   }
  // },

  data() {
    return {
      loadedFromLocalStorage: false
    }
  },
  
  mounted() {
    this.getJacketMasters()

    const saved = localStorage.getItem('jacketHistory')
    if (saved) {
      try {
        const parsed = JSON.parse(saved)
        const flatData = this.normalizeJacketDataFromStorage(parsed)
        console.log('Filling from localStorage:', flatData)
        this.fillData(flatData)
        this.loadedFromLocalStorage = true
      } catch (e) {
        console.error('Failed to parse jacket data from localStorage:', e)
      }
    } else if (this.jacket?.data) {
      console.log('Filling from fallback jacket.data:', this.jacket.data)
      this.fillData(this.jacket.data)
    }
  },

  setup (props, { emit }) {
    const $q = useQuasar()

    // Jacket
    const jacketType = ref(null);
    const jacketTypeOptions = ref(['-', 'Full', 'Half', 'None'])
    const jacketTemperature = ref(null)
    const jacketTemperatureOptions = ref([])
    const jacketPressure = ref(null)
    const jacketPressureOptions = ref([])
    const ndt = ref(null)
    const ndtOptions = ref([])
    const jacketOD = ref(null)
    const jacketODOptions = ref([])
    const jacketMaterial = ref(null)
    const jacketMaterialOptions = ref([])
    const liftingLug = ref(null)
    const liftingLugOptions = ref(["-", "MS", "SS304", "SS316", "MS Suit To Insulation", "SS304 Suit To Insulation", "SS316 Suit To Insulation"])
    const earthingType = ref(null)
    const earthingTypeOptions = ref([])
    const drawingNumberJacket = ref(null)
    const itemCodeJacket = ref(null)

    // Earthing
    const jacketEarthingType = ref(null)
    const jacketEarthingTypeOptions = ref(['-', 'Cleat', 'Boss'])
    const earthingQuantity = ref(null)
    const earthingQuantityOptions = ref(['-', '1', '2'])
    const earthingMaterial = ref(null)
    const earthingMaterialOptions = ref(['-', 'MS', 'SS304', 'SS316'])
    const earthingOther = ref(null)
    const drawingNumberJacketEarthing = ref(null)
    const itemCodeJacketEarthing = ref(null)

    // Support
    const jacketSupport = ref(null);
    const jacketSupportOptions = ref([])
    const supportMaterial = ref(null)
    const supportMaterialOptions = ref(['-', 'MS', 'SS304', 'SS316'])
    const supportType = ref(null)
    const supportTypeOptions = ref(['-', 'Standard', 'Bolted'])
    const sideBracketSupportType = ref(null)
    const sideBracketSupportTypeOptions = ref(['-', 'Standard', 'Bolted'])
    const legSupportType = ref(null)
    const legSupportTypeOptions = ref(['-', 'Half', 'Full', 'Coupling', 'Stiffener', 'Bracine'])
    const supportOD = ref(null)
    const supportHeight = ref(null)
    const cToc = ref(null)
    const supportOther = ref(null)
    const drawingNumberJacketSupport = ref(null)
    const itemCodeJacketSupport = ref(null)

    // Nozzles
    const searchedNozzleName = ref(null)
    const nozzleMaterial = ref(null)
    const nozzleMaterialOptions = ref([])
    const suitToInsulation = ref(null)
    const suitToInsulationOptions = ref(['-', 'Yes', 'No'])
    const shellThickness = ref(null)
    const dishThickness = ref(null)

    const nozzleTable = ref([
    { nozzle: '', length: null, size: null, degree: null, location: '', drawingNumber: null, itemCode: null }
    ]);

    const showField = (field) => {
      const map = {
        'Side Bracket': ['material', 'type', 'cToc'],
        'Leg Support': ['material', 'legSupportType', 'supportHeight'],
        'Side Bracket + Leg Support': ['material', 'legSupportType', 'cToc', 'sideBracketSupportType', 'supportHeight'],
        'Ring Support': ['material', 'suppportOD'],
        'Skirt Support': ['material', 'supportHeight', 'suppportOD']
      };

      return map[jacketSupport.value]?.includes(field);
    }

    const addNozzleRow = () => {
        nozzleTable.value.push({ nozzle: '', length:null, size: null, degree: null, location: '', drawingNumber: null, itemCode: null });
    }

    const removeLastNozzleRow = () => {
        if (nozzleTable.value.length > 0) {
            nozzleTable.value.pop();
        }
    }

    const getJacketMasters = () => {
        const jacketMasters = {
            component: 'jacket',
            master_jacket_type: null,
            master_support: null,
            master_temperature: null,
            master_pressure: null,
            master_jacket_ndt: null,
            master_jacket_od: null,
            master_material_shell_jacket: null,
            master_material_earthing: null,
            master_material_nozzle_jacket: null
        }
        emit('get-jacket-masters', jacketMasters)
    }

    const searchJacketEarthing = () => {
      const earthing = {
        component: 'Earthing',
        jacketEarthingType: jacketEarthingType.value? jacketEarthingType.value: null,
        earthingQuantity: earthingQuantity.value? earthingQuantity.value: null,
        earthingMaterial: earthingMaterial.value? earthingMaterial.value: null,
        earthingOther: earthingOther.value? earthingOther.value: null
      }
      emit('search-data', earthing)
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
          component: 'JacketNozzle',
          nozzleMaterial: nozzleMaterial.value? nozzleMaterial.value: null,
          jacketTemperature: jacketTemperature.value? jacketTemperature.value: null,
          jacketPressure: jacketPressure.value? jacketPressure.value: null,
          suitToInsulation: suitToInsulation.value? suitToInsulation.value: null,
          size: row.size,
          length: row.length
        }
        emit('search-data', nozzle)
      }
      
    }

    const searchJacketSupport = () =>{
      let support = null
      if (jacketSupport.value === 'Side Bracket'){
        support = {
          component: 'SideBracket',
          supportMaterial: supportMaterial.value? supportMaterial.value: null,
          supportType: supportType.value? supportType.value: null,
          cToc: cToc.value? cToc.value: null,
          suitToInsulation: suitToInsulation.value? suitToInsulation.value: null
        }
      }
      else if(jacketSupport.value === 'Leg Support'){
        support = {
          component: 'LegSupport',
          supportMaterial: supportMaterial.value? supportMaterial.value: null,
          supportType: supportType.value? supportType.value: null,
          supportHeight: supportHeight.value? supportHeight.value: null
        }
      }
      else if(jacketSupport.value === 'Side Bracket + Leg Support'){
        support = {
          component: 'SideBracketLegSupport',
          supportMaterial: supportMaterial.value? supportMaterial.value: null,
          legSupportType: legSupportType.value? legSupportType.value: null,
          cToc: cToc.value? cToc.value: null,
          sideBracketSupportType: sideBracketSupportType.value? sideBracketSupportType.value: null,
          supportHeight: supportHeight.value? supportHeight.value: null,
          suitToInsulation: suitToInsulation.value? suitToInsulation.value: null
        }
      }
      else if(jacketSupport.value === 'Ring Support'){
        support = {
          component: 'RingSupport',
          supportMaterial: supportMaterial.value? supportMaterial.value: null,
          supportType: supportType.value? supportType.value: null,
          supportOD: supportOD.value? supportOD.value: null,
          suitToInsulation: suitToInsulation.value? suitToInsulation.value: null
        }
      }
      else if(jacketSupport.value === 'Skirt Support'){
        support = {
          component: 'SkirtSupport',
          supportMaterial: supportMaterial.value? supportMaterial.value: null,
          supportType: supportType.value? supportType.value: null,
          supportOD: supportOD.value? supportOD.value: null,
          supportHeight: supportHeight.value? supportHeight.value: null,
          suitToInsulation: suitToInsulation.value? suitToInsulation.value: null
        }
      }
      emit('search-data', support)
    }

    const hasNull = (obj) => {
      return Object.entries(obj).some(
        ([key, value]) =>
          !['drawingNumber', 'itemCode'].includes(key) && (value === null || value === '')
      );
    }

    const searchJacketData = () => {
        const jacketData = prepareJacketData()
        emit('search-data', jacketData)
    }

    const onUpdateJacketSpport = (val) => {
      console.log(val)
      if(val === null){
        drawingNumberJacketSupport.value = null
        itemCodeJacketSupport.value = null
      }else{
        supportMaterial.value = null
        supportType.value = null
        cToc.value = null
        supportOD.value = null
        supportHeight.value = null
        legSupportType.value = null
        sideBracketSupportType.value = null
        drawingNumberJacketSupport.value = null
        itemCodeJacketSupport.value = null
      }
      
    }

    const prepareJacketData = () => {
        const jacketData = {
            component: 'Jacket',
            jacketType: jacketType.value? jacketType.value.toString() : null,
            jacketTemperature: jacketTemperature.value? jacketTemperature.value.toString() : null,
            jacketPressure: jacketPressure.value? jacketPressure.value.toString() : null,
            suitToInsulation: suitToInsulation.value? suitToInsulation.value: null,
            jacketNDT: ndt.value? ndt.value.toString() : null,
            jacketOD: jacketOD.value? jacketOD.value.toString() : null,
            jacketMaterial: jacketMaterial.value? jacketMaterial.value.toString() : null,
            liftingLug: liftingLug.value? liftingLug.value.toString() : null,
            // earthingType: earthingType.value? earthingType.value.toString() : null,
            shellThickness: shellThickness.value? shellThickness.value.toString() : null,
            dishThickness: dishThickness.value? dishThickness.value.toString() : null,
        }
        const result = flattenForExcel(jacketData)
        return result
    }

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

    // const fillData = (data) => {
    //     jacketType.value = data.jacketType
    //     jacketSupport.value = data.jacketSupport
    //     jacketTemperature.value = data.jacketTemperature
    //     jacketPressure.value = data.jacketPressure
    //     ndt.value = data.jacketNDT
    //     jacketOD.value = data.jacketOD
    //     jacketMaterial.value = data.jacketMaterial
    //     liftingLug.value = data.liftingLug
    //     earthingType.value = data.earthingType
    //     nozzleMaterial.value = data.nozzleMaterial
    //     shellThickness.value = data.shellThickness
    //     dishThickness.value = data.dishThickness
    //     earthingType.value = data.jacketMaterialEarthingType
    //     nozzleTable.value.splice(0, nozzleTable.value.length)
    //     const result = {};
    //     for (const [key, value] of Object.entries(data)) {
    //         if (key.startsWith("nozzle_")) {
    //             try {
    //             result[key] = JSON.parse(value); // Parse JSON strings
    //             nozzleTable.value.push({nozzle: result[key].nozzle, size: result[key].size, degree: result[key].degree, location: result[key].location});
    //             } catch (e) {
    //             console.error(`Failed to parse ${key}:`, e);
    //             result[key] = value;
    //             }
    //         } else {
    //             result[key] = value; // Keep other top-level fields as is
    //         }
    //     }
    // }

    const fillData = (data) => {
      // Jacket
      jacketType.value = data.jacketType || null
      jacketSupport.value = data.jacketSupport || null
      jacketTemperature.value = data.jacketTemperature || null
      jacketPressure.value = data.jacketPressure || null
      ndt.value = data.jacketNDT || null
      jacketOD.value = data.jacketOD || null
      jacketMaterial.value = data.jacketMaterial || null
      liftingLug.value = data.liftingLug || null
      shellThickness.value = data.shellThickness || null
      dishThickness.value = data.dishThickness || null
      drawingNumberJacket.value = data.drawingNumberJacket || null
      itemCodeJacket.value = data.itemCodeJacket || null

      // Earthing
      earthingType.value = data.earthingType || null
      jacketEarthingType.value = data.jacketEarthingType || null
      earthingQuantity.value = data.earthingQuantity || null
      earthingMaterial.value = data.earthingMaterial || null
      earthingOther.value = data.earthingOther || null
      drawingNumberJacketEarthing.value = data.drawingNumberJacketEarthing || null
      itemCodeJacketEarthing.value = data.itemCodeJacketEarthing || null

      // Support
      jacketSupport.value = data.jacketSupport || null  // already set, but harmless
      supportMaterial.value = data.supportMaterial || null
      supportType.value = data.supportType || null
      legSupportType.value = data.legSupportType || null
      sideBracketSupportType.value = data.sideBracketSupportType || null
      supportOD.value = data.supportOD || null
      supportHeight.value = data.supportHeight || null
      cToc.value = data.cToc || null
      supportOther.value = data.supportOther || null
      drawingNumberJacketSupport.value = data.drawingNumberJacketSupport || null
      itemCodeJacketSupport.value = data.itemCodeJacketSupport || null

      // Nozzle and other
      nozzleMaterial.value = data.nozzleMaterial || null
      suitToInsulation.value = data.suitToInsulation || null
      nozzleTable.value.splice(0, nozzleTable.value.length)

      // Parse nozzles if available as JSON strings in keys like "nozzle_0"
      for (const [key, value] of Object.entries(data)) {
        if (key.startsWith("nozzle_")) {
          try {
            const nozzleObj = JSON.parse(value)
            nozzleTable.value.push({
              nozzle: nozzleObj.nozzle || '',
              length: nozzleObj.length || null,
              size: nozzleObj.size || null,
              degree: nozzleObj.degree || null,
              location: nozzleObj.location || '',
              drawingNumber: nozzleObj.drawingNumber || null,
              itemCode: nozzleObj.itemCode || null
            })
          } catch (e) {
            console.error(`Failed to parse ${key}:`, e)
          }
        }
      }
    }

    const normalizeJacketDataFromStorage = (storedData) => {
      if (!storedData || typeof storedData !== 'object') return {}

      const supportComponentToLabel = {
        'SideBracket': 'Side Bracket',
        'LegSupport': 'Leg Support',
        'RingSupport': 'Ring Support',
        'SkirtSupport': 'Skirt Support',
        'SideBracketLegSupport': 'Side Bracket + Leg Support'
      }

      const jacket = storedData.jacket || {}
      const support = storedData.support || {}
      const earthing = storedData.earthing || {}
      const nozzles = Array.isArray(storedData.nozzles) ? storedData.nozzles : []

      const normalized = {
        // Jacket
        jacketType: jacket.jacketType || null,
        jacketSupport: supportComponentToLabel[support.component] || null,  // ✅ HERE
        jacketTemperature: jacket.jacketTemperature || null,
        jacketPressure: jacket.jacketPressure || null,
        jacketNDT: jacket.jacketNDT || null,
        jacketOD: jacket.jacketOD || null,
        jacketMaterial: jacket.jacketMaterial || null,
        liftingLug: jacket.liftingLug || null,
        shellThickness: jacket.shellThickness || null,
        dishThickness: jacket.dishThickness || null,
        drawingNumberJacket: jacket.drawingNumberJacket || null,
        itemCodeJacket: jacket.itemCodeJacket || null,
        suitToInsulation: jacket.suitToInsulation || support.suitToInsulation || null,

        // Support
        supportMaterial: support.supportMaterial || null,
        supportType: support.supportType || null,
        legSupportType: support.legSupportType || null,
        cToc: support.cToc || null,
        sideBracketSupportType: support.sideBracketSupportType || null,
        supportHeight: support.supportHeight || null,
        supportOD: support.supportOD || null,
        supportOther: support.supportOther || null,
        drawingNumberJacketSupport: support.drawingNumberJacketSupport || null,
        itemCodeJacketSupport: support.itemCodeJacketSupport || null,

        // Earthing
        earthingType: earthing.jacketEarthingType || null,
        jacketEarthingType: earthing.jacketEarthingType || null,
        earthingQuantity: earthing.earthingQuantity || null,
        earthingMaterial: earthing.earthingMaterial || null,
        earthingOther: earthing.earthingOther || null,
        drawingNumberJacketEarthing: earthing.drawingNumberJacketEarthing || null,
        itemCodeJacketEarthing: earthing.itemCodeJacketEarthing || null,

        // Material
        nozzleMaterial: storedData.nozzleMaterial || null,
        jacketMaterialEarthingType: earthing.jacketEarthingType || null
      }

      // Nozzles
      nozzles.forEach((nozzle, index) => {
        normalized[`nozzle_${index}`] = JSON.stringify({
          nozzle: nozzle.nozzle || '',
          length: nozzle.length || null,
          size: nozzle.size || null,
          degree: nozzle.degree || null,
          location: nozzle.location || '',
          drawingNumber: nozzle.drawingNumber || null,
          itemCode: nozzle.itemCode || null
        })
      })

      return normalized
    }

    const populateInitialData = (data, master) => {
        jacketType.value = data.jacketType
        jacketSupport.value = data.jacketSupport
        jacketTemperature.value = data.jacketTemperature
        jacketPressure.value = data.jacketPressure
        ndt.value = data.jacketNDT
        jacketOD.value = data.jacketOD
        jacketMaterial.value = data.jacketMaterialShell
        nozzleMaterial.value = data.jacketMaterialNozzle
        earthingType.value = data.jacketMaterialEarthingType
        
        const jacketTypeOptionsTemp = master.master_jacket_type.map(item => item.name)
        jacketTypeOptions.value.splice(0, jacketTypeOptions.value.length)
        jacketTypeOptions.value.push(...jacketTypeOptionsTemp)

        const jacketSupportOptionsTemp = master.master_support.map(item => item.name)
        jacketSupportOptions.value.splice(0, jacketSupportOptions.value.length)

        
        jacketSupportOptionsTemp.push(...['Skirt Support'])
        jacketSupportOptions.value.push(...jacketSupportOptionsTemp)

        const jacketTemperatureOptionsTemp = master.master_temperature.map(item => item.name)
        jacketTemperatureOptions.value.splice(0, jacketTemperatureOptions.value.length)
        jacketTemperatureOptions.value.push(...jacketTemperatureOptionsTemp)

        const jacketPressureOptionsTemp = master.master_pressure.map(item => item.name)
        jacketPressureOptions.value.splice(0, jacketPressureOptions.value.length)
        jacketPressureOptions.value.push(...jacketPressureOptionsTemp)        

        const ndtOptionsTemp = master.master_jacket_ndt.map(item => item.name)
        ndtOptions.value.splice(0, ndtOptions.value.length)
        ndtOptions.value.push(...ndtOptionsTemp)

        const jacketODOptionsTemp = master.master_jacket_od.map(item => item.name)
        jacketODOptions.value.splice(0, jacketODOptions.value.length)
        jacketODOptions.value.push(...jacketODOptionsTemp)

        const jacketMaterialOptionsTemp = master.master_material_shell_jacket.map(item => item.name)
        jacketMaterialOptions.value.splice(0, jacketMaterialOptions.value.length)
        jacketMaterialOptions.value.push(...jacketMaterialOptionsTemp)

        const earthingTypeOptionsTemp = master.master_material_earthing.map(item => item.name)
        earthingTypeOptions.value.splice(0, earthingTypeOptions.value.length)
        earthingTypeOptions.value.push(...earthingTypeOptionsTemp)

        const nozzleMaterialOptionsTemp = master.master_material_nozzle_jacket.map(item => item.name)
        nozzleMaterialOptions.value.splice(0, nozzleMaterialOptions.value.length)
        nozzleMaterialOptions.value.push(...nozzleMaterialOptionsTemp)
                
    }

    const saveToJsonFile = () => {
      let support = null
      console.log('supportType before save:', supportType.value)
      if (jacketSupport.value === 'Side Bracket'){
        support = {
          component: 'SideBracket',
          supportMaterial: supportMaterial.value? supportMaterial.value: null,
          supportType: supportType.value? supportType.value: null,
          // supportType: sideBracketSupportType.value ? sideBracketSupportType.value : null,
          cToc: cToc.value? cToc.value: null,
          suitToInsulation: suitToInsulation.value? suitToInsulation.value: null,
          supportOther: supportOther.value? supportOther.value: null,
        }
      }
      else if(jacketSupport.value === 'Leg Support'){
        support = {
          component: 'LegSupport',
          supportMaterial: supportMaterial.value? supportMaterial.value: null,
          legSupportType: legSupportType.value? legSupportType.value: null,
          supportHeight: supportHeight.value? supportHeight.value: null,
          supportOther: supportOther.value? supportOther.value: null
        }
      }
      else if(jacketSupport.value === 'Side Bracket + Leg Support'){
        support = {
          component: 'SideBracketLegSupport',
          supportMaterial: supportMaterial.value? supportMaterial.value: null,
          legSupportType: legSupportType.value? legSupportType.value: null,
          cToc: cToc.value? cToc.value: null,
          sideBracketSupportType: sideBracketSupportType.value? sideBracketSupportType.value: null,
          supportHeight: supportHeight.value? supportHeight.value: null,
          suitToInsulation: suitToInsulation.value? suitToInsulation.value: null,
          supportOther: supportOther.value? supportOther.value: null
        }
      }
      else if(jacketSupport.value === 'Ring Support'){
        support = {
          component: 'RingSupport',
          supportMaterial: supportMaterial.value? supportMaterial.value: null,
          supportType: supportType.value? supportType.value: null,
          supportOD: supportOD.value? supportOD.value: null,
          suitToInsulation: suitToInsulation.value? suitToInsulation.value: null,
          supportOther: supportOther.value? supportOther.value: null
        }
      }
      else if(jacketSupport.value === 'Skirt Support'){
        support = {
          component: 'SkirtSupport',
          supportMaterial: supportMaterial.value? supportMaterial.value: null,
          supportType: supportType.value? supportType.value: null,
          supportOD: supportOD.value? supportOD.value: null,
          supportHeight: supportHeight.value? supportHeight.value: null,
          suitToInsulation: suitToInsulation.value? suitToInsulation.value: null,
          supportOther: supportOther.value? supportOther.value: null
        }
      }
      const jacketData = {
        component: 'Jacket',
        jacket: {
            jacketType: jacketType.value? jacketType.value.toString() : null,
            jacketTemperature: jacketTemperature.value? jacketTemperature.value.toString() : null,
            jacketPressure: jacketPressure.value? jacketPressure.value.toString() : null,
            suitToInsulation: suitToInsulation.value? suitToInsulation.value: null,
            jacketNDT: ndt.value? ndt.value.toString() : null,
            jacketOD: jacketOD.value? jacketOD.value.toString() : null,
            jacketMaterial: jacketMaterial.value? jacketMaterial.value.toString() : null,
            liftingLug: liftingLug.value? liftingLug.value.toString() : null,
            // earthingType: earthingType.value? earthingType.value.toString() : null,
            shellThickness: shellThickness.value? shellThickness.value.toString() : null,
            dishThickness: dishThickness.value? dishThickness.value.toString() : null,
            drawingNumberJacket: drawingNumberJacket.value? drawingNumberJacket.value: null,
            itemCodeJacket: itemCodeJacket.value? itemCodeJacket.value: null
        },
        support: {
          ...support,
          drawingNumberJacketSupport: drawingNumberJacketSupport.value? drawingNumberJacketSupport.value: null,
          itemCodeJacketSupport: itemCodeJacketSupport.value? itemCodeJacketSupport.value: null
        },
        earthing: {
          jacketEarthingType: jacketEarthingType.value? jacketEarthingType.value: null,
          earthingQuantity: earthingQuantity.value? earthingQuantity.value: null,
          earthingMaterial: earthingMaterial.value? earthingMaterial.value: null,
          earthingOther: earthingOther.value? earthingOther.value: null,
          drawingNumberJacketEarthing: drawingNumberJacketEarthing.value? drawingNumberJacketEarthing.value: null,
          itemCodeJacketEarthing: itemCodeJacketEarthing.value? itemCodeJacketEarthing.value: null
        },
        nozzles: nozzleTable.value
      }

    // ✅ Also save a version to localStorage with all extra fields
      const jacketDataForLocal = {
        ...jacketData,
        nozzleMaterial: nozzleMaterial.value || null,
        nozzles: nozzleTable.value.map(nz => ({
          nozzle: nz.nozzle || '',
          length: nz.length || null, // ✅ Include `length`
          size: nz.size || null,
          degree: nz.degree || null,
          location: nz.location || '',
          drawingNumber: nz.drawingNumber || null,
          itemCode: nz.itemCode || null
        }))
      }
      localStorage.setItem('jacketHistory', JSON.stringify(jacketDataForLocal))
      emit('save-jacket', jacketData)
    }

    const showSaveToJsonButton = ref(false)

    const checkIfAllJacketDataIsComplete = () => {
      const allFilled =
        drawingNumberJacket.value && itemCodeJacket.value &&
        drawingNumberJacketEarthing.value && itemCodeJacketEarthing.value &&
        drawingNumberJacketSupport.value && itemCodeJacketSupport.value &&
        nozzleTable.value.every(row => row.drawingNumber && row.itemCode);

      showSaveToJsonButton.value = Boolean(allFilled);
    };



    const assignValues = (data) => {
      console.log(data)
      if(data?.component === 'JacketNozzle'){
        const foundNozzle = nozzleTable.value.find(row => row.nozzle === searchedNozzleName.value);
        if(foundNozzle){
          foundNozzle.drawingNumber = data.model_info.drawingNumber
          foundNozzle.itemCode = data.model_info.itemCode
        }
      }
      else if(data?.component === 'Jacket'){
        drawingNumberJacket.value = data.model_info.drawingNumber
        itemCodeJacket.value = data.model_info.itemCode
      }
      else if(data?.component === 'Earthing'){
        drawingNumberJacketEarthing.value = data.model_info.drawingNumber
        itemCodeJacketEarthing.value = data.model_info.itemCode
      }else{
        drawingNumberJacketSupport.value = data.model_info.drawingNumber
        itemCodeJacketSupport.value = data.model_info.itemCode
      }

      checkIfAllJacketDataIsComplete();
    }

    return {
        // Jacket
        jacketType,
        jacketTypeOptions,
        jacketTemperature,
        jacketTemperatureOptions,
        jacketPressure,
        jacketPressureOptions,
        ndt,
        ndtOptions,
        jacketOD,
        jacketODOptions,
        jacketMaterial,
        jacketMaterialOptions,
        liftingLug,
        liftingLugOptions,
        earthingType,
        earthingTypeOptions,
        drawingNumberJacket, 
        itemCodeJacket,

        // Earthing
        jacketEarthingType,
        jacketEarthingTypeOptions,
        earthingQuantity,
        earthingQuantityOptions,
        earthingMaterial,
        earthingMaterialOptions,
        earthingOther,
        drawingNumberJacketEarthing,
        itemCodeJacketEarthing,

        // Support
        jacketSupport,
        jacketSupportOptions,
        supportMaterial,
        supportMaterialOptions,
        supportType,
        supportTypeOptions,
        legSupportType,
        legSupportTypeOptions,
        sideBracketSupportType,
        sideBracketSupportTypeOptions,
        supportOD,
        supportHeight,
        cToc,
        supportOther,
        drawingNumberJacketSupport,
        itemCodeJacketSupport,

        // Nozzle
        searchedNozzleName,
        nozzleMaterial,
        nozzleMaterialOptions,
        suitToInsulation,
        suitToInsulationOptions,
        nozzleTable,
        shellThickness,
        dishThickness,

        // Extra
        showSaveToJsonButton,

        // Method
        showField,
        getJacketMasters,
        searchJacketData,
        searchJacketEarthing,
        searchNozzle,
        searchJacketSupport,
        onUpdateJacketSpport,
        prepareJacketData,
        fillData,
        normalizeJacketDataFromStorage,
        checkIfAllJacketDataIsComplete,
        assignValues,
        addNozzleRow,
        removeLastNozzleRow,
        populateInitialData,
        saveToJsonFile
    }
  },
  // watch: {
  //   jacketMasters: {
  //     handler(newVal) {
  //       if (newVal !== null && this.jacket) {
  //         this.populateInitialData(this.jacket, newVal);
  //       }
  //     },
  //     immediate: true
  //   },
  //   jacket: {
  //     handler(newVal) {
  //       if (newVal?.model_info) {
  //         this.assignValues(newVal);
  //       }
  //     },
  //     immediate: true
  //   },

  watch: {
    jacketMasters: {
      handler(newVal) {
        if (!this.loadedFromLocalStorage && newVal !== null && this.jacket) {
          this.populateInitialData(this.jacket, newVal)
        }
      },
      immediate: true
    },
    jacket: {
      handler(newVal) {
        if (newVal?.model_info) {
          this.assignValues(newVal)
        }
      },
      immediate: true
    }
  }
}
</script>