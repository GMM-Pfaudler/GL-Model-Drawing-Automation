<template>
  <q-tab-panel :name="name">
    <div>
      <div class="row">
        <q-chip size="xl" outline square color="blue-5" text-color="white" style="padding-right: 50px;">
          {{ title }}
        </q-chip>
        <q-space />
        <q-chip v-if="drawingNumber !== null" outline square color="blue-5" text-color="white">
          {{ "Drawing Number: " + drawingNumber }}
        </q-chip>
        <q-space />
        <q-chip v-if="itemCode !== null" outline square color="blue-5" text-color="white">
          {{ "Item Code: " + itemCode }}
        </q-chip>
        <q-space />
        <q-chip
          v-if="itemCode !== null && showSaveButton"
          icon="check"
          square
          color="green-5"
          text-color="white"
          clickable
          @click="$emit('save')"
        >
          {{ "Save To File" }}
        </q-chip>
      </div>
      <slot />
    </div>
  </q-tab-panel>
</template>

<script setup>
defineProps({
  name: {
    type: String,
    required: true
  },
  title: {
    type: String,
    required: true
  },
  drawingNumber: {
    type: String,
    default: null
  },
  itemCode: {
    type: String,
    default: null
  },
  showSaveButton: {
    type: Boolean,
    default: true
  }
})

defineEmits(['save'])
</script>
