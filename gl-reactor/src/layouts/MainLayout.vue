<template>
  <div>
    <q-layout view="hHh Lpr lff">
      <q-header elevated>
        <q-toolbar class="bg-white">
          <img src="https://intranet.gmmpfaudler.com/img/logos/Logo.png" style="height: 50px; padding: 5px 0px;">
          <q-avatar square></q-avatar>
          <q-toolbar-title class="text-dark text-center">
            <strong>Glass Lined 3D Model Generation</strong>
          </q-toolbar-title>
        </q-toolbar>
      </q-header>

      <q-page-container v-if="true" style="padding: 70px 0px 0px 0px;">
        <q-page padding style="display: flex; flex-direction: column;">
          <div class="q-gutter-md" style="padding-bottom: 5px; display: flex; justify-content: space-evenly;">
            <div class="item-center">
              <q-btn @click="prompt('Dashboard')" outline color="primary" dense label="Get OFN" />
            </div>
            <div class="row items-center q-gutter-sm">
              <q-input
                ref="sonoRef"
                outlined
                v-model="sono"
                label="Sales Order No"
                :dense="true"
                label-color="blue"
                :rules="[val => !!val || 'SO No is required']"
              >
                <q-tooltip>{{ sono }}</q-tooltip>
              </q-input>
            </div>
            <div class="column">
              <q-chip square outline text-color="black">Technical Specification Number</q-chip>
              <q-chip outline square color="blue-5" text-color="white">
                {{ sfon }}
                <q-tooltip>{{ sfon }}</q-tooltip>
              </q-chip>
            </div>
            <div class="column">
              <q-chip square outline text-color="black">Capacity</q-chip>
              <q-chip outline square color="blue-5" text-color="white">
                {{ capacity }}
                <q-tooltip>{{ capacity }}</q-tooltip>
              </q-chip>
            </div>
            <div class="column">
              <q-chip square outline text-color="black">Model</q-chip>
              <q-chip outline square color="blue-5" text-color="white">
                {{ model }}
                <q-tooltip>{{ model }}</q-tooltip>
              </q-chip>
            </div>
            <div class="column">
              <q-chip square outline text-color="black">Reactor</q-chip>
              <q-chip outline square color="blue-5" text-color="white">
                {{ reactor }}
                <q-tooltip>{{ reactor }}</q-tooltip>
              </q-chip>
            </div>
            <div class="column">
              <q-chip square outline text-color="black">Glass</q-chip>
              <q-chip outline square color="blue-5" text-color="white">
                {{ glass }}
                <q-tooltip>{{ glass }}</q-tooltip>
              </q-chip>
            </div>
            <div class="column">
              <q-chip square outline text-color="black">NDT</q-chip>
              <q-chip outline square color="blue-5" text-color="white">
                {{ ndt }}
                <q-tooltip>{{ ndt }}</q-tooltip>
              </q-chip>
            </div>
            <div class="column">
              <q-chip square outline text-color="black">Temperature</q-chip>
              <q-chip outline square color="blue-5" text-color="white">
                {{ designTemperature }}
                <q-tooltip>{{ designPressure }}</q-tooltip>
              </q-chip>
            </div>
            <div class="column">
              <q-chip square outline text-color="black">Pressure</q-chip>
              <q-chip outline square color="blue-5" text-color="white">
                {{ designPressure }}
                <q-tooltip>{{ designPressure }}</q-tooltip>
              </q-chip>
            </div>
            <div v-if="visibleGenerateButton = true" class="row items-center q-gutter-sm">
              <q-btn @click="generateModel" outline color="green" dense label="Generate Model" />
            </div>
          </div>
          <q-separator color="blue" inset />
          <div style="padding-top: 5px;">
            <q-splitter v-model="splitterModel">
              <template v-slot:before>
                <q-scroll-area style="height: 750px; max-width: 300px;">
                  <q-tabs
                    v-model="tab"
                    class="text-blue"
                    vertical
                    dense
                    style="text-align: left;"
                    @update:model-value="onUpdateTab"
                  >
                    <template v-for="(comp, index) in components" :key="comp.name">
                      <q-tab
                        v-if="showTab(comp.name)"
                        :name="comp.name"
                        :label="comp.label"
                        :class="'text-' + comp.color"
                      />
                      <q-separator v-if="index !== components.length - 1" />
                    </template>
                  </q-tabs>
                </q-scroll-area>
              </template>

              <template v-slot:after>
                <keep-alive>
                  <q-tab-panels
                    v-model="tab"
                    swipeable
                    vertical
                    transition-prev="jump-up"
                    transition-next="jump-up"
                  >
                    <!-- Agitator -->
                    <ComponentTabPanel
                      name="agitator"
                      title="Agitator"
                      :drawing-number="componentState.agitator.drawingNumber"
                      :item-code="componentState.agitator.itemCode"
                      @save="saveToJsonFile(tab, componentState.agitator.data)"
                    >
                      <AgitatorComponent
                        :agitator="componentState.agitator.ofnData"
                        @search-data="searchData"
                      />
                    </ComponentTabPanel>

                    <!-- Monoblock -->
                    <ComponentTabPanel
                      name="monoblock"
                      title="Monoblock"
                      :drawing-number="componentState.monoblock.drawingNumber"
                      :item-code="componentState.monoblock.itemCode"
                      @save="saveToJsonFile(tab, componentState.monoblock.data)"
                    >
                      <MonoblockComponent
                        :monoblock="componentState.monoblock.ofnData"
                        :fittingsData="fittingsData"
                        :fastenerData="fastenerData"
                        :bovMasters="bovMasters"
                        @get-bov-masters="getMasters"
                        @search-data="searchData"
                      />
                    </ComponentTabPanel>

                    <!-- Top Cover -->
                    <ComponentTabPanel
                      name="topCover"
                      title="Top Cover"
                      :drawing-number="componentState.topCover.drawingNumber"
                      :item-code="componentState.topCover.itemCode"
                      @save="saveToJsonFile(tab, componentState.topCover.data)"
                    >
                      <TopCoverComponent
                        :topcover="componentState.topCover.ofnData"
                        :fittingsData="fittingsData"
                        :bovMasters="bovMasters"
                        @get-bov-masters="getMasters"
                        @search-data="searchData"
                      />
                    </ComponentTabPanel>

                    <!-- Pan -->
                    <ComponentTabPanel
                      name="pan"
                      title="Pan"
                      :drawing-number="componentState.pan.drawingNumber"
                      :item-code="componentState.pan.itemCode"
                      @save="saveToJsonFile(tab, componentState.pan.data)"
                    >
                      <PanComponent
                        :pan="componentState.pan.ofnData"
                        :fittingsData="fittingsData"
                        :bovMasters="bovMasters"
                        @get-bov-masters="getMasters"
                        @search-data="searchData"
                      />
                    </ComponentTabPanel>

                    <!-- Jacket -->
                    <ComponentTabPanel
                      name="jacket"
                      title="Jacket Fittings"
                      :show-save-button="false"
                    >
                      <JacketComponent
                        :jacket="componentState.jacket.ofnData"
                        :jacketMasters="jacketMasters"
                        @search-data="searchData"
                        @get-jacket-masters="getMasters"
                        @save-jacket="saveJacket"
                      />
                    </ComponentTabPanel>

                    <!-- Diaphragm Ring -->
                    <ComponentTabPanel
                      name="diaphragmRing"
                      title="Diaphragm Ring"
                      :drawing-number="componentState.diaphragmRing.drawingNumber"
                      :item-code="componentState.diaphragmRing.itemCode"
                      @save="saveToJsonFile(tab, componentState.diaphragmRing.data)"
                    >
                      <DiaphragmRingComponent
                        :diaphragmRing="componentState.diaphragmRing.ofnData"
                        @search-data="searchData"
                      />
                    </ComponentTabPanel>

                    <!-- Manhole Cover -->
                    <ComponentTabPanel
                      name="manholeCover"
                      title="Manhole Cover"
                      :drawing-number="componentState.manholeCover.drawingNumber"
                      :item-code="componentState.manholeCover.itemCode"
                      @save="saveToJsonFile(tab, componentState.manholeCover.data)"
                    >
                      <ManholeCoverComponent
                        :manholeCover="componentState.manholeCover.ofnData"
                        @search-data="searchData"
                      />
                    </ComponentTabPanel>

                    <!-- Protection Ring -->
                    <ComponentTabPanel
                      name="protectingRing"
                      title="Protection Ring"
                      :drawing-number="componentState.protectionRing.drawingNumber"
                      :item-code="componentState.protectionRing.itemCode"
                      @save="saveToJsonFile(tab, componentState.protectionRing.data)"
                    >
                      <ProtectionRingComponent
                        :protectionRing="componentState.protectionRing.ofnData"
                        @search-data="searchData"
                      />
                    </ComponentTabPanel>

                    <!-- Spring Balance Assembly -->
                    <ComponentTabPanel
                      name="springBalanceAssembly"
                      title="Spring Balance Assembly"
                      :drawing-number="componentState.springBalanceAssembly.drawingNumber"
                      :item-code="componentState.springBalanceAssembly.itemCode"
                      @save="saveToJsonFile(tab, componentState.springBalanceAssembly.data)"
                    >
                      <SpringBalanceAssemblyComponent
                        :springbalanceassembly="componentState.springBalanceAssembly.ofnData"
                        @search-data="searchData"
                      />
                    </ComponentTabPanel>

                    <!-- Manhole C Clamp -->
                    <ComponentTabPanel
                      name="MHCClamp"
                      title="Manhole C Clamp"
                      :drawing-number="componentState.manholeCClamp.drawingNumber"
                      :item-code="componentState.manholeCClamp.itemCode"
                      @save="saveToJsonFile(tab, componentState.manholeCClamp.data)"
                    >
                      <ManholeCClampComponent
                        :manholeCClamp="componentState.manholeCClamp.ofnData"
                        :manholeCClampMasters="manholeCClampMasters"
                        @get-mh-masters="getMasters"
                        @search-data="searchData"
                      />
                    </ComponentTabPanel>

                    <!-- COC -->
                    <ComponentTabPanel
                      name="coc"
                      title="COC"
                      :drawing-number="componentState.coc.drawingNumber"
                      :item-code="componentState.coc.itemCode"
                      @save="saveToJsonFile(tab, componentState.coc.data)"
                    >
                      <CocComponent
                        :coc="componentState.coc.ofnData"
                        @search-data="searchData"
                      />
                    </ComponentTabPanel>

                    <!-- Body Flange C Clamp -->
                    <ComponentTabPanel
                      name="bfCClamp"
                      title="Body Flange C-Clamp"
                      :drawing-number="componentState.bfCClamp.drawingNumber"
                      :item-code="componentState.bfCClamp.itemCode"
                      @save="saveToJsonFile(tab, componentState.bfCClamp.data)"
                    >
                      <BodyFlangeCClampComponent
                        :bodyFlangeCClamp="componentState.bfCClamp.ofnData"
                        :bodyFlangeCClampMasters="bfCClampMasters"
                        @get-bf-masters="getMasters"
                        @search-data="searchData"
                      />
                    </ComponentTabPanel>

                    <!-- Thermosyphone -->
                    <ComponentTabPanel
                      name="thermosyphone"
                      title="Thermosyphone"
                      :drawing-number="componentState.thermosyphone.drawingNumber"
                      :item-code="componentState.thermosyphone.itemCode"
                      @save="saveToJsonFile(tab, componentState.thermosyphone.data)"
                    >
                      <ThermosyphoneComponent
                        :thermosyphone="componentState.thermosyphone.ofnData"
                        :thermosyphoneMasters="thermosyphoneMasters"
                        @search-data="searchData"
                        @get-thermosyphone-masters="getMasters"
                      />
                    </ComponentTabPanel>

                    <!-- Gear Box -->
                    <ComponentTabPanel
                      name="gearbox"
                      title="Gear Box"
                      :drawing-number="componentState.gearbox.drawingNumber"
                      :item-code="componentState.gearbox.itemCode"
                      @save="saveToJsonFile(tab, componentState.gearbox.data)"
                    >
                      <GearBoxComponent
                        :gearbox="componentState.gearbox.ofnData"
                        :gearboxMasters="gearboxMasters"
                        @search-data="searchData"
                        @get-gearbox-masters="getMasters"
                      />
                    </ComponentTabPanel>

                    <!-- Motor -->
                    <ComponentTabPanel
                      name="motor"
                      title="Motor"
                      :drawing-number="componentState.motor.drawingNumber"
                      :item-code="componentState.motor.itemCode"
                      @save="saveToJsonFile(tab, componentState.motor.data)"
                    >
                      <MotorComponent
                        :motor="componentState.motor.ofnData"
                        :motorMasters="motorMasters"
                        @search-data="searchData"
                        @get-motor-masters="getMasters"
                      />
                    </ComponentTabPanel>

                    <!-- Drive Assembly -->
                    <ComponentTabPanel
                      name="driveAssembly"
                      title="Drive Assembly"
                      :drawing-number="componentState.driveAssembly.drawingNumber"
                      :item-code="componentState.driveAssembly.itemCode"
                      @save="saveToJsonFile(tab, componentState.driveAssembly.data)"
                    >
                      <DriveAssemblyComponent
                        :driveAssembly="componentState.driveAssembly.ofnData"
                        @search-data="searchData"
                        @save-drive-assembly-data="saveDriveAssemblyData"
                      />
                    </ComponentTabPanel>

                    <!-- Bottom Outlet Valve -->
                    <ComponentTabPanel
                      name="bov"
                      title="Bottom Outlet Valve"
                      :drawing-number="componentState.bov.drawingNumber"
                      :item-code="componentState.bov.itemCode"
                      @save="saveToJsonFile(tab, componentState.bov.data)"
                    >
                      <BottomOutletValveComponent
                        :bov="componentState.bov.ofnData"
                        :bovMasters="bovMasters"
                        @get-bov-masters="getMasters"
                        @search-data="searchData"
                      />
                    </ComponentTabPanel>

                    <!-- Name Plate Bracket -->
                    <ComponentTabPanel
                      name="namePlateBracket"
                      title="Name Plate Bracket"
                      :drawing-number="componentState.namePlateBracket.drawingNumber"
                      :item-code="componentState.namePlateBracket.itemCode"
                      @save="saveToJsonFile(tab, componentState.namePlateBracket.data)"
                    >
                      <NamePlateBracketComponent
                        :npb="componentState.namePlateBracket.ofnData"
                        @search-data="searchData"
                      />
                    </ComponentTabPanel>

                    <!-- Drive Hood -->
                    <ComponentTabPanel
                      name="driveHood"
                      title="Drive Hood"
                      :drawing-number="componentState.driveHood.drawingNumber"
                      :item-code="componentState.driveHood.itemCode"
                      @save="saveToJsonFile(tab, componentState.driveHood.data)"
                    >
                      <DriveHoodComponent
                        :driveHood="componentState.driveHood.ofnData"
                        @search-data="searchData"
                      />
                    </ComponentTabPanel>

                    <!-- Air Vent Coupling Plug -->
                    <ComponentTabPanel
                      name="airVentCouplingPlug"
                      title="Air-Vent Coupling Plug"
                      :show-save-button="false"
                    >
                      <AirVentCouplingPlugComponent
                        :avcp="componentState.airVentCouplingPlug.ofnData"
                        @save-airvent="saveAirVent"
                        @search-data="searchData"
                      />
                    </ComponentTabPanel>

                    <!-- Insulation -->
                    <ComponentTabPanel
                      name="insulation"
                      title="Insulation"
                      :show-save-button="false"
                    >
                      <InsulationComponent
                        :insulation="componentState.insulation.ofnData"
                        @search-data="searchData"
                        @save-insulation-data="saveInsulationData"
                      />
                    </ComponentTabPanel>

                    <!-- Baffle -->
                    <ComponentTabPanel
                      name="baffle"
                      title="Baffle"
                      :drawing-number="componentState.baffle.drawingNumber"
                      :item-code="componentState.baffle.itemCode"
                      @save="saveToJsonFile(tab, componentState.baffle.data)"
                    >
                      <BaffleComponent
                        :baffle="componentState.baffle.ofnData"
                        :baffleMasters="baffleMasters"
                        @search-data="searchData"
                        @get-baffle-masters="getMasters"
                        @save-baffle="saveBaffleData"
                      />
                    </ComponentTabPanel>

                    <!-- Thermowell -->
                    <ComponentTabPanel
                      name="thermowell"
                      title="Thermowell"
                      :show-save-button="false"
                    >
                      <ThermowellComponent
                        :thermowell="componentState.thermowell.ofnData"
                        :thermowellMasters="thermowellMasters"
                        @search-data="searchData"
                        @get-thermowell-masters="getMasters"
                        @save-thermowell="saveThermowellData"
                      />
                    </ComponentTabPanel>

                    <!-- Sensor -->
                    <ComponentTabPanel
                      name="sensor"
                      title="Sensor"
                      :drawing-number="componentState.sensor.drawingNumber"
                      :item-code="componentState.sensor.itemCode"
                      @save="saveToJsonFile(tab, componentState.sensor.data)"
                    >
                      <SensorComponent
                        :sensor="componentState.sensor.ofnData"
                        @search-data="searchData"
                        @save-sensor="saveSensorData"
                      />
                    </ComponentTabPanel>

                    <!-- Shaft Closure -->
                    <ComponentTabPanel
                      name="shaftclosure"
                      title="Shaft Closure"
                      :drawing-number="componentState.shaftclosure.drawingNumber"
                      :item-code="componentState.shaftclosure.itemCode"
                      @save="saveToJsonFile(tab, componentState.shaftclosure.data)"
                    >
                      <ShaftClosureComponent
                        :shaftclosure="componentState.shaftclosure.ofnData"
                        :shaftclosureMasters="shaftclosureMasters"
                        @search-data="searchData"
                        @get-shaftclosure-masters="getMasters"
                      />
                    </ComponentTabPanel>
                  </q-tab-panels>
                </keep-alive>
              </template>
            </q-splitter>
          </div>
        </q-page>
      </q-page-container>
    </q-layout>
  </div>

  <!-- Missing Item Code Dialog -->
  <div class="q-pa-md q-gutter-sm">
    <q-dialog v-model="isItemCodeNull" persistent>
      <q-card class="q-pa-md" style="min-width: 420px; max-width: 95vw; border-radius: 12px;">
        <q-bar class="bg-primary text-white" style="border-top-left-radius: 12px; border-top-right-radius: 12px;">
          <div class="text-h6">Missing Item Code</div>
          <q-space />
          <q-btn dense flat icon="close" v-close-popup>
            <q-tooltip>Close</q-tooltip>
          </q-btn>
        </q-bar>
        <q-card-section class="q-pt-md q-pb-none">
          <div class="text-subtitle2">
            Item code for <strong>{{ comp }}</strong> was not found.<br>
            Please provide the required details below.
          </div>
        </q-card-section>
        <q-card-section>
          <q-form @submit.prevent="saveData">
            <q-input
              v-model="drawingNumber"
              label="Drawing Number"
              outlined
              dense
              label-color="primary"
              :rules="[val => !!val || 'Drawing number is required']"
              class="q-mb-md"
              style="border-radius: 8px; font-size: 15px;"
            />
            <q-input
              v-model="itemCode"
              label="Item Code"
              outlined
              dense
              label-color="primary"
              :rules="[val => !!val || 'Item code is required']"
              class="q-mb-md"
              style="border-radius: 8px; font-size: 15px;"
            />
            <div class="row justify-end q-gutter-sm q-mt-md">
              <q-btn flat label="Cancel" color="grey-7" v-close-popup />
              <q-btn unelevated label="Save" color="primary" @click="saveData" v-close-popup />
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- Sales Order Number Alert -->
    <q-dialog v-model="isSalesOrderNumberNull">
      <q-card class="bg-pink-1 text-red-8">
        <q-card-section class="row items-center q-gutter-sm">
          <q-icon name="warning" size="md" color="red-6" />
          <div class="text-h6">Alert</div>
        </q-card-section>
        <q-card-section class="q-pt-none text-subtitle2">
          Please provide a Sales Order Number.
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="OK" color="red-6" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed } from 'vue'
import axios from 'axios'
import { useQuasar, Notify } from 'quasar'

