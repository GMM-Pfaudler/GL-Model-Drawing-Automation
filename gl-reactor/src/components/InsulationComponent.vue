<template>
  <div class="q-pa-md" style="height: 100vh; display: flex; flex-direction: column;">
    <div class="q-mb-md">
      <div class="row q-gutter-md q-wrap items-center">
        <q-select
          outlined
          v-model="insulationReq"
          :options="insulationReqOptions"
          @update:model-value="onUpdateInsulationReq"
          label="Insulation Requirement"
          :rules="[val => !!val || 'Please select a value']"
          dense
          class="col-12 col-md-2"
        />
        <q-select
          outlined
          v-if="insulationReq === 'Yes'"
          v-model="insulationType"
          :options="insulationTypeOptions"
          @update:model-value="onUpdateInsulationType"
          label="Type"
          :rules="[val => !!val || 'Please select a value']"
          dense
          class="col-12 col-md-2"
        />
        <q-select
          outlined
          v-if="insulationReq === 'Yes' && (insulationType === 'Cleat' || insulationType === 'Nut')"
          v-model="insulationMaterial"
          :options="insulationMaterialOptions"
          label="Material"
          :rules="[val => !!val || 'Please select a value']"
          dense
          class="col-12 col-md-2"
        />
        <q-select
          outlined
          v-if="insulationReq === 'Yes' && (insulationType === 'Cleat' || insulationType === 'Nut')"
          v-model="insulationSize"
          :options="insulationSizeOptions"
          label="Size"
          :rules="[val => !!val || 'Please select a value']"
          dense
          class="col-12 col-md-2"
        />
        <q-btn
            outline
            v-if="insulationReq === 'Yes' && (insulationType === 'Cleat' || insulationType === 'Nut')"
            round
            color="primary"
            icon="search"
            @click="searchInsulationData('cleatNut')"
            dense
            class="self-center"
            />
        <q-space/>
        <!-- v-if="itemCodeOne !== null || itemCodeTwo !== null" -->
        <q-chip  v-if="insulationReq === 'Yes'" icon="check" square color="green-5" text-color="white" clickable @click="saveToJsonFile()">
            {{ "Save To File"}}
        </q-chip>
      </div>
      <div class="row q-gutter-md q-wrap items-center">
            <q-chip
            v-if="drawingNumberCleatNut"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Drawing Number: {{ drawingNumberCleatNut }}
            </q-chip>

            <q-chip
            v-if="itemCodeCleatNut"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Item Code: {{ itemCodeCleatNut }}
            </q-chip>
          </div>
    </div>
    <q-separator spaced />

    <!-- Insulation Nut -->
    <div v-if="insulationReq === 'Yes' && insulationType === 'Top Head & Jacket'" class="text-h6 q-mb-md">Insulation On Top Head</div>
    <div v-if="insulationReq === 'Yes' && insulationType === 'Top Head & Jacket'" class="q-mb-md">
        <div class="row q-gutter-md q-wrap items-center">
            <q-select
            outlined
            v-model="topHeadMaterial"
            :options="topHeadMaterialOptions"
            @update:model-value="onUpdateTopHeadMaterial"
            label="Material"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            />
            <q-select
            outlined
            v-model="topHeadCladdingThickness"
            :options="topHeadCladdingThicknessOptions"
            label="Cladding Thickness"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            />
            <q-select
            outlined
            v-model="topHeadInsulationThickness"
            :options="topHeadInsulationThicknessOptions"
            label="Insulation Thickness"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            />
            <q-btn
            outline
            round
            color="primary"
            icon="search"
            @click="searchInsulationData('topHead')"
            dense
            class="self-center"
            />
          </div>
          <div class="row q-gutter-md q-wrap items-center">
            <q-chip
            v-if="drawingNumberTopHead"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Drawing Number: {{ drawingNumberTopHead }}
            </q-chip>

            <q-chip
            v-if="itemCodeTopHead"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Item Code: {{ itemCodeTopHead }}
            </q-chip>
          </div>
    </div>
    <q-separator spaced />

    <div v-if="insulationReq === 'Yes' && (insulationType === 'Top Head & Jacket' || insulationType === 'Jacket')" class="text-h6 q-mb-md">Insulation On Jacket - Top JCR</div>
    <div v-if="insulationReq === 'Yes' && (insulationType === 'Top Head & Jacket' || insulationType === 'Jacket')" class="q-mb-md">
        <div class="row q-gutter-md q-wrap items-center">
            <q-select
            outlined
            v-model="topJCRMaterial"
            :options="topJCRMaterialOptions"
            @update:model-value="onUpdateTopJCRMaterial"
            label="Material"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            />
            <q-select
            outlined
            v-model="topJCRCladdingThickness"
            :options="topJCRCladdingThicknessOptions"
            label="Cladding Thickness"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            />
            <q-select
            outlined
            v-model="topJCRInsulationThickness"
            :options="topJCRInsulationThicknessOptions"
            label="Insulation Thickness"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            />
            <q-btn
            outline
            round
            color="primary"
            icon="search"
            @click="searchInsulationData('topJCR')"
            dense
            class="self-center"
            />
            </div>
            <div class="row q-gutter-md q-wrap items-center">
            <q-chip
            v-if="drawingNumberTopJCR"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Drawing Number: {{ drawingNumberTopJCR }}
            </q-chip>

            <q-chip
            v-if="itemCodeTopJCR"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Item Code: {{ itemCodeTopJCR }}
            </q-chip>
          </div>
    </div>
    <q-separator spaced />

    <div v-if="insulationReq === 'Yes' && (insulationType === 'Top Head & Jacket' || insulationType === 'Jacket')" class="text-h6 q-mb-md">Insulation On Jacket - Shell</div>
    <div v-if="insulationReq === 'Yes' && (insulationType === 'Top Head & Jacket' || insulationType === 'Jacket')" class="q-mb-md">
        <div class="row q-gutter-md q-wrap items-center">
            <q-select
            outlined
            v-model="shellMaterial"
            :options="shellMaterialOptions"
            @update:model-value="onUpdateShellMaterial"
            label="Material"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            />
            <q-select
            outlined
            v-model="shellCladdingThickness"
            :options="shellCladdingThicknessOptions"
            label="Cladding Thickness"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            />
            <q-select
            outlined
            v-model="shellInsulationThickness"
            :options="shellInsulationThicknessOptions"
            label="Insulation Thickness"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            />
            <q-btn
            outline
            round
            color="primary"
            icon="search"
            @click="searchInsulationData('shell')"
            dense
            class="self-center"
            />
            </div>
            <div class="row q-gutter-md q-wrap items-center">
            <q-chip
            v-if="drawingNumberShell"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Drawing Number: {{ drawingNumberShell }}
            </q-chip>

            <q-chip
            v-if="itemCodeShell"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Item Code: {{ itemCodeShell }}
            </q-chip>
          </div>
    </div>
    <q-separator spaced />

    <div v-if="insulationReq === 'Yes' && (insulationType === 'Top Head & Jacket' || insulationType === 'Jacket')" class="text-h6 q-mb-md">Insulation On Jacket - Head</div>
    <div v-if="insulationReq === 'Yes' && (insulationType === 'Top Head & Jacket' || insulationType === 'Jacket')" class="q-mb-md">
        <div class="row q-gutter-md q-wrap items-center">
            <q-select
            outlined
            v-model="headMaterial"
            :options="headMaterialOptions"
            @update:model-value="onUpdateHeadMaterial"
            label="Material"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            />
            <q-select
            outlined
            v-model="headCladdingThickness"
            :options="headCladdingThicknessOptions"
            label="Cladding Thickness"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            />
            <q-select
            outlined
            v-model="headInsulationThickness"
            :options="headInsulationThicknessOptions"
            label="Insulation Thickness"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            />
            <q-btn
            outline
            round
            color="primary"
            icon="search"
            @click="searchInsulationData('head')"
            dense
            class="self-center"
            />
            </div>
            <div class="row q-gutter-md q-wrap items-center">
            <q-chip
            v-if="drawingNumberHead"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Drawing Number: {{ drawingNumberHead }}
            </q-chip>

            <q-chip
            v-if="itemCodeHead"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Item Code: {{ itemCodeHead }}
            </q-chip>
          </div>
    </div>
    <q-separator spaced />

    <div v-if="insulationReq === 'Yes' && (insulationType === 'Top Head & Jacket' || insulationType === 'Jacket')" class="text-h6 q-mb-md">Insulation On Jacket - Closer</div>
    <div v-if="insulationReq === 'Yes' && (insulationType === 'Top Head & Jacket' || insulationType === 'Jacket')" class="q-mb-md" style="flex-grow: 1; display: flex; flex-direction: column; padding-bottom: 300px;">
        <div class="row q-gutter-md q-wrap items-center">
            <q-select
            outlined
            v-model="closerMaterial"
            :options="closerMaterialOptions"
            @update:model-value="onUpdateCloserMaterial"
            label="Material"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            />
            <q-select
            outlined
            v-model="closerCladdingThickness"
            :options="closerCladdingThicknessOptions"
            label="Cladding Thickness"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            />
            <q-select
            outlined
            v-model="closerInsulationThickness"
            :options="closerInsulationThicknessOptions"
            label="Insulation Thickness"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            />
            <q-btn
            outline
            round
            color="primary"
            icon="search"
            @click="searchInsulationData('closer')"
            dense
            class="self-center"
            />
            </div>
            <div class="row q-gutter-md q-wrap items-center">
            <q-chip
            v-if="drawingNumberCloser"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Drawing Number: {{ drawingNumberCloser }}
            </q-chip>

            <q-chip
            v-if="itemCodeCloser"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Item Code: {{ itemCodeCloser }}
            </q-chip>
          </div>
    </div>
 </div>
