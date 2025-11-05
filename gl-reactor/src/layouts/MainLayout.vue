<template>
  <div>
    <q-layout view="hHh Lpr lff">
      <q-header elevated>
        <q-toolbar class="bg-white">
          <!-- <q-btn flat @click="drawer = !drawer" round dense icon="menu" /> -->
           <img src="https://intranet.gmmpfaudler.com/img/logos/Logo.png" style="height: 50px; padding: 5px 0px;">
          <q-avatar square >
          </q-avatar>
          <q-toolbar-title class="text-dark text-center"><strong>Glass Lined 3D Model Generation</strong> </q-toolbar-title>
        </q-toolbar>
      </q-header>

      <!-- <q-drawer
        v-model="drawer"
        show-if-above
        :width="200"
        :breakpoint="500"
        bordered
        :class="$q.dark.isActive ? 'bg-white' : 'bg-grey-3'"
      >
        <q-scroll-area class="fit">
          <q-list>

            <template v-for="(menuItem, index) in menuList" :key="index">
              <q-item clickable :active="menuItem.label === 'Outbox'" v-ripple @click="prompt(menuItem.label)">
                <q-item-section avatar>
                  <q-icon :name="menuItem.icon" />
                </q-item-section>
                <q-item-section>
                  {{ menuItem.label }}
                </q-item-section>
              </q-item>
              <q-separator :key="'sep' + index"  v-if="menuItem.separator" />
            </template>

          </q-list>
        </q-scroll-area>
      </q-drawer> -->

      <q-page-container v-if="true" style="padding: 70px 0px 0px 0px; ">
        <q-page padding style="display: flex; flex-direction: column;">
          <div class="q-gutter-md" style="padding-bottom: 5px; display: flex; justify-content: space-evenly;">
            <div class="item-center">
              <q-btn @click="prompt('Dashboard')" outline color="primary" dense label="Get OFN" />
            </div>
            <div class="row items-center q-gutter-sm">
              <!-- <q-chip square outline text-color="black">
                Sales Order Number
              </q-chip> -->
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
              <q-chip square outline text-color="black">
                Technical Specification Number
              </q-chip>
              <q-chip outline square color="blue-5" text-color="white">
                {{ sfon }}
                <q-tooltip>{{ sfon }}</q-tooltip>
              </q-chip>
            </div>
            <div class="column">
              <q-chip square outline text-color="black">
                Capacity
              </q-chip>
              <q-chip outline square color="blue-5" text-color="white">
                {{ capacity }}
                <q-tooltip>{{ capacity }}</q-tooltip>
              </q-chip>
            </div>
            <div class="column">
              <q-chip square outline text-color="black">
                Model
              </q-chip>
              <q-chip outline square color="blue-5" text-color="white">
                {{ model }}
                <q-tooltip>{{ model }}</q-tooltip>
              </q-chip>
            </div>
            <div class="column">
              <q-chip square outline text-color="black">
                Reactor
              </q-chip>
              <q-chip outline square color="blue-5" text-color="white">
                {{ reactor }}
                <q-tooltip>{{ reactor }}</q-tooltip>
              </q-chip>
            </div>
            <div class="column">
              <q-chip square outline text-color="black">
                Glass
              </q-chip>
              <q-chip outline square color="blue-5" text-color="white">
                {{ glass }}
                <q-tooltip>{{ glass }}</q-tooltip>
              </q-chip>
            </div>
            <div class="column">
              <q-chip square outline text-color="black">
                NDT
              </q-chip>
              <q-chip outline square color="blue-5" text-color="white">
                {{ ndt }}
                <q-tooltip>{{ ndt }}</q-tooltip>
              </q-chip>
            </div>
            <div class="column">
              <q-chip square outline text-color="black">
                Temperature
              </q-chip>
              <q-chip outline square color="blue-5" text-color="white">
                {{ designTemperature }}
                <q-tooltip>{{ designPressure }}</q-tooltip>
              </q-chip>
            </div>
            <div class="column">
              <q-chip square outline text-color="black">
                Pressure
              </q-chip>
              <q-chip outline square color="blue-5" text-color="white">
                {{ designPressure }}
                <q-tooltip>{{ designPressure }}</q-tooltip>
              </q-chip>
            </div>
            <div 
            v-if="visibleGenerateButton = true"
            class="row items-center q-gutter-sm">
              <q-btn @click="generateModel" outline color="green" dense label="Generate Model" />
            </div>
          </div>
          <q-separator color="blue" inset />
          <div style="padding-top: 5px;">
            <q-splitter
              v-model="splitterModel"
            >
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
                        v-if = "showTab(comp.name)"
                        :name="comp.name"
                        :label="comp.label"
                        :class="'text-'+comp.color"
                      >
                      </q-tab>
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
                    <q-tab-panel name="agitator">
                      <!-- Agitator -->
                      <div>
                        <div class="row">
                          <q-chip size="xl" outline square color="blue-5" text-color="white" style="padding-right: 50px;">
                            {{ "Agitator" }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="agitatorDrawingNumber !== null" outline square color="blue-5" text-color="white">
                            {{ "Drawing Number: " + agitatorDrawingNumber }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="agitatorItemCode !== null" outline square color="blue-5" text-color="white">
                            {{ "Item Code: " + agitatorItemCode }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="agitatorItemCode !== null" icon="check" square color="green-5" text-color="white" clickable @click="saveToJsonFile(tab, agitatorData)">
                            {{ "Save To File "}}
                          </q-chip>
                          <!-- <q-space/>
                          <q-chip icon="file_open" square color="blue-5" text-color="white" clickable @click="openInInventor(tab)">
                            {{ "Open"}}
                          </q-chip> -->
                        </div>
                        <AgitatorComponent
                          :agitator="agitatorOfnData"
                          @search-data="searchData"
                        />
                      </div>
                    </q-tab-panel>
                    <q-tab-panel name="monoblock">
                      <!-- Monoblock -->
                      <div>
                        <div class="row">
                          <q-chip size="xl" outline square color="blue-5" text-color="white" style="padding-right: 50px;">
                            {{ "Monoblock" }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="monoblockDrawingNumber !== null" outline square color="blue-5" text-color="white">
                            {{ "Drawing Number: " + monoblockDrawingNumber }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="monoblockItemCode !== null" outline square color="blue-5" text-color="white">
                            {{ "Item Code: " + monoblockItemCode }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="monoblockItemCode !== null" icon="check" square color="green-5" text-color="white" clickable @click="saveToJsonFile(tab, monoblockData)">
                            {{ "Save To File"}}
                          </q-chip>
                          <!-- <q-space/>
                           <q-chip icon="file_open" square color="blue-5" text-color="white" clickable @click="openInInventor(tab)">
                            {{ "Open"}}
                          </q-chip> -->
                        </div>
                        <MonoblockComponent
                        :monoblock="monoblockOfnData"
                        :fittingsData="fittingsData"
                        :fastenerData="fastenerData"
                        :bovMasters="bovMasters"
                        @get-bov-masters="getMasters"
                        @search-data="searchData"
                        />
                      </div>
                    </q-tab-panel>
                    <q-tab-panel name="topCover">
                      <!-- Top Cover -->
                      <div>
                        <div class="row">
                          <q-chip size="xl" outline square color="blue-5" text-color="white" style="padding-right: 50px;">
                            {{ "Top Cover" }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="topCoverDrawingNumber !== null" outline square color="blue-5" text-color="white">
                            {{ "Drawing Number: " + topCoverDrawingNumber }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="topCoverItemCode !== null" outline square color="blue-5" text-color="white">
                            {{ "Item Code: " + topCoverItemCode }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="topCoverItemCode !== null" icon="check" square color="green-5" text-color="white" clickable @click="saveToJsonFile(tab, topCoverData)">
                            {{ "Save To File "}}
                          </q-chip>
                        </div>
                        <TopCoverComponent
                        :topcover="topCoverOfnData"
                        :fittingsData="fittingsData"
                        :bovMasters="bovMasters"
                        @get-bov-masters="getMasters"
                        @search-data="searchData"
                        />
                      </div>
                    </q-tab-panel>
                    <q-tab-panel name="pan">
                      <!-- Pan -->
                      <div>
                        <div class="row">
                          <q-chip size="xl" outline square color="blue-5" text-color="white" style="padding-right: 50px;">
                            {{ "Pan" }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="panDrawingNumber !== null" outline square color="blue-5" text-color="white">
                            {{ "Drawing Number: " + panDrawingNumber }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="panItemCode !== null" outline square color="blue-5" text-color="white">
                            {{ "Item Code: " + panItemCode }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="panItemCode !== null" icon="check" square color="green-5" text-color="white" clickable @click="saveToJsonFile(tab, panData)">
                            {{ "Save To File "}}
                          </q-chip>
                        </div>
                        <PanComponent
                        :pan="panOfnData"
                        :fittingsData="fittingsData"
                        :bovMasters="bovMasters"
                        @get-bov-masters="getMasters"
                        @search-data="searchData"
                        />
                      </div>
                    </q-tab-panel>
                    <q-tab-panel name="jacket">
                      <!-- Jacket -->
                      <div>
                        <div class="row">
                          <q-chip size="xl" outline square color="blue-5" text-color="white" style="padding-right: 50px;">
                            {{ "Jacket" }}
                          </q-chip>
                          <!-- <q-space/>
                          <q-chip v-if="jacketDrawingNumber !== null" outline square color="blue-5" text-color="white">
                            {{ "Drawing Number: " + jacketDrawingNumber }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="jacketItemCode !== null" outline square color="blue-5" text-color="white">
                            {{ "Item Code: " + jacketItemCode }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="jacketItemCode !== null" icon="check" square color="green-5" text-color="white" clickable @click="saveToJsonFile(tab, jacketData)">
                            {{ "Save To File "}}
                          </q-chip> -->
                        </div>
                        <JacketComponent
                        :jacket="jacketOfnData"
                        :jacketMasters="jacketMasters"
                        @search-data="searchData"
                        @get-jacket-masters="getMasters"
                        @save-jacket="saveJacket"
                        />
                      </div>
                    </q-tab-panel>
                    <q-tab-panel name="diaphragmRing">
                      <!-- Diaphragm Ring -->
                      <div>
                        <div class="row">
                          <q-chip size="xl" outline square color="blue-5" text-color="white" style="padding-right: 50px;">
                            {{ "Diaphragm Ring" }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="ringDrawingNumber !== null" outline square color="blue-5" text-color="white">
                            {{ "Drawing Number: " + ringDrawingNumber }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="ringItemCode !== null" outline square color="blue-5" text-color="white">
                            {{ "Item Code: " + ringItemCode }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="ringItemCode !== null" icon="check" square color="green-5" text-color="white" clickable @click="saveToJsonFile(tab, ringData)">
                            {{ "Save To File "}}
                          </q-chip>
                        </div>
                        <DiaphragmRingComponent
                        :diaphragmRing="ringOfnData"
                        @search-data="searchData"
                        />
                      </div>
                    </q-tab-panel>
                    <q-tab-panel name="manholeCover">
                      <!-- Manhole Cover -->
                      <div>
                        <div class="row">
                          <q-chip size="xl" outline square color="blue-5" text-color="white" style="padding-right: 50px;">
                            {{ "Manhole Cover" }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="manholeCoverDrawingNumber !== null" outline square color="blue-5" text-color="white">
                            {{ "Drawing Number: " + manholeCoverDrawingNumber }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="manholeCoverItemCode !== null" outline square color="blue-5" text-color="white">
                            {{ "Item Code: " + manholeCoverItemCode }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="manholeCoverItemCode !== null" icon="check" square color="green-5" text-color="white" clickable @click="saveToJsonFile(tab, manholeCoverData)">
                            {{ "Save To File "}}
                          </q-chip>
                        </div>
                        <ManholeCoverComponent
                        :manholeCover="manholeCoverOfnData"
                        @search-data="searchData"
                        />
                      </div>
                    </q-tab-panel>
                    <q-tab-panel name="protectingRing">
                      <!-- Protection Ring -->
                      <div>
                        <div class="row">
                          <q-chip size="xl" outline square color="blue-5" text-color="white" style="padding-right: 50px;">
                            {{ "Protection Ring" }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="protectionRingDrawingNumber !== null" outline square color="blue-5" text-color="white">
                            {{ "Drawing Number: " + protectionRingDrawingNumber }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="protectionRingItemCode !== null" outline square color="blue-5" text-color="white">
                            {{ "Item Code: " + protectionRingItemCode }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="protectionRingItemCode !== null" icon="check" square color="green-5" text-color="white" clickable @click="saveToJsonFile(tab, protectionRingData)">
                            {{ "Save To File "}}
                          </q-chip>
                        </div>
                        <ProtectionRingComponent
                        :protectionRing="protectionRingOfnData"
                        @search-data="searchData"
                        />
                      </div>
                    </q-tab-panel>
                    <q-tab-panel name="springBalanceAssembly">
                      <!-- Spring Balance Assembly -->
                      <div>
                        <div class="row">
                          <q-chip size="xl" outline square color="blue-5" text-color="white" style="padding-right: 50px;">
                            {{ "Spring Balance Assembly" }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="springbalanceassemblyDrawingNumber !== null" outline square color="blue-5" text-color="white">
                            {{ "Drawing Number: " + springbalanceassemblyDrawingNumber }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="springbalanceassemblyItemCode !== null" outline square color="blue-5" text-color="white">
                            {{ "Item Code: " + springbalanceassemblyItemCode }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="springbalanceassemblyItemCode !== null" icon="check" square color="green-5" text-color="white" clickable @click="saveToJsonFile(tab, springbalanceassemblyData)">
                            {{ "Save To File "}}
                          </q-chip>
                        </div>
                        <SpringBalanceAssemblyComponent
                        :springbalanceassembly="springbalanceassemblyOfnData"
                        @search-data="searchData"
                        />
                      </div>
                    </q-tab-panel>
                    <q-tab-panel name="MHCClamp">
                      <!-- Manhole C Clamp -->
                      <div>
                        <div class="row">
                          <q-chip size="xl" outline square color="blue-5" text-color="white" style="padding-right: 50px;">
                            {{ "Manhole C Clamp" }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="manholeCClampDrawingNumber !== null" outline square color="blue-5" text-color="white">
                            {{ "Drawing Number: " + manholeCClampDrawingNumber }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="manholeCClampItemCode !== null" outline square color="blue-5" text-color="white">
                            {{ "Item Code: " + manholeCClampItemCode }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="manholeCClampItemCode !== null" icon="check" square color="green-5" text-color="white" clickable @click="saveToJsonFile(tab, manholeCClampData)">
                            {{ "Save To File "}}
                          </q-chip>
                        </div>
                        <ManholeCClampComponent
                        :manholeCClamp="manholeCClampOfnData"
                        :manholeCClampMasters="manholeCClampMasters"
                        @get-mh-masters="getMasters"
                        @search-data="searchData"
                        />
                      </div>
                    </q-tab-panel>
                    <q-tab-panel name="coc">
                      <!-- COC -->
                      <div>
                        <div class="row">
                          <q-chip size="xl" outline square color="blue-5" text-color="white" style="padding-right: 50px;">
                            {{ "COC" }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="cocDrawingNumber !== null" outline square color="blue-5" text-color="white">
                            {{ "Drawing Number: " + cocDrawingNumber }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="cocItemCode !== null" outline square color="blue-5" text-color="white">
                            {{ "Item Code: " + cocItemCode }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="cocItemCode !== null" icon="check" square color="green-5" text-color="white" clickable @click="saveToJsonFile(tab, cocData)">
                            {{ "Save To File "}}
                          </q-chip>
                        </div>
                        <CocComponent
                        :coc="cocOfnData"
                        @search-data="searchData"
                        />
                      </div>
                    </q-tab-panel>
                    <q-tab-panel name="bfCClamp">
                      <!-- Body Flange C Clamp -->
                      <div>
                        <div class="row">
                          <q-chip size="xl" outline square color="blue-5" text-color="white" style="padding-right: 50px;">
                            {{ "Body Flange C-Clamp" }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="bfCClampDrawingNumber !== null" outline square color="blue-5" text-color="white">
                            {{ "Drawing Number: " + bfCClampDrawingNumber }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="bfCClampItemCode !== null" outline square color="blue-5" text-color="white">
                            {{ "Item Code: " + bfCClampItemCode }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="bfCClampItemCode !== null" icon="check" square color="green-5" text-color="white" clickable @click="saveToJsonFile(tab, bfCClampData)">
                            {{ "Save To File "}}
                          </q-chip>
                        </div>
                        <BodyFlangeCClampComponent
                        :bodyFlangeCClamp="bfCClampOfnData"
                        :bodyFlangeCClampMasters="bfCClampMasters"
                        @get-bf-masters="getMasters"
                        @search-data="searchData"
                        />
                      </div>
                    </q-tab-panel>
                    <q-tab-panel name="thermosyphone">
                      <!-- Thermosyphone -->
                      <div>
                        <div class="row">
                          <q-chip size="xl" outline square color="blue-5" text-color="white" style="padding-right: 50px;">
                            {{ "Thermosyphone" }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="thermosyphoneDrawingNumber !== null" outline square color="blue-5" text-color="white">
                            {{ "Drawing Number: " + thermosyphoneDrawingNumber }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="thermosyphoneItemCode !== null" outline square color="blue-5" text-color="white">
                            {{ "Item Code: " + thermosyphoneItemCode }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="thermosyphoneItemCode !== null" icon="check" square color="green-5" text-color="white" clickable @click="saveToJsonFile(tab, thermosyphoneData)">
                            {{ "Save To File "}}
                          </q-chip>
                        </div>
                        <ThermosyphoneComponent
                        :thermosyphone="thermosyphoneOfnData"
                        :thermosyphoneMasters="thermosyphoneMasters"
                        @search-data="searchData"
                        @get-thermosyphone-masters="getMasters"
                        />
                      </div>
                    </q-tab-panel>
                    <q-tab-panel name="gearbox">
                      <!-- Gear Box -->
                      <div>
                        <div class="row">
                          <q-chip size="xl" outline square color="blue-5" text-color="white" style="padding-right: 50px;">
                            {{ "Gear Box" }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="gearboxDrawingNumber !== null" outline square color="blue-5" text-color="white">
                            {{ "Drawing Number: " + gearboxDrawingNumber }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="gearboxItemCode !== null" outline square color="blue-5" text-color="white">
                            {{ "Item Code: " + gearboxItemCode }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="gearboxItemCode !== null" icon="check" square color="green-5" text-color="white" clickable @click="saveToJsonFile(tab, gearboxData)">
                            {{ "Save To File "}}
                          </q-chip>
                          <!-- <q-space/>
                          <q-chip icon="file_open" square color="blue-5" text-color="white" clickable @click="openInInventor(tab)">
                            {{ "Open"}}
                          </q-chip> -->
                        </div>
                        <GearBoxComponent
                        :gearbox="gearboxOfnData"
                        :gearboxMasters="gearboxMasters"
                        @search-data="searchData"
                        @get-gearbox-masters="getMasters"
                        />
                      </div>
                    </q-tab-panel>
                    <q-tab-panel name="motor">
                      <!-- Motor -->
                      <div>
                        <div class="row">
                          <q-chip size="xl" outline square color="blue-5" text-color="white" style="padding-right: 50px;">
                            {{ "Motor" }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="motorDrawingNumber !== null" outline square color="blue-5" text-color="white">
                            {{ "Drawing Number: " + motorDrawingNumber }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="motorItemCode !== null" outline square color="blue-5" text-color="white">
                            {{ "Item Code: " + motorItemCode }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="motorItemCode !== null" icon="check" square color="green-5" text-color="white" clickable @click="saveToJsonFile(tab, motorData)">
                            {{ "Save To File "}}
                          </q-chip>
                        </div>
                        <MotorComponent
                        :motor="motorOfnData"
                        :motorMasters="motorMasters"
                        @search-data="searchData"
                        @get-motor-masters="getMasters"
                        />
                      </div>
                    </q-tab-panel>
                    <q-tab-panel name="driveAssembly">
                      <!-- Drive Assembly -->
                      <div>
                        <div class="row">
                          <q-chip size="xl" outline square color="blue-5" text-color="white" style="padding-right: 50px;">
                            {{ "Drive Assembly" }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="driveAssemblyDrawingNumber !== null" outline square color="blue-5" text-color="white">
                            {{ "Drawing Number: " + driveAssemblyDrawingNumber }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="driveAssemblyItemCode !== null" outline square color="blue-5" text-color="white">
                            {{ "Item Code: " + driveAssemblyItemCode }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="driveAssemblyItemCode !== null" icon="check" square color="green-5" text-color="white" clickable @click="saveToJsonFile(tab, driveAssemblyData)">
                            {{ "Save To File "}}
                          </q-chip>
                        </div>
                        <DriveAssemblyComponent
                        :driveAssembly="driveAssemblyOfnData"
                        @search-data="searchData"
                        @save-drive-assembly-data="saveDriveAssemblyData"
                        />
                      </div>
                    </q-tab-panel>
                    <q-tab-panel name="bov">
                      <!-- Bottom Outlet Valve -->
                      <div>
                        <div class="row">
                          <q-chip size="xl" outline square color="blue-5" text-color="white" style="padding-right: 50px;">
                            {{ "Bottom Outlet Valve" }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="bovDrawingNumber !== null" outline square color="blue-5" text-color="white">
                            {{ "Drawing Number: " + bovDrawingNumber }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="bovItemCode !== null" outline square color="blue-5" text-color="white">
                            {{ "Item Code: " + bovItemCode }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="bovItemCode !== null" icon="check" square color="green-5" text-color="white" clickable @click="saveToJsonFile(tab, bovData)">
                            {{ "Save To File "}}
                          </q-chip>
                        </div>
                        <BottomOutletValveComponent
                        :bov="bovOfnData"
                        :bovMasters="bovMasters"
                        @get-bov-masters="getMasters"
                        @search-data="searchData"
                        />
                      </div>
                    </q-tab-panel>
                    <q-tab-panel name="namePlateBracket">
                      <!-- Name Plate Bracket -->
                      <div>
                        <div class="row">
                          <q-chip size="xl" outline square color="blue-5" text-color="white" style="padding-right: 50px;">
                            {{ "Name Plate Bracket" }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="npbDrawingNumber !== null" outline square color="blue-5" text-color="white">
                            {{ "Drawing Number: " + npbDrawingNumber }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="npbItemCode !== null" outline square color="blue-5" text-color="white">
                            {{ "Item Code: " + npbItemCode }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="npbItemCode !== null" icon="check" square color="green-5" text-color="white" clickable @click="saveToJsonFile(tab, npbData)">
                            {{ "Save To File "}}
                          </q-chip>
                        </div>
                        <NamePlateBracketComponent
                        :npb="npbOfnData"
                        @search-data="searchData"
                        />
                      </div>
                    </q-tab-panel>
                    <q-tab-panel name="driveHood">
                      <!-- Drive Hood -->
                      <div>
                        <div class="row">
                          <q-chip size="xl" outline square color="blue-5" text-color="white" style="padding-right: 50px;">
                            {{ "Drive Hood" }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="driveHoodDrawingNumber !== null" outline square color="blue-5" text-color="white">
                            {{ "Drawing Number: " + driveHoodDrawingNumber }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="driveHoodItemCode !== null" outline square color="blue-5" text-color="white">
                            {{ "Item Code: " + driveHoodItemCode }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="driveHoodItemCode !== null" icon="check" square color="green-5" text-color="white" clickable @click="saveToJsonFile(tab, driveHoodData)">
                            {{ "Save To File "}}
                          </q-chip>
                        </div>
                        <DriveHoodComponent
                        :driveHood="driveHoodOfnData"
                        @search-data="searchData"
                        />
                      </div>
                    </q-tab-panel>
                    <q-tab-panel name="airVentCouplingPlug">
                      <!-- Air Vent Coupling Plug -->
                      <div>
                        <div class="row">
                          <q-chip size="xl" outline square color="blue-5" text-color="white" style="padding-right: 50px;">
                            {{ "Air-Vent Coupling Plug" }}
                          </q-chip>
                          <!-- <q-space/>
                          <q-chip v-if="avcpDrawingNumber !== null" outline square color="blue-5" text-color="white">
                            {{ "Drawing Number: " + avcpDrawingNumber }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="avcpItemCode !== null" outline square color="blue-5" text-color="white">
                            {{ "Item Code: " + avcpItemCode }}
                          </q-chip> -->
                          <!-- <q-space/>
                          <q-chip v-if="avcpItemCode !== null" icon="check" square color="green-5" text-color="white" clickable @click="saveToJsonFile(tab, avcpData)">
                            {{ "Save To File "}}
                          </q-chip> -->
                        </div>
                        <AirVentCouplingPlugComponent
                        :avcp="avcpOfnData"
                        @save-airvent="saveAirVent"
                        @search-data="searchData"
                        />
                      </div>
                    </q-tab-panel>
                    <q-tab-panel name="insulation">
                      <!-- Insulation -->
                      <div>
                        <div class="row">
                          <q-chip size="xl" outline square color="blue-5" text-color="white" style="padding-right: 50px;">
                            {{ "Insulation" }}
                          </q-chip>
                          <q-space/>
                          <!-- <q-chip v-if="insulationDrawingNumber !== null" outline square color="blue-5" text-color="white">
                            {{ "Drawing Number: " + insulationDrawingNumber }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="avcpItemCode !== null" outline square color="blue-5" text-color="white">
                            {{ "Item Code: " + avcpItemCode }}
                          </q-chip> -->
                          <!-- <q-space/> -->
                          <!-- <q-chip v-if="avcpItemCode !== null" icon="check" square color="green-5" text-color="white" clickable @click="saveToJsonFile(tab, insulationData)">
                            {{ "Save To File "}}
                          </q-chip> -->
                        </div>
                        <InsulationComponent
                        :insulation="insulationOfnData"
                        @search-data="searchData"
                        @save-insulation-data="saveInsulationData"
                        />
                      </div>
                    </q-tab-panel>
                    <q-tab-panel name="baffle">
                      <!-- Baffle -->
                      <div>
                        <div class="row">
                          <q-chip size="xl" outline square color="blue-5" text-color="white" style="padding-right: 50px;">
                            {{ "Baffle" }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="baffleDrawingNumber !== null" outline square color="blue-5" text-color="white">
                            {{ "Drawing Number: " + baffleDrawingNumber }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="baffleItemCode !== null" outline square color="blue-5" text-color="white">
                            {{ "Item Code: " + baffleItemCode }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="baffleItemCode !== null" icon="check" square color="green-5" text-color="white" clickable @click="saveToJsonFile(tab, baffleData)">
                            {{ "Save To File "}}
                          </q-chip>
                        </div>
                        <BaffleComponent
                        :baffle="baffleOfnData"
                        :baffleMasters="baffleMasters"
                        @search-data="searchData"
                        @get-baffle-masters="getMasters"
                        @save-baffle="saveBaffleData"
                        />
                      </div>
                    </q-tab-panel>
                    <q-tab-panel name="thermowell">
                      <!-- Thermowell -->
                      <div>
                        <div class="row">
                          <q-chip size="xl" outline square color="blue-5" text-color="white" style="padding-right: 50px;">
                            {{ "Thermowell" }}
                          </q-chip>
                          <q-space/>
                          <!-- <q-chip v-if="thermowellDrawingNumber !== null" outline square color="blue-5" text-color="white">
                            {{ "Drawing Number: " + thermowellDrawingNumber }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="thermowellItemCode !== null" outline square color="blue-5" text-color="white">
                            {{ "Item Code: " + thermowellItemCode }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="thermowellItemCode !== null" icon="check" square color="green-5" text-color="white" clickable @click="saveToJsonFile(tab, thermowellData)">
                            {{ "Save To File "}}
                          </q-chip> -->
                        </div>
                        <ThermowellComponent
                        :thermowell="thermowellOfnData"
                        :thermowellMasters="thermowellMasters"
                        @search-data="searchData"
                        @get-thermowell-masters="getMasters"
                        @save-thermowell="saveThermowellData"
                        />
                      </div>
                    </q-tab-panel>
                    <q-tab-panel name="sensor">
                      <!-- Sensor -->
                      <div>
                        <div class="row">
                          <q-chip size="xl" outline square color="blue-5" text-color="white" style="padding-right: 50px;">
                            {{ "Sensor" }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="sensorDrawingNumber !== null" outline square color="blue-5" text-color="white">
                            {{ "Drawing Number: " + sensorDrawingNumber }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="sensorItemCode !== null" outline square color="blue-5" text-color="white">
                            {{ "Item Code: " + sensorItemCode }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="sensorItemCode !== null" icon="check" square color="green-5" text-color="white" clickable @click="saveToJsonFile(tab, sensorData)">
                            {{ "Save To File "}}
                          </q-chip>
                        </div>
                        <SensorComponent
                        :sensor="sensorOfnData"
                        @search-data="searchData"
                        @save-sensor="saveSensorData"
                        />
                      </div>
                    </q-tab-panel>
                    <q-tab-panel name="shaftclosure">
                      <!-- Shaft Closure = Mechanical Seal -->
                      <div>
                        <div class="row">
                          <q-chip size="xl" outline square color="blue-5" text-color="white" style="padding-right: 50px;">
                            {{ "Shaft Closure" }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="shaftclosureDrawingNumber !== null" outline square color="blue-5" text-color="white">
                            {{ "Drawing Number: " + shaftclosureDrawingNumber }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="shaftclosureItemCode !== null" outline square color="blue-5" text-color="white">
                            {{ "Item Code: " + shaftclosureItemCode }}
                          </q-chip>
                          <q-space/>
                          <q-chip v-if="shaftclosureItemCode !== null" icon="check" square color="green-5" text-color="white" clickable @click="saveToJsonFile(tab, shaftclosureData)">
                            {{ "Save To File "}}
                          </q-chip>
                        </div>
                        <ShaftClosureComponent
                        :shaftclosure="shaftclosureOfnData"
                        :shaftclosureMasters="shaftclosureMasters"
                        @search-data="searchData"
                        @get-shaftclosure-masters="getMasters"
                        />
                      </div>
                    </q-tab-panel>
                  </q-tab-panels>
                </keep-alive>
              </template>
            </q-splitter>
          </div>
        </q-page>
      </q-page-container>
    </q-layout>
  </div>
  <div class="q-pa-md q-gutter-sm">
    <!-- drawing No. -->
    <q-dialog v-model="isItemCodeNull" persistent>
      <q-card class="q-pa-md" style="min-width: 420px; max-width: 95vw; border-radius: 12px;">
        
        <!-- Header -->
        <q-bar class="bg-primary text-white" style="border-top-left-radius: 12px; border-top-right-radius: 12px;">
          <div class="text-h6">Missing Item Code</div>
          <q-space />
          <q-btn dense flat icon="close" v-close-popup>
            <q-tooltip>Close</q-tooltip>
          </q-btn>
        </q-bar>

        <!-- Info Text -->
        <q-card-section class="q-pt-md q-pb-none">
          <div class="text-subtitle2">
            Item code for <strong>{{ comp }}</strong> was not found.<br>
            Please provide the required details below.
          </div>
        </q-card-section>

        <!-- Inputs -->
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

            <!-- Buttons -->
            <div class="row justify-end q-gutter-sm q-mt-md">
              <q-btn flat label="Cancel" color="grey-7" v-close-popup />
              <q-btn unelevated label="Save" color="primary" @click="saveData" v-close-popup />
            </div>
          </q-form>
        </q-card-section>

      </q-card>
    </q-dialog>

    <!-- General -->
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

import { ref } from 'vue'
import axios from 'axios'
import { useQuasar ,Notify} from 'quasar';
import AgitatorComponent from 'components/AgitatorComponent.vue'
import MonoblockComponent from 'components/MonoblockComponent.vue'
import JacketComponent from 'components/JacketComponent.vue'
import DriveAssemblyComponent from 'components/DriveAssemblyComponent.vue'
import BaffleComponent from 'components/BaffleComponent.vue'
import SensorComponent from 'src/components/SensorComponent.vue'
import ShaftClosureComponent from 'src/components/ShaftClosureComponent.vue'
import ThermosyphoneComponent from 'src/components/ThermosyphoneComponent.vue'
import GearBoxComponent from 'src/components/GearBoxComponent.vue'
import MotorComponent from 'src/components/MotorComponent.vue';
import DiaphragmRingComponent from 'src/components/DiaphragmRingComponent.vue';
import ManholeCoverComponent from 'src/components/ManholeCoverComponent.vue';
import ProtectionRingComponent from 'src/components/ProtectionRingComponent.vue';
import SpringBalanceAssemblyComponent from 'src/components/SpringBalanceAssemblyComponent.vue';
import ManholeCClampComponent from 'src/components/ManholeCClampComponent.vue';
import CocComponent from 'src/components/CocComponent.vue';
import BodyFlangeCClampComponent from 'src/components/BodyFlangeCClampComponent.vue';
import BottomOutletValveComponent from 'src/components/BottomOutletValveComponent.vue';
import NamePlateBracketComponent from 'src/components/NamePlateBracketComponent.vue';
import AirVentCouplingPlugComponent from 'src/components/AirVentCouplingPlugComponent.vue';
import InsulationComponent from 'src/components/InsulationComponent.vue';
import DriveHoodComponent from 'src/components/DriveHoodComponent.vue';
import ThermowellComponent from 'src/components/ThermowellComponent.vue';
import PanComponent from 'src/components/PanComponent.vue';
import TopCoverComponent from 'src/components/TopCoverComponent.vue';
export default {
    components: {
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
  setup () {
    const $q = useQuasar();
    const menuList = [
    {
      icon: 'dashboard',
      label: 'Dashboard',
      separator: true
    },
    {
      icon: 'send',
      label: 'Outbox',
      separator: false
    },
    {
      icon: 'delete',
      label: 'Trash',
      separator: false
    },
    {
      icon: 'error',
      label: 'Spam',
      separator: true
    },
    {
      icon: 'settings',
      label: 'Settings',
      separator: false
    },
    {
      icon: 'feedback',
      label: 'Send Feedback',
      separator: false
    },
    {
      icon: 'help',
      iconColor: 'primary',
      label: 'Help',
      separator: false
    }
  ]
  const comp = ref(null)
  const components = ref([])
  const componentsArray = ref([
    {
      icon: 'error_outline',
      label: 'Pan',
      name: 'pan',
      color: 'orange',
      saved: false
    },
    {
      icon: 'error_outline',
      label: 'Top Cover',
      name: 'topCover',
      color: 'orange',
      saved: false
    },
    {
      icon: 'error_outline',
      label: 'Monoblock',
      name: 'monoblock',
      color: 'orange',
      saved: false
    },
    {
      icon: 'error_outline',
      label: 'Jacket',
      name: 'jacket',
      color: 'orange',
      saved: false
    },
    {
      icon: 'error_outline',
      label: 'Diaphragm Ring',
      name: 'diaphragmRing',
      color: 'orange',
      saved: false
    },
    // {
    //   icon: 'error_outline',
    //   label: 'Manhole Cover',
    //   name: 'manholeCover',
    //   color: 'orange',
      // saved: false
    // },
    // {
    //   icon: 'error_outline',
    //   label: 'Protecting Ring',
    //   name: 'protectingRing',
    //   color: 'orange',
      // saved: false
    // },
    {
      icon: 'error_outline',
      label: 'Spring Balance Assembly',
      name: 'springBalanceAssembly',
      color: 'orange',
      saved: false
    },
    {
      icon: 'error_outline',
      label: 'Manhole C-Clamp',
      name: 'MHCClamp',
      color: 'orange',
      saved: false
    },
    {
      icon: 'error_outline',
      label: 'COC',
      name: 'coc',
      color: 'orange',
      saved: false
    },
    {
      icon: 'error_outline',
      label: 'Body Flange C-Clamp',
      name: 'bfCClamp',
      color: 'orange',
      saved: false
    },
    // {
    //   icon: 'error_outline',
    //   label: 'Baffle',
    //   name: 'baffle',
    //   color: 'orange',
      // saved: false
    // },
    {
      icon: 'error_outline',
      label: 'Thermowell',
      name: 'thermowell',
      color: 'orange',
      saved: false
    },
    {
      icon: 'error_outline',
      label: 'Sensor',
      name: 'sensor',
      color: 'orange',
      saved: false
    },
    {
      icon: 'error_outline',
      label: 'Agitator',
      name: 'agitator',
      color: 'orange',
      saved: false
    },
    {
      icon: 'error_outline',
      label: 'Shaft Closure',
      name: 'shaftclosure',
      color: 'orange',
      saved: false
    },
    {
      icon: 'error_outline',
      label: 'Thermosyphone',
      name: 'thermosyphone',
      color: 'orange',
      saved: false
    },
    {
      icon: 'error_outline',
      label: 'Gear Box',
      name: 'gearbox',
      color: 'orange',
      saved: false
    },
    {
      icon: 'error_outline',
      label: 'Motor',
      name: 'motor',
      color: 'orange',
      saved: false
    },
    {
      icon: 'error_outline',
      label: 'Drive Assembly',
      name: 'driveAssembly',
      color: 'orange',
      saved: false
    },
    {
      icon: 'error_outline',
      label: 'Drive Hood',
      name: 'driveHood',
      color: 'orange',
      saved: false
    },
    // {
    //   icon: 'error_outline',
    //   label: 'Bottom Outlet Valve',
    //   name: 'bov',
    //   color: 'orange',
      // saved: false
    // },
    {
      icon: 'error_outline',
      label: 'Name Plate Bracket',
      name: 'namePlateBracket',
      color: 'orange',
      saved: false
    },
    {
      icon: 'error_outline',
      label: 'Air-Vent Coupling Plug',
      name: 'airVentCouplingPlug',
      color: 'orange',
      saved: false
    },
    {
      icon: 'error_outline',
      label: 'Insulation',
      name: 'insulation',
      color: 'orange',
      saved: false
    }
  ])
  const visibleGenerateButton = ref(false)
  const tab = ref(null)
  const sono = ref(null)
  const sonoRef = ref(null)
  const sfon = ref(null)
  const capacity = ref(null)
  const modelId = ref(null)
  const reactor = ref(null)
  const reactorId = ref(null)
  const model = ref(null)
  const glass = ref()
  const ndt = ref()
  const designTemperature = ref(null)
  const designPressure = ref(null)
  const sTypes = ref(['Select Model Type','Standard', 'Non-Standard'])
  const sType = ref(sTypes.value[0])
  const mTypes = ref(['Select', 'AE', 'BE', 'CE'])
  const mType = ref(mTypes.value[0])
  const host = ref("http://127.0.0.1:8000")
  const isSalesOrderNumberNull = ref(false)
  const drawingNumber = ref(null)
  const itemCode = ref(null)
  
  // Agitator
  const agitatorOfnData = ref(null)
  const agitatorData = ref(null)
  const isItemCodeNull = ref(false)
  const agitatorDrawingNumber = ref(null)
  const agitatorItemCode = ref(null)
  const agitatorSaveRef = ref(null)
  
  // Monoblock
  const monoblockOfnData = ref(null)
  const monoblockData = ref(null)
  const monoblockDrawingNumber = ref(null)
  const monoblockItemCode = ref(null)
  const fittingsData = ref(null)
  const fastenerData = ref(null)

  // Top Cover
  const topCoverOfnData = ref(null)
  const topCoverData = ref(null)
  const topCoverDrawingNumber = ref(null)
  const topCoverItemCode = ref(null)

  // Pan
  const panOfnData = ref(null)
  const panData = ref(null)
  const panDrawingNumber = ref(null)
  const panItemCode = ref(null)

  // Jacket
  const jacketOfnData = ref(null)
  const jacketData = ref(null)
  const jacketDrawingNumber = ref(null)
  const jacketItemCode = ref(null)
  const jacketMasters = ref(null)

  // Diaphragm Ring
  const ringOfnData = ref(null)
  const ringData = ref(null)
  const ringDrawingNumber = ref(null)
  const ringItemCode = ref(null)

  // Manhole Cover
  const manholeCoverOfnData = ref(null)
  const manholeCoverData = ref(null)
  const manholeCoverDrawingNumber = ref(null)
  const manholeCoverItemCode = ref(null)

  //Protection Ring
  const protectionRingOfnData = ref(null)
  const protectionRingData = ref(null)
  const protectionRingDrawingNumber = ref(null)
  const protectionRingItemCode = ref(null)

  // Spring Balance Assembly
  const springbalanceassemblyDrawingNumber = ref(null)
  const springbalanceassemblyData = ref(null)
  const springbalanceassemblyOfnData = ref(null)
  const springbalanceassemblyItemCode = ref(null)

  // Manhole C Clamp
  const manholeCClampDrawingNumber = ref(null)
  const manholeCClampData = ref(null)
  const manholeCClampOfnData = ref(null)
  const manholeCClampItemCode = ref(null)
  const manholeCClampMasters = ref(null)

  // COC
  const cocDrawingNumber = ref(null)
  const cocData = ref(null)
  const cocOfnData = ref(null)
  const cocItemCode = ref(null)

  // Body Flange C Clamp
  const bfCClampDrawingNumber = ref(null)
  const bfCClampData = ref(null)
  const bfCClampOfnData = ref(null)
  const bfCClampItemCode = ref(null)
  const bfCClampMasters = ref(null)

  // Drive Assembly
  const driveAssemblyOfnData = ref(null)
  const driveAssemblyData = ref(null)
  const driveAssemblyDrawingNumber = ref(null)
  const driveAssemblyItemCode = ref(null)

  // Bottom Outlet Valve
  const bovOfnData = ref(null)
  const bovData = ref(null)
  const bovDrawingNumber = ref(null)
  const bovItemCode = ref(null)
  const bovMasters = ref(null)

  // Name Plate Bracket
  const npbOfnData = ref(null)
  const npbData = ref(null)
  const npbDrawingNumber = ref(null)
  const npbItemCode = ref(null)

  // Drive Hood
  const driveHoodOfnData = ref(null)
  const driveHoodData = ref(null)
  const driveHoodDrawingNumber = ref(null)
  const driveHoodItemCode = ref(null)

  // Air Vent Coupling Bracket
  const avcpOfnData = ref(null)
  const avcpData = ref(null)
  const avcpDrawingNumber = ref(null)
  const avcpItemCode = ref(null)

  // Baffle
  const baffleOfnData = ref(null)
  const baffleData = ref(null)
  const baffleDrawingNumber = ref(null)
  const baffleItemCode = ref(null)
  const baffleMasters = ref(null)

  // Thermowell - For AE
  const thermowellOfnData = ref(null)
  const thermowellData = ref(null)
  const thermowellDrawingNumber = ref(null)
  const thermowellItemCode = ref(null)
  const thermowellMasters = ref(null)

  // Sensor
  const sensorOfnData = ref(null)
  const sensorData = ref(null)
  const sensorDrawingNumber = ref(null)
  const sensorItemCode = ref(null)

  // ShaftClosure = Mechanical Seal
  const shaftclosureOfnData = ref(null)
  const shaftclosureData = ref(null)
  const shaftclosureDrawingNumber = ref(null)
  const shaftclosureItemCode = ref(null)
  const shaftclosureMasters = ref(null)

  // Thermosyphone
  const isDisplayTab = ref(false)
  const thermosyphoneOfnData = ref(null)
  const thermosyphoneData = ref(null)
  const thermosyphoneDrawingNumber = ref(null)
  const thermosyphoneItemCode = ref(null)
  const thermosyphoneMasters = ref(null)

  // Gear Box
  const gearboxOfnData = ref(null)
  const gearboxData = ref(null)
  const gearboxDrawingNumber = ref(null)
  const gearboxItemCode = ref(null)
  const gearboxMasters = ref(null)

  // Motor
  const motorOfnData = ref(null)
  const motorData = ref(null)
  const motorDrawingNumber = ref(null)
  const motorItemCode = ref(null)
  const motorMasters = ref(null)

  // Insulation
  const insulationOfnData = ref(null)
  const insulationData = ref(null)

    const onUpdateTab = (val) => {
      if (val === 'agitator'){
        agitatorOfnData.value.data = agitatorData.value
      }
      else if(val === 'monoblock'){
        monoblockOfnData.value.data = monoblockData.value
      }
      else if(val === 'jacket'){
        jacketOfnData.value.data = jacketData.value
      }
      else if(val === 'baffle'){
        baffleOfnData.value = baffleData.value
      }
      // sensor
      // mseal
    }

    const onUpdateModelType = (modelType) => {
      console.log(modelType)
      tab.value = null
      localStorage.clear()
      let disallowedNames = [];
      if (modelType === 'AE') {
        disallowedNames = ['monoblock', 'coc', 'baffle']
        // axios.post(host.value + '/api/v1/getofn', JSON.stringify({sfon: '074254'}), {
        //   headers: {
        //   'Content-Type': 'application/json'
        // }
        // })
        // .then(response => {
        //   const data = response.data
        //   console.log(data)
        // })
        // .catch(error => { 
        //   console.error('Error:', error);
        // });
      } else if (modelType === 'BE') {
        disallowedNames = ['pan', 'topCover', 'bfcClamp', 'coc', 'baffle']
      } else if (modelType === 'CE') {
        disallowedNames = ['pan', 'topCover', 'thermowell']
      }

      // Filter out disallowed component names
      const filteredComponents = componentsArray.value.filter(comp =>
        !disallowedNames.includes(comp.name)
      )
      components.value.splice(0, components.value.length)
      components.value.push(...filteredComponents)
      // components.value.push(...componentsArray.value)
      // tab.value = components.value[0].name
    }

    const prompt = (clickedItem) => {
      if (clickedItem === 'Dashboard'){
        $q.dialog({
          title: 'Prompt',
          message: 'Enter Salesforce Order Number (SFON)',
          prompt: {
            model: '',
            isValid: val => val.length > 5,
            type: 'number' // optional
          },
          cancel: true,
          persistent: true
        }).onOk(data => {
          getOFNDetails(data)
        }).onCancel(() => {
          // console.log('>>>> Cancel')
        }).onDismiss(() => {
          // console.log('I am triggered on both OK and Cancel')
        })
      }
    }

    const getOFNDetails = (sfno) => {
      axios.post(host.value + '/api/v1/getofn', JSON.stringify({sfon: sfno}), {
          headers: {
          'Content-Type': 'application/json'
        }
        })
        .then(response => {
          const data = response.data
          console.log(data.ofn_details)
          if (data.ofn_details !== null){
            fillOFNDetails(data)
          }else{
            $q.dialog({
              title: 'Invalid SFON',
              message: 'You must provide a valid Salesforce Order Number.',
              icon: 'error',
              ok: {
                label: 'Try Again',
                color: 'negative'
              },
              class: 'text-negative'
            }).onOk(() => {
              prompt('Dashboard'); // Reopen the input dialog
            });
          }
          
        })
        .catch(error => { 
          console.error('Error:', error);
        });
    }

    const fillOFNDetails = (data) => {
      sfon.value = data.ofn_details.sfon_no
      capacity.value = data.ofn_details.v_capacity
      model.value = data.ofn_details.model
      modelId.value = data.ofn_details.model_id
      reactor.value = data.ofn_details.reactor
      reactorId.value = data.ofn_details.reactor_id
      glass.value = data.ofn_details.glass
      ndt.value = data.ofn_details.ndt_value
      designTemperature.value = data.ofn_details.design_temperature
      designPressure.value = data.ofn_details.design_pressure
      const mt = data.ofn_details.model.split('_')[0]
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
      agitatorOfnData.value = {
        agitator_shaft: data.ofn_details.agitator_shaft,
        sealing_type: data.ofn_details.sealing_type,
        agitator_flight: data.ofn_details.agitator_flight,
        agitator_sweeps: data.ofn_details.agitator_sweep,
        agitator_flight_types: data.ofn_details.agitator_flight_types
      }
    }

    const prepareMonoblockData = (data) => {
      monoblockOfnData.value = {
        id: data.ofn_details.v_id_mm,
        osTos: data.ofn_details.v_ostoos_mm,
        reactor: data.ofn_details.reactor,
        nozzle_names: data.ofn_details.non_field1,
        nozzle_sizes: data.ofn_details.non_field2,
        nozzle_locations: data.ofn_details.non_field4,
      }
    }

    const prepareTopCoverData = (data) => {
      topCoverOfnData.value = {
        id: data.ofn_details.v_id_mm,
        osTos: data.ofn_details.v_ostoos_mm,
        reactor: data.ofn_details.reactor,
        nozzle_names: data.ofn_details.non_field1,
        nozzle_sizes: data.ofn_details.non_field2,
        nozzle_locations: data.ofn_details.non_field4,
      }
    }

    const preparePanData = (data) => {
      panOfnData.value = {
        id: data.ofn_details.v_id_mm,
        osTos: data.ofn_details.v_ostoos_mm,
        reactor: data.ofn_details.reactor,
        nozzle_names: data.ofn_details.non_field1,
        nozzle_sizes: data.ofn_details.non_field2,
        nozzle_locations: data.ofn_details.non_field4,
      }
    }

    const prepareJacketData = (data) => {
      jacketOfnData.value = {
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
      ringOfnData.value = {
        nozzle_names: data.ofn_details.non_field1,
        nozzle_sizes: data.ofn_details.non_field2
      }
    }

    const prepareShaftClosureData = (data) => {
      shaftclosureOfnData.value = {
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
      if(data.ofn_details.shaft_type === 'Single Mechanical Seal' || data.ofn_details.shaft_type == 'Stuffing Box'){
        isDisplayTab.value = false
      }
      else{
        isDisplayTab.value = true
      }
    }

    const showTab = (compName) => {
      if(compName === 'thermosyphone'){
        return isDisplayTab.value
      }else{
        return true
      }
    }

    const prepareGearboxData = (data) => {
      gearboxOfnData.value = {
        gear_make: data.ofn_details.gear_make,
        gear_type: data.ofn_details.gear_type
      }
    }

    const prepareMotorData = (data) => {
      motorOfnData.value = {
        motor_type: data.ofn_details.motor_type,
        motor_make: data.ofn_details.motor_make,
        motor_mounting: data.ofn_details.motor_mounting,
        motor_standard: data.ofn_details.motor_standard,
        motor_hp: data.ofn_details.motor_hp
      }
    }

    const prepareManholeCoverData = (data) => {
      manholeCoverOfnData.value = {
        nozzle_services: data.ofn_details.non_field3,
        nozzle_sizes: data.ofn_details.non_field2
      }
    }

    const prepareProtectionRingData = (data) => {
      protectionRingOfnData.value = {
        nozzle_services: data.ofn_details.non_field3,
        nozzle_sizes: data.ofn_details.non_field2
      }
    }

    const prepareSpringbalanceassemblyData = (data) => {
      springbalanceassemblyOfnData.value = {
        nozzle_services: data.ofn_details.non_field3,
        nozzle_sizes: data.ofn_details.non_field2
      }
    }

    const prepareBovData = (data) => {
      bovOfnData.value = {
        nozzle_names: data.ofn_details.non_field1,
        nozzle_sizes: data.ofn_details.non_field2,
        gasket: data.ofn_details.gasket,
        fastener: data.ofn_details.fastener,
        split_flange: data.ofn_details.split_flange
      }
    }

    const prepareInsulationData = (data) => {
      insulationOfnData.value = {
        reactor: data.ofn_details.reactor
      }
    }

    const prepareDriveAssemblyData = (data) => {
      driveAssemblyOfnData.value = {
        model: model.value? model.value: null,
        shaft_dia: data.ofn_details.agitator_shaft
      }
    }

    // const saveToJsonFile = (comp_name, data) => {
    //   if(sono.value === null || sono.value === "" || sono.value === ''){
    //     isSalesOrderNumberNull.value = true
    //   }
    //   else{
    //     const compDetails = {[comp_name]: data, so_no: sono.value}
    //     axios.post(host.value + '/api/v1/savetojson', JSON.stringify({componentDetails: compDetails}), {
    //       headers: {
    //       'Content-Type': 'application/json'
    //       }
    //     })
    //     .then(response => {
    //     if (response.data) {
    //        $q.notify({
    //           message: 'Successfully saved information.',
    //           color: 'green-5'
    //         })
    //         const target = components.value.find(item => item.name === comp_name);
    //         if(target){
    //           target.icon = 'check_circle_outline'
    //           target.color= 'green'
    //           target.saved = true
    //         }
    //         visibleGenerateButton.value = components.value.every(obj => obj.saved === true);
    //       }
    //     })
    //     .catch(error => { 
    //       console.error('Error:', error);
    //     });
    //   }
    // }

  const saveToJsonFile = (comp_name, data) => {
      if (!sono.value) {
        isSalesOrderNumberNull.value = true;
        return;
      }

      const compDetails = { [comp_name]: data, so_no: sono.value };

      // Save to localStorage
      localStorage.setItem(`savedData:${comp_name}`, JSON.stringify(compDetails));

      axios.post(`${host.value}/api/v1/savetojson`, JSON.stringify({ componentDetails: compDetails }), {
        headers: {
          'Content-Type': 'application/json'
        }
      })
      .then(response => {
        if (response.data) {
          $q.notify({
            message: 'Successfully saved information.',
            color: 'green-5'
          });

          const target = components.value.find(item => item.name === comp_name);
          if (target) {
            target.icon = 'check_circle_outline';
            target.color = 'green';
            target.saved = true;
          }

          visibleGenerateButton.value = components.value.every(obj => obj.saved === true);
        }
      })
      .catch(error => {
        console.error('Error:', error);
      });
    };

    const openInInventor = (compName) => {
      if(sono.value === null || sono.value === "" || sono.value === ''){
        isSalesOrderNumberNull.value = true
      }else{
        $q.loading.show({
          message: `Opening ${compName} in Inventor...`,
          spinnerColor: 'white'
        })
        const sonoDetails = {sono: sono.value, comp_name: compName}
        axios.post(host.value + '/api/v1/open', JSON.stringify({details: sonoDetails}), {
          headers: {
          'Content-Type': 'application/json'
          }
        })
        .then(response => {
        if (response.data) {
            if(response.data.isOpen){
              $q.loading.hide()
            }
          }
        })
        .catch(error => { 
          console.error('Error:', error);
        });
      }
    }

    const generateModel = () => {
      if(sono.value === null || sono.value === "" || sono.value === ''){
        isSalesOrderNumberNull.value = true
      }else{
        const sonoDetails = {sono: sono.value, model: model.value, reactor: reactor.value, capacity: capacity.value}
        axios.post(host.value + '/api/v1/generate', JSON.stringify({details: sonoDetails}), {
          headers: {
          'Content-Type': 'application/json'
          }
        })
        .then(response => {
        if (response.data) {
           $q.notify({
              message: 'Successfully saved information.',
              color: 'green-5'
            })
          }
        })
        .catch(error => { 
          console.error('Error:', error);
        });
      }
    }

    // const enableGenerateButton = (comps) => {
    //   if(comps.length > 0){
    //     visibleGenerateButton.value = comps.every(obj => obj.saved === true);
    //   }
    // }

    return {
      comp,
      drawer: ref(false),
      tab,
      splitterModel: ref(15),
      menuList,
      visibleGenerateButton,
      componentsArray,
      components,
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
      sTypes,
      sType,
      mTypes,
      mType,
      host,
      isSalesOrderNumberNull,
      drawingNumber,
      itemCode,

      // Agitator
      agitatorOfnData,
      agitatorData,
      isItemCodeNull,
      agitatorDrawingNumber,
      agitatorItemCode,
      agitatorSaveRef,

      // Monoblock
      monoblockOfnData,
      monoblockData,
      monoblockDrawingNumber,
      monoblockItemCode,
      fittingsData,
      fastenerData,

      // Top Cover
      topCoverOfnData,
      topCoverData,
      topCoverDrawingNumber,
      topCoverItemCode,

      // Pan
      panOfnData,
      panData,
      panDrawingNumber,
      panItemCode,

      // Jacket
      jacketOfnData,
      jacketData,
      jacketDrawingNumber,
      jacketItemCode,
      jacketMasters,

      // Diaphragm Ring
      ringOfnData,
      ringData,
      ringDrawingNumber,
      ringItemCode,

      // Manhole Cover
      manholeCoverOfnData,
      manholeCoverData,
      manholeCoverDrawingNumber,
      manholeCoverItemCode,

      // Protection Ring
      protectionRingOfnData,
      protectionRingData,
      protectionRingDrawingNumber,
      protectionRingItemCode,

      // Spring Balance Assembly
      springbalanceassemblyOfnData,
      springbalanceassemblyData,
      springbalanceassemblyDrawingNumber,
      springbalanceassemblyItemCode,

      // Manhole C Clamp
      manholeCClampOfnData,
      manholeCClampData,
      manholeCClampDrawingNumber,
      manholeCClampItemCode,
      manholeCClampMasters,

      // COC
      cocOfnData,
      cocData,
      cocDrawingNumber,
      cocItemCode,

      // Body Flange C Clamp
      bfCClampOfnData,
      bfCClampData,
      bfCClampDrawingNumber,
      bfCClampItemCode,
      bfCClampMasters,

      // Drive Assembly
      driveAssemblyOfnData,
      driveAssemblyData,
      driveAssemblyDrawingNumber,
      driveAssemblyItemCode,

      // Bottom Outlet Valve
      bovOfnData,
      bovData,
      bovDrawingNumber,
      bovItemCode,
      bovMasters,

      // Name Plate Bracket
      npbOfnData,
      npbData,
      npbDrawingNumber,
      npbItemCode,

      // Drive Hood
      driveHoodOfnData,
      driveHoodData,
      driveHoodDrawingNumber,
      driveHoodItemCode,

      // Air Vent Coupling Bracket
      avcpOfnData,
      avcpData,
      avcpDrawingNumber,
      avcpItemCode,

      // Insulation
      insulationOfnData,
      insulationData,

      // Baffle
      baffleOfnData,
      baffleData,
      baffleDrawingNumber,
      baffleItemCode,
      baffleMasters,

      // Thermowell - For AE and BE
      thermowellOfnData,
      thermowellData,
      thermowellDrawingNumber,
      thermowellItemCode,
      thermowellMasters,

      // Sensor
      sensorOfnData,
      sensorData,
      sensorDrawingNumber,
      sensorItemCode,

      // Shaft Closure = Mechanical Seal
      shaftclosureOfnData,
      shaftclosureData,
      shaftclosureDrawingNumber,
      shaftclosureItemCode,
      shaftclosureMasters,

      // Thermosyphone
      isDisplayTab,
      isThermosyphoneVisible,
      thermosyphoneOfnData,
      thermosyphoneData,
      thermosyphoneDrawingNumber,
      thermosyphoneItemCode,
      thermosyphoneMasters,

      // Gear Box
      gearboxOfnData,
      gearboxData,
      gearboxDrawingNumber,
      gearboxItemCode,
      gearboxMasters,

      // Motor
      motorOfnData,
      motorData,
      motorDrawingNumber,
      motorItemCode,
      motorMasters,

      // Methods
      prompt,
      showTab,
      onUpdateTab,
      onUpdateModelType,
      saveToJsonFile,
      generateModel,
      openInInventor,
      // enableGenerateButton
    }
  },
  methods: {
      async searchData(data) {
        const component = data.component?data.component.toLowerCase():null
        data.model_info = {
            capacity: this.capacity,
            model: this.model,
            reactor: this.reactor,
            glass: this.glass,
            ndt: this.ndt,
            designPressure: this.designPressure,
            designTemperature: this.designTemperature,
            drawingNumber: '',
            itemCode: ''
          }
        axios.post(this.host + '/api/v1/search', JSON.stringify({[component]: data}), {
          headers: {
          'Content-Type': 'application/json'
        }
        })
        .then(response => {
          if (component === 'agitator'){
            if(response.data.result === null){
              this.comp = component[0].toUpperCase() + component.substr(1)
              this.agitatorDrawingNumber = null
              this.agitatorItemCode = null
              this.drawingNumber = null
              this.itemCode = null
              this.isItemCodeNull = true
            }
            else {
              this.agitatorItemCode = response.data.result.itemCode.toString()
              this.agitatorDrawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.drawingNumber = this.agitatorDrawingNumber
              data.model_info.itemCode = this.agitatorItemCode
            }
            this.agitatorData = data
          }
          else if(component === 'monoblock'){
            if(response.data.result === null){
              this.comp = component[0].toUpperCase() + component.substr(1)
              this.monoblockDrawingNumber = null
              this.monoblockItemCode = null
              this.drawingNumber = null
              this.itemCode = null
              this.isItemCodeNull = true
            }
            else {
              this.monoblockItemCode = response.data.result.itemCode.toString()
              this.monoblockDrawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.drawingNumber = this.monoblockDrawingNumber
              data.model_info.itemCode = this.monoblockItemCode
            }
            this.monoblockData = data
          }
          else if(component === 'gasket'
          || component === 'split flange' 
          || component === 'blind cover' 
          || component === 'reducing flange' 
          || component === 'dip pipe' 
          || component === 'sparger' 
          || component === 'spray ball pipe' 
          || component === 'spray ball'
          || component === 'tee'
          || component === 'manhole protection ring'
          || component === 'manhole cover'
          || component === 'toughened glass'
          || component === 'sight/light glass flange'
          || component === 'extension piece'
          || component === 'baffle'
          // || component === 'thermowell'
          || component === 'bov'){
            if(response.data.result === null){
              this.comp = component[0].toUpperCase() + component.substr(1)
              this.drawingNumber = null
              this.itemCode = null
              this.isItemCodeNull = true
            }
            else {
              data.model_info.drawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.itemCode = response.data.result.itemCode.toString()
            }
            this.fittingsData = data
          }
          else if(component === 'topcover'){
            if(response.data.result === null){
              this.comp = component[0].toUpperCase() + component.substr(1)
              this.topCoverDrawingNumber = null
              this.topCoverItemCode = null
              this.drawingNumber = null
              this.itemCode = null
              this.isItemCodeNull = true
            }
            else {
              this.topCoverItemCode = response.data.result.itemCode.toString()
              this.topCoverDrawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.drawingNumber = this.topCoverDrawingNumber
              data.model_info.itemCode = this.topCoverItemCode
            }
            this.topCoverData = data
          }
          else if(component === 'pan'){
            if(response.data.result === null){
              this.comp = component[0].toUpperCase() + component.substr(1)
              this.panDrawingNumber = null
              this.panItemCode = null
              this.drawingNumber = null
              this.itemCode = null
              this.isItemCodeNull = true
            }
            else {
              this.panItemCode = response.data.result.itemCode.toString()
              this.panDrawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.drawingNumber = this.panDrawingNumber
              data.model_info.itemCode = this.panItemCode
            }
            this.panData = data
          }
          // else if(component === 'jacket'){
          //   if(response.data.result === null){
          //     this.comp = component[0].toUpperCase() + component.substr(1)
          //     this.jacketDrawingNumber = null
          //     this.jacketItemCode = null
          //     this.drawingNumber = null
          //     this.itemCode = null
          //     this.isItemCodeNull = true
          //   }
          //   else {
          //     this.jacketItemCode = response.data.result.itemCode.toString()
          //     this.jacketDrawingNumber = response.data.result.drawingNumber.toString()
          //     data.model_info.drawingNumber = this.jacketDrawingNumber
          //     data.model_info.itemCode = this.jacketItemCode
          //   }
          //   this.jacketData = data
          // }
          // else if(component === 'baffle'){
          //   if(response.data.result === null){
          //     this.comp = component[0].toUpperCase() + component.substr(1)
          //     this.baffleDrawingNumber = null
          //     this.baffleItemCode = null
          //     this.drawingNumber = null
          //     this.itemCode = null
          //     this.isItemCodeNull = true
          //   }
          //   else {
          //     data.model_info.drawingNumber = response.data.result.drawingNumber.toString()
          //     data.model_info.itemCode = response.data.result.itemCode.toString()
          //     this.baffleOfnData = data
          //   }
          //   this.baffleData = data
          // }
          else if(component === 'thermowell'){
            if(response.data.result === null){
              this.comp = component[0].toUpperCase() + component.substr(1)
              this.thermowellDrawingNumber = null
              this.thermowellItemCode = null
              this.drawingNumber = null
              this.itemCode = null
              this.isItemCodeNull = true
            }
            else {
              data.model_info.drawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.itemCode = response.data.result.itemCode.toString()
              this.thermowellOfnData = data
            }
            this.thermowellData = data
          }
          else if(component === 'sensor'){
            if(response.data.result === null){
              this.comp = component[0].toUpperCase() + component.substr(1)
              this.sensorDrawingNumber = null
              this.sensorItemCode = null
              this.drawingNumber = null
              this.itemCode = null
              this.isItemCodeNull = true
            }
            else {
              // this.sensorItemCode = response.data.result.itemCode.toString()
              // this.sensorDrawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.drawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.itemCode = response.data.result.itemCode.toString()
              this.sensorOfnData = data
            }
            this.sensorData = data
          }
          else if(component === 'shaftclosure'){
            if(response.data.result === null){
              this.comp = component[0].toUpperCase() + component.substr(1)
              this.shaftclosureDrawingNumber = null
              this.shaftclosureItemCode = null
              this.drawingNumber = null
              this.itemCode = null
              this.isItemCodeNull = true
            }
            else {
              this.shaftclosureItemCode = response.data.result.itemCode.toString()
              this.shaftclosureDrawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.drawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.itemCode = response.data.result.itemCode.toString()
            }
            this.shaftclosureData = data
          }
          else if(component === 'thermosyphone'){
            if(response.data.result === null){
              this.comp = component[0].toUpperCase() + component.substr(1)
              this.thermosyphoneDrawingNumber = null
              this.thermosyphoneItemCode = null
              this.drawingNumber = null
              this.itemCode = null
              this.isItemCodeNull = true
            }
            else {
              this.thermosyphoneItemCode = response.data.result.itemCode.toString()
              this.thermosyphoneDrawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.drawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.itemCode = response.data.result.itemCode.toString()
            }
            this.thermosyphoneData = data
          }
          else if(component === 'gearbox'){
            if(response.data.result === null){
              this.comp = component[0].toUpperCase() + component.substr(1)
              this.gearboxDrawingNumber = null
              this.gearboxItemCode = null
              this.drawingNumber = null
              this.itemCode = null
              this.isItemCodeNull = true
            }
            else {
              this.gearboxItemCode = response.data.result.itemCode.toString()
              this.gearboxDrawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.drawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.itemCode = response.data.result.itemCode.toString()
            }
            this.gearboxData = data
          }
          else if(component === 'motor'){
            if(response.data.result === null){
              this.comp = component[0].toUpperCase() + component.substr(1)
              this.motorDrawingNumber = null
              this.motorItemCode = null
              this.drawingNumber = null
              this.itemCode = null
              this.isItemCodeNull = true
            }
            else {
              this.motorItemCode = response.data.result.itemCode.toString()
              this.motorDrawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.drawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.itemCode = response.data.result.itemCode.toString()
            }
            this.motorData = data
          }
          else if(component === 'diaphragmring'){
            if(response.data.result === null){
              this.comp = component[0].toUpperCase() + component.substr(1)
              this.ringDrawingNumber = null
              this.ringItemCode = null
              this.drawingNumber = null
              this.itemCode = null
              this.isItemCodeNull = true
            }
            else {
              this.ringItemCode = response.data.result.itemCode.toString()
              this.ringDrawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.drawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.itemCode = response.data.result.itemCode.toString()
            }
            this.ringData = data
          }
          else if(component === 'manholecover'){
            if(response.data.result === null){
              this.comp = component[0].toUpperCase() + component.substr(1)
              this.manholeCoverDrawingNumber = null
              this.manholeCoverItemCode = null
              this.drawingNumber = null
              this.itemCode = null
              this.isItemCodeNull = true
            }
            else {
              this.manholeCoverItemCode = response.data.result.itemCode.toString()
              this.manholeCoverDrawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.drawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.itemCode = response.data.result.itemCode.toString()
            }
            this.manholeCoverData = data
          }
          else if(component === 'protectionring'){
            if(response.data.result === null){
              this.comp = component[0].toUpperCase() + component.substr(1)
              this.protectionRingDrawingNumber = null
              this.protectionRingItemCode = null
              this.drawingNumber = null
              this.itemCode = null
              this.isItemCodeNull = true
            }
            else {
              this.protectionRingItemCode = response.data.result.itemCode.toString()
              this.protectionRingDrawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.drawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.itemCode = response.data.result.itemCode.toString()
            }
            this.protectionRingData = data
          }
          else if(component === 'springbalanceassembly'){
            if(response.data.result === null){
              this.comp = component[0].toUpperCase() + component.substr(1)
              this.springbalanceassemblyDrawingNumber = null
              this.springbalanceassemblyItemCode = null
              this.drawingNumber = null
              this.itemCode = null
              this.isItemCodeNull = true
            }
            else {
              this.springbalanceassemblyItemCode = response.data.result.itemCode.toString()
              this.springbalanceassemblyDrawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.drawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.itemCode = response.data.result.itemCode.toString()
            }
            this.springbalanceassemblyData = data
          }
          else if(component === 'manholecclamp'){
            if(response.data.result === null){
              this.comp = component[0].toUpperCase() + component.substr(1)
              this.manholeCClampDrawingNumber = null
              this.manholeCClampItemCode = null
              this.drawingNumber = null
              this.itemCode = null
              this.isItemCodeNull = true
            }
            else {
              this.manholeCClampItemCode = response.data.result.itemCode.toString()
              this.manholeCClampDrawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.drawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.itemCode = response.data.result.itemCode.toString()
            }
            this.manholeCClampData = data
          }
          else if(component === 'coc'){
            if(response.data.result === null){
              this.comp = component[0].toUpperCase() + component.substr(1)
              this.cocDrawingNumber = null
              this.cocItemCode = null
              this.drawingNumber = null
              this.itemCode = null
              this.isItemCodeNull = true
            }
            else {
              this.cocItemCode = response.data.result.itemCode.toString()
              this.cocDrawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.drawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.itemCode = response.data.result.itemCode.toString()
            }
            this.cocData = data
          }
          else if(component === 'bodyflangecclamp'){
            if(response.data.result === null){
              this.comp = component[0].toUpperCase() + component.substr(1)
              this.bfCClampDrawingNumber = null
              this.bfCClampItemCode = null
              this.drawingNumber = null
              this.itemCode = null
              this.isItemCodeNull = true
            }
            else {
              this.bfCClampItemCode = response.data.result.itemCode.toString()
              this.bfCClampDrawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.drawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.itemCode = response.data.result.itemCode.toString()
            }
            this.bfCClampData = data
          }
          else if(component === 'drivehood'){
            if(response.data.result === null){
              this.comp = component[0].toUpperCase() + component.substr(1)
              this.driveHoodDrawingNumber = null
              this.driveHoodItemCode = null
              this.drawingNumber = null
              this.itemCode = null
              this.isItemCodeNull = true
            }
            else {
              this.driveHoodItemCode = response.data.result.itemCode.toString()
              this.driveHoodDrawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.drawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.itemCode = response.data.result.itemCode.toString()
            }
            this.driveHoodData = data
          }
          // else if(component === 'bov'){
          //   if(response.data.result === null){
          //     this.comp = component[0].toUpperCase() + component.substr(1)
          //     this.bovDrawingNumber = null
          //     this.bovItemCode = null
          //     this.drawingNumber = null
          //     this.itemCode = null
          //     this.isItemCodeNull = true
          //   }
          //   else {
          //     this.bovItemCode = response.data.result.itemCode.toString()
          //     this.bovDrawingNumber = response.data.result.drawingNumber.toString()
          //     data.model_info.drawingNumber = response.data.result.drawingNumber.toString()
          //     data.model_info.itemCode = response.data.result.itemCode.toString()
          //   }
          //   this.bovData = data
          // }
          else if(component === 'nameplatebracket'){
            if(response.data.result === null){
              this.comp = component[0].toUpperCase() + component.substr(1)
              this.npbDrawingNumber = null
              this.npbItemCode = null
              this.drawingNumber = null
              this.itemCode = null
              this.isItemCodeNull = true
            }
            else {
              this.npbItemCode = response.data.result.itemCode.toString()
              this.npbDrawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.drawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.itemCode = response.data.result.itemCode.toString()
            }
            this.npbData = data
          }
          else if(component === 'airventcouplingplug'){
            if(response.data.result === null){
              this.comp = component[0].toUpperCase() + component.substr(1)
              this.avcpDrawingNumber = null
              this.avcpItemCode = null
              this.drawingNumber = null
              this.itemCode = null
              this.isItemCodeNull = true
            }
            else {
              this.avcpItemCode = response.data.result.itemCode.toString()
              this.avcpDrawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.drawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.itemCode = response.data.result.itemCode.toString()
              this.avcpOfnData = data
            }
            this.avcpData = data
          }
          else if(component === 'cleat' || component === 'nut' || component === 'tophead' || component === 'topjcr' || component === 'head' || component === 'shell' || component === 'closer'){
            if(response.data.result === null){
              this.comp = component[0].toUpperCase() + component.substr(1)
              this.drawingNumber = null
              this.itemCode = null
              this.isItemCodeNull = true
            }
            else {
              data.model_info.drawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.itemCode = response.data.result.itemCode.toString()
              this.insulationOfnData = data
            }
            this.insulationData = data
          }
          else if (component === 'fastener' || component === 'washer' || component === 'fastener_nut') {
            if (response.data.result === null) {
              this.comp = component[0].toUpperCase() + component.substr(1)
              this.drawingNumber = null
              this.itemCode = null
              this.isItemCodeNull = true
            } else {
              data.model_info.drawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.itemCode = response.data.result.itemCode.toString()
            }
            this.fastenerData = data
          }
          else if(component === 'drivebasering'
          || component === 'padplate'
          || component === 'lanternsupport'
          || component === 'lanternguard'
          || component === 'agitatorgearcoupling'
          || component === 'gearboxmodel'
          || component === 'bearingnumber'
          || component === 'sleeve'
          || component === 'oilseal'
          || component === 'circlip'
          || component === 'locknut'
          || component === 'lockwasher'){
            if(response.data.result === null){
              this.comp = component[0].toUpperCase() + component.substr(1)
              this.drawingNumber = null
              this.itemCode = null
              this.isItemCodeNull = true
            }
            else {
              data.model_info.drawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.itemCode = response.data.result.itemCode.toString()
              this.driveAssemblyOfnData = data
            }
            this.driveAssemblyData = data
          }
          else if(component === 'jacketnozzle'
          || component === 'jacket'
          || component === 'sidebracket'
          || component === 'legsupport'
          || component === 'sidebracketlegsupport'
          || component === 'ringsupport'
          || component === 'skirtsupport'
          || component === 'earthing'){
            if(response.data.result === null){
              this.comp = component[0].toUpperCase() + component.substr(1)
              this.drawingNumber = null
              this.itemCode = null
              this.isItemCodeNull = true
            }
            else {
              data.model_info.drawingNumber = response.data.result.drawingNumber.toString()
              data.model_info.itemCode = response.data.result.itemCode.toString()
              this.jacketOfnData = data
            }
            this.jacketData = data
          }
        })
        .catch(error => { 
          console.error('Error:', error);
        });
      },

      async saveData() {
        let objToSave = null
        const model_info = {
            capacity: this.capacity,
            model: this.model,
            reactor: this.reactor,
            glass: this.glass,
            ndt: this.ndt,
            designPressure: this.designPressure,
            designTemperature: this.designTemperature,
            drawingNumber: this.drawingNumber,
            itemCode: this.itemCode
        }
        if (this.comp.toLowerCase() === 'agitator'){
          this.agitatorData.model_info = model_info
          objToSave = {[this.comp.toLowerCase()]: this.agitatorData}
        }
        else if(this.comp.toLowerCase() === 'monoblock') {
          this.monoblockData.model_info = model_info
          objToSave = {[this.comp.toLowerCase()]: this.monoblockData}
        }
        else if (this.comp.toLowerCase() === 'fastener' || this.comp.toLowerCase() === 'washer' || this.comp.toLowerCase() === 'fastener_nut')
        {
          this.fastenerData.model_info = model_info
          objToSave = { [this.comp.toLowerCase()]: this.fastenerData }
        }
        else if(this.comp.toLowerCase() === 'gasket'
          || this.comp.toLowerCase() === 'split flange' 
          || this.comp.toLowerCase() === 'blind cover' 
          || this.comp.toLowerCase() === 'reducing flange' 
          || this.comp.toLowerCase() === 'dip pipe' 
          || this.comp.toLowerCase() === 'sparger' 
          || this.comp.toLowerCase() === 'spray ball pipe' 
          || this.comp.toLowerCase() === 'spray ball'
          || this.comp.toLowerCase() === 'tee'
          || this.comp.toLowerCase() === 'manhole protection ring'
          || this.comp.toLowerCase() === 'manhole cover'
          || this.comp.toLowerCase() === 'toughened glass'
          || this.comp.toLowerCase() === 'sight/light glass flange'
          || this.comp.toLowerCase() === 'extension piece'
          || this.comp.toLowerCase() === 'baffle'
          // || this.comp.toLowerCase() === 'thermowell'
          || this.comp.toLowerCase() === 'bov') {
          this.fittingsData.model_info = model_info
          objToSave = {[this.comp.toLowerCase()]: this.fittingsData}
        }
        else if(this.comp.toLowerCase() === 'topcover') {
          this.topCoverData.model_info = model_info
          objToSave = {[this.comp.toLowerCase()]: this.topCoverData}
        }
        else if(this.comp.toLowerCase() === 'pan') {
          this.panData.model_info = model_info
          objToSave = {[this.comp.toLowerCase()]: this.panData}
        }
        else if(this.comp.toLowerCase() === 'diaphragmring') {
          this.ringData.model_info = model_info
          objToSave = {[this.comp.toLowerCase()]: this.ringData}
        }
        else if(this.comp.toLowerCase() === 'manholecover') {
          this.manholeCoverData.model_info = model_info
          objToSave = {[this.comp.toLowerCase()]: this.manholeCoverData}
        }
        else if(this.comp.toLowerCase() === 'protectionring') {
          this.protectionRingData.model_info = model_info
          objToSave = {[this.comp.toLowerCase()]: this.protectionRingData}
        }
        else if(this.comp.toLowerCase() === 'springbalanceassembly') {
          this.springbalanceassemblyData.model_info = model_info
          objToSave = {[this.comp.toLowerCase()]: this.springbalanceassemblyData}
        }
        else if(this.comp.toLowerCase() === 'manholecclamp') {
          this.manholeCClampData.model_info = model_info
          objToSave = {[this.comp.toLowerCase()]: this.manholeCClampData}
        }
        else if(this.comp.toLowerCase() === 'coc') {
          this.cocData.model_info = model_info
          objToSave = {[this.comp.toLowerCase()]: this.cocData}
        }
        else if(this.comp.toLowerCase() === 'bodyflangecclamp') {
          this.bfCClampData.model_info = model_info
          objToSave = {[this.comp.toLowerCase()]: this.bfCClampData}
        }
        // else if(this.comp.toLowerCase() === 'bov') {
        //   this.bovData.model_info = model_info
        //   objToSave = {[this.comp.toLowerCase()]: this.bovData}
        // }
        else if(this.comp.toLowerCase() === 'nameplatebracket') {
          this.npbData.model_info = model_info
          objToSave = {[this.comp.toLowerCase()]: this.npbData}
        }
        else if(this.comp.toLowerCase() === 'airventcouplingplug') {
          this.avcpData.model_info = model_info
          objToSave = {[this.comp.toLowerCase()]: this.avcpData}
        }
        else if(this.comp.toLowerCase() === 'drivehood') {
          this.driveHoodData.model_info = model_info
          objToSave = {[this.comp.toLowerCase()]: this.driveHoodData}
        }
        // else if(this.comp.toLowerCase() === 'baffle') {
        //   this.baffleData.model_info = model_info
        //   objToSave = {[this.comp.toLowerCase()]: this.baffleData}
        // }
        else if(this.comp.toLowerCase() === 'thermowell') {
          this.thermowellData.model_info = model_info
          objToSave = {[this.comp.toLowerCase()]: this.thermowellData}
        }
        else if(this.comp.toLowerCase() === 'sensor') {
          this.sensorData.model_info = model_info
          objToSave = {[this.comp.toLowerCase()]: this.sensorData}
        }
        else if(this.comp.toLowerCase() === 'shaftclosure') {
          this.shaftclosureData.model_info = model_info
          objToSave = {[this.comp.toLowerCase()]: this.shaftclosureData}
        }
        else if(this.comp.toLowerCase() === 'thermosyphone') {
          this.thermosyphoneData.model_info = model_info
          objToSave = {[this.comp.toLowerCase()]: this.thermosyphoneData}
        }
        else if(this.comp.toLowerCase() === 'gearbox') {
          this.gearboxData.model_info = model_info
          objToSave = {[this.comp.toLowerCase()]: this.gearboxData}
        }
        else if(this.comp.toLowerCase() === 'motor') {
          this.motorData.model_info = model_info
          objToSave = {[this.comp.toLowerCase()]: this.motorData}
        }
        else if(this.comp.toLowerCase() === 'cleat' || this.comp.toLowerCase() === 'nut' || this.comp.toLowerCase() === 'tophead' || this.comp.toLowerCase() === 'topjcr' || this.comp.toLowerCase() === 'head' || this.comp.toLowerCase() === 'shell' || this.comp.toLowerCase() === 'closer') {
          this.insulationData.model_info = model_info
          objToSave = {[this.comp.toLowerCase()]: this.insulationData}
        }
        else if(this.comp.toLowerCase() === 'drivebasering' 
        || this.comp.toLowerCase() === 'padplate' 
        || this.comp.toLowerCase() === 'lanternsupport' 
        || this.comp.toLowerCase() === 'lanternguard' 
        || this.comp.toLowerCase() === 'agitatorgearcoupling' 
        || this.comp.toLowerCase() === 'gearboxmodel' 
        || this.comp.toLowerCase() === 'bearingnumber'
        || this.comp.toLowerCase() === 'sleeve'
        || this.comp.toLowerCase() === 'oilseal'
        || this.comp.toLowerCase() === 'circlip'
        || this.comp.toLowerCase() === 'locknut'
        || this.comp.toLowerCase() === 'lockwasher') {
          this.driveAssemblyData.model_info = model_info
          objToSave = {[this.comp.toLowerCase()]: this.driveAssemblyData}
        }
        else if(this.comp.toLowerCase() === 'jacketnozzle'
        || this.comp.toLowerCase() === 'jacket'
        || this.comp.toLowerCase() === 'sidebracket'
        || this.comp.toLowerCase() === 'legsupport'
        || this.comp.toLowerCase() === 'sidebracketlegsupport'
        || this.comp.toLowerCase() === 'ringsupport'
        || this.comp.toLowerCase() === 'skirtsupport'
        || this.comp.toLowerCase() === 'earthing') {
          this.jacketData.model_info = model_info
          objToSave = {[this.comp.toLowerCase()]: this.jacketData}
        }
        axios.post(this.host + '/api/v1/save', JSON.stringify(objToSave), {
          headers: {
          'Content-Type': 'application/json'
        }
        })
        .then(response => {
          if (response.data){
            if (this.comp.toLowerCase() === 'agitator'){
              this.agitatorDrawingNumber = this.drawingNumber
              this.agitatorItemCode = this.itemCode
            }
            else if (this.comp.toLowerCase() === 'gasket'
            || this.comp.toLowerCase() === 'split flange' 
            || this.comp.toLowerCase() === 'blind cover' 
            || this.comp.toLowerCase() === 'reducing flange' 
            || this.comp.toLowerCase() === 'dip pipe' 
            || this.comp.toLowerCase() === 'sparger' 
            || this.comp.toLowerCase() === 'spray ball pipe' 
            || this.comp.toLowerCase() === 'spray ball'
            || this.comp.toLowerCase() === 'tee'
            || this.comp.toLowerCase() === 'manhole protection ring'
            || this.comp.toLowerCase() === 'manhole cover'
            || this.comp.toLowerCase() === 'toughened glass'
            || this.comp.toLowerCase() === 'sight/light glass flange'
            || this.comp.toLowerCase() === 'extension piece'
            || this.comp.toLowerCase() === 'baffle'
            // || this.comp.toLowerCase() === 'thermowell'
            || this.comp.toLowerCase() === 'bov'){
              this.fittingsData = {fittings: this.fittingsData}
            }
            else if(this.comp.toLowerCase() === 'monoblock') {
              this.monoblockDrawingNumber = this.drawingNumber
              this.monoblockItemCode = this.itemCode
            }
            else if(this.comp.toLowerCase() === 'topcover') {
              this.topCoverDrawingNumber = this.drawingNumber
              this.topCoverItemCode = this.itemCode
            }
            else if (this.comp.toLowerCase() === 'fastener' || this.comp.toLowerCase() === 'washer' || this.comp.toLowerCase() === 'nut') {
              this.fastenerData = {fastener: this.fastenerData}
            }
            else if(this.comp.toLowerCase() === 'pan') {
              this.panDrawingNumber = this.drawingNumber
              this.panItemCode = this.itemCode
            }
            else if(this.comp.toLowerCase() === 'diaphragmring') {
              this.ringDrawingNumber = this.drawingNumber
              this.ringItemCode = this.itemCode
            }
            else if(this.comp.toLowerCase() === 'manholecover') {
              this.manholeCoverDrawingNumber = this.drawingNumber
              this.manholeCoverItemCode = this.itemCode
            }
            // else if(this.comp.toLowerCase() === 'baffle') {
            //   // this.baffleDrawingNumber = this.drawingNumber
            //   // this.baffleItemCode = this.itemCode
            //   this.baffleOfnData = this.baffleData
            // }
            // else if(this.comp.toLowerCase() === 'thermowell') {
            //   // this.baffleDrawingNumber = this.drawingNumber
            //   // this.baffleItemCode = this.itemCode
            //   this.thermowellOfnData = this.thermowellData
            // }
            else if(this.comp.toLowerCase() === 'cleat' || this.comp.toLowerCase() === 'nut' || this.comp.toLowerCase() === 'tophead' || this.comp.toLowerCase() === 'topjcr' || this.comp.toLowerCase() === 'head' || this.comp.toLowerCase() === 'shell' || this.comp.toLowerCase() === 'closer') {
              // this.baffleDrawingNumber = this.drawingNumber
              // this.baffleItemCode = this.itemCode
              this.insulationOfnData = this.insulationData
            }
            else if(this.comp.toLowerCase() === 'drivebasering' 
            || this.comp.toLowerCase() === 'padplate' 
            || this.comp.toLowerCase() === 'lanternsupport' 
            || this.comp.toLowerCase() === 'lanternguard' 
            || this.comp.toLowerCase() === 'agitatorGearCoupling' 
            || this.comp.toLowerCase() === 'gearboxmodel' 
            || this.comp.toLowerCase() === 'bearingnumber'
            || this.comp.toLowerCase() === 'sleeve'
            || this.comp.toLowerCase() === 'oilseal'
            || this.comp.toLowerCase() === 'circlip'
            || this.comp.toLowerCase() === 'locknut'
            || this.comp.toLowerCase() === 'lockwasher'){
              this.driveAssemblyOfnData = this.driveAssemblyData
            }
            else if(this.comp.toLowerCase() === 'jacketnozzle'
            || this.comp.toLowerCase() === 'jacket'
            || this.comp.toLowerCase() === 'sidebracket'
            || this.comp.toLowerCase() === 'legsupport'
            || this.comp.toLowerCase() === 'sidebracketlegsupport'
            || this.comp.toLowerCase() === 'ringsupport'
            || this.comp.toLowerCase() === 'skirtsupport'
            || this.comp.toLowerCase() === 'earthing'){
              this.jacketOfnData = this.jacketData
            }
            else if(this.comp.toLowerCase() === 'sensor'){
              this.sensorOfnData = this.sensorData
            }
            else if(this.comp.toLowerCase() === 'shaftclosure'){
              this.shaftclosureDrawingNumber = this.drawingNumber
              this.shaftclosureItemCode = this.itemCode
            }
            else if(this.comp.toLowerCase() === 'thermosyphone'){
              this.thermosyphoneDrawingNumber = this.drawingNumber
              this.thermosyphoneItemCode = this.itemCode
            }
            else if(this.comp.toLowerCase() === 'gearbox'){
              this.gearboxDrawingNumber = this.drawingNumber
              this.gearboxItemCode = this.itemCode
            }
            else if(this.comp.toLowerCase() === 'motor'){
              this.motorDrawingNumber = this.drawingNumber
              this.motorItemCode = this.itemCode
            }
            else if(this.comp.toLowerCase() === 'protectionring'){
              this.protectionRingDrawingNumber = this.drawingNumber
              this.protectionRingItemCode = this.itemCode
            }
            else if(this.comp.toLowerCase() === 'springbalanceassembly'){
              this.springbalanceassemblyDrawingNumber = this.drawingNumber
              this.springbalanceassemblyItemCode = this.itemCode
            }
            else if(this.comp.toLowerCase() === 'manholecclamp'){
              this.manholeCClampDrawingNumber = this.drawingNumber
              this.manholeCClampItemCode = this.itemCode
            }
            else if(this.comp.toLowerCase() === 'coc'){
              this.cocDrawingNumber = this.drawingNumber
              this.cocItemCode = this.itemCode
            }
            else if(this.comp.toLowerCase() === 'bodyflangecclamp'){
              this.bfCClampDrawingNumber = this.drawingNumber
              this.bfCClampItemCode = this.itemCode
            }
            // else if(this.comp.toLowerCase() === 'bov'){
            //   this.bovDrawingNumber = this.drawingNumber
            //   this.bovItemCode = this.itemCode
            // }
            else if(this.comp.toLowerCase() === 'nameplatebracket'){
              this.npbDrawingNumber = this.drawingNumber
              this.npbItemCode = this.itemCode
            }
            else if(this.comp.toLowerCase() === 'airventcouplingplug'){
              // this.avcpDrawingNumber = this.drawingNumber
              // this.avcpItemCode = this.itemCode
              this.avcpOfnData = this.avcpData
            }
            else if(this.comp.toLowerCase() === 'drivehood'){
              this.driveHoodDrawingNumber = this.drawingNumber
              this.driveHoodItemCode = this.itemCode
            }
            else{
              this.drawingNumber = null
              this.itemCode = null
            }
            this.$q.notify({
              message: 'Successfully saved '+ this.comp +' data to excel file.',
              color: 'green-5'
            })
          }
        })
        .catch(error => {
          console.error('Error:', error);

          if (error.response && error.response.status === 409) {
            Notify.create({
              type: 'warning',
              message: error.response.data.detail || 'Excel file is open. Please close it before saving.',
              timeout: 0,  // stays on screen until manually dismissed
              actions: [{ label: 'Dismiss', color: 'white' }]
            });
          } else {
            Notify.create({
              type: 'negative',
              message: 'An unexpected error occurred. Please try again.',
              timeout: 5000
            });
          }
        });
      },

      async getMasters(data){
        const model_info = {
            capacity: this.capacity,
            model: this.model,
            reactor: this.reactor,
            modelId: this.modelId,
            reactorId: this.reactorId
        }
        const master_details = {model_info: model_info, masters: data}
        axios.post(this.host + '/api/v1/getmasters', JSON.stringify(master_details), {
          headers: {
          'Content-Type': 'application/json'
        }
        })
        .then(response => {
          if (response?.data){
            const comp = response.data.master_details.masters.component
            if (comp === 'baffle'){
              this.baffleMasters =  response.data.master_details.masters
            }
            if (comp === 'thermowell'){
              this.thermowellMasters =  response.data.master_details.masters
            }
            if (comp === 'thermowell'){
              this.thermowellMasters =  response.data.master_details.masters
            }
            else if(comp === 'jacket'){
              this.jacketMasters = response.data.master_details.masters
            }
            else if(comp === 'shftclosure'){
               this.shaftclosureMasters = response.data.master_details.masters
            }
            else if(comp === 'thermosyphone'){
               this.thermosyphoneMasters = response.data.master_details.masters
            }
            else if(comp === 'gearbox'){
               this.gearboxMasters = response.data.master_details.masters
            }
            else if(comp === 'motor'){
               this.motorMasters = response.data.master_details.masters
            }
            else if(comp ===  'manholecclamp'){
               this.manholeCClampMasters = response.data.master_details.masters
            }
            else if(comp ===  'coc'){
               this.cocMasters = response.data.master_details.masters
            }
            else if(comp ===  'bfcclamp'){
               this.bfCClampMasters = response.data.master_details.masters
            }
            else if(comp ===  'bov'){
               this.bovMasters = response.data.master_details.masters
            }
          }
        })
        .catch(error => { 
          console.error('Error:', error);
        });
      },

      async saveBaffleData(data) {
        data.one.model_info = {
            capacity: this.capacity,
            model: this.model,
            reactor: this.reactor,
            glass: this.glass,
            ndt: this.ndt,
            designPressure: this.designPressure,
            designTemperature: this.designTemperature,
            drawingNumber: data.one.drawingNumberOne,
            itemCode: data.one.itemCodeOne
        }
        data.two.model_info = {
            capacity: this.capacity,
            model: this.model,
            reactor: this.reactor,
            glass: this.glass,
            ndt: this.ndt,
            designPressure: this.designPressure,
            designTemperature: this.designTemperature,
            drawingNumber: data.two.drawingNumberTwo,
            itemCode: data.two.itemCodeTwo
        }
        this.saveToJsonFile('baffle', data)
        this.baffleData = data
      },

      async saveThermowellData(data) {
        data.one.model_info = {
            capacity: this.capacity,
            model: this.model,
            reactor: this.reactor,
            glass: this.glass,
            ndt: this.ndt,
            designPressure: this.designPressure,
            designTemperature: this.designTemperature,
            drawingNumber: data.one.drawingNumberOne,
            itemCode: data.one.itemCodeOne
        }
        data.two.model_info = {
            capacity: this.capacity,
            model: this.model,
            reactor: this.reactor,
            glass: this.glass,
            ndt: this.ndt,
            designPressure: this.designPressure,
            designTemperature: this.designTemperature,
            drawingNumber: data.two.drawingNumberTwo,
            itemCode: data.two.itemCodeTwo
        }
        this.saveToJsonFile('thermowell', data)
        this.thermowellData = data
      },

      async saveSensorData(data){
        data.one.model_info = {
            capacity: this.capacity,
            model: this.model,
            reactor: this.reactor,
            glass: this.glass,
            ndt: this.ndt,
            designPressure: this.designPressure,
            designTemperature: this.designTemperature,
            drawingNumber: data.one.rtdDrawingNumberOne,
            itemCode: data.one.rtdItemCodeOne
        }
        data.two.model_info = {
            capacity: this.capacity,
            model: this.model,
            reactor: this.reactor,
            glass: this.glass,
            ndt: this.ndt,
            designPressure: this.designPressure,
            designTemperature: this.designTemperature,
            drawingNumber: data.two.rtdDrawingNumberTwo,
            itemCode: data.two.rtdItemCodeTwo
        }
        data.dialThermo.model_info = {
            capacity: this.capacity,
            model: this.model,
            reactor: this.reactor,
            glass: this.glass,
            ndt: this.ndt,
            designPressure: this.designPressure,
            designTemperature: this.designTemperature,
            drawingNumber: data.dialThermo.dialThermoDrawingNumber,
            itemCode: data.dialThermo.dialThermoItemCode
        }
        this.saveToJsonFile('sensor', data)
        this.sensorData = data
      },

      async saveInsulationData(data){
        data.model_info = {
          capacity: this.capacity,
          model: this.model,
          reactor: this.reactor,
          glass: this.glass,
          ndt: this.ndt,
          designPressure: this.designPressure,
          designTemperature: this.designTemperature,
        }
        this.saveToJsonFile('insulation', data)
        this.insulationData = data
      },

      async saveDriveAssemblyData(data){
        data.model_info = {
          capacity: this.capacity,
          model: this.model,
          reactor: this.reactor,
          glass: this.glass,
          ndt: this.ndt,
          designPressure: this.designPressure,
          designTemperature: this.designTemperature,
        }
        this.saveToJsonFile('driveAssembly', data)
        this.driveAssemblyData = data
      },

      async saveJacket(data){
        data.model_info = {
          capacity: this.capacity,
          model: this.model,
          reactor: this.reactor,
          glass: this.glass,
          ndt: this.ndt,
          designPressure: this.designPressure,
          designTemperature: this.designTemperature,
        }
        this.saveToJsonFile('jacket', data)
        this.jacketData = data
      },

      async saveAirVent(data){
        data.model_info = {
          capacity: this.capacity,
          model: this.model,
          reactor: this.reactor,
          glass: this.glass,
          ndt: this.ndt,
          designPressure: this.designPressure,
          designTemperature: this.designTemperature,
        }
        this.saveToJsonFile('airVentCouplingPlug', data)
        this.avcpData = data
      }

  }
  // watch: {
  //   components: {
  //     handler(newVal) {
  //       if (newVal !== null) {
  //         this.enableGenerateButton(newVal);
  //       }
  //     },
  //     immediate: true
  //   }
  // }
}
</script>
<style lang="css">
.bg-white {
  background: hsl(0, 0%, 100%) !important;
}
</style>