<template>
  <div class="q-pa-md" style="height: 100vh; display: flex; flex-direction: column;">
    <div class="q-mb-md">
      <div class="row q-gutter-md q-wrap items-center">
        <q-space/>
        <q-chip icon="check" square color="green-5" text-color="white" clickable :disable="!showSaveToJsonButton" @click="saveToJsonFile()">
          {{ "Save To File" }}
          <q-tooltip v-if="!showSaveToJsonButton">
            Please complete all required drawing numbers and item codes.
          </q-tooltip>
        </q-chip>
      </div>
    </div>
    <q-separator spaced />

    <div class="text-h6 q-mb-md">Drive Base Ring</div>
    <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap items-center">
            <q-select
            outlined
            v-model="driveBaseRingMaterial"
            :options="driveBaseRingMaterialOptions"
            label="Material"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            />
            <q-input
            outlined
            v-model="driveBaseRingFlangeNominalSize"
            label="Flange Nominal Size (DBR Size)"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            clearable
            />
            <q-input
            outlined
            v-model="driveBaseRingOther"
            label="Other / Addition Information"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            clearable
            />
            <q-btn
            outline
            round
            color="primary"
            icon="search"
            @click="searchDriveAssemblyData('driveBaseRing')"
            dense
            class="self-center"
            />
          </div>
          <div class="row q-gutter-md q-wrap items-center">
            <q-chip
            v-if="drawingNumberDriveBaseRing"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Drawing Number: {{ drawingNumberDriveBaseRing }}
            </q-chip>

            <q-chip
            v-if="itemCodeDriveBaseRing"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Item Code: {{ itemCodeDriveBaseRing }}
            </q-chip>
          </div>
    </div>
    <q-separator spaced />

    <div class="text-h6 q-mb-md">Pad Plate</div>
    <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap items-center">
            <q-input
            outlined
            v-model="padPlateShaftDia" 
            label="Shaft Dia"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            clearable
            />
            <q-select
            outlined
            v-model="padPlateSuitTo"
            :options="padPlateSuitToOptions"
            label="Suit To"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            />
            <q-input
            outlined
            v-model="padPlateOther"
            :options="padPlateOtherOptions"
            label="Other / Additional Information"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            clearable
            />
            <q-btn
            outline
            round
            color="primary"
            icon="search"
            @click="searchDriveAssemblyData('padPlate')"
            dense
            class="self-center"
            />
            </div>
            <div class="row q-gutter-md q-wrap items-center">
            <q-chip
            v-if="drawingNumberPadPlate"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Drawing Number: {{ drawingNumberPadPlate }}
            </q-chip>

            <q-chip
            v-if="itemCodePadPlate"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Item Code: {{ itemCodePadPlate }}
            </q-chip>
          </div>
    </div>
    <q-separator spaced />

    <div class="text-h6 q-mb-md">Lantern Support</div>
    <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap items-center">
            <q-select
            outlined
            v-model="lanternSupportMaterial"
            :options="lanternSupportMaterialOptions"
            label="Material"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            />
            <q-input
            outlined
            v-model="lanternSupportFlangeNominalSize"
            label="Flange Nominal Size (DBR Size)"
            :rules="[val => !!val || 'Please select a value']"
            type="number"
            dense
            class="col-12 col-md-2"
            clearable
            />
            <q-input
            outlined
            v-model="lanternSupportGearBoxModel"
            label="Gear Box Model"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            clearable
            />
            <q-input
            outlined
            v-model="lanternSupportOther"
            label="Other / Additional Information"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            clearable
            />
            <q-btn
            outline
            round
            color="primary"
            icon="search"
            @click="searchDriveAssemblyData('lanternSupport')"
            dense
            class="self-center"
            />
            </div>
            <div class="row q-gutter-md q-wrap items-center">
            <q-chip
            v-if="drawingNumberLanternSupport"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Drawing Number: {{ drawingNumberLanternSupport }}
            </q-chip>

            <q-chip
            v-if="itemCodeLanternSupport"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Item Code: {{ itemCodeLanternSupport }}
            </q-chip>
          </div>
    </div>
    <q-separator spaced />

    <div class="text-h6 q-mb-md">Lantern Guard</div>
    <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap items-center">
            <q-select
            outlined
            v-model="lanternGuardMaterial"
            :options="lanternGuardMaterialOptions"
            label="Material"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            />
            <q-input
            outlined
            v-model="lanternGuardFlangeNominalSize"
            label="Flange Nominal Size (BDR Size)"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            clearable
            />
            <q-select
            outlined
            v-model="lanternGuardType"
            :options="lanternGuardTypeOptions"
            label="Type"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            />
            <q-input
            outlined
            v-model="lanternGuardOther"
            label="Other / Additional Information"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            clearable
            />
            <q-btn
            outline
            round
            color="primary"
            icon="search"
            @click="searchDriveAssemblyData('lanternGuard')"
            dense
            class="self-center"
            />
            </div>
            <div class="row q-gutter-md q-wrap items-center">
            <q-chip
            v-if="drawingNumberLanternGuard"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Drawing Number: {{ drawingNumberLanternGuard }}
            </q-chip>

            <q-chip
            v-if="itemCodeLanternGuard"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Item Code: {{ itemCodeLanternGuard }}
            </q-chip>
          </div>
    </div>
    <q-separator spaced />
    <div class="text-h6 q-mb-md">Agitator-Gear Coupling</div>
    <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap items-center">
            <q-select
            outlined
            v-model="agitatorGearCouplingMaterial"
            :options="agitatorGearCouplingMaterialOptions"
            label="Material"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            />
            <q-input
            outlined
            v-model="agitatorGearCouplingShaftDia"
            label="Shaft Dia"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            clearable
            />
            <q-input
            outlined
            v-model="agitatorGearCouplingGearBoxModel"
            label="Gear Box Model"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            clearable
            />
            <q-select
            outlined
            v-model="agitatorGearCouplingType"
            :options="agitatorGearCouplingTypeOptions"
            label="Type"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            />
            <q-input
            outlined
            v-model="agitatorGearCouplingOther"
            label="Other / Additional Information"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            clearable
            />
            <q-btn
            outline
            round
            color="primary"
            icon="search"
            @click="searchDriveAssemblyData('agitatorGearCoupling')"
            dense
            class="self-center"
            />
            </div>
            <div class="row q-gutter-md q-wrap items-center">
            <q-chip
            v-if="drawingNumberAgitatorGearCoupling"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Drawing Number: {{ drawingNumberAgitatorGearCoupling }}
            </q-chip>

            <q-chip
            v-if="itemCodeAgitatorGearCoupling"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Item Code: {{ itemCodeAgitatorGearCoupling }}
            </q-chip>
          </div>
    </div>
    <q-separator spaced />
    <div class="text-h6 q-mb-md">Adaptor Assembly</div>
    <!-- Gear Box Model -->
    <div class="q-mb-md">
       <div class="col"><strong>Adaptor</strong></div>
        <div class="row q-gutter-md q-wrap items-center">
            <q-input
            outlined
            v-model="adapterGearBoxModel"
            label="Gear Box Model"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            clearable
            />
            <q-btn
            outline
            round
            color="primary"
            icon="search"
            @click="searchDriveAssemblyData('gearBoxModel')"
            dense
            class="self-center"
            />
            </div>
            <div class="row q-gutter-md q-wrap items-center">
            <q-chip
            v-if="drawingNumberGearBoxModel"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Drawing Number: {{ drawingNumberGearBoxModel }}
            </q-chip>

            <q-chip
            v-if="itemCodeGearBoxModel"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Item Code: {{ itemCodeGearBoxModel }}
            </q-chip>
          </div>
    </div>
    <!-- Bearing Number -->
    <div class="q-mb-md">
        <div class="col"><strong>Bearing</strong></div>
        <div class="row q-gutter-md q-wrap items-center">
            <q-input
            outlined
            v-model="adapterBearingNumber"
            label="Number"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            clearable
            />
            <q-btn
            outline
            round
            color="primary"
            icon="search"
            @click="searchDriveAssemblyData('bearingNumber')"
            dense
            class="self-center"
            />
            </div>
            <div class="row q-gutter-md q-wrap items-center">
            <q-chip
            v-if="drawingNumberBearingNumber"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Drawing Number: {{ drawingNumberBearingNumber }}
            </q-chip>

            <q-chip
            v-if="itemCodeBearingNumber"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Item Code: {{ itemCodeBearingNumber }}
            </q-chip>
          </div>
    </div>
    <!-- Sleeve -->
    <div class="q-mb-md">
        <div class="col"><strong>Sleeve</strong></div>
        <div class="row q-gutter-md q-wrap items-center">
            <q-select
            outlined
            v-model="adapterSleeve"
            :options="adapterSleeveOptions"
            @update:model-value="onUpdateSleeve"
            label="Requirement"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            />
            <q-input
            v-if="adapterSleeve === 'Yes'"
            outlined
            v-model="adapterSleevenumber"
            label="Number"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            clearable
            />
            <q-btn
            outline
            round
            color="primary"
            icon="search"
            @click="searchDriveAssemblyData('sleeve')"
            dense
            class="self-center"
            />
            </div>
            <div class="row q-gutter-md q-wrap items-center">
            <q-chip
            v-if="drawingNumberSleeve"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Drawing Number: {{ drawingNumberSleeve }}
            </q-chip>

            <q-chip
            v-if="itemCodeSleeve"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Item Code: {{ itemCodeSleeve }}
            </q-chip>
          </div>
    </div>
    <!-- Oil Seal -->
    <div class="q-mb-md">
      <div class="col"><strong>Oil Seal</strong></div>
        <div class="row q-gutter-md q-wrap items-center">
            <q-input
            outlined
            v-model="adapterOilSeal"
            label="Size"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            clearable
            />
            <q-btn
            outline
            round
            color="primary"
            icon="search"
            @click="searchDriveAssemblyData('oilSeal')"
            dense
            class="self-center"
            />
            </div>
            <div class="row q-gutter-md q-wrap items-center">
            <q-chip
            v-if="drawingNumberOilSeal"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Drawing Number: {{ drawingNumberOilSeal }}
            </q-chip>

            <q-chip
            v-if="itemCodeOilSeal"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Item Code: {{ itemCodeOilSeal }}
            </q-chip>
          </div>
    </div>
    <!-- Circlip -->
    <div class="q-mb-md">
      <div class="col"><strong>Circlip</strong></div>
        <div class="row q-gutter-md q-wrap items-center">
            <q-input
            outlined
            v-model="adapterCirclip"
            label="Size"
            :rules="[val => !!val || 'Please select a value']"
            dense
            type="number"
            class="col-12 col-md-2"
            clearable
            />
            <q-btn
            outline
            round
            color="primary"
            icon="search"
            @click="searchDriveAssemblyData('circlip')"
            dense
            class="self-center"
            />
            </div>
            <div class="row q-gutter-md q-wrap items-center">
            <q-chip
            v-if="drawingNumberCirclip"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Drawing Number: {{ drawingNumberCirclip }}
            </q-chip>

            <q-chip
            v-if="itemCodeCirclip"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Item Code: {{ itemCodeCirclip }}
            </q-chip>
          </div>
    </div>
    <!-- Lock-Nut -->
    <div class="q-mb-md">
      <div class="col"><strong>Lock Nut</strong></div>
        <div class="row q-gutter-md q-wrap items-center">
            <q-input
            outlined
            v-model="adapterLocknut"
            label="Size"
            :rules="[val => !!val || 'Please select a value']"
            dense
            class="col-12 col-md-2"
            clearable
            />
            <q-btn
            outline
            round
            color="primary"
            icon="search"
            @click="searchDriveAssemblyData('lockNut')"
            dense
            class="self-center"
            />
            </div>
            <div class="row q-gutter-md q-wrap items-center">
            <q-chip
            v-if="drawingNumberLockNut"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Drawing Number: {{ drawingNumberLockNut }}
            </q-chip>

            <q-chip
            v-if="itemCodeLockNut"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Item Code: {{ itemCodeLockNut }}
            </q-chip>
          </div>
    </div>
    <!-- Lock Washer -->
    <div class="q-mb-md"  style="flex-grow: 1; display: flex; flex-direction: column; padding-bottom: 300px;">
      <div class="col"><strong>Lock Washer</strong></div>
        <div class="row q-gutter-md q-wrap items-center">
            <q-input
            outlined
            v-model="adapterLockWasher"
            label="Size"
            :rules="[val => !!val || 'Please select a value']"
            dense
            type="number"
            class="col-12 col-md-2"
            clearable
            />
            <q-btn
            outline
            round
            color="primary"
            icon="search"
            @click="searchDriveAssemblyData('lockWasher')"
            dense
            class="self-center"
            />
            </div>
            <div class="row q-gutter-md q-wrap items-center">
            <q-chip
            v-if="drawingNumberLockWasher"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Drawing Number: {{ drawingNumberLockWasher }}
            </q-chip>

            <q-chip
            v-if="itemCodeLockWasher"
            color="primary"
            outline
            square
            text-color="white"
            label
            class="col-12 col-md-2"
            >
            Item Code: {{ itemCodeLockWasher }}
            </q-chip>
          </div>
    </div>
 </div>
