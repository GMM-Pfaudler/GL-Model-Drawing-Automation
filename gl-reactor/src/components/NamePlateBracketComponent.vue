<template>
    <q-page class="q-pa-md">
        <div class="q-mb-md">
            <div class="row q-gutter-md q-wrap">
                <q-select
                outlined
                v-model="npbMaterial"
                :options="npbMaterialOptions"
                label="Material"
                dense
                class="col-12 col-md-2"
                />
                <q-space/>
                <q-btn outline rounded color="primary" icon="search" label="Search" @click="searchNamePlateBracketData"/>
            </div>
        </div>
        <div class="q-mb-md">
            <div class="row q-gutter-md q-wrap">
                <q-select
                outlined
                v-model="npbType"
                :options="npbTypeOptions"
                label="Type"
                dense
                class="col-12 col-md-2"
                />
            </div>
        </div>
        <div class="q-mb-md">
            <div class="row q-gutter-md q-wrap">
                <q-select
                outlined
                v-model="npbMounting"
                :options="npbMountingOptions"
                label="Mounting"
                dense
                class="col-12 col-md-2"
                />
            </div>
        </div>
    </q-page>
</template>
<script>
// import { nodeBuiltin } from 'globals'
import { onMounted, ref } from 'vue'
export default {
  name: 'NamePlateBracket',
  props: {
    npb: Object
  },
  emits: ['search-data'],
  setup (props, { emit }) {
    const npbMaterial = ref(null)
    const npbMaterialOptions = ref(['-', 'MS', 'SS304', 'SS316'])
    const npbType = ref(null)
    const npbTypeOptions = ref(['-', 'Standard', 'Suit To Insulation'])
    const npbMounting = ref(null)
    const npbMountingOptions= ref(['-', 'Top Head', 'Jacket'])

    onMounted(() => {
        try {
            const data = localStorage.getItem('nameplatebracket')
            if (data) {
                const npbData = JSON.parse(data)
                if (npbData) {
                    npbMaterial.value = npbData.npbMaterial || null
                    npbType.value = npbData.npbType || null
                    npbMounting.value = npbData.npbMounting || null
                }
            }
        } catch (error) {
            console.error('Error parsing localStorage data:', error)
        }
    })

    const searchNamePlateBracketData = () => {
        const data = prepareNamePlateBracketData()
        emit('search-data', data)
    }

    const prepareNamePlateBracketData = () => {
        const namePlateBracket = {
            component: 'NamePlateBracket',
            npbMaterial: npbMaterial.value? npbMaterial.value: null,
            npbType: npbType.value? npbType.value: null,
            npbMounting: npbMounting.value? npbMounting.value: null
        }
        localStorage.setItem('nameplatebracket',JSON.stringify(namePlateBracket))
        return namePlateBracket
    }

    return {
        npbMaterial,
        npbMaterialOptions,
        npbType,
        npbTypeOptions,
        npbMounting,
        npbMountingOptions,

        // Methods
        searchNamePlateBracketData
    }
  }
}
</script>