// Component imports
import ComponentTabPanel from 'components/ComponentTabPanel.vue'
import AgitatorComponent from 'components/AgitatorComponent.vue'
import MonoblockComponent from 'components/MonoblockComponent.vue'
import JacketComponent from 'components/JacketComponent.vue'
import DriveAssemblyComponent from 'components/DriveAssemblyComponent.vue'
import BaffleComponent from 'components/BaffleComponent.vue'
import SensorComponent from 'src/components/SensorComponent.vue'
import ShaftClosureComponent from 'src/components/ShaftClosureComponent.vue'
import ThermosyphoneComponent from 'src/components/ThermosyphoneComponent.vue'
import GearBoxComponent from 'src/components/GearBoxComponent.vue'
import MotorComponent from 'src/components/MotorComponent.vue'
import DiaphragmRingComponent from 'src/components/DiaphragmRingComponent.vue'
import ManholeCoverComponent from 'src/components/ManholeCoverComponent.vue'
import ProtectionRingComponent from 'src/components/ProtectionRingComponent.vue'
import SpringBalanceAssemblyComponent from 'src/components/SpringBalanceAssemblyComponent.vue'
import ManholeCClampComponent from 'src/components/ManholeCClampComponent.vue'
import CocComponent from 'src/components/CocComponent.vue'
import BodyFlangeCClampComponent from 'src/components/BodyFlangeCClampComponent.vue'
import BottomOutletValveComponent from 'src/components/BottomOutletValveComponent.vue'
import NamePlateBracketComponent from 'src/components/NamePlateBracketComponent.vue'
import AirVentCouplingPlugComponent from 'src/components/AirVentCouplingPlugComponent.vue'
import InsulationComponent from 'src/components/InsulationComponent.vue'
import DriveHoodComponent from 'src/components/DriveHoodComponent.vue'
import ThermowellComponent from 'src/components/ThermowellComponent.vue'
import PanComponent from 'src/components/PanComponent.vue'
import TopCoverComponent from 'src/components/TopCoverComponent.vue'

