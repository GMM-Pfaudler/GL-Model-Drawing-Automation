<template>
    <q-page class="q-pa-md">
     <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap">
            <q-select
            outlined
            v-model="driveHoodMaterial"
            :options="driveHoodMaterialOptions"
            label="Material"
            dense
            class="col-12 col-md-2"
            />
            <q-select
            outlined
            v-model="driveHoodType"
            :options="driveHoodTypeOptions"
            label="Type"
            dense
            class="col-12 col-md-2"
            />

            <q-select
            outlined
            v-model="driveHoodLength"
            :options="driveHoodLengthOptions"
            label="Length"
            dense
            class="col-12 col-md-2"
            />

            <q-space/>
            <q-btn outline rounded color="primary" icon="search" label="Search" @click="searchDriveHoodData"/>
        </div>
    </div>
    <!-- Second Row -->
    <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap">

            <q-select
            outlined
            v-model="driveHoodShape"
            :options="driveHoodShapeOptions"
            label="Shape"
            dense
            class="col-12 col-md-2"
            />

            <q-input
            outlined
            v-model="driveHoodGearBoxModel"
            label="Gear Box Model"
            dense
            class="col-12 col-md-2"
            />

            <q-input
            outlined
            v-model="driveHoodGearBoxFrame"
            label="Frame"
            dense
            class="col-12 col-md-2"
            />
        </div>
    </div>
    <!-- Three Row -->
    <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap">

            <q-input
            outlined
            v-model="hoodOutsideDia"
            label="Hood Outside Dia"
            type="text"
            dense
            class="col-12 col-md-2"
            />

            <q-input
            outlined
            v-model="hoodHeight"
            label="Hood Height"
            type="text"
            dense
            class="col-12 col-md-2"
            />

            <q-input
            outlined
            v-model="mountingPCD"
            label="Mounting PCD"
            type="text"
            dense
            class="col-12 col-md-2"
            />
        </div>
    </div>
  </q-page>
</template>
<script>
import { onMounted, ref } from 'vue'
import emitter from '../event-bus.js'

export default {
  name: 'DriveHood',
  props: {
    driveHood: Object
  },
  emits: ['search-data'],
  setup (props, { emit }) {
    const driveHoodMaterial = ref(null)
    const driveHoodMaterialOptions = ref(['-', 'MS', 'SS304', 'SS316'])
    const driveHoodType = ref(null)
    const driveHoodTypeOptions = ref(['-', 'Regular', 'Perforated', 'Slotted', 'Louvers'])
    const driveHoodLength = ref(null)
    const driveHoodLengthOptions = ref(['-', 'Full Length', 'Half Length'])
    const driveHoodShape = ref(null)
    const driveHoodShapeOptions = ref(['-', 'Square', 'Round'])
    const driveHoodGearBoxFrame = ref(null)
    const driveHoodGearBoxModel = ref(null)
    const hoodOutsideDia = ref(null)
    const hoodHeight = ref(null)
    const mountingPCD = ref(null)

    onMounted(() => {
      console.log('Drive Hood mounted')

      // ✅ Load drive hood fields (excluding gear box)
      const stored = localStorage.getItem('driveHood')
      const data = JSON.parse(stored)
      if (data !== null) {
        driveHoodMaterial.value = data.driveHoodMaterial ?? null
        driveHoodType.value = data.driveHoodType ?? null
        driveHoodLength.value = data.driveHoodLength ?? null
        driveHoodShape.value = data.driveHoodShape ?? null
        hoodOutsideDia.value = data.hoodOutsideDia ?? null
        hoodHeight.value = data.hoodHeight ?? null
        mountingPCD.value = data.mountingPCD ?? null
        // ❌ Don't restore GearBox from driveHood, it will come from gearBoxTemp
      }

      // ✅ Load GearBox from gearBoxTemp
      const gearData = localStorage.getItem('gearBoxTemp')
      const parsedGear = JSON.parse(gearData)
      if (parsedGear !== null) {
        driveHoodGearBoxModel.value = parsedGear.gearboxModel ?? null
        driveHoodGearBoxFrame.value = parsedGear.gearboxFrame ?? null
      }

      // ✅ Listen to GearBox update event
      emitter.on('custom-event-gearbox', handleEvent)
    })

    const handleEvent = (gearBox) => {
      localStorage.setItem('gearBoxTemp', JSON.stringify(gearBox))
      driveHoodGearBoxModel.value = gearBox.gearboxModel ?? null
      driveHoodGearBoxFrame.value = gearBox.gearboxFrame ?? null
    }

    const searchDriveHoodData = () => {
      const data = prepareDriveHoodData()
      emit('search-data', data)
    }

    const prepareDriveHoodData = () => {
      const driveHood = {
        component: 'DriveHood',
        driveHoodMaterial: driveHoodMaterial.value ?? null,
        driveHoodType: driveHoodType.value ?? null,
        driveHoodLength: driveHoodLength.value ?? null,
        driveHoodShape: driveHoodShape.value ?? null,
        hoodOutsideDia: hoodOutsideDia.value ?? null,
        hoodHeight: hoodHeight.value ?? null,
        mountingPCD: mountingPCD.value ?? null,
        // ✅ Include GearBox values when emitting
        driveHoodGearBoxFrame: driveHoodGearBoxFrame.value ?? null,
        driveHoodGearBoxModel: driveHoodGearBoxModel.value ?? null
      }

      // ✅ Save only non-GearBox fields to localStorage
      const storageCopy = { ...driveHood }
      delete storageCopy.driveHoodGearBoxFrame
      delete storageCopy.driveHoodGearBoxModel

      localStorage.setItem('driveHood', JSON.stringify(storageCopy))
      return driveHood
    }

    return {
      driveHoodMaterial,
      driveHoodMaterialOptions,
      driveHoodType,
      driveHoodTypeOptions,
      driveHoodLength,
      driveHoodLengthOptions,
      driveHoodShape,
      driveHoodShapeOptions,
      driveHoodGearBoxFrame,
      driveHoodGearBoxModel,
      hoodOutsideDia,
      hoodHeight,
      mountingPCD,

      // Methods
      searchDriveHoodData
    }
  }
}
</script>