</template>

<script>
import { onMounted, ref } from 'vue'
import { useQuasar } from 'quasar'
import emitter from '../event-bus.js';
export default {
  name: 'DriveAssemblyComponent',
  props: {
    driveAssembly: Object
  },
  emits: ['search-data', 'save-drive-assembly-data'],
  mounted() {
    console.log('Drive Assembly Mounted.')
  },

  setup (props, { emit }) {
    const $q = useQuasar()
    // Drive Base Ring
    const driveBaseRingMaterial = ref(null)
    const driveBaseRingMaterialOptions = ref(['-', 'MS', 'SS304', 'SS316'])
    const driveBaseRingFlangeNominalSize = ref(null)
    const driveBaseRingOther = ref(null)
    const drawingNumberDriveBaseRing = ref(null)
    const itemCodeDriveBaseRing = ref(null)

    // Pad Plate
    const padPlateShaftDia = ref(null)
    const padPlateSuitTo = ref(null)
    const padPlateSuitToOptions = ref(['-','Mechanical Seal', 'Stuffing Box', 'Mechanical Seal + Stuffing Box'])
    const padPlateOther = ref(null)
    const drawingNumberPadPlate = ref(null)
    const itemCodePadPlate = ref(null)

    // Latern Support
    const lanternSupportMaterial = ref(null)
    const lanternSupportMaterialOptions = ref(['-', 'MS', 'SS304', 'SS316'])
    const lanternSupportFlangeNominalSize = ref(driveBaseRingFlangeNominalSize)
    const lanternSupportGearBoxModel = ref(null)
    const lanternSupportOther = ref(null)
    const drawingNumberLanternSupport = ref(null)
    const itemCodeLanternSupport = ref(null)

    // Lantern Guard
    const lanternGuardMaterial = ref(null)
    const lanternGuardMaterialOptions = ref(['-', 'MS', 'SS304', 'SS316'])
    const lanternGuardFlangeNominalSize = ref(driveBaseRingFlangeNominalSize)
    const lanternGuardType = ref(null)
    const lanternGuardTypeOptions = ref(['-', 'Perforated', 'Wire Mesh', 'Plain'])
    const lanternGuardOther = ref(null)
    const drawingNumberLanternGuard = ref(null)
    const itemCodeLanternGuard = ref(null)

    // Agitator-Gear Coupling
    const agitatorGearCouplingMaterial = ref(null)
    const agitatorGearCouplingMaterialOptions = ref(['-', 'MS', 'SS304', 'SS316'])
    const agitatorGearCouplingShaftDia = ref(null)
    const agitatorGearCouplingGearBoxModel = ref(null)
    const agitatorGearCouplingType = ref(null)
    const agitatorGearCouplingTypeOptions = ref(['-', 'Rigid', 'Muff'])
    const agitatorGearCouplingOther = ref(null)
    const drawingNumberAgitatorGearCoupling = ref(null)
    const itemCodeAgitatorGearCoupling = ref(null)

    // Adapter
    const adapterGearBoxModel = ref(null)
    const drawingNumberGearBoxModel = ref(null)
    const itemCodeGearBoxModel = ref(null)

    const adapterBearingNumber = ref(null)  
    const drawingNumberBearingNumber = ref(null)
    const itemCodeBearingNumber = ref(null)
    
    const adapterSleeve = ref(null)
    const adapterSleeveOptions = ref(['-', 'Yes', 'No'])
    const adapterSleevenumber = ref(null)
    const drawingNumberSleeve = ref(null)
    const itemCodeSleeve = ref(null)

    const adapterOilSeal = ref(null)
    const drawingNumberOilSeal = ref(null)
    const itemCodeOilSeal = ref(null)

    const adapterCirclip = ref(null)
    const drawingNumberCirclip = ref(null)
    const itemCodeCirclip = ref(null)

    const adapterLocknut = ref(null)
    const drawingNumberLockNut = ref(null)
    const itemCodeLockNut = ref(null)

    const adapterLockWasher = ref(null)
    const drawingNumberLockWasher = ref(null)
    const itemCodeLockWasher = ref(null)

    onMounted(() => {
        emitter.on('custom-event-gearbox', handleEvent);
        const data = localStorage.getItem('gearbox')
        const gearboxData = JSON.parse(data)
        if(gearboxData !== null){
            lanternSupportGearBoxModel.value = gearboxData.gearboxModel
            agitatorGearCouplingGearBoxModel.value = gearboxData.gearboxModel
            adapterGearBoxModel.value = gearboxData.gearboxModel
        }
        const driveData = localStorage.getItem('driveAssembly')
        if (driveData) {
        const driveAssemblyData = JSON.parse(driveData)

        if (driveAssemblyData) {
          // Drive Base Ring
          driveBaseRingMaterial.value = driveAssemblyData.driveBaseRing?.driveBaseRingMaterial ?? null
          driveBaseRingFlangeNominalSize.value = driveAssemblyData.driveBaseRing?.driveBaseRingFlangeNominalSize ?? null
          driveBaseRingOther.value = driveAssemblyData.driveBaseRing?.driveBaseRingOther ?? null
          drawingNumberDriveBaseRing.value = driveAssemblyData.driveBaseRing?.drawingNumberDriveBaseRing ?? null
          itemCodeDriveBaseRing.value = driveAssemblyData.driveBaseRing?.itemCodeDriveBaseRing ?? null

          // Pad Plat
          padPlateShaftDia.value = driveAssemblyData.padPlat?.padPlateShaftDia ?? null
          padPlateSuitTo.value = driveAssemblyData.padPlat?.padPlateSuitTo ?? null
          padPlateOther.value = driveAssemblyData.padPlat?.padPlateOther ?? null
          drawingNumberPadPlate.value = driveAssemblyData.padPlat?.drawingNumberPadPlate ?? null
          itemCodePadPlate.value = driveAssemblyData.padPlat?.itemCodePadPlate ?? null

          // Lantern Support
          lanternSupportMaterial.value = driveAssemblyData.lanternSupport?.lanternSupportMaterial ?? null
          lanternSupportFlangeNominalSize.value = driveAssemblyData.lanternSupport?.lanternSupportFlangeNominalSize ?? null
          lanternSupportGearBoxModel.value = driveAssemblyData.lanternSupport?.lanternSupportGearBoxModel ?? null
          lanternSupportOther.value = driveAssemblyData.lanternSupport?.lanternSupportOther ?? null
          drawingNumberLanternSupport.value = driveAssemblyData.lanternSupport?.drawingNumberLanternSupport ?? null
          itemCodeLanternSupport.value = driveAssemblyData.lanternSupport?.itemCodeLanternSupport ?? null

          // Lantern Guard
          lanternGuardMaterial.value = driveAssemblyData.lanternGuard?.lanternGuardMaterial ?? null
          lanternGuardFlangeNominalSize.value = driveAssemblyData.lanternGuard?.lanternGuardFlangeNominalSize ?? null
          lanternGuardType.value = driveAssemblyData.lanternGuard?.lanternGuardType ?? null
          lanternGuardOther.value = driveAssemblyData.lanternGuard?.lanternGuardOther ?? null
          drawingNumberLanternGuard.value = driveAssemblyData.lanternGuard?.drawingNumberLanternGuard ?? null
          itemCodeLanternGuard.value = driveAssemblyData.lanternGuard?.itemCodeLanternGuard ?? null

          // Agitator Gear Coupling
          agitatorGearCouplingMaterial.value = driveAssemblyData.agitatorGearCoupling?.agitatorGearCouplingMaterial ?? null
          agitatorGearCouplingShaftDia.value = driveAssemblyData.agitatorGearCoupling?.agitatorGearCouplingShaftDia ?? null
          agitatorGearCouplingGearBoxModel.value = driveAssemblyData.agitatorGearCoupling?.agitatorGearCouplingGearBoxModel ?? null
          agitatorGearCouplingType.value = driveAssemblyData.agitatorGearCoupling?.agitatorGearCouplingType ?? null
          agitatorGearCouplingOther.value = driveAssemblyData.agitatorGearCoupling?.agitatorGearCouplingOther ?? null
          drawingNumberAgitatorGearCoupling.value = driveAssemblyData.agitatorGearCoupling?.drawingNumberAgitatorGearCoupling ?? null
          itemCodeAgitatorGearCoupling.value = driveAssemblyData.agitatorGearCoupling?.itemCodeAgitatorGearCoupling ?? null

          // Adaptor Gear Box Model
          adapterGearBoxModel.value = driveAssemblyData.adaptorGearBoxModel?.adapterGearBoxModel ?? null
          drawingNumberGearBoxModel.value = driveAssemblyData.adaptorGearBoxModel?.drawingNumberGearBoxModel ?? null
          itemCodeGearBoxModel.value = driveAssemblyData.adaptorGearBoxModel?.itemCodeGearBoxModel ?? null

          // Bearing
          adapterBearingNumber.value = driveAssemblyData.bearing?.adapterBearingNumber ?? null
          drawingNumberBearingNumber.value = driveAssemblyData.bearing?.drawingNumberBearingNumber ?? null
          itemCodeBearingNumber.value = driveAssemblyData.bearing?.itemCodeBearingNumber ?? null

          // Sleeve
          adapterSleeve.value = driveAssemblyData.sleeve?.adapterSleeve ?? null
          adapterSleevenumber.value = driveAssemblyData.sleeve?.adapterSleevenumber ?? null
          drawingNumberSleeve.value = driveAssemblyData.sleeve?.drawingNumberSleeve ?? null
          itemCodeSleeve.value = driveAssemblyData.sleeve?.itemCodeSleeve ?? null

          // Oil Seal
          adapterOilSeal.value = driveAssemblyData.oilSeal?.adapterOilSeal ?? null
          drawingNumberOilSeal.value = driveAssemblyData.oilSeal?.drawingNumberOilSeal ?? null
          itemCodeOilSeal.value = driveAssemblyData.oilSeal?.itemCodeOilSeal ?? null

          // Circlip
          adapterCirclip.value = driveAssemblyData.circlip?.adapterCirclip ?? null
          drawingNumberCirclip.value = driveAssemblyData.circlip?.drawingNumberCirclip ?? null
          itemCodeCirclip.value = driveAssemblyData.circlip?.itemCodeCirclip ?? null

          // Lock Nut
          adapterLocknut.value = driveAssemblyData.lockNut?.adapterLocknut ?? null
          drawingNumberLockNut.value = driveAssemblyData.lockNut?.drawingNumberLockNut ?? null
          itemCodeLockNut.value = driveAssemblyData.lockNut?.itemCodeLockNut ?? null

          // Lock Washer
          adapterLockWasher.value = driveAssemblyData.lockWasher?.adapterLockWasher ?? null
          drawingNumberLockWasher.value = driveAssemblyData.lockWasher?.drawingNumberLockWasher ?? null
          itemCodeLockWasher.value = driveAssemblyData.lockWasher?.itemCodeLockWasher ?? null
        }
      }
    })

    const handleEvent = (gearBox) => {
        localStorage.setItem('gearBoxTemp', JSON.stringify(gearBox))
    }

    const onUpdateSleeve = (val) => {
      if (val === 'No' || val === '-'){
        adapterSleevenumber.value = null
      }
    }

    const saveToJsonFile = () => {
      const driveAssembly = {
        component: 'DriveAssembly',
        driveBaseRing: {
          driveBaseRingMaterial: driveBaseRingMaterial.value? driveBaseRingMaterial.value: null,
          driveBaseRingFlangeNominalSize: driveBaseRingFlangeNominalSize.value? driveBaseRingFlangeNominalSize.value: null,
          driveBaseRingOther: driveBaseRingOther.value? driveBaseRingOther.value: null,
          drawingNumberDriveBaseRing: drawingNumberDriveBaseRing.value? drawingNumberDriveBaseRing.value: null,
          itemCodeDriveBaseRing: itemCodeDriveBaseRing.value? itemCodeDriveBaseRing.value: null,
        },
        padPlat: {
          padPlateShaftDia: padPlateShaftDia.value? padPlateShaftDia.value: null,
          padPlateSuitTo: padPlateSuitTo.value? padPlateSuitTo.value: null,
          padPlateOther: padPlateOther.value? padPlateOther.value: null,
          drawingNumberPadPlate: drawingNumberPadPlate.value? drawingNumberPadPlate.value: null,
          itemCodePadPlate: itemCodePadPlate.value? itemCodePadPlate.value: null,
        },
        lanternSupport: {
          lanternSupportMaterial: lanternSupportMaterial.value ? lanternSupportMaterial.value : null,
          lanternSupportFlangeNominalSize: lanternSupportFlangeNominalSize.value ? lanternSupportFlangeNominalSize.value : null,
          lanternSupportGearBoxModel: lanternSupportGearBoxModel.value ? lanternSupportGearBoxModel.value : null,
          lanternSupportOther: lanternSupportOther.value ? lanternSupportOther.value : null,
          drawingNumberLanternSupport: drawingNumberLanternSupport.value ? drawingNumberLanternSupport.value : null,
          itemCodeLanternSupport: itemCodeLanternSupport.value ? itemCodeLanternSupport.value : null,
        },

        lanternGuard: {
          lanternGuardMaterial: lanternGuardMaterial.value ? lanternGuardMaterial.value : null,
          lanternGuardFlangeNominalSize: lanternGuardFlangeNominalSize.value ? lanternGuardFlangeNominalSize.value : null,
          lanternGuardType: lanternGuardType.value ? lanternGuardType.value : null,
          lanternGuardOther: lanternGuardOther.value ? lanternGuardOther.value : null,
          drawingNumberLanternGuard: drawingNumberLanternGuard.value ? drawingNumberLanternGuard.value : null,
          itemCodeLanternGuard: itemCodeLanternGuard.value ? itemCodeLanternGuard.value : null,
        },

        agitatorGearCoupling: {
          agitatorGearCouplingMaterial: agitatorGearCouplingMaterial.value ? agitatorGearCouplingMaterial.value : null,
          agitatorGearCouplingShaftDia: agitatorGearCouplingShaftDia.value ? agitatorGearCouplingShaftDia.value : null,
          agitatorGearCouplingGearBoxModel: agitatorGearCouplingGearBoxModel.value ? agitatorGearCouplingGearBoxModel.value : null,
          agitatorGearCouplingType: agitatorGearCouplingType.value ? agitatorGearCouplingType.value : null,
          agitatorGearCouplingOther: agitatorGearCouplingOther.value ? agitatorGearCouplingOther.value : null,
          drawingNumberAgitatorGearCoupling: drawingNumberAgitatorGearCoupling.value ? drawingNumberAgitatorGearCoupling.value : null,
          itemCodeAgitatorGearCoupling: itemCodeAgitatorGearCoupling.value ? itemCodeAgitatorGearCoupling.value : null,
        },

        adaptorGearBoxModel: {
          adapterGearBoxModel: adapterGearBoxModel.value ? adapterGearBoxModel.value : null,
          drawingNumberGearBoxModel: drawingNumberGearBoxModel.value ? drawingNumberGearBoxModel.value : null,
          itemCodeGearBoxModel: itemCodeGearBoxModel.value ? itemCodeGearBoxModel.value : null,
        },

        bearing: {
          adapterBearingNumber: adapterBearingNumber.value ? adapterBearingNumber.value : null,
          drawingNumberBearingNumber: drawingNumberBearingNumber.value ? drawingNumberBearingNumber.value : null,
          itemCodeBearingNumber: itemCodeBearingNumber.value ? itemCodeBearingNumber.value : null,
        },

        sleeve: {
          adapterSleeve: adapterSleeve.value ? adapterSleeve.value : null,
          adapterSleevenumber: adapterSleevenumber.value ? adapterSleevenumber.value : null,
          drawingNumberSleeve: drawingNumberSleeve.value ? drawingNumberSleeve.value : null,
          itemCodeSleeve: itemCodeSleeve.value ? itemCodeSleeve.value : null,
        },

        oilSeal: {
          adapterOilSeal: adapterOilSeal.value ? adapterOilSeal.value : null,
          drawingNumberOilSeal: drawingNumberOilSeal.value ? drawingNumberOilSeal.value : null,
          itemCodeOilSeal: itemCodeOilSeal.value ? itemCodeOilSeal.value : null,
        },

        circlip: {
          adapterCirclip: adapterCirclip.value ? adapterCirclip.value : null,
          drawingNumberCirclip: drawingNumberCirclip.value ? drawingNumberCirclip.value : null,
          itemCodeCirclip: itemCodeCirclip.value ? itemCodeCirclip.value : null,
        },

        lockNut: {
          adapterLocknut: adapterLocknut.value ? adapterLocknut.value : null,
          drawingNumberLockNut: drawingNumberLockNut.value ? drawingNumberLockNut.value : null,
          itemCodeLockNut: itemCodeLockNut.value ? itemCodeLockNut.value : null,
        },

        lockWasher: {
          adapterLockWasher: adapterLockWasher.value ? adapterLockWasher.value : null,
          drawingNumberLockWasher: drawingNumberLockWasher.value ? drawingNumberLockWasher.value : null,
          itemCodeLockWasher: itemCodeLockWasher.value ? itemCodeLockWasher.value : null,
        }
      }
      localStorage.setItem('driveAssembly', JSON.stringify(driveAssembly))
      emit('save-drive-assembly-data', driveAssembly)
    }

    const searchDriveAssemblyData = (item) => {
      let dataToSearch = null
      if(item === 'driveBaseRing'){
        dataToSearch = {
          component: 'DriveBaseRing',
          driveBaseRingMaterial: driveBaseRingMaterial.value? driveBaseRingMaterial.value: null,
          driveBaseRingFlangeNominalSize: driveBaseRingFlangeNominalSize.value? driveBaseRingFlangeNominalSize.value: null,
          driveBaseRingOther: driveBaseRingOther.value? driveBaseRingOther.value: null,
        }
      }
      else if(item === 'padPlate'){
        dataToSearch = {
          component: 'PadPlate',
          padPlateShaftDia: padPlateShaftDia.value? padPlateShaftDia.value: null,
          padPlateSuitTo: padPlateSuitTo.value? padPlateSuitTo.value: null,
          padPlateOther: padPlateOther.value? padPlateOther.value: null
        }
      }
      else if(item === 'lanternSupport'){
        dataToSearch = {
          component: 'LanternSupport',
          lanternSupportMaterial: lanternSupportMaterial.value? lanternSupportMaterial.value: null,
          lanternSupportFlangeNominalSize: lanternSupportFlangeNominalSize.value? lanternSupportFlangeNominalSize.value: null,
          lanternSupportGearBoxModel: lanternSupportGearBoxModel.value? lanternSupportGearBoxModel.value: null,
          lanternSupportOther: lanternSupportOther.value? lanternSupportOther.value: null
        }
      }
      else if(item === 'lanternGuard'){
        dataToSearch = {
          component: 'LanternGuard',
          lanternGuardMaterial: lanternGuardMaterial.value? lanternGuardMaterial.value: null,
          lanternGuardFlangeNominalSize: lanternGuardFlangeNominalSize.value? lanternGuardFlangeNominalSize.value: null,
          lanternGuardType: lanternGuardType.value? lanternGuardType.value: null,
          lanternGuardOther: lanternGuardOther.value? lanternGuardOther.value: null
        }
      }
      else if(item === 'agitatorGearCoupling'){
        dataToSearch = {
          component: 'AgitatorGearCoupling',
          agitatorGearCouplingMaterial: agitatorGearCouplingMaterial.value? agitatorGearCouplingMaterial.value: null,
          agitatorGearCouplingShaftDia: agitatorGearCouplingShaftDia.value? agitatorGearCouplingShaftDia.value: null,
          agitatorGearCouplingType: agitatorGearCouplingType.value? agitatorGearCouplingType.value: null,
          agitatorGearCouplingOther: agitatorGearCouplingOther.value? agitatorGearCouplingOther.value: null,
        }
      }
      else if(item === 'gearBoxModel'){
        dataToSearch = {
          component: 'GearBoxModel',
          adapterGearBoxModel: adapterGearBoxModel.value? adapterGearBoxModel.value: null
        }
      }
      else if(item === 'bearingNumber'){
        dataToSearch = {
          component: 'BearingNumber',
          adapterBearingNumber: adapterBearingNumber.value? adapterBearingNumber.value: null
        }
      }
      else if(item === 'sleeve'){
        dataToSearch = {
          component: 'Sleeve',
          adapterSleeve: adapterSleeve.value? adapterSleeve.value: null,
          adapterSleevenumber: adapterSleevenumber.value? adapterSleevenumber.value: null
        }
      }
      else if(item === 'oilSeal'){
        dataToSearch = {
          component: 'OilSeal',
          adapterOilSeal: adapterOilSeal.value? adapterOilSeal.value: null
        }
      }
      else if(item === 'circlip'){
        dataToSearch = {
          component: 'Circlip',
          adapterCirclip: adapterCirclip.value? adapterCirclip.value: null
        }
      }
      else if(item === 'lockNut'){
        dataToSearch = {
          component: 'LockNut',
          adapterLocknut: adapterLocknut.value? adapterLocknut.value: null
        }
      }
      else if(item === 'lockWasher'){
        dataToSearch = {
          component: 'LockWasher',
          adapterLockWasher: adapterLockWasher.value? adapterLockWasher.value: null
        }
      }
      const isNull = hasNull(dataToSearch)
      if(isNull){
        $q.dialog({
                title: '<span class="text-red">Alert</span>',
                message: `Please enter the value of empty field.`,
                color: 'red-5',
                html: true
            });
      }else {
        emit('search-data', dataToSearch)
      }
    }

    function hasNull(obj) {
        for (const key in obj) {
            if (obj[key] === null) {
            return true;
            }
            // If nested object, check recursively
            if (typeof obj[key] === 'object' && obj[key] !== null) {
            if (hasNull(obj[key])) {
                return true;
            }
            }
        }
        return false;
    }

    const showSaveToJsonButton = ref(false);

    const checkIfAllSearchResultsComplete = () => {
      const allFilled =
        drawingNumberDriveBaseRing.value && itemCodeDriveBaseRing.value &&
        drawingNumberPadPlate.value && itemCodePadPlate.value &&
        drawingNumberLanternSupport.value && itemCodeLanternSupport.value &&
        drawingNumberLanternGuard.value && itemCodeLanternGuard.value &&
        drawingNumberAgitatorGearCoupling.value && itemCodeAgitatorGearCoupling.value &&
        drawingNumberGearBoxModel.value && itemCodeGearBoxModel.value &&
        drawingNumberBearingNumber.value && itemCodeBearingNumber.value &&
        drawingNumberSleeve.value && itemCodeSleeve.value &&
        drawingNumberOilSeal.value && itemCodeOilSeal.value &&
        drawingNumberCirclip.value && itemCodeCirclip.value &&
        drawingNumberLockNut.value && itemCodeLockNut.value &&
        drawingNumberLockWasher.value && itemCodeLockWasher.value;

      showSaveToJsonButton.value = Boolean(allFilled);
    }

    const assignData = (obj) => {
      if(obj?.model){
        if (obj?.model.includes('AE') || obj?.model.includes('CE')){
          agitatorGearCouplingType.value = agitatorGearCouplingTypeOptions.value[1]
        }
        else{
          agitatorGearCouplingType.value = agitatorGearCouplingTypeOptions.value[2]
        }
        padPlateShaftDia.value = obj.shaft_dia
        agitatorGearCouplingShaftDia.value = obj.shaft_dia
      }else{
        if(obj !== null && obj.component === 'DriveBaseRing') {
          drawingNumberDriveBaseRing.value = obj?.model_info.drawingNumber
          itemCodeDriveBaseRing.value = obj?.model_info.itemCode
        }else if(obj !== null && obj.component === 'PadPlate') {
          drawingNumberPadPlate.value = obj?.model_info.drawingNumber
          itemCodePadPlate.value = obj?.model_info.itemCode
        }else if(obj !== null && obj.component === 'LanternSupport') {
          drawingNumberLanternSupport.value = obj?.model_info.drawingNumber
          itemCodeLanternSupport.value = obj?.model_info.itemCode
        }else if(obj !== null && obj.component === 'LanternGuard') {
          drawingNumberLanternGuard.value = obj?.model_info.drawingNumber
          itemCodeLanternGuard.value = obj?.model_info.itemCode
        }else if(obj !== null && obj.component === 'AgitatorGearCoupling') {
          drawingNumberAgitatorGearCoupling.value = obj?.model_info.drawingNumber
          itemCodeAgitatorGearCoupling.value = obj?.model_info.itemCode
        }else if(obj !== null && obj.component === 'GearBoxModel') {
          drawingNumberGearBoxModel.value = obj?.model_info.drawingNumber
          itemCodeGearBoxModel.value = obj?.model_info.itemCode
        }else if(obj !== null && obj.component === 'BearingNumber') {
          drawingNumberBearingNumber.value = obj?.model_info.drawingNumber
          itemCodeBearingNumber.value = obj?.model_info.itemCode
        }
        else if(obj !== null && obj.component === 'Sleeve') {
          drawingNumberSleeve.value = obj?.model_info.drawingNumber
          itemCodeSleeve.value = obj?.model_info.itemCode
        }
        else if(obj !== null && obj.component === 'OilSeal') {
          drawingNumberOilSeal.value = obj?.model_info.drawingNumber
          itemCodeOilSeal.value = obj?.model_info.itemCode
        }
        else if(obj !== null && obj.component === 'Circlip') {
          drawingNumberCirclip.value = obj?.model_info.drawingNumber
          itemCodeCirclip.value = obj?.model_info.itemCode
        }
        else if(obj !== null && obj.component === 'LockNut') {
          drawingNumberLockNut.value = obj?.model_info.drawingNumber
          itemCodeLockNut.value = obj?.model_info.itemCode
        }
        else if(obj !== null && obj.component === 'LockWasher') {
          drawingNumberLockWasher.value = obj?.model_info.drawingNumber
          itemCodeLockWasher.value = obj?.model_info.itemCode
        }
      }
      checkIfAllSearchResultsComplete();
    }


    return {
        // Drive Base Ring
        driveBaseRingMaterial,
        driveBaseRingMaterialOptions,
        driveBaseRingFlangeNominalSize,
        driveBaseRingOther,
        drawingNumberDriveBaseRing,
        itemCodeDriveBaseRing,

        // Pad Plate
        padPlateShaftDia,
        padPlateSuitTo,
        padPlateSuitToOptions,
        padPlateOther,
        drawingNumberPadPlate,
        itemCodePadPlate,

        // Lantern Support
        lanternSupportMaterial,
        lanternSupportMaterialOptions,
        lanternSupportFlangeNominalSize,
        lanternSupportGearBoxModel,
        lanternSupportOther,
        drawingNumberLanternSupport,
        itemCodeLanternSupport,

        // Lantern Guard
        lanternGuardMaterial,
        lanternGuardMaterialOptions,
        lanternGuardFlangeNominalSize,
        lanternGuardType,
        lanternGuardTypeOptions,
        lanternGuardOther,
        drawingNumberLanternGuard,
        itemCodeLanternGuard,

        // Agitator-Gear Coupling
        agitatorGearCouplingMaterial,
        agitatorGearCouplingMaterialOptions,
        agitatorGearCouplingShaftDia,
        agitatorGearCouplingGearBoxModel,
        agitatorGearCouplingType,
        agitatorGearCouplingTypeOptions,
        agitatorGearCouplingOther,
        drawingNumberAgitatorGearCoupling,
        itemCodeAgitatorGearCoupling,

        // Adapter
        adapterGearBoxModel,
        drawingNumberGearBoxModel,
        itemCodeGearBoxModel,

        adapterBearingNumber,
        drawingNumberBearingNumber,
        itemCodeBearingNumber,

        adapterSleeve,
        adapterSleeveOptions,
        adapterSleevenumber,
        drawingNumberSleeve,
        itemCodeSleeve,

        adapterOilSeal,
        drawingNumberOilSeal,
        itemCodeOilSeal,

        adapterCirclip,
        drawingNumberCirclip,
        itemCodeCirclip,

        adapterLocknut,
        drawingNumberLockNut,
        itemCodeLockNut,

        adapterLockWasher,
        drawingNumberLockWasher,
        itemCodeLockWasher,

        // Methods
        showSaveToJsonButton,
        saveToJsonFile,
        searchDriveAssemblyData,
        assignData,
        onUpdateSleeve

    }
  },
  watch: {
    driveAssembly: {
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