// Component configuration for search/save lookup
const FITTING_COMPONENTS = [
  'gasket', 'split flange', 'blind cover', 'reducing flange', 'dip pipe',
  'sparger', 'spray ball pipe', 'spray ball', 'tee', 'manhole protection ring',
  'manhole cover', 'toughened glass', 'sight/light glass flange', 'extension piece',
  'baffle', 'bov'
]

const DRIVE_ASSEMBLY_COMPONENTS = [
  'drivebasering', 'padplate', 'lanternsupport', 'lanternguard',
  'agitatorgearcoupling', 'gearboxmodel', 'bearingnumber', 'sleeve',
  'oilseal', 'circlip', 'locknut', 'lockwasher'
]

const JACKET_COMPONENTS = [
  'jacketnozzle', 'jacket', 'sidebracket', 'legsupport',
  'sidebracketlegsupport', 'ringsupport', 'skirtsupport', 'earthing'
]

const INSULATION_COMPONENTS = ['cleat', 'nut', 'tophead', 'topjcr', 'head', 'shell', 'closer']

const FASTENER_COMPONENTS = ['fastener', 'washer', 'fastener_nut']

// Components array definition
const COMPONENTS_ARRAY = [
  { icon: 'error_outline', label: 'Pan', name: 'pan', color: 'orange', saved: false },
  { icon: 'error_outline', label: 'Top Cover', name: 'topCover', color: 'orange', saved: false },
  { icon: 'error_outline', label: 'Monoblock', name: 'monoblock', color: 'orange', saved: false },
  { icon: 'error_outline', label: 'Jacket', name: 'jacket', color: 'orange', saved: false },
  { icon: 'error_outline', label: 'Diaphragm Ring', name: 'diaphragmRing', color: 'orange', saved: false },
  { icon: 'error_outline', label: 'Spring Balance Assembly', name: 'springBalanceAssembly', color: 'orange', saved: false },
  { icon: 'error_outline', label: 'Manhole C-Clamp', name: 'MHCClamp', color: 'orange', saved: false },
  { icon: 'error_outline', label: 'COC', name: 'coc', color: 'orange', saved: false },
  { icon: 'error_outline', label: 'Body Flange C-Clamp', name: 'bfCClamp', color: 'orange', saved: false },
  { icon: 'error_outline', label: 'Thermowell', name: 'thermowell', color: 'orange', saved: false },
  { icon: 'error_outline', label: 'Sensor', name: 'sensor', color: 'orange', saved: false },
  { icon: 'error_outline', label: 'Agitator', name: 'agitator', color: 'orange', saved: false },
  { icon: 'error_outline', label: 'Shaft Closure', name: 'shaftclosure', color: 'orange', saved: false },
  { icon: 'error_outline', label: 'Thermosyphone', name: 'thermosyphone', color: 'orange', saved: false },
  { icon: 'error_outline', label: 'Gear Box', name: 'gearbox', color: 'orange', saved: false },
  { icon: 'error_outline', label: 'Motor', name: 'motor', color: 'orange', saved: false },
  { icon: 'error_outline', label: 'Drive Assembly', name: 'driveAssembly', color: 'orange', saved: false },
  { icon: 'error_outline', label: 'Drive Hood', name: 'driveHood', color: 'orange', saved: false },
  { icon: 'error_outline', label: 'Name Plate Bracket', name: 'namePlateBracket', color: 'orange', saved: false },
  { icon: 'error_outline', label: 'Air-Vent Coupling Plug', name: 'airVentCouplingPlug', color: 'orange', saved: false },
  { icon: 'error_outline', label: 'Insulation', name: 'insulation', color: 'orange', saved: false }
]

