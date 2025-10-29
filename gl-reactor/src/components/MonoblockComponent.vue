<template>
  <div class="q-pa-md" style="height: 100vh; display: flex; flex-direction: column;">

    <!-- First Row Section -->
    <div class="q-mb-md">
      <div class="row q-gutter-md q-wrap">
        <q-input
          outlined
          v-model="id"
          type="number"
          label="I/D"
          dense
          class="col-12 col-md-2"
        />
        <q-input
          outlined
          v-model="osTos"
          type="number"
          label="O/S To O/S"
          dense
          class="col-12 col-md-2"
        />
        <q-select
          outlined
          v-model="insulationOnTop"
          :options="insulationOnTopOptions"
          label="Insulation On Top"
          dense
          class="col-12 col-md-2"
        />
        <q-select
          outlined
          v-model="spilageCollectionTray"
          :options="spilageCollectionTrayOptions"
          label="Spilage Collection Tray"
          dense
          class="col-12 col-md-2"
        />
        <q-space/>
        <q-btn outline rounded icon="search" color="primary" label="Search" @click="searchMonoblockData"/>
      </div>
    </div>

    <!-- Second Row Section -->
    <div class="q-mb-md">
      <div class="row q-gutter-md q-wrap">
        <q-select
          outlined
          v-model="liftingMOC"
          :options="liftingMOCOptions"
          label="Lifting MOC"
          dense
          class="col-12 col-md-2"
        />
        <q-input
          outlined
          v-model="topDishedEndThickness"
          type="number"
          label="Top Dished End Thickness"
          dense
          class="col-12 col-md-2"
        />
        <q-input
          outlined
          v-model="innerShellThickness"
          type="number"
          label="Inner Shell Thickness"
          dense
          class="col-12 col-md-2"
        />
        <q-input
          outlined
          v-model="bottomDishedEndThickness"
          type="number"
          label="Bottom Dished End Thickness"
          dense
          class="col-12 col-md-2"
        />
      </div>
    </div>

    <!-- Nozzles Section -->
    <div class="q-mt-md" style="flex-grow: 1; display: flex; flex-direction: column; padding-bottom: 300px;">
      <div class="row items-center justify-between q-mb-sm">
        <div class="text-subtitle1">Nozzles</div>
        <div>
            <q-select
            outlined
            v-model="modelType"
            :options="modelTypeOptions"
            label="Model Type"
            dense
            class="col-12 col-md-2"
            />
        </div>
        <div>
          <q-btn
            v-if="modelType === 'Non-Standard'"
            dense
            flat
            icon="add"
            label="Add Nozzle"
            color="primary"
            @click="addNozzle"
            class="q-mr-sm"
          />
          <q-btn
            v-if="modelType === 'Non-Standard'"
            dense
            flat
            icon="remove"
            label="Remove Last"
            color="negative"
            @click="removeNozzle"
            :disable="nozzles.length === 0"
          />
        </div>
      </div>
      <div style="flex-grow: 1; overflow-y: auto; padding-right: 8px; padding-bottom: 20px;">
        <div class="column q-gutter-md">
            <div
            v-for="(nozzle, index) in nozzles"
            :key="index"
            class="q-pa-md q-mb-sm q-rounded-borders"
            style="background: #f9f9f9; border: 1px solid #ddd;"
            >
            <div class="row q-col-gutter-md q-wrap">
            <q-input
            v-model="nozzles[index].nozzleNo"
            label="Nozzle No"
            outlined
            dense
            class="col"
            />

            <q-input
            v-model="nozzles[index].size"
            label="Size"
            outlined
            dense
            class="col"
            />

            <q-select
            v-model="nozzles[index].drillingStandard"
            :options="['-','ASA150#', 'PN-10 DIN 2673']"
            label="Drilling Standard"
            outlined
            dense
            class="col"
            />

            <q-input
            v-model="nozzles[index].degree"
            label="Degree"
            outlined
            dense
            class="col"
            />

            <q-input
            v-model="nozzles[index].radius"
            label="Radius"
            outlined
            dense
            class="col"
            />

            <q-input
            v-model="nozzles[index].location"
            label="Location"
            outlined
            dense
            class="col"
            />
            <div class="col-12">
                <div class="text-subtitle2 q-mb-sm">Fittings</div>

                <div class="row q-gutter-sm items-center">
                    <!-- Each fitting input -->
                    <div
                    v-for="(fitting, fitIndex) in nozzle.fittings"
                    :key="fitIndex"
                    class="row items-center"
                    style="max-width: 250px;"
                    >
                    <q-input
                      :model-value="formatFittingLabel(fitting)"
                      label="Fitting"
                      outlined
                      dense
                      class="col"
                      style="min-width: 180px;"
                      disable
                    />
                    <q-btn
                        icon="close"
                        color="negative"
                        dense
                        flat
                        @click="removeFitting(index, fitIndex)"
                        class="q-ml-xs"
                    />
                    </div>

                    <!-- Add fitting button -->
                    <q-btn
                    icon="add"
                    color="primary"
                    dense
                    flat
                    @click="addFitting(index)"
                    class="q-ml-sm"
                    label="Add Fitting"
                    />
                </div>
                </div>
            </div>
            </div>
        </div>
        </div>
    </div>
  </div>

  <div class="q-pa-md q-gutter-sm">
    <q-dialog v-model="isFitting" persistent>
        <q-card style="min-width: 500px">
          <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Fittings</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-card-section>
          <div class="q-mb-md">
            <div class="row q-gutter-md q-wrap">
              <q-select
              outlined
              v-model="fitting"
              :options="fittingsOptions"
              @update:model-value="onUpdateFittings"
              label="Fittings"
              dense
              class="col-12 col-md-5"
            />
            <q-space/>
            <q-btn outline rounded icon="search" color="primary" label="Search" @click="searchFittings(fitting)"/>
            </div>
          </div>
        </q-card-section>

        <!-- Split Flange -->
        <q-card-section v-if="isSplitFlange" class="q-pt-none">
          <div class="q-mb-md">
            <div class="row q-gutter-md q-wrap">
              <q-select
                outlined
                v-model="splitFlangetype"
                :options="splitFlangeTypeOptions"
                label="Type"
                dense
                class="col-12 col-md-3"
              />
              <q-input
                outlined
                v-model="splitFlangeSize"
                type="number"
                label="Size"
                dense
                class="col-12 col-md-3"
              />
              <q-select
                outlined
                v-model="splitFlangeMaterial"
                :options="splitFlangeMaterialOptions"
                label="Material"
                dense
                class="col-12 col-md-3"
              />
              <q-select
                outlined
                v-model="splitFlangeRatings"
                :options="splitFlangeRatingsOptions"
                label="Ratings"
                dense
                class="col-12 col-md-3"
              />
              <q-input
                outlined
                v-model="splitFlangeOther"
                label="Other/Additional Information"
                dense
                class="col-12 col-md-3"
              />
            </div>
          </div>
        </q-card-section>

        <!-- Gasket -->
        <q-card-section v-if="isGasket" class="q-pt-none">
          <!-- <q-input dense v-model="address" autofocus @keyup.enter="prompt = false" /> -->  
          <div class="q-mb-md">
            <div class="row q-gutter-md q-wrap">
              <q-input
                outlined
                v-model="gasketSize"
                type="number"
                label="Size"
                dense
                class="col-12 col-md-3"
              />
              <q-select
                outlined
                v-model="gasketMaterial"
                :options="gasketMaterialOptions"
                label="Material"
                dense
                class="col-12 col-md-3"
              />
              <q-input
                outlined
                v-model="gasketOther"
                label="Other/Additional Information"
                dense
                class="col-12 col-md-3"
              />
            </div>
          </div>
        </q-card-section>

        <!-- Blind Cover -->
        <q-card-section v-if="isBlindCover" class="q-pt-none">
          <div class="q-mb-md">
            <div class="row q-gutter-md q-wrap">
              <q-input
                outlined
                v-model="blindCoverSize"
                type="number"
                label="Size"
                dense
                class="col-12 col-md-3"
              />
              <q-select
                outlined
                v-model="blindCoverMaterial"
                :options="blindCoverMaterialOptions"
                label="Material"
                dense
                class="col-12 col-md-3"
              />
              <q-select
                outlined
                v-model="blindCoverRatings"
                :options="blindCoverRatingsOptions"
                label="Ratings"
                dense
                class="col-12 col-md-3"
              />
              <q-input
                outlined
                v-model="blindCoverOther"
                label="Other/Additional Information"
                dense
                class="col-12 col-md-3"
              />
            </div>
          </div>
        </q-card-section>

        <!-- Reducing Flange-->
        <q-card-section v-if="isReducingFlange" class="q-pt-none">
          <div class="q-mb-md">
            <div class="row q-gutter-md q-wrap">
              <q-input
                outlined
                v-model="reducingFlangeSize"
                type="number"
                label="Size"
                dense
                class="col-12 col-md-3"
              />
              <q-select
                outlined
                v-model="reducingFlangeMaterial"
                :options="reducingFlangeMaterialOptions"
                label="Material"
                dense
                class="col-12 col-md-3"
              />
              <q-select
                outlined
                v-model="reducingFlangeRatings"
                :options="reducingFlangeRatingsOptions"
                label="Ratings"
                dense
                class="col-12 col-md-3"
              />
              <q-input
                outlined
                v-model="reducingFlangeOther"
                label="Other/Additional Information"
                dense
                class="col-12 col-md-3"
              />
            </div>
          </div>
        </q-card-section>

        <!-- Dip Pipe-->
        <q-card-section v-if="isDipPipe" class="q-pt-none">
          <div class="q-mb-md">
            <div class="row q-gutter-md q-wrap">
              <q-select
                outlined
                v-model="dipPipeType"
                :options="dipPipeTypeOptions"
                label="Type"
                dense
                class="col-12 col-md-3"
              />
              <q-input
                outlined
                v-model="dipPipeSize"
                type="number"
                label="Size"
                dense
                class="col-12 col-md-3"
              />
              <q-select
                outlined
                v-model="dipPipeMaterial"
                :options="dipPipeMaterialOptions"
                label="Material"
                dense
                class="col-12 col-md-3"
              />
              <q-select
                outlined
                v-model="dipPipeRatings"
                :options="dipPipeRatingsOptions"
                label="Ratings"
                dense
                class="col-12 col-md-3"
              />
              <q-input
                outlined
                v-model="dipPipeLength"
                label="Length"
                dense
                class="col-12 col-md-3"
              />
              <q-input
                outlined
                v-model="dipPipeOther"
                label="Other/Additional Information"
                dense
                class="col-12 col-md-3"
              />
            </div>
          </div>
        </q-card-section>

        <!-- Sparger-->
        <q-card-section v-if="isSparger" class="q-pt-none">
          <div class="q-mb-md">
            <div class="row q-gutter-md q-wrap">
              <q-input
                outlined
                v-model="spargerSize"
                type="number"
                label="Size"
                dense
                class="col-12 col-md-3"
              />
              <q-select
                outlined
                v-model="spargerMaterial"
                :options="spargerMaterialOptions"
                label="Material"
                dense
                class="col-12 col-md-3"
              />
              <q-select
                outlined
                v-model="spargerRatings"
                :options="spargerRatingsOptions"
                label="Ratings"
                dense
                class="col-12 col-md-3"
              />
              <q-input
                outlined
                v-model="spargerLength"
                label="Length"
                dense
                class="col-12 col-md-3"
              />
              <q-input
                outlined
                v-model="spargerOther"
                label="Other/Additional Information"
                dense
                class="col-12 col-md-3"
              />
            </div>
          </div>
        </q-card-section>

        <!-- Spray Ball Pipe-->
        <q-card-section v-if="isSprayBallPipe" class="q-pt-none">
          <div class="q-mb-md">
            <div class="row q-gutter-md q-wrap">
              <q-input
                outlined
                v-model="sprayBallPipeSize"
                type="number"
                label="Size"
                dense
                class="col-12 col-md-3"
              />
              <q-select
                outlined
                v-model="sprayBallPipeMaterial"
                :options="sprayBallPipeMaterialOptions"
                label="Material"
                dense
                class="col-12 col-md-3"
              />
              <q-select
                outlined
                v-model="sprayBallPipeRatings"
                :options="sprayBallPipeRatingsOptions"
                label="Ratings"
                dense
                class="col-12 col-md-3"
              />
              <q-input
                outlined
                v-model="sprayBallPipeLength"
                label="Length"
                dense
                class="col-12 col-md-3"
              />
              <q-input
                outlined
                v-model="sprayBallPipeOther"
                label="Other/Additional Information"
                dense
                class="col-12 col-md-3"
              />
            </div>
          </div>
        </q-card-section>

        <!-- Spray Ball-->
        <q-card-section v-if="isSprayBall" class="q-pt-none">
          <div class="q-mb-md">
            <div class="row q-gutter-md q-wrap">
              <q-select
                outlined
                v-model="sprayBallMake"
                :options="sprayBallMakeOptions"
                label="Make"
                dense
                class="col-12 col-md-3"
              />
              <q-select
                outlined
                v-model="sprayBallModel"
                :options="sprayBallModelOptions"
                label="Material"
                dense
                class="col-12 col-md-3"
              />
              <q-input
                outlined
                v-model="sprayBallSize"
                type="number"
                label="Size"
                dense
                class="col-12 col-md-3"
              />
              <q-input
                outlined
                v-model="sprayBallOther"
                label="Other/Additional Information"
                dense
                class="col-12 col-md-3"
              />
            </div>
          </div>
        </q-card-section>

        <!-- Tee-->
        <q-card-section v-if="isTee" class="q-pt-none">
          <div class="q-mb-md">
            <div class="row q-gutter-md q-wrap">
              <q-input
                outlined
                v-model="teeSize"
                type="number"
                label="Size"
                dense
                class="col-12 col-md-3"
              />
              <q-select
                outlined
                v-model="teeMaterial"
                :options="teeMaterialOptions"
                label="Material"
                dense
                class="col-12 col-md-3"
              />
              <q-select
                outlined
                v-model="teeRatings"
                :options="teeRatingsOptions"
                label="Ratings"
                dense
                class="col-12 col-md-3"
              />
              <q-input
                outlined
                v-model="teeLength"
                label="Length"
                dense
                class="col-12 col-md-3"
              />
              <q-input
                outlined
                v-model="teeOther"
                label="Other/Additional Information"
                dense
                class="col-12 col-md-3"
              />
            </div>
          </div>
        </q-card-section>

        <!-- Protection Ring -->
        <q-card-section v-if="isProtectionRing" class="q-pt-none">
          <div class="q-mb-md">
            <div class="row q-gutter-md q-wrap">
              <q-input
                outlined
                v-model="protectionRingSize"
                type="number"
                label="Size"
                dense
                class="col-12 col-md-3"
              />
              <q-select
                outlined
                v-model="protectionRingMaterial"
                :options="protectionRingMaterialOptions"
                label="Material"
                dense
                class="col-12 col-md-3"
              />
              <q-select
                outlined
                v-model="protectionRingType"
                :options="protectionRingTypeOptions"
                label="Type"
                dense
                class="col-12 col-md-3"
              />
              <q-input
                outlined
                v-model="protectionRingOther"
                label="Other/Additional Information"
                dense
                class="col-12 col-md-3"
              />
            </div>
          </div>
        </q-card-section>

        <!-- Manhole Cover-->
        <q-card-section v-if="isManholeCover" class="q-pt-none">
          <div class="q-mb-md">
            <div class="row q-gutter-md q-wrap">
              <q-input
                outlined
                v-model="manholeCoverSize"
                type="number"
                label="Size"
                dense
                class="col-12 col-md-3"
              />
              <q-select
                outlined
                v-model="manholeMaterial"
                :options="manholeMaterialOptions"
                label="Material"
                dense
                class="col-12 col-md-3"
              />
              <q-select
                outlined
                v-model="manholeLiningType"
                :options="manholeLiningTypeOptions"
                label="Type - Lining"
                dense
                class="col-12 col-md-3"
              />
              <q-select
                outlined
                v-model="manholeType"
                :options="manholeTypeOptions"
                label="Type"
                dense
                class="col-12 col-md-3"
              />
              <q-input
                outlined
                v-model="manholeOther"
                label="Other/Additional Information"
                dense
                class="col-12 col-md-3"
              />
            </div>
          </div>
        </q-card-section>

        <!-- Toughened Glass-->
        <q-card-section v-if="isToughenedGlass" class="q-pt-none">
          <div class="q-mb-md">
            <div class="row q-gutter-md q-wrap">
              <q-input
                outlined
                v-model="toughenedGlassSize"
                type="number"
                label="Size"
                dense
                class="col-12 col-md-3"
              />
              <q-select
                outlined
                v-model="toughenedGlassMaterial"
                :options="toughenedGlassMaterialOptions"
                label="Material"
                dense
                class="col-12 col-md-3"
              />
              <q-input
                outlined
                v-model="toughenedGlassOther"
                label="Other/Additional Information"
                dense
                class="col-12 col-md-3"
              />
            </div>
          </div>
        </q-card-section>

        <!-- Sight/Light Glass Flange -->
        <q-card-section v-if="isGlassFlange" class="q-pt-none">
          <div class="q-mb-md">
            <div class="row q-gutter-md q-wrap">
              <q-input
                outlined
                v-model="glassFlangeSize"
                type="number"
                label="Size"
                dense
                class="col-12 col-md-3"
              />
              <q-select
                outlined
                v-model="glassFlangeMaterial"
                :options="glassFlangeMaterialOptions"
                label="Material"
                dense
                class="col-12 col-md-3"
              />
              <q-input
                outlined
                v-model="glassFlangeOther"
                label="Other/Additional Information"
                dense
                class="col-12 col-md-3"
              />
            </div>
          </div>
        </q-card-section>

        <!-- Extension Piece -->
        <q-card-section v-if="isExtensionPiece" class="q-pt-none">
          <div class="q-mb-md">
            <div class="row q-gutter-md q-wrap">
              <q-input
                outlined
                v-model="extensionPieceSize"
                type="number"
                label="Size"
                dense
                class="col-12 col-md-3"
              />
              <q-select
                outlined
                v-model="extensionPieceMaterial"
                :options="extensionPieceMaterialOptions"
                label="Material"
                dense
                class="col-12 col-md-3"
              />
              <q-input
                outlined
                v-model="extensionPieceLength"
                label="Length"
                dense
                class="col-12 col-md-3"
              />
              <q-input
                outlined
                v-model="extensionPieceOther"
                label="Other/Additional Information"
                dense
                class="col-12 col-md-3"
              />
            </div>
          </div>
        </q-card-section>

        <!-- Baffle -->
        <q-card-section v-if="isBaffle" class="q-pt-none">
          <div class="q-mb-md">
            <div class="row q-gutter-md q-wrap">
              <q-select
                outlined
                v-model="baffleType"
                :options="baffleTypeOptions"
                label="Type"
                dense
                class="col-12 col-md-3"
              />
              <q-select
                outlined
                v-model="baffleTipType"
                :options="baffleTipTypeOptions"
                label="Tip Type"
                dense
                class="col-12 col-md-3"
              />
              <q-input
                outlined
                v-model="baffleMountingNozzle"
                type="number"
                label="Mounting Nozzle"
                dense
                class="col-12 col-md-3"
              />
              <q-input
                outlined
                v-model="baffleImmersionLength"
                type="number"
                label="Immersion Length"
                dense
                class="col-12 col-md-3"
              />
              <q-input
                outlined
                v-model="baffleOther"
                label="Other/Additional Information"
                dense
                class="col-12 col-md-3"
              />
            </div>
          </div>
        </q-card-section>

        <!-- Thermowell -->
        <q-card-section v-if="isThermowell" class="q-pt-none">
          <div class="q-mb-md">
            <div class="row q-gutter-md q-wrap">
              <q-select
                outlined
                v-model="thermowellType"
                :options="thermowellTypeOptions"
                label="Type"
                dense
                class="col-12 col-md-3"
              />
              <q-select
                outlined
                v-model="thermowellTipType"
                :options="thermowellTipTypeOptions"
                label="Tip Type"
                dense
                class="col-12 col-md-3"
              />
              <q-input
                outlined
                v-model="thermowellMountingNozzle"
                type="number"
                label="Mounting Nozzle"
                dense
                class="col-12 col-md-3"
              />
              <q-input
                outlined
                v-model="thermowellImmersionLength"
                type="number"
                label="Immersion Length"
                dense
                class="col-12 col-md-3"
              />
              <q-input
                outlined
                v-model="thermowellOther"
                label="Other/Additional Information"
                dense
                class="col-12 col-md-3"
              />
            </div>
          </div>
        </q-card-section>

        <!-- Bottom Outlet Valve -->
        <q-card-section v-if="isBOV" class="q-pt-none">
          <div class="q-mb-md">
            <div class="row q-gutter-md q-wrap">
              <q-select
                outlined
                v-model="bovType"
                :options="bovTypeOptions"
                @update:model-value="onUpdateBovType"
                label="Type"
                dense
                class="col-12 col-md-3"
              />
              <q-select
                outlined
                v-model="bovModel"
                :options="bovModelOptions"
                @update:model-value="onUpdateBovModel"
                label="Model"
                dense
                class="col-12 col-md-3"
              />
              <q-select
                outlined
                v-model="bovGasket"
                :options="bovGasketOptions"
                label="Gasket"
                dense
                class="col-12 col-md-3"
              />
              <q-select
                outlined
                v-model="bovFastenersMaterial"
                :options="bovFastenersMaterialOptions"
                label="Fastener Materials"
                dense
                class="col-12 col-md-3"
              />
              <q-select
                outlined
                v-model="bovActuatorType"
                :options="bovActuatorTypeOptions"
                label="Actautor Type/Make"
                dense
                class="col-12 col-md-3"
              />
              <q-select
                outlined
                v-model="bovSplitFlangeMaterial"
                :options="bovSplitFlangeMaterialOptions"
                label="Split Flange Material"
                dense
                class="col-12 col-md-3"
              />
              <q-input
                outlined
                v-model="bovProximitySwitch"
                type="number"
                label="Proxomity/Limit Switch"
                :disable="bovActuatorType === '-'"
                dense
                class="col-12 col-md-3"
              />
              <q-input
                outlined
                v-model="bovSOV"
                type="number"
                label="SOV Type/Make"
                :disable="bovActuatorType === '-'"
                dense
                class="col-12 col-md-3"
              />
              <q-input
                outlined
                v-model="bovAFR"
                label="AFR Type/Make"
                :disable="bovActuatorType === '-'"
                dense
                class="col-12 col-md-3"
              />
              <q-input
                outlined
                v-model="bovRTD"
                type="number"
                label="RTD Type/Make"
                dense
                class="col-12 col-md-3"
              />
              <q-input
                outlined
                v-model="bovOther"
                label="Other/Additional Information"
                dense
                class="col-12 col-md-3"
              />
            </div>
          </div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <!-- <q-input dense v-model="address" autofocus @keyup.enter="prompt = false" /> -->  
          <div class="q-mb-md">
          <div class="row q-gutter-md q-wrap">
            <q-chip v-if="true" outline square color="blue-5" text-color="white">
              {{ "Drawing Number: " + fittingDrawingNumber }}
            </q-chip>
            <q-chip v-if="true" outline square color="blue-5" text-color="white">
              {{ "Item Code: " + fittingItemCode }}
            </q-chip>
          </div>
        </div>
        </q-card-section>

        <q-card-actions align="right" class="text-primary">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn flat label="Submit" v-close-popup @click="addObjectToList(fitting)" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>


