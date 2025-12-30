<template>
    <div>
        <div class="q-gutter-md row items-center" style="padding-top: 20px; padding-right: 20px;">
            <q-select
            outlined
            v-model="shaftDia"
            :options="shaftDiameters"
            label="Shaft Dia @ Sealing"
            dense
            style="width: 300px; padding-right: 50px;"
            />
            <q-select
            outlined
            v-model="sealingType"
            :options="sealingTypes"
            dense
            label="Sealing Type"
            style="width: 300px;"
            />
            <q-space/>
            <q-btn outline rounded icon="search" color="primary" label="Search" @click="searchAgitatorData"/>
        </div>

        <div class="q-gutter-md row" style="padding-top: 50px; padding-right: 20px;">
            <q-select
            outlined
            v-model="volumeMarking"
            :options="volumeMarkingOptions"
            label="Volume Marking Require"
            dense
            style="width: 300px; padding-right: 50px;"
            />

            <q-select
            outlined
            v-model="hastalloySleeve"
            :options="hastalloySleeveOptions"
            @update:model-value="onUpdateHastalloySleeve"
            dense
            label="With Hastalloy Sleeve"
            style="width: 300px;"
            />
            
        </div>

        <div class="q-gutter-md row" style="padding-top: 50px; padding-right: 20px;">
            <q-input
            outlined
            v-model="agitatorHeight"
            dense
            type="text"
            label="Length / Height"
            style="width: 300px; padding-right: 50px;"
            clearable
            />

            <q-input
            outlined
            v-model="shaftDiaWithSleeve"
            dense
            type="text"
            label="Shaft Dia with Sleeve"
            style="width: 300px;"
            clearable
            :disable="hastalloySleeve === 'No'"
            />
        </div>

        <div class="q-gutter-md row" style="padding-top: 50px; padding-right: 20px;">
            <div>
                <q-select
                outlined
                v-model="flight"
                :options="flightOptions"
                dense
                label="Flight"
                style="width: 300px; padding-right: 50px;"
                />
            </div>
            
            <div v-if="flight !== null" class="row">
                <q-select
                outlined
                v-model="singleFlightType"
                :options="singleFlightTypeOptions"
                dense
                label="Flight Type"
                style="width: 350px; padding-right: 50px;"
                
                />

                <q-input
                outlined
                v-model="singleFlightDia"
                dense
                type="text"
                label="Sweep Diameter"
                style="width: 300px;"
                clearable
                />

            </div>

            <div v-if="flight === 'Double' || flight === 'Triple' || flight === 'Special'" class="row" style="padding-top: 50px; padding-left: 320px;">
                <q-select
                outlined
                v-model="doubleFlightType"
                :options="doubleFlightTypeOptions"
                dense
                label="Flight Type"
                style="width: 350px; padding-right: 50px;"
                />

                <q-input
                outlined
                v-model="doubleFlightDia"
                dense
                type="text"
                label="Sweep Diameter"
                style="width: 350px; padding-right: 50px;"
                clearable
                />

                <q-input
                outlined
                v-model="doubleFlightDistance"
                dense
                type="text"
                label="Distance"
                style="width: 300px;"
                clearable
                />
            </div>

            <div v-if="flight === 'Triple' || flight === 'Special'" class="row" style="padding-top: 50px; padding-left: 320px;">
                <q-select
                outlined
                v-model="tripleFlightType"
                :options="tripleFlightTypeOptions"
                dense
                label="Flight Type"
                style="width: 350px; padding-right: 50px;"
                />

                <q-input
                outlined
                v-model="tripleFlightDia"
                dense
                type="text"
                label="Sweep Diameter"
                style="width: 350px; padding-right: 50px;"
                clearable
                />

                <q-input
                outlined
                v-model="tripleFlightDistance"
                dense
                type="text"
                label="Distance"
                style="width: 300px;"
                clearable
                />
            </div>

            <div v-if="flight === 'Special'" class="row" style="padding-top: 50px; padding-left: 320px;">
                <q-input
                outlined
                v-model="specialFlightType"
                dense
                label="Flight Type"
                style="width: 350px; padding-right: 50px;"
                clearable
                />

                <q-input
                outlined
                v-model="specialFlightDia"
                dense
                type="text"
                label="Sweep Diameter"
                style="width: 350px; padding-right: 50px;"
                clearable
                />

                <q-input
                outlined
                v-model="specialFlightDistance"
                dense
                type="text"
                label="Distance"
                style="width: 300px;"
                clearable
                />
            </div>
        </div>
    </div>
</template>