// Helper function to create initial component state
const createComponentState = () => ({
  ofnData: null,
  data: null,
  drawingNumber: null,
  itemCode: null
})

export default {
  components: {
    ComponentTabPanel,
    AgitatorComponent,
    MonoblockComponent,
    JacketComponent,
    DriveAssemblyComponent,
    BaffleComponent,
    SensorComponent,
    ShaftClosureComponent,
    ThermosyphoneComponent,
    GearBoxComponent,
    MotorComponent,
    DiaphragmRingComponent,
    ManholeCoverComponent,
    ProtectionRingComponent,
    SpringBalanceAssemblyComponent,
    ManholeCClampComponent,
    CocComponent,
    BodyFlangeCClampComponent,
    BottomOutletValveComponent,
    NamePlateBracketComponent,
    AirVentCouplingPlugComponent,
    InsulationComponent,
    DriveHoodComponent,
    ThermowellComponent,
    PanComponent,
    TopCoverComponent
  },

  setup() {
    const $q = useQuasar()

    // Consolidated component state
    const componentState = reactive({
      agitator: createComponentState(),
      monoblock: createComponentState(),
      topCover: createComponentState(),
      pan: createComponentState(),
      jacket: createComponentState(),
      diaphragmRing: createComponentState(),
      manholeCover: createComponentState(),
      protectionRing: createComponentState(),
      springBalanceAssembly: createComponentState(),
      manholeCClamp: createComponentState(),
      coc: createComponentState(),
      bfCClamp: createComponentState(),
      driveAssembly: createComponentState(),
      bov: createComponentState(),
      namePlateBracket: createComponentState(),
      driveHood: createComponentState(),
      airVentCouplingPlug: createComponentState(),
      baffle: createComponentState(),
      thermowell: createComponentState(),
      sensor: createComponentState(),
      shaftclosure: createComponentState(),
      thermosyphone: createComponentState(),
      gearbox: createComponentState(),
      motor: createComponentState(),
      insulation: createComponentState()
    })

    // UI State
    const comp = ref(null)
    const components = ref([])
    const componentsArray = ref([...COMPONENTS_ARRAY])
    const visibleGenerateButton = ref(false)
    const tab = ref(null)
    const splitterModel = ref(15)
    const isDisplayTab = ref(false)

    // OFN Details
    const sono = ref(null)
    const sonoRef = ref(null)
    const sfon = ref(null)
    const capacity = ref(null)
    const modelId = ref(null)
    const reactor = ref(null)
    const reactorId = ref(null)
    const model = ref(null)
    const glass = ref(null)
    const ndt = ref(null)
    const designTemperature = ref(null)
    const designPressure = ref(null)

    // Dialog state
    const isSalesOrderNumberNull = ref(false)
    const isItemCodeNull = ref(false)
    const drawingNumber = ref(null)
    const itemCode = ref(null)

    // Shared data
    const fittingsData = ref(null)
    const fastenerData = ref(null)

    // Masters data
    const jacketMasters = ref(null)
    const baffleMasters = ref(null)
    const thermowellMasters = ref(null)
    const shaftclosureMasters = ref(null)
    const thermosyphoneMasters = ref(null)
    const gearboxMasters = ref(null)
    const motorMasters = ref(null)
    const manholeCClampMasters = ref(null)
    const bfCClampMasters = ref(null)
    const bovMasters = ref(null)

    const host = ref('http://127.0.0.1:8000')

    // Computed model info
    const modelInfo = computed(() => ({
      capacity: capacity.value,
      model: model.value,
      reactor: reactor.value,
      glass: glass.value,
      ndt: ndt.value,
      designPressure: designPressure.value,
      designTemperature: designTemperature.value,
      drawingNumber: '',
      itemCode: ''
    }))

    // Component state mapping for search/save operations
    const COMPONENT_STATE_MAP = {
      agitator: { state: () => componentState.agitator, dataKey: 'agitatorData' },
      monoblock: { state: () => componentState.monoblock, dataKey: 'monoblockData' },
      topcover: { state: () => componentState.topCover, dataKey: 'topCoverData' },
      pan: { state: () => componentState.pan, dataKey: 'panData' },
      diaphragmring: { state: () => componentState.diaphragmRing, dataKey: 'ringData' },
      manholecover: { state: () => componentState.manholeCover, dataKey: 'manholeCoverData' },
      protectionring: { state: () => componentState.protectionRing, dataKey: 'protectionRingData' },
      springbalanceassembly: { state: () => componentState.springBalanceAssembly, dataKey: 'springbalanceassemblyData' },
      manholecclamp: { state: () => componentState.manholeCClamp, dataKey: 'manholeCClampData' },
      coc: { state: () => componentState.coc, dataKey: 'cocData' },
      bodyflangecclamp: { state: () => componentState.bfCClamp, dataKey: 'bfCClampData' },
      thermowell: { state: () => componentState.thermowell, dataKey: 'thermowellData' },
      sensor: { state: () => componentState.sensor, dataKey: 'sensorData' },
      shaftclosure: { state: () => componentState.shaftclosure, dataKey: 'shaftclosureData' },
      thermosyphone: { state: () => componentState.thermosyphone, dataKey: 'thermosyphoneData' },
      gearbox: { state: () => componentState.gearbox, dataKey: 'gearboxData' },
      motor: { state: () => componentState.motor, dataKey: 'motorData' },
      drivehood: { state: () => componentState.driveHood, dataKey: 'driveHoodData' },
      nameplatebracket: { state: () => componentState.namePlateBracket, dataKey: 'npbData' },
      airventcouplingplug: { state: () => componentState.airVentCouplingPlug, dataKey: 'avcpData' }
    }

    // Helper to capitalize first letter
    const capitalize = (str) => str ? str.charAt(0).toUpperCase() + str.slice(1) : ''

    const onUpdateTab = (val) => {
      const stateMap = {
        agitator: () => { if (componentState.agitator.ofnData) componentState.agitator.ofnData.data = componentState.agitator.data },
        monoblock: () => { if (componentState.monoblock.ofnData) componentState.monoblock.ofnData.data = componentState.monoblock.data },
        jacket: () => { if (componentState.jacket.ofnData) componentState.jacket.ofnData.data = componentState.jacket.data },
        baffle: () => { componentState.baffle.ofnData = componentState.baffle.data }
      }
      if (stateMap[val]) stateMap[val]()
    }

    const onUpdateModelType = (modelTypeVal) => {
      tab.value = null
      localStorage.clear()

      const disallowedByModel = {
        AE: ['monoblock', 'coc', 'baffle'],
        BE: ['pan', 'topCover', 'bfcClamp', 'coc', 'baffle'],
        CE: ['pan', 'topCover', 'thermowell']
      }

      const disallowedNames = disallowedByModel[modelTypeVal] || []
      const filteredComponents = componentsArray.value.filter(c => !disallowedNames.includes(c.name))
      components.value.splice(0, components.value.length)
      components.value.push(...filteredComponents)
    }

    const prompt = (clickedItem) => {
      if (clickedItem === 'Dashboard') {
        $q.dialog({
          title: 'Prompt',
          message: 'Enter Salesforce Order Number (SFON)',
          prompt: {
            model: '',
            isValid: val => val.length > 5,
            type: 'number'
          },
          cancel: true,
          persistent: true
        }).onOk(data => {
          getOFNDetails(data)
        })
      }
    }

    const getOFNDetails = (sfno) => {
      axios.post('http://10.9.206.246:8000/ofn/getofn', JSON.stringify({ sfon: sfno }), {
        headers: { 'Content-Type': 'application/json' }
      })
        .then(response => {
          const data = response.data
          if (data.ofn_details !== null) {
            fillOFNDetails(data)
          } else {
            $q.dialog({
              title: 'Invalid SFON',
              message: 'You must provide a valid Salesforce Order Number.',
              icon: 'error',
              ok: { label: 'Try Again', color: 'negative' },
              class: 'text-negative'
            }).onOk(() => {
              prompt('Dashboard')
            })
          }
        })
        .catch(error => {
          console.error('Error:', error)
        })
    }

    const fillOFNDetails = (data) => {
      const details = data.ofn_details
      sfon.value = details.sfon_no
      capacity.value = details.v_capacity
      model.value = details.model
      modelId.value = details.model_id
      reactor.value = details.reactor
      reactorId.value = details.reactor_id
      glass.value = details.glass
      ndt.value = details.ndt_value
      designTemperature.value = details.design_temperature
      designPressure.value = details.design_pressure

      const mt = details.model.split('_')[0]
      onUpdateModelType(mt)

      prepareAgitatorData(data)
      prepareMonoblockData(data)
      prepareTopCoverData(data)
      preparePanData(data)
      prepareJacketData(data)
      prepareShaftClosureData(data)
      isThermosyphoneVisible(data)
      prepareGearboxData(data)
      prepareMotorData(data)
      prepareDiaphragmRingData(data)
      prepareManholeCoverData(data)
      prepareProtectionRingData(data)
      prepareSpringbalanceassemblyData(data)
      prepareBovData(data)
      prepareInsulationData(data)
      prepareDriveAssemblyData(data)
    }

    const prepareAgitatorData = (data) => {
      componentState.agitator.ofnData = {
        agitator_shaft: data.ofn_details.agitator_shaft,
        sealing_type: data.ofn_details.sealing_type,
        agitator_flight: data.ofn_details.agitator_flight,
        agitator_sweeps: data.ofn_details.agitator_sweep,
        agitator_flight_types: data.ofn_details.agitator_flight_types
      }
    }

    const prepareMonoblockData = (data) => {
      componentState.monoblock.ofnData = {
        id: data.ofn_details.v_id_mm,
        osTos: data.ofn_details.v_ostoos_mm,
        reactor: data.ofn_details.reactor,
        nozzle_names: data.ofn_details.non_field1,
        nozzle_sizes: data.ofn_details.non_field2,
        nozzle_locations: data.ofn_details.non_field4
      }
    }

    const prepareTopCoverData = (data) => {
      componentState.topCover.ofnData = {
        id: data.ofn_details.v_id_mm,
        osTos: data.ofn_details.v_ostoos_mm,
        reactor: data.ofn_details.reactor,
        nozzle_names: data.ofn_details.non_field1,
        nozzle_sizes: data.ofn_details.non_field2,
        nozzle_locations: data.ofn_details.non_field4
      }
    }

    const preparePanData = (data) => {
      componentState.pan.ofnData = {
        id: data.ofn_details.v_id_mm,
        osTos: data.ofn_details.v_ostoos_mm,
        reactor: data.ofn_details.reactor,
        nozzle_names: data.ofn_details.non_field1,
        nozzle_sizes: data.ofn_details.non_field2,
        nozzle_locations: data.ofn_details.non_field4
      }
    }

    const prepareJacketData = (data) => {
      componentState.jacket.ofnData = {
        jacketType: data.ofn_details.jacketType,
        jacketSupport: data.ofn_details.jacketSupport,
        jacketPressure: data.ofn_details.jacketPressure,
        jacketTemperature: data.ofn_details.jacketTemperature,
        jacketNDT: data.ofn_details.jacketNDT,
        jacketOD: data.ofn_details.v_jacket_od,
        jacketMaterialShell: data.ofn_details.jacketMaterialShell,
        jacketMaterialNozzle: data.ofn_details.jacketMaterialNozzle,
        jacketMaterialEarthingType: data.ofn_details.material_earthing_type
      }
    }

    const prepareDiaphragmRingData = (data) => {
      componentState.diaphragmRing.ofnData = {
        nozzle_names: data.ofn_details.non_field1,
        nozzle_sizes: data.ofn_details.non_field2
      }
    }

    const prepareShaftClosureData = (data) => {
      componentState.shaftclosure.ofnData = {
        shaft_dia: data.ofn_details.agitator_shaft,
        shaft_type: data.ofn_details.shaft_type,
        shaft_make: data.ofn_details.shaft_make,
        shaft_housing: data.ofn_details.shaft_housing,
        shaft_sealing: data.ofn_details.shaft_sealing,
        shaft_inboard: data.ofn_details.shaft_inboard,
        shaft_outboard: data.ofn_details.shaft_outboard,
        shaft_other: data.ofn_details.shaft_other
      }
    }

    const isThermosyphoneVisible = (data) => {
      const shaftType = data.ofn_details.shaft_type
      isDisplayTab.value = !(shaftType === 'Single Mechanical Seal' || shaftType === 'Stuffing Box')
    }

    const showTab = (compName) => {
      return compName === 'thermosyphone' ? isDisplayTab.value : true
    }

    const prepareGearboxData = (data) => {
      componentState.gearbox.ofnData = {
        gear_make: data.ofn_details.gear_make,
        gear_type: data.ofn_details.gear_type
      }
    }

    const prepareMotorData = (data) => {
      componentState.motor.ofnData = {
        motor_type: data.ofn_details.motor_type,
        motor_make: data.ofn_details.motor_make,
        motor_mounting: data.ofn_details.motor_mounting,
        motor_standard: data.ofn_details.motor_standard,
        motor_hp: data.ofn_details.motor_hp
      }
    }

    const prepareManholeCoverData = (data) => {
      componentState.manholeCover.ofnData = {
        nozzle_services: data.ofn_details.non_field3,
        nozzle_sizes: data.ofn_details.non_field2
      }
    }

    const prepareProtectionRingData = (data) => {
      componentState.protectionRing.ofnData = {
        nozzle_services: data.ofn_details.non_field3,
        nozzle_sizes: data.ofn_details.non_field2
      }
    }

    const prepareSpringbalanceassemblyData = (data) => {
      componentState.springBalanceAssembly.ofnData = {
        nozzle_services: data.ofn_details.non_field3,
        nozzle_sizes: data.ofn_details.non_field2
      }
    }

    const prepareBovData = (data) => {
      componentState.bov.ofnData = {
        nozzle_names: data.ofn_details.non_field1,
        nozzle_sizes: data.ofn_details.non_field2,
        gasket: data.ofn_details.gasket,
        fastener: data.ofn_details.fastener,
        split_flange: data.ofn_details.split_flange
      }
    }

    const prepareInsulationData = (data) => {
      componentState.insulation.ofnData = {
        reactor: data.ofn_details.reactor
      }
    }

    const prepareDriveAssemblyData = (data) => {
      componentState.driveAssembly.ofnData = {
        model: model.value || null,
        shaft_dia: data.ofn_details.agitator_shaft
      }
    }

    const saveToJsonFile = (comp_name, data) => {
      if (!sono.value) {
        isSalesOrderNumberNull.value = true
        return
      }

      const compDetails = { [comp_name]: data, so_no: sono.value }
      localStorage.setItem(`savedData:${comp_name}`, JSON.stringify(compDetails))

      axios.post(`${host.value}/api/v1/savetojson`, JSON.stringify({ componentDetails: compDetails }), {
        headers: { 'Content-Type': 'application/json' }
      })
        .then(response => {
          if (response.data) {
            $q.notify({ message: 'Successfully saved information.', color: 'green-5' })
            const target = components.value.find(item => item.name === comp_name)
            if (target) {
              target.icon = 'check_circle_outline'
              target.color = 'green'
              target.saved = true
            }
            visibleGenerateButton.value = components.value.every(obj => obj.saved === true)
          }
        })
        .catch(error => {
          console.error('Error:', error)
        })
    }

    const generateModel = () => {
      if (!sono.value) {
        isSalesOrderNumberNull.value = true
        return
      }

      const sonoDetails = {
        sono: sono.value,
        model: model.value,
        reactor: reactor.value,
        capacity: capacity.value
      }

      axios.post(`${host.value}/api/v1/generate`, JSON.stringify({ details: sonoDetails }), {
        headers: { 'Content-Type': 'application/json' }
      })
        .then(response => {
          if (response.data) {
            $q.notify({ message: 'Successfully saved information.', color: 'green-5' })
          }
        })
        .catch(error => {
          console.error('Error:', error)
        })
    }

    // Search data handler with lookup pattern
    const searchData = async (data) => {
      const component = data.component ? data.component.toLowerCase() : null
      data.model_info = { ...modelInfo.value }

      try {
        const response = await axios.post(
          `${host.value}/api/v1/search`,
          JSON.stringify({ [component]: data }),
          { headers: { 'Content-Type': 'application/json' } }
        )

        handleSearchResponse(component, response, data)
      } catch (error) {
        console.error('Error:', error)
      }
    }

    const handleSearchResponse = (component, response, data) => {
      const result = response.data.result

      // Check if it's a standard component with direct state mapping
      if (COMPONENT_STATE_MAP[component]) {
        const stateObj = COMPONENT_STATE_MAP[component].state()
        if (result === null) {
          comp.value = capitalize(component)
          stateObj.drawingNumber = null
          stateObj.itemCode = null
          drawingNumber.value = null
          itemCode.value = null
          isItemCodeNull.value = true
        } else {
          stateObj.itemCode = result.itemCode.toString()
          stateObj.drawingNumber = result.drawingNumber.toString()
          data.model_info.drawingNumber = stateObj.drawingNumber
          data.model_info.itemCode = stateObj.itemCode
        }
        stateObj.data = data
        return
      }

      // Handle fitting components
      if (FITTING_COMPONENTS.includes(component)) {
        if (result === null) {
          comp.value = capitalize(component)
          drawingNumber.value = null
          itemCode.value = null
          isItemCodeNull.value = true
        } else {
          data.model_info.drawingNumber = result.drawingNumber.toString()
          data.model_info.itemCode = result.itemCode.toString()
        }
        fittingsData.value = data
        return
      }

      // Handle fastener components
      if (FASTENER_COMPONENTS.includes(component)) {
        if (result === null) {
          comp.value = capitalize(component)
          drawingNumber.value = null
          itemCode.value = null
          isItemCodeNull.value = true
        } else {
          data.model_info.drawingNumber = result.drawingNumber.toString()
          data.model_info.itemCode = result.itemCode.toString()
        }
        fastenerData.value = data
        return
      }

      // Handle drive assembly components
      if (DRIVE_ASSEMBLY_COMPONENTS.includes(component)) {
        if (result === null) {
          comp.value = capitalize(component)
          drawingNumber.value = null
          itemCode.value = null
          isItemCodeNull.value = true
        } else {
          data.model_info.drawingNumber = result.drawingNumber.toString()
          data.model_info.itemCode = result.itemCode.toString()
          componentState.driveAssembly.ofnData = data
        }
        componentState.driveAssembly.data = data
        return
      }

      // Handle jacket components
      if (JACKET_COMPONENTS.includes(component)) {
        if (result === null) {
          comp.value = capitalize(component)
          drawingNumber.value = null
          itemCode.value = null
          isItemCodeNull.value = true
        } else {
          data.model_info.drawingNumber = result.drawingNumber.toString()
          data.model_info.itemCode = result.itemCode.toString()
          componentState.jacket.ofnData = data
        }
        componentState.jacket.data = data
        return
      }

      // Handle insulation components
      if (INSULATION_COMPONENTS.includes(component)) {
        if (result === null) {
          comp.value = capitalize(component)
          drawingNumber.value = null
          itemCode.value = null
          isItemCodeNull.value = true
        } else {
          data.model_info.drawingNumber = result.drawingNumber.toString()
          data.model_info.itemCode = result.itemCode.toString()
          componentState.insulation.ofnData = data
        }
        componentState.insulation.data = data
      }
    }

    // Save data handler with lookup pattern
    const saveData = async () => {
      const componentLower = comp.value ? comp.value.toLowerCase() : null
      let objToSave = null

      const currentModelInfo = {
        capacity: capacity.value,
        model: model.value,
        reactor: reactor.value,
        glass: glass.value,
        ndt: ndt.value,
        designPressure: designPressure.value,
        designTemperature: designTemperature.value,
        drawingNumber: drawingNumber.value,
        itemCode: itemCode.value
      }

      // Check standard components
      if (COMPONENT_STATE_MAP[componentLower]) {
        const stateObj = COMPONENT_STATE_MAP[componentLower].state()
        stateObj.data.model_info = currentModelInfo
        objToSave = { [componentLower]: stateObj.data }
      } else if (FITTING_COMPONENTS.includes(componentLower)) {
        fittingsData.value.model_info = currentModelInfo
        objToSave = { [componentLower]: fittingsData.value }
      } else if (FASTENER_COMPONENTS.includes(componentLower)) {
        fastenerData.value.model_info = currentModelInfo
        objToSave = { [componentLower]: fastenerData.value }
      } else if (DRIVE_ASSEMBLY_COMPONENTS.includes(componentLower)) {
        componentState.driveAssembly.data.model_info = currentModelInfo
        objToSave = { [componentLower]: componentState.driveAssembly.data }
      } else if (JACKET_COMPONENTS.includes(componentLower)) {
        componentState.jacket.data.model_info = currentModelInfo
        objToSave = { [componentLower]: componentState.jacket.data }
      } else if (INSULATION_COMPONENTS.includes(componentLower)) {
        componentState.insulation.data.model_info = currentModelInfo
        objToSave = { [componentLower]: componentState.insulation.data }
      }

      if (!objToSave) return

      try {
        const response = await axios.post(
          `${host.value}/api/v1/save`,
          JSON.stringify(objToSave),
          { headers: { 'Content-Type': 'application/json' } }
        )

        if (response.data) {
          handleSaveResponse(componentLower)
          $q.notify({
            message: `Successfully saved ${comp.value} data to excel file.`,
            color: 'green-5'
          })
        }
      } catch (error) {
        console.error('Error:', error)
        if (error.response && error.response.status === 409) {
          Notify.create({
            type: 'warning',
            message: error.response.data.detail || 'Excel file is open. Please close it before saving.',
            timeout: 0,
            actions: [{ label: 'Dismiss', color: 'white' }]
          })
        } else {
          Notify.create({
            type: 'negative',
            message: 'An unexpected error occurred. Please try again.',
            timeout: 5000
          })
        }
      }
    }

    const handleSaveResponse = (componentLower) => {
      // Update drawing number and item code for standard components
      if (COMPONENT_STATE_MAP[componentLower]) {
        const stateObj = COMPONENT_STATE_MAP[componentLower].state()
        stateObj.drawingNumber = drawingNumber.value
        stateObj.itemCode = itemCode.value
      } else if (FITTING_COMPONENTS.includes(componentLower)) {
        fittingsData.value = { fittings: fittingsData.value }
      } else if (FASTENER_COMPONENTS.includes(componentLower)) {
        fastenerData.value = { fastener: fastenerData.value }
      } else if (DRIVE_ASSEMBLY_COMPONENTS.includes(componentLower)) {
        componentState.driveAssembly.ofnData = componentState.driveAssembly.data
      } else if (JACKET_COMPONENTS.includes(componentLower)) {
        componentState.jacket.ofnData = componentState.jacket.data
      } else if (INSULATION_COMPONENTS.includes(componentLower)) {
        componentState.insulation.ofnData = componentState.insulation.data
      }
    }

    // Get masters handler
    const getMasters = async (data) => {
      const masterInfo = {
        capacity: capacity.value,
        model: model.value,
        reactor: reactor.value,
        modelId: modelId.value,
        reactorId: reactorId.value
      }

      try {
        const response = await axios.post(
          `${host.value}/api/v1/getmasters`,
          JSON.stringify({ model_info: masterInfo, masters: data }),
          { headers: { 'Content-Type': 'application/json' } }
        )

        if (response?.data) {
          const masterComp = response.data.master_details.masters.component
          const mastersData = response.data.master_details.masters

          const mastersMap = {
            baffle: () => { baffleMasters.value = mastersData },
            thermowell: () => { thermowellMasters.value = mastersData },
            jacket: () => { jacketMasters.value = mastersData },
            shftclosure: () => { shaftclosureMasters.value = mastersData },
            thermosyphone: () => { thermosyphoneMasters.value = mastersData },
            gearbox: () => { gearboxMasters.value = mastersData },
            motor: () => { motorMasters.value = mastersData },
            manholecclamp: () => { manholeCClampMasters.value = mastersData },
            bfcclamp: () => { bfCClampMasters.value = mastersData },
            bov: () => { bovMasters.value = mastersData }
          }

          if (mastersMap[masterComp]) mastersMap[masterComp]()
        }
      } catch (error) {
        console.error('Error:', error)
      }
    }

    // Special save handlers
    const saveBaffleData = (data) => {
      const baseInfo = {
        capacity: capacity.value,
        model: model.value,
        reactor: reactor.value,
        glass: glass.value,
        ndt: ndt.value,
        designPressure: designPressure.value,
        designTemperature: designTemperature.value
      }

      data.one.model_info = { ...baseInfo, drawingNumber: data.one.drawingNumberOne, itemCode: data.one.itemCodeOne }
      data.two.model_info = { ...baseInfo, drawingNumber: data.two.drawingNumberTwo, itemCode: data.two.itemCodeTwo }

      saveToJsonFile('baffle', data)
      componentState.baffle.data = data
    }

    const saveThermowellData = (data) => {
      const baseInfo = {
        capacity: capacity.value,
        model: model.value,
        reactor: reactor.value,
        glass: glass.value,
        ndt: ndt.value,
        designPressure: designPressure.value,
        designTemperature: designTemperature.value
      }

      data.one.model_info = { ...baseInfo, drawingNumber: data.one.drawingNumberOne, itemCode: data.one.itemCodeOne }
      data.two.model_info = { ...baseInfo, drawingNumber: data.two.drawingNumberTwo, itemCode: data.two.itemCodeTwo }

      saveToJsonFile('thermowell', data)
      componentState.thermowell.data = data
    }

    const saveSensorData = (data) => {
      data.model_info = {
        capacity: capacity.value,
        model: model.value,
        reactor: reactor.value,
        glass: glass.value,
        ndt: ndt.value,
        designPressure: designPressure.value,
        designTemperature: designTemperature.value
      }
      saveToJsonFile('sensor', data)
      componentState.sensor.data = data
    }

    const saveInsulationData = (data) => {
      data.model_info = {
        capacity: capacity.value,
        model: model.value,
        reactor: reactor.value,
        glass: glass.value,
        ndt: ndt.value,
        designPressure: designPressure.value,
        designTemperature: designTemperature.value
      }
      saveToJsonFile('insulation', data)
      componentState.insulation.data = data
    }

    const saveDriveAssemblyData = (data) => {
      data.model_info = {
        capacity: capacity.value,
        model: model.value,
        reactor: reactor.value,
        glass: glass.value,
        ndt: ndt.value,
        designPressure: designPressure.value,
        designTemperature: designTemperature.value
      }
      saveToJsonFile('driveAssembly', data)
      componentState.driveAssembly.data = data
    }

    const saveJacket = (data) => {
      data.model_info = {
        capacity: capacity.value,
        model: model.value,
        reactor: reactor.value,
        glass: glass.value,
        ndt: ndt.value,
        designPressure: designPressure.value,
        designTemperature: designTemperature.value
      }
      saveToJsonFile('jacket', data)
      componentState.jacket.data = data
    }

    const saveAirVent = (data) => {
      data.model_info = {
        capacity: capacity.value,
        model: model.value,
        reactor: reactor.value,
        glass: glass.value,
        ndt: ndt.value,
        designPressure: designPressure.value,
        designTemperature: designTemperature.value
      }
      saveToJsonFile('airVentCouplingPlug', data)
      componentState.airVentCouplingPlug.data = data
    }

    return {
      // Component state
      componentState,
      comp,
      components,
      componentsArray,
      tab,
      splitterModel,
      visibleGenerateButton,

      // OFN Details
      sonoRef,
      sono,
      sfon,
      capacity,
      modelId,
      reactor,
      reactorId,
      model,
      glass,
      ndt,
      designTemperature,
      designPressure,

      // Dialog state
      isSalesOrderNumberNull,
      isItemCodeNull,
      drawingNumber,
      itemCode,

      // Shared data
      fittingsData,
      fastenerData,

      // Masters
      jacketMasters,
      baffleMasters,
      thermowellMasters,
      shaftclosureMasters,
      thermosyphoneMasters,
      gearboxMasters,
      motorMasters,
      manholeCClampMasters,
      bfCClampMasters,
      bovMasters,

      // Methods
      prompt,
      showTab,
      onUpdateTab,
      onUpdateModelType,
      saveToJsonFile,
      generateModel,
      searchData,
      saveData,
      getMasters,
      saveBaffleData,
      saveThermowellData,
      saveSensorData,
      saveInsulationData,
      saveDriveAssemblyData,
      saveJacket,
      saveAirVent
    }
  }
}
</script>

<style lang="css">
.bg-white {
  background: hsl(0, 0%, 100%) !important;
}
</style>