<script>
import { ref } from 'vue'
import { useQuasar } from 'quasar'
export default {
  name: 'MonoblockComponent',
  props: {
    monoblock: Object,
    fittingsData: Object,
    bovMasters: Object
  },
  emits: ['search-data', 'get-bov-masters'],
  mounted() {

    const localData = this.loadFromLocalStorage('MonoblockComponent')

    if (localData) {
      this.fillMonoBlockData(localData);  // Load from local storage
    } else {
      if (this.monoblock !== null) {
        this.fillData(this.monoblock);
      }
      if (this.monoblock?.data) {
        this.fillMonoBlockData(this.monoblock?.data);
      }
    }

    this.getBovMastrers();
  },
  setup (props, { emit }) {
    const $q = useQuasar()
    // Fittings
    const isFitting = ref(false)
    const fittingsOptions = ref(['-', 
    'Split Flange', 
    'Gasket', 
    'Blind Cover', 
    'Reducing Flange', 
    'Dip Pipe', 
    'Sparger', 
    'Spray Ball Pipe', 
    'Spray Ball', 
    'Tee', 
    'Manhole Protection Ring', 
    'Manhole Cover', 
    'Toughened Glass', 
    'Sight/Light Glass Flange',
    'Extension Piece',
    'Baffle',
    'Thermowell'])
    const fitting = ref(fittingsOptions.value[0])
    const fittingDrawingNumber = ref(null)
    const fittingItemCode = ref(null)
    
    const isSplitFlange = ref(false)
    const splitFlangetype = ref(null)
    const splitFlangeTypeOptions = ref(['-', 'Tapped', 'Drilled'])
    const splitFlangeMaterial = ref(null)
    const splitFlangeMaterialOptions = ref(['-', 'MS', 'SS304', 'SS316'])
    const splitFlangeSize = ref(null)
    const splitFlangeRatings = ref(null)
    const splitFlangeRatingsOptions = ref(['-', 'ASA', 'DIN'])
    const splitFlangeOther = ref(null)

    const fittingIndex = ref(null)
    const isGasket = ref(false)
    const gasketSize = ref(null)
    const gasketMaterial = ref(null)
    const gasketMaterialOptions = ref(['-', 'Non-Asbestos', 'MS', 'SS304', 'SS316'])
    const gasketOther = ref(null)
    
    const isBlindCover = ref(false)
    const blindCoverSize = ref(null)
    const blindCoverMaterial = ref(null)
    const blindCoverMaterialOptions = ref(['-', 'MS', 'SS304', 'SS316'])
    const blindCoverRatings = ref(null)
    const blindCoverRatingsOptions = ref(['-', 'ASA', 'DIN'])
    const blindCoverOther = ref(null)

    const isReducingFlange = ref(false)
    const reducingFlangeSize = ref(null)
    const reducingFlangeMaterial = ref(null)
    const reducingFlangeMaterialOptions = ref(['-', 'MS', 'SS304', 'SS316'])
    const reducingFlangeRatings = ref(null)
    const reducingFlangeRatingsOptions = ref(['-', 'ASA', 'DIN'])
    const reducingFlangeOther = ref(null)

    const isDipPipe = ref(false)
    const dipPipeType = ref(null)
    const dipPipeTypeOptions = ref(['-', 'Type1', 'Type2'])
    const dipPipeSize = ref(null)
    const dipPipeMaterial = ref(null)
    const dipPipeMaterialOptions = ref(['-', 'MS', 'SS304', 'SS316'])
    const dipPipeRatings = ref(null)
    const dipPipeRatingsOptions = ref(['-', 'ASA', 'DIN'])
    const dipPipeLength = ref(null)
    const dipPipeOther = ref(null)

    const isSparger = ref(false)
    const spargerSize = ref(null)
    const spargerMaterial = ref(null)
    const spargerMaterialOptions = ref(['-', 'MS', 'SS304', 'SS316'])
    const spargerRatings = ref(null)
    const spargerRatingsOptions = ref(['-', 'ASA', 'DIN'])
    const spargerLength = ref(null)
    const spargerOther = ref(null)

    const isSprayBallPipe = ref(false)
    const sprayBallPipeSize = ref(null)
    const sprayBallPipeMaterial = ref(null)
    const sprayBallPipeMaterialOptions = ref(['-', 'MS', 'SS304', 'SS316'])
    const sprayBallPipeRatings = ref(null)
    const sprayBallPipeRatingsOptions = ref(['-', 'ASA', 'DIN'])
    const sprayBallPipeLength = ref(null)
    const sprayBallPipeOther = ref(null)

    const isSprayBall = ref(false)
    const sprayBallMake = ref(null)
    const sprayBallMakeOptions = ref([])
    const sprayBallSize = ref(null)
    const sprayBallModel = ref(null)
    const sprayBallModelOptions = ref(['-', 'MS', 'SS304', 'SS316'])
    const sprayBallOther = ref(null)

    const isTee = ref(false)
    const teeSize = ref(null)
    const teeMaterial = ref(null)
    const teeMaterialOptions = ref(['-', 'MS', 'SS304', 'SS316'])
    const teeRatings = ref(null)
    const teeRatingsOptions = ref(['-', 'ASA', 'DIN'])
    const teeLength = ref(null)
    const teeOther = ref(null)

    const isProtectionRing = ref(false)
    const protectionRingSize = ref(null)
    const protectionRingMaterial = ref(null)
    const protectionRingMaterialOptions = ref(['-', 'MS', 'SS304', 'SS316'])
    const protectionRingType = ref(null)
    const protectionRingTypeOptions = ref(['-', 'Type1', 'Type2'])
    const protectionRingOther = ref(null)

    const isManholeCover = ref(false)
    const manholeCoverSize = ref(null)
    const manholeLiningType = ref(null)
    const manholeLiningTypeOptions = ref(['-', 'Glass Lined', 'PFA Lined'])
    const manholeMaterial = ref(null)
    const manholeMaterialOptions = ref(['-', 'MS', 'SS304', 'SS316'])
    const manholeType = ref(null)
    const manholeTypeOptions = ref(['-', 'Dome with pad type', 'Dome with nozzle', 'Flat'])
    const manholeOther = ref(null)

    const isToughenedGlass = ref(false)
    const toughenedGlassSize = ref(null)
    const toughenedGlassMaterial = ref(null)
    const toughenedGlassMaterialOptions = ref(['-', 'MS', 'SS304', 'SS316'])
    const toughenedGlassOther = ref(null)

    const isGlassFlange = ref(false)
    const glassFlangeSize = ref(null)
    const glassFlangeMaterial = ref(null)
    const glassFlangeMaterialOptions = ref(['-', 'MS', 'SS304', 'SS316'])
    const glassFlangeOther = ref(null)

    const isExtensionPiece = ref(false)
    const extensionPieceSize = ref(null)
    const extensionPieceMaterial = ref(null)
    const extensionPieceMaterialOptions = ref(['-', 'MS', 'SS304', 'SS316'])
    const extensionPieceLength = ref(null)
    const extensionPieceOther = ref(null)

    const isBaffle = ref(false)
    const baffleType = ref(null)
    const baffleTypeOptions = ref(['-','Flange', 'Pfaudler', 'C-Baffle', 'Fingure', 'Loose Flange'])
    const baffleTipType = ref(null)
    const baffleTipTypeOptions = ref(['-', 'Tantalum Tip', 'Hastalloy Tip', 'Glass Tip', 'Without Tip'])
    const baffleMountingNozzle = ref(null)
    const baffleImmersionLength = ref(null)
    const baffleOther = ref(null)

    const isThermowell = ref(false)
    const thermowellType = ref(null)
    const thermowellTypeOptions = ref(['-','Angular', 'Straight', 'Loose Flange'])
    const thermowellTipType = ref(null)
    const thermowellTipTypeOptions = ref(['-', 'Tantalum Tip', 'Hastalloy Tip', 'Glass Tip', 'Without Tip'])
    const thermowellMountingNozzle = ref(null)
    const thermowellImmersionLength = ref(null)
    const thermowellOther = ref(null)

    const isBOV = ref(false)
    const bovType = ref(null)
    const bovTypeOptions = ref(['-', 'Gland', 'Bellow'])
    const bovModel = ref(null)
    const bovModelOptions = ref([])
    const bovGasket = ref(null)
    const bovGasketOptions = ref([])
    const bovFastenersMaterial = ref(null)
    const bovFastenersMaterialOptions = ref([])
    const bovActuatorType = ref(null)
    const bovActuatorTypeOptions = ref([])
    const bovSplitFlangeMaterial = ref(null)
    const bovSplitFlangeMaterialOptions = ref([])
    const bovProximitySwitch = ref(null)
    const bovAFR = ref(null)
    const bovRTD = ref(null)
    const bovSOV = ref(null)
    const bovOther = ref(null)
    const bovModelTypeSize = ref([{model: '201', type: 'Gland', size: '100', actuator: null},
        {model: '201', type: 'Gland', size: '100', actuator: null},
        {model: '202', type: 'Gland', size: '80', actuator: null},
        {model: '203', type: 'Gland', size: '50', actuator: null},
        {model: '204', type: 'Gland', size: '150', actuator: null},
        {model: '901', type: 'Gland', size: '100', actuator: ['VKE']},
        {model: '902', type: 'Gland', size: '80', actuator: ['VKE']},
        {model: '903', type: 'Gland', size: '50', actuator: ['VKE']},
        {model: '904', type: 'Gland', size: '150', actuator: ['VKE']},
        {model: '2801', type: 'Gland', size: '100', actuator: null},
        {model: '2802', type: 'Gland', size: '80', actuator: null},
        {model: '2803', type: 'Gland', size: '50', actuator: null},
        {model: '2804', type: 'Gland', size: '150', actuator: null},
        {model: '701', type: 'Gland', size: '100', actuator: null},
        {model: '702', type: 'Gland', size: '80', actuator: null},
        {model: '703', type: 'Gland', size: '50', actuator: null},
        {model: '704', type: 'Gland', size: '150', actuator: null},
        {model: '1701', type: 'Gland', size: '100', actuator: ['VKE']},
        {model: '1702', type: 'Gland', size: '80', actuator: ['VKE']},
        {model: '1703', type: 'Gland', size: '50', actuator: ['VKE']},
        {model: '1704', type: 'Gland', size: '150', actuator: ['VKE']},
        {model: '801', type: 'Gland', size: '100', actuator: null},
        {model: '802', type: 'Gland', size: '80', actuator: null},
        {model: '803', type: 'Gland', size: '50', actuator: null},
        {model: '804', type: 'Gland', size: '150', actuator: null},
        {model: '1901', type: 'Gland', size: '100', actuator: ['VKE']},
        {model: '1902', type: 'Gland', size: '80', actuator: ['VKE']},
        {model: '1903', type: 'Gland', size: '50', actuator: ['VKE']},
        {model: '1904', type: 'Gland', size: '150', actuator: ['VKE']},
        {model: '301', type: 'Bellow', size: '100', actuator: null},
        {model: '302', type: 'Bellow', size: '80', actuator: null},
        {model: '303', type: 'Bellow', size: '50', actuator: null},
        {model: '304', type: 'Bellow', size: '150', actuator: null},
        {model: '401', type: 'Bellow', size: '100', actuator: ['VKE']},
        {model: '402', type: 'Bellow', size: '80', actuator: ['VKE']},
        {model: '403', type: 'Bellow', size: '50', actuator: ['VKE']},
        {model: '404', type: 'Bellow', size: '150', actuator: ['VKE']},
        {model: '1801', type: 'Bellow', size: '100', actuator: ['Demble', 'Aira']},
        {model: '1802', type: 'Bellow', size: '80', actuator: ['Demble', 'Aira']},
        {model: '1803', type: 'Bellow', size: '50', actuator: ['Demble', 'Aira']},
        {model: '1804', type: 'Bellow', size: '150', actuator: ['Demble', 'Aira']},
        {model: '601', type: 'Bellow', size: '100', actuator: null},
        {model: '602', type: 'Bellow', size: '80', actuator: null},
        {model: '603', type: 'Bellow', size: '50', actuator: null},
        {model: '604', type: 'Bellow', size: '150', actuator: null},
        {model: '501', type: 'Bellow', size: '100', actuator: ['VKE']},
        {model: '502', type: 'Bellow', size: '80', actuator: ['VKE']},
        {model: '503', type: 'Bellow', size: '50', actuator: ['VKE']},
        {model: '504', type: 'Bellow', size: '150', actuator: ['VKE']},
        {model: '2701', type: 'Bellow', size: '100', actuator: ['Demble', 'Aira']},
        {model: '2702', type: 'Bellow', size: '80', actuator: ['Demble', 'Aira']},
        {model: '2703', type: 'Bellow', size: '50', actuator: ['Demble', 'Aira']},
        {model: '2704', type: 'Bellow', size: '150', actuator: ['Demble', 'Aira']},
    ])

    const insulationOnTop = ref(null) 
    const insulationOnTopOptions = ref(["-", "Yes", "No"])
    const id = ref(null)
    const osTos = ref(null)
    const topDishedEndThickness = ref(null)
    const innerShellThickness = ref(null)
    const bottomDishedEndThickness = ref(null)
    const spilageCollectionTray = ref(null)
    const spilageCollectionTrayOptions = ref(["-", "Yes", "No"])
    const liftingMOC = ref(null)
    const liftingMOCOptions = ref(["-", "MS", "SS304", "SS316"])
    const modelType = ref("Standard")
    const modelTypeOptions = ref(["-", "Standard", "Non-Standard"])
    const nozzles = ref([])
    const standardDegree = ref(['0', '60', '95', '135', '180', '225', '265', '300', '-', '-'])
    
    // const statndardFittings = ref([])
    // ['DN500 Gasket', 'PTFE Bush Type Ring', 'Manhole Cover', 'DN100 Gasket', 'DN100 Toughened Glass', 'DN100 Sight Glass Flange'],
    // ['DN150 Split Flange', 'DN150 gasket', 'DN150 Wooden Blind Cover'],
    // ['DN150 Split Flange', 'DN150 gasket', 'DN150 Wooden Blind Cover'],
    // ['DN250 Split Flange', 'DN250 gasket', 'DN150 Wooden Blind Cover'],
    // ['DN150 Split Flange', 'DN150 gasket', 'DN150 Toughened Glass', 'DN150 Light Glass Flange'],
    // ['DN250 Split Flange', 'DN250 gasket', 'Baffle'],
    // ['DN150 Split Flange', 'DN150 gasket', 'DN150 Wooden Blind Cover'],
    // ['DN150 Split Flange', 'DN150 gasket', 'DN150 Wooden Blind Cover'],
    // ['Mechanical Seal', 'Agitator', 'Pad Plate'],
    // ['DN150 Split Flange', 'DN150 Gasket', 'BOV']

    const addNozzle = () => {
      nozzles.value.push({
        nozzleNo: '',
        size: '',
        drillingStandard: '-',
        degree: '-',
        radius: '-',
        location: '',
        fittings: []
      })
    }

    const removeNozzle = () => {
      nozzles.value.pop()
    }

    function addFitting(nozzleIndex) {
      //  nozzles.value[nozzleIndex].fittings.push('');
       fitting.value = '-'
       onUpdateFittings(fitting.value)
       isFitting.value = true
       fittingIndex.value = nozzleIndex
       const currentNozzleSize = nozzles.value[fittingIndex.value].size
       const index = fittingsOptions.value.indexOf('BOV');
       if(currentNozzleSize <= '150'){
        if (index === -1) {
          fittingsOptions.value.push('BOV')
        }
       }
      //  else if(currentNozzleSize === '500' || currentNozzleSize === '600' || currentNozzleSize === '350x450'){
      //   fittingsOptions.value.splice(fittingsOptions.value.length, 0)
      //   fittingsOptions.value = ['Gasket', 'Manhole Cover']
      //  }
       else{
        if (index !== -1) {
          fittingsOptions.value.splice(index, 1);
        }
       }
    }

    function removeFitting(nozzleIndex, fittingIndex) {
        nozzles.value[nozzleIndex].fittings.splice(fittingIndex, 1);
    }

    const searchMonoblockData = () => {
        const monoblcockData = prepareMonoblockData()
        emit('search-data', monoblcockData)
    }

    const prepareMonoblockData = () => {
        const monoblcockData = {
            component: 'Monoblock',
            id: id.value?id.value.toString():null,
            osTos: osTos.value?osTos.value.toString():null,
            insulationOnTop: insulationOnTop.value?insulationOnTop.value.toString():null,
            spilageCollectionTray: spilageCollectionTray.value?spilageCollectionTray.value.toString():null,
            liftingMOC: liftingMOC.value?liftingMOC.value.toString():null,
            topDishedEndThickness: topDishedEndThickness.value?topDishedEndThickness.value.toString():null,
            innerShellThickness: innerShellThickness.value?innerShellThickness.value.toString():null,
            bottomDishedEndThickness: bottomDishedEndThickness.value?bottomDishedEndThickness.value.toString():null,
            modelType: modelType.value?modelType.value.toString():null,
            nozzles: nozzles.value?nozzles.value:null
        }
        const res = flattenForExcel(monoblcockData)
        return res
    }

    const fillData = (data) => {
        const nozzle_names = JSON.parse(data.nozzle_names)
        const nozzle_sizes = JSON.parse(data.nozzle_sizes)
        const nozzle_locations = JSON.parse(data.nozzle_locations)
        id.value = parseInt(data.id.split(" ")[0])
        osTos.value = data.osTos
        if(data.reactor === 'MSGL Reactor'){
            insulationOnTop.value = insulationOnTopOptions.value[1]
        }else{
            insulationOnTop.value = null
        }
        for (let i = 0; i < nozzle_names.length; i++) {
            nozzles.value.push({
                nozzleNo: nozzle_names[i],
                size: nozzle_sizes[i],
                location: nozzle_locations[i],
                drillingStandard: '-',
                degree: standardDegree.value[i],
                radius: '-',
                fittings: []
            });
        }
    }

    const fillMonoBlockData = (data) => {
        id.value = data.id?data.id:null
        osTos.value = data.osTos?data.osTos:null
        bottomDishedEndThickness.value = data.bottomDishedEndThickness?data.bottomDishedEndThickness:null
        innerShellThickness.value = data.innerShellThickness?data.innerShellThickness:null
        topDishedEndThickness.value = data.topDishedEndThickness?data.topDishedEndThickness:null
        spilageCollectionTray.value = data.spilageCollectionTray?data.spilageCollectionTray:null
        insulationOnTop.value = data.insulationOnTop?data.insulationOnTop:null
        liftingMOC.value = data.liftingMOC?data.liftingMOC:null
        modelType.value = data.modelType?data.modelType:null
        nozzles.value.splice(0, nozzles.value.length)
        const result = {};
        for (const [key, value] of Object.entries(data)) {
            if (key.startsWith("nozzle_")) {
                try {
                result[key] = JSON.parse(value); // Parse JSON strings
                nozzles.value.push({
                    nozzleNo: result[key].nozzleNo,
                    size: result[key].size,
                    location: result[key].location,
                    drillingStandard: result[key].drillingStandard,
                    degree: result[key].degree,
                    radius: result[key].radius,
                    fittings: result[key].fittings
                });
                } catch (e) {
                console.error(`Failed to parse ${key}:`, e);
                result[key] = value;
                }
            } else {
                result[key] = value; // Keep other top-level fields as is
            }
        }
    }

    const flattenForExcel = (obj) => {
        const output = {};

        // Copy top-level properties except 'nozzles'
        for (const key in obj) {
            if (key !== 'nozzles') {
            output[key] = obj[key];
            }
        }

        // Ensure nozzles is plain JS (unwrap Proxy if needed)
        const rawNozzles = JSON.parse(JSON.stringify(obj.nozzles || []));

        // Flatten each nozzle into its own stringified JSON field
        rawNozzles.forEach((nozzle, index) => {
            output[`nozzle_${index}`] = JSON.stringify(nozzle);
        });

        return output;
    }

    // Fittings
    const getBovMastrers = () => {
        const bovMasters = {
            component: 'bov',
            master_material_gasket: null,
            master_material_fasteners_pressure: null,
            master_material_split: null
        }
        emit('get-bov-masters', bovMasters)
    }

    const populateBovMasterData = (masters) => {
        const gasket = masters.master_material_gasket.map(item => item.name)
        bovGasketOptions.value.splice(0, bovGasketOptions.value.length)
        bovGasketOptions.value.push('-')
        bovGasketOptions.value.push(...gasket)

        const fasteners = masters.master_material_fasteners_pressure.map(item => item.name)
        bovFastenersMaterialOptions.value.splice(0, bovFastenersMaterialOptions.value.length)
        bovFastenersMaterialOptions.value.push('-')
        bovFastenersMaterialOptions.value.push(...fasteners)

        const splits = masters.master_material_split.map(item => item.name)
        bovSplitFlangeMaterialOptions.value.splice(0, bovSplitFlangeMaterialOptions.value.length)
        bovSplitFlangeMaterialOptions.value.push('-')
        bovSplitFlangeMaterialOptions.value.push(...splits)

    }

    const onUpdateBovType = (val) => {
        const nozzle = nozzles.value[fittingIndex.value]
        const size = nozzle.size
        const results = bovModelTypeSize.value.filter(item => item.type === val && item.size === size);
        const models = results.map(item => item.model)
        bovModelOptions.value.splice(0, bovModelOptions.value.length)
        bovModelOptions.value.push('-')
        bovModelOptions.value.push(...models)
    }

    const onUpdateBovModel = (val) => {
        const modelObj = bovModelTypeSize.value.filter(item => item.model === val);
        if(modelObj.length === 1){
            if(modelObj[0].actuator !== null && modelObj[0].actuator.length === 1){
                bovActuatorTypeOptions.value.splice(0, bovActuatorTypeOptions.value.length)
                bovActuatorTypeOptions.value.push('-')
                bovActuatorTypeOptions.value.push(...modelObj[0].actuator)
                bovActuatorType.value = bovActuatorTypeOptions.value[1]
            }
            else if(modelObj[0].actuator !== null && modelObj[0].actuator.length === 2){
                bovActuatorTypeOptions.value.splice(0, bovActuatorTypeOptions.value.length)
                bovActuatorType.value = null
                bovActuatorTypeOptions.value.push('-')
                bovActuatorTypeOptions.value.push(...modelObj[0].actuator)
            }
            else if(modelObj[0].actuator === null){
                bovActuatorTypeOptions.value.splice(0, bovActuatorTypeOptions.value.length)
                bovActuatorTypeOptions.value.push('-')
                bovActuatorType.value = bovActuatorTypeOptions.value[0]
            }
        }
        else{
            bovActuatorTypeOptions.value.splice(0, bovActuatorTypeOptions.value)
            bovActuatorTypeOptions.value.push('-')
            bovActuatorType.value = bovActuatorTypeOptions.value[0]
        }
    }

    const onUpdateFittings = (val) => {
      fittingDrawingNumber.value = null
      fittingItemCode.value = null
      let nozzle = null
      if(val === 'Split Flange'){
        isSplitFlange.value = true
        nozzle = nozzles.value[fittingIndex.value]
        splitFlangeSize.value = nozzle.size
      }
      else {
        isSplitFlange.value = false
      }

      if(val === 'Gasket'){
        isGasket.value = true
        nozzle = nozzles.value[fittingIndex.value]
        gasketSize.value = nozzle.size
      }
      else {
        isGasket.value = false
      }

      if(val === 'Blind Cover'){
        isBlindCover.value = true
        nozzle = nozzles.value[fittingIndex.value]
        blindCoverSize.value = nozzle.size
      }
      else {
        isBlindCover.value = false
      }

      if(val === 'Reducing Flange'){
        isReducingFlange.value = true
        nozzle = nozzles.value[fittingIndex.value]
        reducingFlangeSize.value = nozzle.size
      }
      else {
        isReducingFlange.value = false
      }

      if(val === 'Dip Pipe'){
        isDipPipe.value = true
        nozzle = nozzles.value[fittingIndex.value]
        dipPipeSize.value = nozzle.size
      }
      else {
        isDipPipe.value = false
      }

      if(val === 'Sparger'){
        isSparger.value = true
        nozzle = nozzles.value[fittingIndex.value]
        spargerSize.value = nozzle.size
      }
      else {
        isSparger.value = false
      }

      if(val === 'Spray Ball Pipe'){
        isSprayBallPipe.value = true
        nozzle = nozzles.value[fittingIndex.value]
        sprayBallPipeSize.value = nozzle.size
      }
      else {
        isSprayBallPipe.value = false
      }

      if(val === 'Spray Ball'){
        isSprayBall.value = true
        nozzle = nozzles.value[fittingIndex.value]
        sprayBallSize.value = nozzle.size
      }
      else {
        isSprayBall.value = false
      }

      if(val === 'Tee'){
        isTee.value = true
        nozzle = nozzles.value[fittingIndex.value]
        teeSize.value = nozzle.size
      }
      else {
        isTee.value = false
      }

      if(val === 'Manhole Protection Ring'){
        isProtectionRing.value = true
        nozzle = nozzles.value[fittingIndex.value]
        protectionRingSize.value = nozzle.size
      }
      else {
        isProtectionRing.value = false
      }

      if(val === 'Manhole Cover'){
        isManholeCover.value = true
        nozzle = nozzles.value[fittingIndex.value]
        manholeCoverSize.value = nozzle.size
      }
      else {
        isManholeCover.value = false
      }

      if(val === 'Toughened Glass'){
        isToughenedGlass.value = true
        nozzle = nozzles.value[fittingIndex.value]
        toughenedGlassSize.value = nozzle.size
      }
      else {
        isToughenedGlass.value = false
      }

      if(val === 'Sight/Light Glass Flange'){
        isGlassFlange.value = true
        nozzle = nozzles.value[fittingIndex.value]
        glassFlangeSize.value = nozzle.size
      }
      else {
        isGlassFlange.value = false
      }

      if(val === 'Extension Piece'){
        isExtensionPiece.value = true
        nozzle = nozzles.value[fittingIndex.value]
        extensionPieceSize.value = nozzle.size
      }
      else {
        isExtensionPiece.value = false
      }

      if(val === 'Baffle'){
        isBaffle.value = true
      }
      else {
        isBaffle.value = false
      }

      if(val === 'Thermowell'){
        isThermowell.value = true
      }
      else {
        isThermowell.value = false
      }

      if(val === 'BOV'){
        isBOV.value = true
      }
      else {
        isBOV.value = false
      }
      // isSplitFlange.value = val === 'Split Flange'? true: false
      // isGasket.value = val === 'Gasket'? true: false
      // isBlindCover.value = val === 'Blind Cover'? true: false
      // isReducingFlange.value = val === 'Reducing Flange'? true: false
      // isDipPipe.value = val === 'Dip Pipe'? true: false
      // isSparger.value = val === 'Sparger'? true: false
      // isSprayBallPipe.value = val === 'Spray Ball Pipe'? true: false
      // isSprayBall.value = val === 'Spray Ball'? true: false
      // isTee.value = val === 'Tee'? true: false
      // isProtectionRing.value = val === 'Manhole Protection Ring'? true: false
      // isManholeCover.value = val === 'Manhole Cover'? true: false
      // isToughenedGlass.value = val === 'Toughened Glass'? true: false
      // isGlassFlange.value = val === 'Sight/Light Glass Flange'? true: false
      // isExtensionPiece.value = val === 'Extension Piece'? true: false
    }

    const searchFittings = (fitting) => {
      // const nozzleNo = nozzles.value[fittingIndex.value].nozzleNo
      let toSearchObject = null
      if(fitting === 'Split Flange'){
        toSearchObject = {
          component: fitting,
          splitFlangetype: splitFlangetype.value? splitFlangetype.value: null,
          splitFlangeSize: splitFlangeSize.value? splitFlangeSize.value: null,
          splitFlangeMaterial: splitFlangeMaterial.value? splitFlangeMaterial.value: null,
          splitFlangeRatings: splitFlangeRatings.value? splitFlangeRatings.value: null,
          splitFlangeOther: splitFlangeOther.value? splitFlangeOther.value: null
        }
      }
      else if(fitting === 'Gasket'){
        toSearchObject = {
          component: fitting,
          gasketSize: gasketSize.value? gasketSize.value: null,
          gasketMaterial: gasketMaterial.value? gasketMaterial.value: null,
          gasketOther: gasketOther.value? gasketOther.value: null
        }
      }
      else if(fitting === 'Blind Cover'){
        toSearchObject = {
          component: fitting,
          blindCoverSize: blindCoverSize.value? blindCoverSize.value: null,
          blindCoverMaterial: blindCoverMaterial.value? blindCoverMaterial.value: null,
          blindCoverRatings: blindCoverRatings.value? blindCoverRatings.value: null,
          blindCoverOther: blindCoverOther.value? blindCoverOther.value: null
        }
      }
      else if(fitting === 'Reducing Flange'){
        toSearchObject = {
          component: fitting,
          reducingFlangeSize: reducingFlangeSize.value? reducingFlangeSize.value: null,
          reducingFlangeMaterial: reducingFlangeMaterial.value? reducingFlangeMaterial.value: null,
          reducingFlangeRatings: reducingFlangeRatings.value? reducingFlangeRatings.value: null,
          reducingFlangeOther: reducingFlangeOther.value? reducingFlangeOther.value: null
        }
      }
      else if(fitting === 'Dip Pipe'){
        toSearchObject = {
          component: fitting,
          dipPipeType: dipPipeType.value? dipPipeType.value: null,
          dipPipeSize: dipPipeSize.value? dipPipeSize.value: null,
          dipPipeMaterial: dipPipeMaterial.value? dipPipeMaterial.value: null,
          dipPipeRatings: dipPipeRatings.value? dipPipeRatings.value: null,
          dipPipeLength: dipPipeLength.value? dipPipeLength.value: null,
          dipPipeOther: dipPipeOther.value? dipPipeOther.value: null
        }
      }
      else if(fitting === 'Sparger'){
        toSearchObject = {
          component: fitting,
          spargerSize: spargerSize.value? spargerSize.value: null,
          spargerMaterial: spargerMaterial.value? spargerMaterial.value: null,
          spargerRatings: spargerRatings.value? spargerRatings.value: null,
          spargerLength: spargerLength.value? spargerLength.value: null,
          spargerOther: spargerOther.value? spargerOther.value: null
        }
      }
      else if(fitting === 'Spray Ball Pipe'){
        toSearchObject = {
          component: fitting,
          sprayBallPipeSize: sprayBallPipeSize.value? sprayBallPipeSize.value: null,
          sprayBallPipeMaterial: sprayBallPipeMaterial.value? sprayBallPipeMaterial.value: null,
          sprayBallPipeRatings: sprayBallPipeRatings.value? sprayBallPipeRatings.value: null,
          sprayBallPipeLength: sprayBallPipeLength.value? sprayBallPipeLength.value: null,
          sprayBallPipeOther: sprayBallPipeOther.value? sprayBallPipeOther.value: null
        }
      }
      else if(fitting === 'Spray Ball'){
        toSearchObject = {
          component: fitting,
          sprayBallMake: sprayBallMake.value? sprayBallMake.value: null,
          sprayBallModel: sprayBallModel.value? sprayBallModel.value: null,
          sprayBallSize: sprayBallSize.value? sprayBallSize.value: null,
          sprayBallOther: sprayBallOther.value? sprayBallOther.value: null
        }
      }
      else if(fitting === 'Tee'){
        toSearchObject = {
          component: fitting,
          teeSize: teeSize.value? teeSize.value: null,
          teeMaterial: teeMaterial.value? teeMaterial.value: null,
          teeRatings: teeRatings.value? teeRatings.value: null,
          teeLength: teeLength.value? teeLength.value: null,
          teeOther: teeOther.value? teeOther.value: null
        }
      }
      else if(fitting === 'Manhole Protection Ring'){
        toSearchObject = {
          component: fitting,
          protectionRingSize: protectionRingSize.value? protectionRingSize.value: null,
          protectionRingMaterial: protectionRingMaterial.value? protectionRingMaterial.value: null,
          protectionRingType: protectionRingType.value? protectionRingType.value: null,
          protectionRingOther: protectionRingOther.value? protectionRingOther.value: null
        }
      }
      else if(fitting === 'Manhole Cover'){
        toSearchObject = {
          component: fitting,
          manholeCoverSize: manholeCoverSize.value? manholeCoverSize.value: null,
          manholeMaterial: manholeMaterial.value? manholeMaterial.value: null,
          manholeType: manholeType.value? manholeType.value: null,
          manholeLiningType: manholeLiningType.value? manholeLiningType.value: null,
          manholeOther: manholeOther.value? manholeOther.value: null,
        }
      }
      else if(fitting === 'Toughened Glass'){
        toSearchObject = {
          component: fitting,
          toughenedGlassSize: toughenedGlassSize.value? toughenedGlassSize.value: null,
          toughenedGlassMaterial: toughenedGlassMaterial.value? toughenedGlassMaterial.value: null,
          toughenedGlassOther: toughenedGlassOther.value? toughenedGlassOther.value: null,
        }
      }
      else if(fitting === 'Sight/Light Glass Flange'){
        toSearchObject = {
          component: fitting,
          glassFlangeSize: glassFlangeSize.value? glassFlangeSize.value: null,
          glassFlangeMaterial: glassFlangeMaterial.value? glassFlangeMaterial.value: null,
          glassFlangeOther: glassFlangeOther.value? glassFlangeOther.value: null,
        }
      }
      else if(fitting === 'Extension Piece'){
        toSearchObject = {
          component: fitting,
          extensionPieceSize: extensionPieceSize.value? extensionPieceSize.value: null,
          extensionPieceMaterial: extensionPieceMaterial.value? extensionPieceMaterial.value: null,
          extensionPieceLength: extensionPieceLength.value? extensionPieceLength.value: null,
          extensionPieceOther: extensionPieceOther.value? extensionPieceOther.value: null
        }
      }
      else if(fitting === 'Baffle'){
        toSearchObject = {
          component: fitting,
          baffleType: baffleType.value? baffleType.value: null,
          baffleTipType: baffleTipType.value? baffleTipType.value: null,
          baffleMountingNozzle: baffleMountingNozzle.value? baffleMountingNozzle.value: null,
          baffleImmersionLength: baffleImmersionLength.value? baffleImmersionLength.value: null,
          baffleOther: baffleOther.value? baffleOther.value: null
        }
      }
      else if(fitting === 'Thermowell'){
        toSearchObject = {
          component: fitting,
          thermowellType: thermowellType.value? thermowellType.value: null,
          thermowellTipType: thermowellTipType.value? thermowellTipType.value: null,
          thermowellMountingNozzle: thermowellMountingNozzle.value? thermowellMountingNozzle.value: null,
          thermowellImmersionLength: thermowellImmersionLength.value? thermowellImmersionLength.value: null,
          thermowellOther: thermowellOther.value? thermowellOther.value: null
        }
      }
      else if(fitting === 'BOV'){
        toSearchObject = {
          component: fitting,
          bovType: bovType.value? bovType.value: null,
          bovModel: bovModel.value? bovModel.value: null,
          bovGasket: bovGasket.value? bovGasket.value: null,
          bovFastenersMaterial: bovFastenersMaterial.value? bovFastenersMaterial.value: null,
          bovActuatorType: bovActuatorType.value? bovActuatorType.value: null,
          bovSplitFlangeMaterial: bovSplitFlangeMaterial.value? bovSplitFlangeMaterial.value: null,
          bovProximitySwitch: bovActuatorType.value === '-'? '-': bovProximitySwitch.value,
          bovAFR: bovActuatorType.value === '-'? '-': bovAFR.value,
          bovSOV: bovActuatorType.value === '-'? '-': bovSOV.value,
          bovRTD: bovRTD.value? bovRTD.value: null,
          bovOther: bovOther.value? bovOther.value: null
        }
      }
      const isNull = hasNull(toSearchObject)
      if(isNull){
        $q.dialog({
                title: '<span class="text-red">Alert</span>',
                message: `Please enter all the values`,
                color: 'red-5',
                html: true
            });
      }
      else{
        emit('search-data', toSearchObject)
      }
    }

    const fillUpdatedData = (data) => {
      if(data?.fittings){
        console.log(data.fittings.model_info.itemCode)
        fittingDrawingNumber.value = data.fittings.model_info.drawingNumber
        fittingItemCode.value = data.fittings.model_info.itemCode
      }
      else if(data !== null){
        if(data.model_info.drawingNumber !== ""){
          fittingDrawingNumber.value = data.model_info.drawingNumber
        }
        if(data.model_info.itemCode !== ""){
          fittingItemCode.value = data.model_info.itemCode
        }
      }
    }

    const addObjectToList = (fitting) => {
      // Build the fitting data object
      const fittingData = {
        name: fitting || null,
        itemCode: fittingItemCode.value || null,
        drawingNumber: fittingDrawingNumber.value || null,
      }

      // Assign size or specific fields depending on the fitting type
      switch (fitting) {
        case 'Gasket':
          fittingData.size = gasketSize.value
          break

        case 'Split Flange':
          fittingData.size = splitFlangeSize.value
          break

        case 'Blind Cover':
          fittingData.size = blindCoverSize.value
          break

        case 'Reducing Flange':
          fittingData.size = reducingFlangeSize.value
          break

        case 'Dip Pipe':
          fittingData.size = dipPipeSize.value
          break

        case 'Sparger':
          fittingData.size = splitFlangeSize.value
          break

        case 'Spray Ball Pipe':
          fittingData.size = sprayBallPipeSize.value
          break

        case 'Spray Ball':
          fittingData.size = sprayBallSize.value
          break

        case 'Tee':
          fittingData.size = teeSize.value
          break

        case 'Manhole Protection Ring':
          fittingData.size = protectionRingSize.value
          break

        case 'Manhole Cover':
          fittingData.size = manholeCoverSize.value
          break

        case 'Toughened Glass':
          fittingData.size = toughenedGlassSize.value
          break

        case 'Sight/Light Glass Flange':
          fittingData.size = glassFlangeSize.value
          break

        case 'Extension Piece':
          fittingData.size = extensionPieceSize.value
          break

        case 'Baffle':
          fittingData.type = baffleType.value
          break

        case 'Thermowell':
          fittingData.type = thermowellType.value
          break

        case 'BOV':
          fittingData.type = bovType.value
          fittingData.model = bovModel.value
          break
      }

      // Push into the fittings array of the selected nozzle
      nozzles.value[fittingIndex.value].fittings.push(fittingData)

      // Optional: console log to verify
      console.log('Added fitting:', JSON.stringify(fittingData, null, 2))
    }

    const formatFittingLabel = (fitting) => {
      if (!fitting) return ''
      let label = fitting.name || ''
      if (fitting.size) label += ` - ${fitting.size}`
      if (fitting.itemCode) label += ` (${fitting.itemCode})`
      return label
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

    function loadFromLocalStorage(comp_name){
      const saved = localStorage.getItem(`savedData:${comp_name}`)
      if(saved){
        const parsed = JSON.parse(saved)
        if(parsed.so_no === this.sono) {
        return parsed.monoblock
       }
      }
      return null
    }

    return {
        insulationOnTop,
        insulationOnTopOptions,
        id,
        osTos,
        topDishedEndThickness,
        innerShellThickness,
        bottomDishedEndThickness,
        spilageCollectionTray,
        spilageCollectionTrayOptions,
        liftingMOC,
        liftingMOCOptions,
        modelType,
        modelTypeOptions,
        nozzles,
        // Methods
        addNozzle,
        removeNozzle,
        addFitting,
        removeFitting,
        searchMonoblockData,
        prepareMonoblockData,
        flattenForExcel,
        fillData,
        fillMonoBlockData,
        loadFromLocalStorage,

        // Fittings
        isFitting,
        fitting,
        fittingsOptions,
        fittingDrawingNumber,
        fittingItemCode,

        isSplitFlange,
        splitFlangetype,
        splitFlangeTypeOptions,
        splitFlangeMaterial,
        splitFlangeMaterialOptions,
        splitFlangeRatings,
        splitFlangeRatingsOptions,
        splitFlangeSize,
        splitFlangeOther,

        fittingIndex,
        isGasket,
        gasketSize,
        gasketMaterial,
        gasketMaterialOptions,
        gasketOther,
        
        isBlindCover,
        blindCoverSize,
        blindCoverMaterial,
        blindCoverMaterialOptions,
        blindCoverRatings,
        blindCoverRatingsOptions,
        blindCoverOther,

        isReducingFlange,
        reducingFlangeSize,
        reducingFlangeMaterial,
        reducingFlangeMaterialOptions,
        reducingFlangeRatings,
        reducingFlangeRatingsOptions,
        reducingFlangeOther,

        isDipPipe,
        dipPipeType,
        dipPipeTypeOptions,
        dipPipeSize,
        dipPipeMaterial,
        dipPipeMaterialOptions,
        dipPipeRatings,
        dipPipeRatingsOptions,
        dipPipeLength,
        dipPipeOther,

        isSparger,
        spargerSize,
        spargerMaterial,
        spargerMaterialOptions,
        spargerRatings,
        spargerRatingsOptions,
        spargerLength,
        spargerOther,

        isSprayBallPipe,
        sprayBallPipeSize,
        sprayBallPipeMaterial,
        sprayBallPipeMaterialOptions,
        sprayBallPipeRatings,
        sprayBallPipeRatingsOptions,
        sprayBallPipeLength,
        sprayBallPipeOther,

        isSprayBall,
        sprayBallMake,
        sprayBallMakeOptions,
        sprayBallSize,
        sprayBallModel,
        sprayBallModelOptions,
        sprayBallOther,

        isTee,
        teeSize,
        teeMaterial,
        teeMaterialOptions,
        teeRatings,
        teeRatingsOptions,
        teeLength,
        teeOther,

        isProtectionRing,
        protectionRingSize,
        protectionRingMaterial,
        protectionRingMaterialOptions,
        protectionRingType,
        protectionRingTypeOptions,
        protectionRingOther,

        isManholeCover,
        manholeCoverSize,
        manholeMaterial,
        manholeMaterialOptions,
        manholeLiningType,
        manholeLiningTypeOptions,
        manholeType,
        manholeTypeOptions,
        manholeOther,

        isToughenedGlass,
        toughenedGlassMaterial,
        toughenedGlassMaterialOptions,
        toughenedGlassSize,
        toughenedGlassOther,

        isGlassFlange,
        glassFlangeSize,
        glassFlangeMaterial,
        glassFlangeMaterialOptions,
        glassFlangeOther,

        isExtensionPiece,
        extensionPieceSize,
        extensionPieceMaterial,
        extensionPieceMaterialOptions,
        extensionPieceLength,
        extensionPieceOther,

        isBaffle,
        baffleType,
        baffleTypeOptions,
        baffleTipType,
        baffleTipTypeOptions,
        baffleMountingNozzle,
        baffleImmersionLength,
        baffleOther,

        isThermowell,
        thermowellType,
        thermowellTypeOptions,
        thermowellTipType,
        thermowellTipTypeOptions,
        thermowellMountingNozzle,
        thermowellImmersionLength,
        thermowellOther,

        isBOV,
        bovModelTypeSize,
        bovType,
        bovTypeOptions,
        bovModel,
        bovModelOptions,
        bovGasket,
        bovGasketOptions,
        bovFastenersMaterial,
        bovFastenersMaterialOptions,
        bovActuatorType,
        bovActuatorTypeOptions,
        bovSplitFlangeMaterial,
        bovSplitFlangeMaterialOptions,
        bovProximitySwitch,
        bovAFR,
        bovRTD,
        bovSOV,
        bovOther,

        getBovMastrers,
        populateBovMasterData,
        onUpdateBovType,
        onUpdateBovModel,
        onUpdateFittings,
        searchFittings,
        fillUpdatedData,
        addObjectToList,
        formatFittingLabel,
        hasNull
    }
  },
  watch: {
    bovMasters: {
      handler(newVal) {
        if (newVal !== null) {
          this.populateBovMasterData(newVal);
        }
      },
      immediate: true
    },
    fittingsData: {
      handler(newVal) {
        if (newVal !== null) {
          this.fillUpdatedData(newVal)
        }
      },
      immediate: true
    }
  }
}
</script>
<style scoped>
.full-height {
  height: 100vh;
}
</style>