</template>
<script>
import { ref , onMounted} from 'vue'
export default {
  name: 'InsulationComponent',
  props: {
    insulation: Object
  },
  emits: ['search-data', 'save-insulation-data'],
  setup (props, { emit }) {
    const insulationReq = ref(null)
    const insulationReqOptions = ref(['-', 'Yes', 'No'])
    const insulationType = ref(null)
    const insulationTypeOptions = ref(['-','Cleat', 'Nut', 'Top Head & Jacket', 'Jacket'])
    const insulationMaterial = ref(null)
    const insulationMaterialOptions = ref(['-','MS', 'SS304', 'SS316'])
    const insulationSize = ref(null)
    const insulationSizeOptions = ref(['-'])
    const drawingNumberCleatNut = ref(null)
    const itemCodeCleatNut = ref(null)
    // Top Head
    const topHeadMaterial = ref(null)
    const topHeadMaterialOptions = ref(['-','MS', 'SS304', 'SS316'])
    const topHeadCladdingThicknessOptions = ref(['-', '2.5 mm', '3 mm', '6 mm'])
    const topHeadCladdingThickness = ref(topHeadCladdingThicknessOptions.value[2])
     const topHeadInsulationThicknessOptions = ref(['-', '25mm', '75 mm', '100 mm', '125 mm'])
    const topHeadInsulationThickness = ref(topHeadInsulationThicknessOptions.value[1])
    const drawingNumberTopHead = ref(null)
    const itemCodeTopHead = ref(null)
    // Top JCR
    const topJCRMaterial = ref(null)
    const topJCRMaterialOptions = ref(['-','MS', 'SS304', 'SS316'])
    const topJCRCladdingThickness = ref(null)
    const topJCRCladdingThicknessOptions = ref(['-', '2.5 mm', '3 mm', '6 mm'])
    const topJCRInsulationThickness = ref(null)
    const topJCRInsulationThicknessOptions = ref(['-', '75 mm', '100 mm', '125 mm'])
    const drawingNumberTopJCR = ref(null)
    const itemCodeTopJCR = ref(null)
    // Shell
    const shellMaterial = ref(null)
    const shellMaterialOptions = ref(['-','MS', 'SS304', 'SS316'])
    const shellCladdingThickness = ref(null)
    const shellCladdingThicknessOptions = ref(['-', '2.5 mm', '3 mm', '6 mm'])
    const shellInsulationThickness = ref(null)
    const shellInsulationThicknessOptions = ref(['-', '75 mm', '100 mm', '125 mm'])
    const drawingNumberShell = ref(null)
    const itemCodeShell = ref(null)
    // Head
    const headMaterial = ref(null)
    const headMaterialOptions = ref(['-','MS', 'SS304', 'SS316'])
    const headCladdingThickness = ref(null)
    const headCladdingThicknessOptions = ref(['-', '2.5 mm', '3 mm', '6 mm'])
    const headInsulationThickness = ref(null)
    const headInsulationThicknessOptions = ref(['-', '75 mm', '100 mm', '125 mm'])
    const drawingNumberHead = ref(null)
    const itemCodeHead = ref(null)
    // Closer
    const closerMaterial = ref(null)
    const closerMaterialOptions = ref(['-','MS', 'SS304', 'SS316'])
    const closerCladdingThickness = ref(null)
    const closerCladdingThicknessOptions = ref(['-', '2.5 mm', '3 mm', '6 mm'])
    const closerInsulationThickness = ref(null)
    const closerInsulationThicknessOptions = ref(['-', '75 mm', '100 mm', '125 mm'])
    const drawingNumberCloser = ref(null)
    const itemCodeCloser = ref(null)

    // onMounted(() => {
    //     console.log('Insulation')
    // })
    
    const LOCAL_STORAGE_KEY = 'insulation'

    onMounted(() => {
      const saved = localStorage.getItem(LOCAL_STORAGE_KEY)
      if (!saved) return

      try {
        const parsed = JSON.parse(saved)

        // Top-level
        insulationReq.value = parsed.insulationReq ?? null
        insulationType.value = parsed.insulationType ?? null

        // Cleat Nut
        const cleatNut = parsed.cleatNut || {}
        insulationMaterial.value = cleatNut.insulationMaterial ?? null
        insulationSize.value = cleatNut.insulationSize ?? null
        drawingNumberCleatNut.value = cleatNut.drawingNumberCleatNut ?? null
        itemCodeCleatNut.value = cleatNut.itemCodeCleatNut ?? null

        // Top Head
        const topHead = parsed.topHead || {}
        topHeadMaterial.value = topHead.topHeadMaterial ?? null
        topHeadCladdingThickness.value = topHead.topHeadCladdingThickness ?? null
        topHeadInsulationThickness.value = topHead.topHeadInsulationThickness ?? null
        drawingNumberTopHead.value = topHead.drawingNumberTopHead ?? null
        itemCodeTopHead.value = topHead.itemCodeTopHead ?? null

        // Top JCR
        const topJCR = parsed.topJCR || {}
        topJCRMaterial.value = topJCR.topJCRMaterial ?? null
        topJCRCladdingThickness.value = topJCR.topJCRCladdingThickness ?? null
        topJCRInsulationThickness.value = topJCR.topJCRInsulationThickness ?? null
        drawingNumberTopJCR.value = topJCR.drawingNumberTopJCR ?? null
        itemCodeTopJCR.value = topJCR.itemCodeTopJCR ?? null

        // Shell
        const shell = parsed.shell || {}
        shellMaterial.value = shell.shellMaterial ?? null
        shellCladdingThickness.value = shell.shellCladdingThickness ?? null
        shellInsulationThickness.value = shell.shellInsulationThickness ?? null
        drawingNumberShell.value = shell.drawingNumberShell ?? null
        itemCodeShell.value = shell.itemCodeShell ?? null

        // Head
        const head = parsed.head || {}
        headMaterial.value = head.headMaterial ?? null
        headCladdingThickness.value = head.headCladdingThickness ?? null
        headInsulationThickness.value = head.headInsulationThickness ?? null
        drawingNumberHead.value = head.drawingNumberHead ?? null
        itemCodeHead.value = head.itemCodeHead ?? null

        // Closer
        const closer = parsed.closer || {}
        closerMaterial.value = closer.closerMaterial ?? null
        closerCladdingThickness.value = closer.closerCladdingThickness ?? null
        closerInsulationThickness.value = closer.closerInsulationThickness ?? null
        drawingNumberCloser.value = closer.drawingNumberCloser ?? null
        itemCodeCloser.value = closer.itemCodeCloser ?? null

      } catch (err) {
        console.error('Failed to parse insulation localStorage:', err)
      }
    })


    const saveToJsonFile = () => {
      const allInsulationData = {
        component: 'Insulation',
        insulationReq: insulationReq.value? insulationReq.value: null,
        insulationType: insulationType.value? insulationType.value: null,
        cleatNut: {
          insulationMaterial: insulationMaterial.value? insulationMaterial.value: null,
          insulationSize: insulationSize.value? insulationSize.value: null,
          drawingNumberCleatNut: drawingNumberCleatNut.value? drawingNumberCleatNut.value: null,
          itemCodeCleatNut: itemCodeCleatNut.value? itemCodeCleatNut.value: null
        },
        topHead: {
          topHeadMaterial: topHeadMaterial.value? topHeadMaterial.value: null,
          topHeadCladdingThickness: topHeadCladdingThickness.value? topHeadCladdingThickness.value: null,
          topHeadInsulationThickness: topHeadInsulationThickness.value? topHeadInsulationThickness.value: null,
          drawingNumberTopHead: drawingNumberTopHead.value? drawingNumberTopHead.value: null,
          itemCodeTopHead: itemCodeTopHead.value? itemCodeTopHead.value: null
        },
        topJCR: {
          topJCRMaterial: topJCRMaterial.value? topJCRMaterial.value: null,
          topJCRCladdingThickness: topJCRCladdingThickness.value? topJCRCladdingThickness.value: null,
          topJCRInsulationThickness: topJCRInsulationThickness.value? topJCRInsulationThickness.value: null,
          drawingNumberTopJCR: drawingNumberTopJCR.value? drawingNumberTopJCR.value: null,
          itemCodeTopJCR: itemCodeTopJCR.value? itemCodeTopJCR.value: null
        },
        shell: {
          shellMaterial: shellMaterial.value? shellMaterial.value: null,
          shellCladdingThickness: shellCladdingThickness.value? shellCladdingThickness.value: null,
          shellInsulationThickness: shellInsulationThickness.value? shellInsulationThickness.value: null,
          drawingNumberShell: drawingNumberShell.value? drawingNumberShell.value: null,
          itemCodeShell: itemCodeShell.value? itemCodeShell.value: null,
        },
        head: {
          headMaterial: headMaterial.value? headMaterial.value: null,
          headCladdingThickness: headCladdingThickness.value? headCladdingThickness.value: null,
          headInsulationThickness: headInsulationThickness.value? headInsulationThickness.value: null,
          drawingNumberHead: drawingNumberHead.value? drawingNumberHead.value: null,
          itemCodeHead: itemCodeHead.value? itemCodeHead.value: null,
        },
        closer: {
          closerMaterial: closerMaterial.value? closerMaterial.value: null,
          closerCladdingThickness: closerCladdingThickness.value? closerCladdingThickness.value: null,
          closerInsulationThickness: closerInsulationThickness.value? closerCladdingThickness.value: null,
          drawingNumberCloser: drawingNumberCloser.value? drawingNumberCloser.value: null,
          itemCodeCloser: itemCodeCloser.value? itemCodeCloser.value: null
        }
      }
      emit('save-insulation-data', allInsulationData)
      localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(allInsulationData))
    }
    

    
    const searchInsulationData = (item) => {
      let toSearchObj = null
      if(item === 'cleatNut'){
        toSearchObj = {
          component: insulationType.value? insulationType.value: null, // 'Cleat' or 'Nut'
          insulationReq: insulationReq.value? insulationReq.value: null,
          insulationType: insulationType.value? insulationType.value: null,
          insulationMaterial: insulationMaterial.value? insulationMaterial.value: null,
          insulationSize: insulationSize.value? insulationSize.value: null
        }
      }else if(item === 'topHead'){
        toSearchObj = {
          component: 'TopHead',
          insulationReq: insulationReq.value? insulationReq.value: null,
          insulationType: insulationType.value? insulationType.value: null,
          topHeadMaterial: topHeadMaterial.value? topHeadMaterial.value: null,
          topHeadCladdingThickness: topHeadCladdingThickness.value? topHeadCladdingThickness.value: null,
          topHeadInsulationThickness: topHeadInsulationThickness.value? topHeadInsulationThickness.value: null
        }
      }else if(item === 'topJCR'){
        toSearchObj = {
          component: 'TopJCR',
          insulationReq: insulationReq.value? insulationReq.value: null,
          insulationType: insulationType.value? insulationType.value: null,
          topJCRMaterial: topJCRMaterial.value? topJCRMaterial.value: null,
          topJCRCladdingThickness: topJCRCladdingThickness.value? topJCRCladdingThickness.value: null,
          topJCRInsulationThickness: topJCRInsulationThickness.value? topJCRInsulationThickness.value: null
        }
      }else if(item === 'head'){
        toSearchObj = {
          component: 'Head',
          insulationReq: insulationReq.value? insulationReq.value: null,
          insulationType: insulationType.value? insulationType.value: null,
          headMaterial: headMaterial.value? headMaterial.value: null,
          headCladdingThickness: headCladdingThickness.value? headCladdingThickness.value: null,
          headInsulationThickness: headInsulationThickness.value? headInsulationThickness.value: null
        }
      }else if(item === 'shell'){
        toSearchObj = {
          component: 'Shell',
          insulationReq: insulationReq.value? insulationReq.value: null,
          insulationType: insulationType.value? insulationType.value: null,
          shellMaterial: shellMaterial.value? shellMaterial.value: null,
          shellCladdingThickness: shellCladdingThickness.value? shellCladdingThickness.value: null,
          shellInsulationThickness: shellInsulationThickness.value? shellInsulationThickness.value: null
        }
      }else if(item === 'closer'){
        toSearchObj = {
          component: 'Closer',
          insulationReq: insulationReq.value? insulationReq.value: null,
          insulationType: insulationType.value? insulationType.value: null,
          closerMaterial: closerMaterial.value? closerMaterial.value: null,
          closerCladdingThickness: closerCladdingThickness.value? closerCladdingThickness.value: null,
          closerInsulationThickness: closerInsulationThickness.value? closerInsulationThickness.value: null
        }
      }
      emit('search-data', toSearchObj)
    }

    const onUpdateInsulationReq = (val) => {
      if(val === 'No' || insulationReq.value === null || val === '-'){
        drawingNumberCleatNut.value = null
        itemCodeCleatNut.value = null
      }
    }

    const onUpdateInsulationType = (val) => {
      if(val === 'Nut'){
        insulationSizeOptions.value.splice(0, insulationSizeOptions.value.length)
        insulationSizeOptions.value.push(...['-', 'M8', 'M12', 'M12 UNC'])
        insulationSize.value = insulationSizeOptions.value[1]
      }else if(val === 'Cleat'){
        insulationSizeOptions.value.splice(0, insulationSizeOptions.value.length)
        insulationSizeOptions.value.push(...['-', 'Standard'])
        insulationSize.value = insulationSizeOptions.value[1]
      }else if(val === 'Top Head & Jacket'){
        drawingNumberCleatNut.value = null
        itemCodeCleatNut.value = null
        insulationMaterial.value = null
        insulationSize.value = null
      }else if(val === 'Jacket'){
        drawingNumberCleatNut.value = null
        itemCodeCleatNut.value = null
        insulationMaterial.value = null
        insulationSize.value = null
        drawingNumberTopHead.value = null
        itemCodeTopHead.value = null
        topHeadMaterial.value = null
        topHeadCladdingThickness.value = null
        topHeadInsulationThickness.value = null
      }
    }

    const onUpdateTopHeadMaterial = (val) => {
      if(val === 'MS'){
        topHeadCladdingThickness.value = topHeadCladdingThicknessOptions.value[3]
      }
    }

    const onUpdateTopJCRMaterial = (val) => {
      if(val === 'MS'){
        topJCRCladdingThickness.value = topJCRCladdingThicknessOptions.value[3]
      }
    }

    const onUpdateHeadMaterial = (val) => {
      if(val === 'MS'){
        headCladdingThickness.value = headCladdingThicknessOptions.value[3]
      }
    }

    const onUpdateShellMaterial = (val) => {
      if(val === 'MS'){
        shellCladdingThickness.value = shellCladdingThicknessOptions.value[3]
      }
    }

    const onUpdateCloserMaterial = (val) => {
      if(val === 'MS'){
        closerCladdingThickness.value = closerCladdingThicknessOptions.value[3]
      }
    }

    const assignData = (obj) => {
      if(obj?.reactor){
        if(obj?.reactor === 'MSGL Reactor'){
          insulationReq.value = insulationReqOptions.value[2]
        }
      }else{
        if(obj !== null && obj.component === 'Cleat') {
          drawingNumberCleatNut.value = obj?.model_info.drawingNumber
          itemCodeCleatNut.value = obj?.model_info.itemCode
        }else if(obj !== null && obj.component === 'Nut') {
          drawingNumberCleatNut.value = obj?.model_info.drawingNumber
          itemCodeCleatNut.value = obj?.model_info.itemCode
        }else if(obj !== null && obj.component === 'TopHead') {
          drawingNumberTopHead.value = obj?.model_info.drawingNumber
          itemCodeTopHead.value = obj?.model_info.itemCode
        }else if(obj !== null && obj.component === 'TopJCR') {
          drawingNumberTopJCR.value = obj?.model_info.drawingNumber
          itemCodeTopJCR.value = obj?.model_info.itemCode
        }else if(obj !== null && obj.component === 'Head') {
          drawingNumberHead.value = obj?.model_info.drawingNumber
          itemCodeHead.value = obj?.model_info.itemCode
        }else if(obj !== null && obj.component === 'Shell') {
          drawingNumberShell.value = obj?.model_info.drawingNumber
          itemCodeShell.value = obj?.model_info.itemCode
        }else if(obj !== null && obj.component === 'Closer') {
          drawingNumberCloser.value = obj?.model_info.drawingNumber
          itemCodeCloser.value = obj?.model_info.itemCode
        }
      }
    }

    return {
        // Insulation Details
        insulationReq,
        insulationReqOptions,
        insulationType,
        insulationTypeOptions,
        insulationMaterial,
        insulationMaterialOptions,
        insulationSize,
        insulationSizeOptions,
        drawingNumberCleatNut,
        itemCodeCleatNut,
        // Top Head
        topHeadMaterial,
        topHeadMaterialOptions,
        topHeadCladdingThickness,
        topHeadCladdingThicknessOptions,
        topHeadInsulationThickness,
        topHeadInsulationThicknessOptions,
        drawingNumberTopHead,
        itemCodeTopHead,
        // Top JCR
        topJCRMaterial,
        topJCRMaterialOptions,
        topJCRCladdingThickness,
        topJCRCladdingThicknessOptions,
        topJCRInsulationThickness,
        topJCRInsulationThicknessOptions,
        drawingNumberTopJCR,
        itemCodeTopJCR,
        // Shell
        shellMaterial,
        shellMaterialOptions,
        shellCladdingThickness,
        shellCladdingThicknessOptions,
        shellInsulationThickness,
        shellInsulationThicknessOptions,
        drawingNumberShell,
        itemCodeShell,
        // Head
        headMaterial,
        headMaterialOptions,
        headCladdingThickness,
        headCladdingThicknessOptions,
        headInsulationThickness,
        headInsulationThicknessOptions,
        drawingNumberHead,
        itemCodeHead,
        // Closer
        closerMaterial,
        closerMaterialOptions,
        closerCladdingThickness,
        closerCladdingThicknessOptions,
        closerInsulationThickness,
        closerInsulationThicknessOptions,
        drawingNumberCloser,
        itemCodeCloser,
        // Methods
        searchInsulationData,
        onUpdateInsulationReq,
        onUpdateInsulationType,
        onUpdateTopHeadMaterial,
        onUpdateTopJCRMaterial,
        onUpdateHeadMaterial,
        onUpdateShellMaterial,
        onUpdateCloserMaterial,
        assignData,
        saveToJsonFile
    }
  },
  watch: {
    insulation: {
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