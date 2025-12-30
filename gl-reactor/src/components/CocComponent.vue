<template>
    <q-page class="q-pa-md">
     <!-- First Row -->
    <div class="q-mb-md">
        <div class="row q-gutter-md q-wrap">
            <q-input
            outlined
            v-model="cocSize"
            label="Size"
            type="text"
            dense
            class="col-12 col-md-2"
            />

            <q-space/>
            <q-btn outline rounded color="primary" icon="search" label="Search" @click="searchCocData"/>
        </div>
    </div>
  </q-page>
</template>
<script>
import { onMounted, ref } from 'vue'
export default {
  name: 'COC',
  props: {
    coc: Object
  },
  emits: ['search-data', 'get-mh-masters'],
  setup (props, { emit }) {
    const cocSize = ref(null)

    onMounted(() => {
        console.log('COC')
        const coc = localStorage.getItem('coc')
        const data = JSON.parse(coc)
        if(data !== null){
            cocSize.value = data.cocSize
        }
    })

    const searchCocData = () => {
        const data = prepareCocData()
        emit('search-data', data)
    }

    const prepareCocData = () => {
        const coc = {
            component: 'Coc',
            cocSize: cocSize.value? cocSize.value : null
        }
        localStorage.setItem('coc', JSON.stringify(coc))
        return coc
    }
    return {
        cocSize,

        // Methods
        searchCocData
    }
  }
}
</script>