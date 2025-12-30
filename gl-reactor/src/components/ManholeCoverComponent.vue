<template>
    <q-page class="q-pa-md">
     <!-- First Row -->
    <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap">
            <q-input
            outlined
            v-model="manholeCoverSize"
            label="Size"
            dense
            class="col-12 col-md-2"
            />
            <q-select
            outlined
            v-model="manholeLiningType"
            :options="manholeLiningTypeOptions"
            @update:model-value="onUpdateLiningType"
            label="Type - Lining"
            dense
            class="col-12 col-md-2"
            />

            <q-space/>
            <q-btn outline rounded color="primary" icon="search" label="Search" @click="searchManholeCoverData"/>
        </div>
    </div>
    <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap">
            <q-select
            outlined
            v-model="manholeMaterial"
            :options="manholeMaterialOptions"
            label="Material"
            dense
            class="col-12 col-md-2"
            />
            <q-select
            outlined
            v-model="manholeType"
            :options="manholeTypeOptions"
            label="Type"
            dense
            class="col-12 col-md-2"
            />
        </div>
    </div>

    <q-separator spaced />
    <!-- Jacket Nozzle Table -->
    <div>
      <!-- Table Header -->
      <div class="row q-col-gutter-sm items-center q-pb-sm">
        <div class="col"><strong>Nozzle</strong></div>
        <div class="col"><strong>Size</strong></div>
        <div class="col"><strong>Degree</strong></div>
      </div>

      <!-- Table Rows -->
      <div
        v-for="(row, index) in nozzleTable"
        :key="index"
        class="row q-col-gutter-sm items-center q-mb-sm"
      >
        <div class="col">
          <q-input v-model="row.nozzle" outlined dense />
        </div>
        <div class="col">
          <q-input v-model.number="row.size" type="text" outlined dense />
        </div>
        <div class="col">
          <q-input v-model.number="row.degree" type="text" outlined dense />
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
export default {
  name: 'ManholeCover',
  props: {
    manholeCover: Object
  },
  emits: ['search-data'],
  setup (props, { emit }) {
    const nozzleTable = ref([{ nozzle: '', size: null, degree: null }]);
    const manholeCoverSize = ref(null)
    const manholeLiningType = ref(null)
    const manholeLiningTypeOptions = ref(['-', 'Glass Lined', 'PFA Lined'])
    const manholeMaterial = ref(null)
    const manholeMaterialOptions = ref(['MS', 'SS304', 'SS316', 'SS316L'])
    const manholeType = ref(null)
    const manholeTypeOptions = ref(['-', 'Dome with pad type', 'Dome with nozzle', 'Flat'])

    onMounted(() => {
        const manholecover = localStorage.getItem('manholecover')
        const data = JSON.parse(manholecover)
        if(data !== null){
            manholeCoverSize.value = data.manholeCoverSize
            manholeLiningType.value = data.manholeLiningType
            manholeType.value = data.manholeType
            manholeMaterial.value = data.manholeMaterial
            nozzleTable.value.splice(0, nozzleTable.value.length)
            const result = {};
            for (const [key, value] of Object.entries(data)) {
                if (key.startsWith("nozzle_")) {
                    try {
                    result[key] = JSON.parse(value); // Parse JSON strings
                    nozzleTable.value.push({nozzle: result[key].nozzle, size: result[key].size, degree: result[key].degree, location: result[key].location});
                    } catch (e) {
                    console.error(`Failed to parse ${key}:`, e);
                    result[key] = value;
                    }
                } else {
                    result[key] = value; // Keep other top-level fields as is
                }
            }
        }
    })

    const addNozzleRow = () => {
        nozzleTable.value.push({ nozzle: '', size: null, degree: null });
    }

    const removeLastNozzleRow = () => {
        if (nozzleTable.value.length > 0) {
            nozzleTable.value.pop();
        }
    }

    const searchManholeCoverData = () => {
        const manholeCoverData = prepareManholeCoverData()
        emit('search-data', manholeCoverData)
    }

    const prepareManholeCoverData = () => {
        const data = {
            component: 'ManholeCover',
            manholeCoverSize: manholeCoverSize.value?manholeCoverSize.value:null,
            nozzleTable: nozzleTable.value?nozzleTable.value:null,
            manholeLiningType: manholeLiningType.value? manholeLiningType.value: null,
            manholeType: manholeType.value? manholeType.value: null,
            manholeMaterial: manholeMaterial.value? manholeMaterial.value: null
        }
        const result = flattenForExcel(data)
        localStorage.setItem('manholecover', JSON.stringify(result))
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

    const populateInitialData = (data) => {
      const nozzle_services = JSON.parse(data.nozzle_services)
        const nozzle_sizes = JSON.parse(data.nozzle_sizes)
        for (let i = 0; i < nozzle_services.length; i++) {
            if(nozzle_services[i] === 'Manhole'){
                manholeCoverSize.value = nozzle_sizes[i]
            }
        }
    }

    const onUpdateLiningType = (val) => {
      if(val === 'Glass Lined'){
        manholeMaterialOptions.value.splice(0, manholeMaterialOptions.value.length)
        manholeMaterialOptions.value.push(...['-', 'MS', 'SS316L'])
      }else {
        manholeMaterialOptions.value.splice(0, manholeMaterialOptions.value.length)
        manholeMaterialOptions.value.push(...['-', 'MS', 'SS304', 'SS316', 'SS316L'])
      }
    }

    return {
        nozzleTable,
        manholeCoverSize,
        manholeLiningType,
        manholeLiningTypeOptions,
        manholeMaterial,
        manholeMaterialOptions,
        manholeType,
        manholeTypeOptions,

        // Methods
        addNozzleRow,
        removeLastNozzleRow,
        searchManholeCoverData,
        onUpdateLiningType,
        populateInitialData
    }
  },
  watch: {
    manholeCover: {
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