<script>
import { onMounted, ref } from 'vue'
import { useQuasar } from 'quasar'
export default {
  name: 'AgitatorComponent',
  props: {
    agitator: Object,
  },
  emits: ['search-data'],
//   mounted() {
//     // this.shaftDia = parseInt(this.agitator.agitator_shaft.split(" ")[0])
//     if (this.agitator !== null) {
//         this.populateInitialData(this.agitator)
//     }
//     if (this.agitator?.data) {
//         this.fillData(this.agitator?.data)
//     }
//   },
  setup (props, { emit }) {
    const $q = useQuasar()
    const shaftDiameters = ref([])
    const shaftDia = ref(null)
    const sealingTypes = ref(['Meachanical Seal', 'Stuffing Box'])
    const sealingType = ref(null)
    const agitatorHeight = ref(null)
    const volumeMarkingOptions = ref(['-', 'Yes', 'No'])
    const volumeMarking = ref(null)
    const hastalloySleeveOptions = ref(['-', 'Yes', 'No'])
    const hastalloySleeve = ref(null)
    const shaftDiaWithSleeve = ref(null)
    const flight = ref(null)
    const flightOptions = ref(['-', 'Single', 'Double', 'Triple', 'Special'])
    const singleFlightType = ref(null)
    const singleFlightTypeOptions = ref(['-', 'Anchor', 'RCI', 'PBT', 'CBRT', 'CBT', 'Ruston', 'FBT', 'TBF'])
    const singleFlightDia = ref(null)
    const doubleFlightType = ref(null)
    const doubleFlightTypeOptions = ref(['-', 'RCI', 'PBT', 'FBT',  'TBF', 'MXT'])
    const doubleFlightDia = ref(null)
    const doubleFlightDistance = ref(null)
    const tripleFlightType = ref(null)
    const tripleFlightTypeOptions = ref(['-', 'RCI', 'PBT', 'TBF', 'MXT'])
    const tripleFlightDia = ref(null)
    const tripleFlightDistance = ref(null)
    const specialFlightType = ref(null)
    const specialFlightTypeOptions = ref([])
    const specialFlightDia = ref(null)
    const specialFlightDistance = ref(null)

    onMounted(() => {
        console.log("Agitator")
    });

    const onUpdateHastalloySleeve = () => {
        const dia = shaftDia.value
        if (hastalloySleeve.value === 'Yes') {
            if (dia === 125){
                shaftDiaWithSleeve.value = 133
            }else if (dia === 100){
                shaftDiaWithSleeve.value = 108
            }else if (dia === 80) {
                shaftDiaWithSleeve.value = 90
            }else if (dia === 60) {
                shaftDiaWithSleeve.value = 68
            }else if (dia === 50) {
                shaftDiaWithSleeve.value = 58
            }else if (dia === 40){
                shaftDiaWithSleeve.value = 46
            }
        }
        else {
            shaftDiaWithSleeve.value = null
        }
    }

    const searchAgitatorData = () => {
        const agitatorData = prepareAgitatorData();

        // Step 1: Check core/base agitator fields first
        const baseFields = [
            { key: 'shaftDia', value: shaftDia.value ? shaftDia.value.toString() : null, label: 'Shaft Diameter' },
            { key: 'sealingType', value: sealingType.value ? sealingType.value : null, label: 'Sealing Type' },
            { key: 'volumeMarking', value: volumeMarking.value ? volumeMarking.value : null, label: 'Volume Marking' },
            { key: 'hastalloySleeve', value: hastalloySleeve.value ? hastalloySleeve.value : null, label: 'Hastelloy Sleeve' },
            { key: 'agitatorHeight', value: agitatorHeight.value ? agitatorHeight.value.toString() : null, label: 'Agitator Height' },
            { key: 'shaftDiaWithSleeve', value: shaftDiaWithSleeve.value ? shaftDiaWithSleeve.value.toString() : '-', label: 'Shaft Dia with Sleeve' }
        ];

        const missingBaseFields = baseFields
            .filter(field => field.value === null)
            .map(field => field.label);

        if (missingBaseFields.length > 0) {
            $q.dialog({
                title: '<span class="text-red">Alert</span>',
                message: `Please enter the value of: <b>${missingBaseFields.join(', ')}</b><br><br>`,
                color: 'red-5',
                html: true
            });
            return; // 🚫 stop here if base fields are missing
        }

        // Step 2: Validate flight-specific fields based on rules
        const flightFieldMap = {
            Single: [
                { key: 'singleFlightDia', value: singleFlightDia.value, label: 'Single Flight Diameter' },
                { key: 'singleFlightType', value: singleFlightType.value, label: 'Single Flight Type' }
            ],
            Double: [
                { key: 'doubleFlightDia', value: doubleFlightDia.value, label: 'Double Flight Diameter' },
                { key: 'doubleFlightType', value: doubleFlightType.value, label: 'Double Flight Type' },
                { key: 'doubleFlightDistance', value: doubleFlightDistance.value, label: 'Double Flight Distance' }
            ],
            Triple: [
                { key: 'tripleFlightDia', value: tripleFlightDia.value, label: 'Triple Flight Diameter' },
                { key: 'tripleFlightType', value: tripleFlightType.value, label: 'Triple Flight Type' },
                { key: 'tripleFlightDistance', value: tripleFlightDistance.value, label: 'Triple Flight Distance' }
            ],
            Special: [
                { key: 'specialFlightDia', value: specialFlightDia.value, label: 'Special Flight Diameter' },
                { key: 'specialFlightType', value: specialFlightType.value, label: 'Special Flight Type' },
                { key: 'specialFlightDistance', value: specialFlightDistance.value, label: 'Special Flight Distance' }
            ]
        };

        const flight = agitatorData.flight;

        // Cascading validation logic
        const flightCheckOrder = {
            Single: ['Single'],
            Double: ['Single', 'Double'],
            Triple: ['Single', 'Double', 'Triple'],
            Special: ['Single', 'Double', 'Triple', 'Special']
        };

        const flightsToCheck = flightCheckOrder[flight] || [];

        const flightFieldsToCheck = flightsToCheck.flatMap(f => flightFieldMap[f] || []);

        const missingFlightFields = flightFieldsToCheck
            .filter(field => field.value === null)
            .map(field => field.label);

        if (missingFlightFields.length > 0) {
            $q.dialog({
                title: '<span class="text-red">Alert</span>',
                message: `Please enter the value of: <b>${missingFlightFields.join(', ')}</b><br><br>`,
                color: 'red-5',
                html: true
            });
        } else {
            emit('search-data', agitatorData);
        }
    };


    // function hasNull(obj) {
    //     for (const key in obj) {
    //         if (obj[key] === null) {
    //         return true;
    //         }
    //         // If nested object, check recursively
    //         if (typeof obj[key] === 'object' && obj[key] !== null) {
    //         if (hasNull(obj[key])) {
    //             return true;
    //         }
    //         }
    //     }
    //     return false;
    // }

    const prepareAgitatorData = () => {
        const agitatorData = {
            component: 'Agitator',
            shaftDia: shaftDia.value? shaftDia.value.toString() : null,
            sealingType: sealingType.value? sealingType.value : null,
            volumeMarking: volumeMarking.value? volumeMarking.value : null,
            hastalloySleeve: hastalloySleeve.value? hastalloySleeve.value : null,
            agitatorHeight: agitatorHeight.value? agitatorHeight.value.toString() : null,
            shaftDiaWithSleeve: shaftDiaWithSleeve.value? shaftDiaWithSleeve.value.toString() : null,
            flight: flight.value,
            singleFlightData: {
                singleFlightType: singleFlightType.value? singleFlightType.value : null,
                singleFlightDia: singleFlightDia.value? singleFlightDia.value.toString() : null
            },
            doubleFlightData: {
                doubleFlightType: doubleFlightType.value? doubleFlightType.value : null,
                doubleFlightDia: doubleFlightDia.value? doubleFlightDia.value.toString() : null,
                doubleFlightDistance: doubleFlightDistance.value? doubleFlightDistance.value.toString() : null
            },
            tripleFlightData: {
                tripleFlightType: tripleFlightType.value? tripleFlightType.value : null,
                tripleFlightDia: tripleFlightDia.value? tripleFlightDia.value.toString(): null,
                tripleFlightDistance: tripleFlightDistance.value? tripleFlightDistance.value.toString() :  null
            },
            specialFlightData: {
                specialFlightType: specialFlightType.value ? specialFlightType.value : null,
                specialFlightDia: specialFlightDia.value ? specialFlightDia.value.toString() : null,
                specialFlightDistance: specialFlightDistance.value ? specialFlightDistance.value.toString() : null
            }
        }
        return agitatorData
    }

    const populateInitialData = (data) => {
        shaftDia.value = parseInt(data.agitator_shaft.split(" ")[0])
        sealingType.value = data.sealing_type
        const flight_number = parseInt(data.agitator_flight) - 1
        flight.value = flightOptions.value[flight_number]
        
        const flight_sweeps_arr = JSON.parse(data.agitator_sweeps)
        const flight_sweeps = flight_sweeps_arr.map(item => {
            if (typeof item === "string") {
                const match = item.match(/\d+/); 
                return match ? parseInt(match[0]) : null;
            }
            return null;                                                                                         
        });
        
        if (flight.value == 'Single'){
            singleFlightType.value = data.agitator_flight_types[0]
            singleFlightDia.value = flight_sweeps[0]
        }
        else if(flight.value == 'Double'){
            singleFlightType.value = data.agitator_flight_types[0]
            singleFlightDia.value = flight_sweeps[0]
            doubleFlightType.value = data.agitator_flight_types[1]
            doubleFlightDia.value = flight_sweeps[1]
        }
        else if(flight.value == 'Triple'){
            singleFlightType.value = data.agitator_flight_types[0]
            singleFlightDia.value = flight_sweeps[0]
            doubleFlightType.value = data.agitator_flight_types[1]
            doubleFlightDia.value = flight_sweeps[1]
            tripleFlightType.value = data.agitator_flight_types[2]
            tripleFlightDia.value = flight_sweeps[2]
        }
        else if(flight.value == 'Special'){
            singleFlightType.value = data.agitator_flight_types[0]
            singleFlightDia.value = flight_sweeps[0]
            doubleFlightType.value = data.agitator_flight_types[1]
            doubleFlightDia.value = flight_sweeps[1]
            tripleFlightType.value = data.agitator_flight_types[2]
            tripleFlightDia.value = flight_sweeps[2]
            specialFlightType.value = data.agitator_flight_types[3]
            specialFlightDia.value = flight_sweeps[3]
        }
    }

    const fillData = (data) => {
        shaftDia.value = data.shaftDia?data.shaftDia:null
        sealingType.value = data.sealingType?data.sealingType:null
        volumeMarking.value = data.volumeMarking?data.volumeMarking:null
        hastalloySleeve.value = data.hastalloySleeve?data.hastalloySleeve:null
        agitatorHeight.value = data.agitatorHeight?data.agitatorHeight:null
        shaftDiaWithSleeve.value = data.shaftDiaWithSleeve?data.shaftDiaWithSleeve:null
        flight.value = data.flight?data.flight:null
        singleFlightType.value = data.singleFlightData.singleFlightType?data.singleFlightData.singleFlightType:null
        singleFlightDia.value = data.singleFlightData.singleFlightDia?data.singleFlightData.singleFlightDia:null
        doubleFlightType.value = data.doubleFlightData.doubleFlightType?data.doubleFlightData.doubleFlightType:null
        doubleFlightDia.value = data.doubleFlightData.doubleFlightDia?data.doubleFlightData.doubleFlightDia:null
        doubleFlightDistance.value = data.doubleFlightData.doubleFlightDistance?data.doubleFlightData.doubleFlightDistance:null
        tripleFlightType.value = data.tripleFlightData.tripleFlightType?data.tripleFlightData.tripleFlightType:null
        tripleFlightDia.value = data.tripleFlightData.tripleFlightDia?data.tripleFlightData.tripleFlightDia:null
        tripleFlightDistance.value = data.tripleFlightData.tripleFlightDistance?data.tripleFlightData.tripleFlightDistance:null
        specialFlightType.value = data.specialFlightData.specialFlightType?data.specialFlightData.specialFlightType:null
        specialFlightDia.value = data.specialFlightData.specialFlightDia?data.specialFlightData.specialFlightDia:null
        specialFlightDistance.value = data.specialFlightData.specialFlightDistance?data.specialFlightData.specialFlightDistance:null
    }

    return {
        shaftDiameters,
        shaftDia,
        sealingTypes,
        sealingType,
        agitatorHeight,
        volumeMarkingOptions,
        volumeMarking,
        hastalloySleeve,
        hastalloySleeveOptions,
        shaftDiaWithSleeve,
        flight,
        flightOptions,
        singleFlightType,
        singleFlightTypeOptions,
        singleFlightDia,
        doubleFlightType,
        doubleFlightTypeOptions,
        doubleFlightDia,
        doubleFlightDistance,
        tripleFlightType,
        tripleFlightTypeOptions,
        tripleFlightDia,
        tripleFlightDistance,
        specialFlightType,
        specialFlightTypeOptions,
        specialFlightDia,
        specialFlightDistance,
        // Methods
        onUpdateHastalloySleeve,
        searchAgitatorData,
        populateInitialData,
        fillData
    }
  },
  watch: {
    agitator: {
      handler(newVal) {
        if (newVal !== null) {
          this.populateInitialData(newVal)
        }
        if(newVal?.data){
             this.fillData(newVal?.data)
        }
      },
      immediate: true
    }
  }
}
</script>
