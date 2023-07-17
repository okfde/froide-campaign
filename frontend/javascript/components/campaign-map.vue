<template>
  <div>
    <campaign-request
      v-if="showRequestForm"
      :config="requestConfig"
      :buttonText="config.button_text"
      :request-form="requestForm"
      :user-info="user"
      :user-form="userForm"
      :data="showRequestForm"
      :current-url="currentUrl"
      :campaignId="config.campaignId"
      :lawType="config.lawType"
      :extraText="config.requestExtraText"
      :hideNewsletterCheckbox="hideNewsletterCheckbox"
      :subscribeText="config.subscribe_text"
      :hasSubscription="config.hasSubscription"
      :publicbody="publicbody"
      :publicbodies="[publicbody]"
      :publicbodiesOptions="publicbodies"
      @publicBodyChanged="updatePublicBody"
      @detailfetched="detailFetched"
      @requestmade="requestMade"
      @userupdated="userUpdated"
      @tokenupdated="tokenUpdated"
      @close="requestFormClosed"></campaign-request>

    <div v-show="!showRequestForm">
      <div
        class="campaign-map-container container-fluid"
        ref="campaignMapContainer"
        id="campaign-map-container">
        <div class="searchbar d-block d-md-none" id="searchbar">
          <div class="searchbar-inner">
            <div class="input-group">
              <div class="clearable-input">
                <input
                  type="text"
                  v-model="query"
                  :class="{ 'search-query-active': !!lastQuery }"
                  class="form-control"
                  :placeholder="placeholderText"
                  @keydown.enter.prevent="userSearch" />
                <span
                  class="clearer fa fa-close"
                  v-if="query.length > 0"
                  @click="clearSearch"></span>
              </div>
              <button
                class="btn btn-outline-secondary"
                type="button"
                @click="userSearch">
                <i class="fa fa-search" aria-hidden="true"></i>
                <span class="d-none d-sm-none d-md-inline">Suchen</span>
              </button>
              <button
                class="btn btn-outline-secondary"
                @click="setLocator(true)">
                <i class="fa fa-location-arrow" aria-hidden="true"></i>
                <span class="d-none d-sm-none d-md-inline">Ort</span>
              </button>
              <button
                v-if="
                  !this.config.hide_status_filter ||
                  this.config.show_featured_only_filter
                "
                class="btn btn-outline-secondary"
                :class="{ active: showFilter }"
                @click="openFilter">
                <i class="fa fa-gears" aria-hidden="true"></i>
                <span class="d-none d-sm-none d-md-inline">Filter</span>
              </button>
            </div>
            <slide-up-down :active="showFilter" :duration="300">
              <div class="switch-filter">
                <switch-button
                  v-if="!this.config.hide_status_filter"
                  v-model="onlyRequested"
                  color="#FFC006"
                  @toggle="search"
                  >nur angefragte Orte zeigen</switch-button
                >
                <switch-button
                  v-if="this.config.show_featured_only_filter"
                  color="#FFC006"
                  v-model="onlyFeatured"
                  @toggle="getFeatured"
                  >{{ this.showFeaturedSwitchText }}</switch-button
                >
              </div>
            </slide-up-down>
          </div>
        </div>

        <div class="row">
          <div class="col-md-8 col-lg-9 order-md-2 map-column">
            <div
              class="map-container"
              ref="campaignMap"
              id="campaign-map"
              :class="mapContainerClass"
              :style="mapContainerStyle">
              <div v-if="showRefresh || searching" class="redo-search">
                <button v-if="showRefresh" class="btn btn-dark" @click="search">
                  Im aktuellen Bereich suchen
                </button>
                <button
                  v-if="searching"
                  class="btn btn-secondary btn-sm disabled">
                  <div class="spinner-border" role="status">
                    <span class="visually-hidden">Wird geladen...</span>
                  </div>
                  Suche läuft&hellip;
                </button>
              </div>
              <div
                class="map-search d-none d-md-block"
                :class="{ 'map-search-full': !(showRefresh || searching) }">
                <div class="input-group">
                  <div class="clearable-input">
                    <input
                      type="text"
                      v-model="query"
                      :class="{ 'search-query-active': !!lastQuery }"
                      class="form-control"
                      :placeholder="placeholderText"
                      @keydown.enter.prevent="userSearch" />
                    <span
                      class="clearer fa fa-close"
                      v-if="query.length > 0"
                      @click="clearSearch"></span>
                  </div>
                  <button
                    class="btn btn-outline-secondary"
                    type="button"
                    @click="userSearch">
                    <i class="fa fa-search me-1" aria-hidden="true"></i>
                    <span class="d-none d-sm-none d-lg-inline">Suchen</span>
                  </button>
                  <div
                    v-if="showFeaturedSwitch"
                    class="switch-filter py-0 border-top border-bottom border-dark">
                    <switch-button
                      color="#FFC006"
                      v-model="onlyFeatured"
                      @toggle="getFeatured"
                      >{{ this.showFeaturedSwitchText }}</switch-button
                    >
                  </div>
                  <button
                    class="btn btn-outline-secondary"
                    @click="setLocator(true)">
                    <i class="fa fa-location-arrow me-1" aria-hidden="true"></i>
                    <span class="d-none d-lg-inline">Ort</span>
                  </button>
                  <button
                    v-if="!hideStatusFilter"
                    class="btn btn-outline-secondary"
                    :class="{ active: showFilter }"
                    @click="openFilter">
                    <i class="fa fa-gears me-1" aria-hidden="true"></i>
                    <span class="d-none d-sm-none d-md-inline">Filter</span>
                  </button>
                </div>

                <slide-up-down :active="showFilter" :duration="300">
                  <div class="switch-filter">
                    <switch-button
                      v-if="!this.config.hide_status_filter"
                      v-model="onlyRequested"
                      color="#FFC006"
                      @toggle="search"
                      >nur angefragte Orte zeigen</switch-button
                    >
                  </div>
                </slide-up-down>
              </div>

              <l-map
                ref="map"
                :zoom.sync="zoom"
                :center="center"
                :options="mapOptions"
                :max-bounds="maxBounds">
                <l-tile-layer
                  :url="tileUrl"
                  :prefix="tileProvider.attribution"
                  :attribution="attribution" />
                <l-control-zoom position="bottomright" />
                <l-control position="bottomleft">
                  <ul class="color-legend">
                    <li :style="colorLegend.normal">
                      <span>{{ getStatusString('normal') }}</span>
                    </li>
                    <li :style="colorLegend.pending">
                      <span>{{ getStatusString('pending') }}</span>
                    </li>
                    <li :style="colorLegend.success">
                      <span>{{ getStatusString('success') }}</span>
                    </li>
                    <li :style="colorLegend.failure">
                      <span>{{ getStatusString('failure') }}</span>
                    </li>
                  </ul>
                </l-control>
                <l-marker
                  v-for="(location, index) in locationWithGeo"
                  :key="index"
                  :lat-lng="[location.lat, location.lng]"
                  :title="location.title"
                  :draggable="false"
                  :icon="getMarker(getStatus(location), location.featured)"
                  :options="markerOptions"
                  v-focusmarker>
                  <l-tooltip
                    :content="location.title"
                    :options="tooltipOptions"
                    v-if="!isMobile" />
                  <l-popup :options="popupOptions">
                    <campaign-popup
                      :color="getStatusColor(getStatus(location))"
                      :status="getStatus(location)"
                      :statusString="getStatusString(getStatus(location))"
                      :data="location"
                      :buttonText="config.button_text"
                      :allowMultipleRequests="allowMultipleRequests"
                      @startRequest="startRequest"
                      @detail="setDetail" />
                  </l-popup>
                </l-marker>
              </l-map>
            </div>
          </div>
          <div class="col-md-4 col-lg-3 order-md-1 sidebar-column">
            <div
              class="sidebar"
              :class="{ 'modal-active': modalActive }"
              ref="campaignList"
              id="campaign-list"
              v-scroll.window="handleSidebarScroll">
              <div class="new-venue-area" v-if="hasSearched || error">
                <template v-if="searchEmpty">
                  <p>{{ nothingFoundText }}</p>
                </template>
                <button
                  v-if="config.addLocationAllowed"
                  class="btn btn-sm btn-secondary"
                  @click="setNewPlace(true)">
                  Ort nicht gefunden?
                </button>
              </div>
              <campaign-sidebar-item
                v-for="(location, index) in locations"
                :key="index"
                :color="getStatusColor(getStatus(location))"
                :status="getStatus(location)"
                :statusString="getStatusString(getStatus(location))"
                :data="location"
                :buttonText="config.button_text"
                :allowMultipleRequests="allowMultipleRequests"
                @startRequest="startRequest"></campaign-sidebar-item>
            </div>
          </div>
          <campaign-locator
            ref="locator"
            :defaultPostcode="postcode"
            :defaultLocation="locationName"
            :exampleCity="city"
            :locationKnown="locationKnown"
            :error="error"
            :error-message="locatorErrorMessage"
            :geolocation-disabled="geolocationDisabled"
            :isMobile="isMobile"
            @close="setLocator(false)"
            @coordinatesChosen="coordinatesChosen"
            @locationChosen="locationChosen"></campaign-locator>
          <campaign-new-location
            ref="newvenue"
            @close="setNewPlace(false)"
            @locationcreated="locationCreated"
            :campaignId="config.campaignId"></campaign-new-location>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/* global L */
import Vue from 'vue'
import 'leaflet/dist/leaflet.css'

import {
  LMap,
  LTileLayer,
  LControlZoom,
  LControl,
  LMarker,
  LPopup,
  LTooltip
} from 'vue2-leaflet'
import Modal from 'bootstrap/js/dist/modal'
import 'leaflet.icon.glyph'
import bbox from '@turf/bbox'
import SlideUpDown from 'vue-slide-up-down'
import CampaignLocator from './campaign-locator'
import CampaignSidebarItem from './campaign-sidebar-item'
import CampaignPopup from './campaign-popup'
import SwitchButton from './switch-button'
import CampaignNewLocation from './campaign-new-location'
import CampaignRequest from './campaign-request'

import {
  getQueryVariable,
  canUseLocalStorage,
  getPinURL,
  COLORS,
  STATUS_STRINGS,
  latlngToGrid
} from '../lib/utils'

Vue.directive('scroll', {
  inserted: function (el, binding) {
    let scrollElement = el
    if (binding.modifiers.window) {
      scrollElement = window
    }
    const f = function (evt) {
      if (binding.value(evt, el)) {
        scrollElement.removeEventListener('scroll', f)
      }
    }
    scrollElement.addEventListener('scroll', f)
  }
})

const GERMANY_BOUNDS = [
  [56.9449741808516, 24.609375000000004],
  [44.402391829093915, -3.5156250000000004]
]
const DETAIL_ZOOM_LEVEL = 12
const DEFAULT_ZOOM = 6
const DEFAULT_POS = [51.00289959043832, 10.245523452758789]
const MIN_DISTANCE_MOVED_REFRESH = 800 // in meters
const MIN_MAP_HEIGHT = 300

function getColorMode() {
  return document.documentElement.getAttribute('data-bs-theme') || 'light'
}

export default {
  name: 'campaign-map',
  props: {
    config: {
      type: Object
    },
    userInfo: {
      type: Object,
      default: null
    },
    userForm: {
      type: Object,
      default: null
    },
    requestForm: {
      type: Object
    },
    requestConfig: {
      type: Object
    }
  },
  components: {
    LMap,
    LTileLayer,
    LControlZoom,
    LControl,
    LMarker,
    LPopup,
    LTooltip,
    CampaignPopup,
    SwitchButton,
    SlideUpDown,
    CampaignSidebarItem,
    CampaignNewLocation,
    CampaignLocator,
    CampaignRequest
  },
  data() {
    let locationKnown = false
    let zoom = null
    let center = null
    const postcode = null
    const latlng = getQueryVariable('latlng')
    const query = getQueryVariable('query')
    const marker = null

    let city = this.config.city
    if (city.country_code && city.country_code !== 'DE') {
      city = {}
    }

    if (latlng) {
      const parts = latlng.split(',')
      center = [parseFloat(parts[0]), parseFloat(parts[1])]
      if (center[0] && center[1]) {
        zoom = DETAIL_ZOOM_LEVEL
      }
    }

    if (canUseLocalStorage(window)) {
      zoom = parseInt(window.localStorage.getItem('froide-campaign:zoom'))
      if (center === null) {
        center = JSON.parse(
          window.localStorage.getItem('froide-campaign:center')
        )
        if (center !== null) {
          center = [center.lat, center.lng]
        }
      }
    }
    if (center === null) {
      center = [null, null]
    }

    center = [
      center[0] || city.latitude || DEFAULT_POS[0],
      center[1] || city.longitude || DEFAULT_POS[1]
    ]

    const maxBounds = L.latLngBounds(GERMANY_BOUNDS)
    if (!maxBounds.contains(L.latLng(center))) {
      center = DEFAULT_POS
    }

    if (center[0] !== DEFAULT_POS[0]) {
      locationKnown = true
      zoom = zoom || DETAIL_ZOOM_LEVEL
    } else {
      zoom = DEFAULT_ZOOM
    }

    this.$root.csrfToken = document.querySelector(
      '[name=csrfmiddlewaretoken]'
    ).value

    return {
      allowMultipleRequests: this.config.allow_multiple_requests
        ? this.config.allow_multiple_requests
        : false,
      alreadyRequested: {},
      attribution:
        'leaflet | &copy; <a href="https://osm.org/copyright">OpenStreetMap</a> contributors',
      user: this.userInfo,
      showRequestForm: null,
      locations: [],
      zoom,
      locationKnown,
      locationName: '',
      locatorErrorMessage: '',
      geolocationDisabled: false,
      center,
      city: city.city,
      postcode: '' + (postcode || city.postal_code || ''),
      maxBounds,
      searching: false,
      marker,
      mapMoved: false,
      mapHeight: null,
      isMapTop: false,
      autoMoved: false,
      showLocator: false,
      locatorModal: null,
      hasSearched: false,
      searchCenter: null,
      searchEmpty: false,
      error: false,
      showNewPlace: false,
      newPlaceModal: null,
      showDetail: null,
      showFilter: false,
      markerOptions: {
        riseOnHover: true
      },
      stacked: this.isStacked(),
      publicbody: {},
      publicbodies: [],
      query: query || '',
      lastQuery: '',
      onlyRequested: false,
      onlyFeatured: false,
      colorMode: getColorMode(),
      tileProvider: {
        name: 'Carto',
        url: `//cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}${
          window.L.Browser.retina ? '@2x' : ''
        }.png`,
        // url: 'https://api.mapbox.com/styles/v1/{username}/{style}/tiles/{tileSize}/{z}/{x}/{y}{r}?access_token={accessToken}',
        // url: 'https://api.tiles.mapbox.com/v4/{style}/{z}/{x}/{y}.png?access_token={accessToken}',
        // url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        attribution:
          '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>, &copy; <a href="https://carto.com/attribution">CARTO</a>',
        options: {
          // style: 'mapbox.streets',
          // username: 'okfde',
          // tileSize: 512,
          // r: window.L.Browser.retina ? '@2x' : '',
          // accessToken: 'pk.eyJ1Ijoib2tmZGUiLCJhIjoiY2p3aHBpZ2wzMjVxbTQ4bWduM2YwenQ2eCJ9.kzkjyGM8xIEShOZ7ekH5AA'
        }
      }
    }
  },
  created() {
    Vue.directive('focusmarker', {
      // When the bound element is inserted into the DOM...
      componentUpdated: (el, binding, vnode) => {
        if (vnode.key === self.selectedVenueId) {
          vnode.componentInstance.mapObject.setZIndexOffset(300)
        } else {
          vnode.componentInstance.mapObject.setZIndexOffset(0)
        }
      }
    })
    const observer = new MutationObserver(
      () => (this.colorMode = getColorMode())
    )
    observer.observe(document.documentElement, {
      attributeFilter: ['data-bs-theme'],
      attributeOldValue: true
    })
  },
  mounted() {
    this.$nextTick(() => {
      this.map.attributionControl.setPrefix('')
      this.map.on('zoomend', (e) => {
        this.mapHasMoved()
        this.recordMapPosition()
      })
      this.map.on('moveend', (e) => {
        if (this.searchCenter !== null) {
          const currentPosition = this.map.getCenter()
          const distance = this.searchCenter.distanceTo(currentPosition)
          if (distance < MIN_DISTANCE_MOVED_REFRESH) {
            return
          }
        }
        this.mapHasMoved()
        this.recordMapPosition()
      })
      window.addEventListener('resize', () => {
        this.isStacked()
      })
      this.search()
    })
    this.map.on('popupopen', (e) => {
      this.preventMapMoved()
    })
  },
  computed: {
    tileUrl() {
      return `//cartodb-basemaps-{s}.global.ssl.fastly.net/${
        this.colorMode
      }_all/{z}/{x}/{y}${window.L.Browser.retina ? '@2x' : ''}.png`
    },
    currentUrl() {
      let url = `${this.config.appUrl}?latlng=${this.center[0]},${this.center[1]}`
      if (this.selectedVenueId) {
        url += `&ident=${encodeURIComponent(this.selectedVenue.ident)}`
        url += `&query=${encodeURIComponent(this.selectedVenue.name)}`
      } else if (this.query) {
        url += `&query=${encodeURIComponent(this.query)}`
      }
      return url
    },
    locationWithGeo() {
      if (this.locations.length > 0) {
        return this.locations.filter((location) => location.lat)
      }
      return this.locations
    },
    hideNewsletterCheckbox() {
      return this.config.hide_newsletter_checkbox
        ? this.config.hide_newsletter_checkbox
        : false
    },
    hideStatusFilter() {
      return this.config.hide_status_filter
        ? this.config.hide_status_filter
        : false
    },
    showFeaturedSwitch() {
      return this.config.showFeaturedSwitch
        ? this.config.showFeaturedSwitch
        : false
    },
    ignoreMapFilter() {
      return this.config.ignore_mapfilter ? this.config.ignore_mapfilter : false
    },
    placeholderText() {
      return this.config.placeholder_text
        ? this.config.placeholder_text
        : 'Nach Ort suchen'
    },
    nothingFoundText() {
      return this.config.nothing_found
        ? this.config.nothing_found
        : 'Keine Orte gefunden.'
    },
    showFeaturedSwitchText() {
      return this.config.feature_switch_text
        ? this.config.feature_switch_text
        : 'besondere Orte zeigen'
    },
    modalActive() {
      return this.showLocator || this.showDetail
    },
    showRefresh() {
      return this.mapMoved && this.zoom >= 10
    },
    tooltipOptions() {
      return {
        offset: L.point(0, -40),
        direction: 'top'
      }
    },
    isMobile() {
      return this.stacked || L.Browser.mobile
    },
    map() {
      return this.$refs.map.mapObject
    },
    colorLegend() {
      return {
        normal: `background-image: url('${getPinURL(COLORS.normal)}')`,
        pending: `background-image: url('${getPinURL(COLORS.pending)}')`,
        success: `background-image: url('${getPinURL(COLORS.success)}')`,
        failure: `background-image: url('${getPinURL(COLORS.failure)}')`
      }
    },
    mapContainerClass() {
      if (this.isMapTop && !this.stacked) {
        return 'map-full-height'
      }
      return ''
    },
    mapContainerStyle() {
      if (this.mapHeight === null) {
        return ''
      }
      return `height: ${this.mapHeight}px`
    },
    mapOptions() {
      return {
        scrollWheelZoom: !this.isMobile,
        doubleClickZoom: true,
        zoomControl: false,
        maxZoom: 18
      }
    },
    popupOptions() {
      return {
        autoPanPaddingTopLeft: L.point([5, 85]),
        maxWidth: Math.round(window.innerWidth * 0.7)
      }
    }
  },
  methods: {
    updatePublicBody(publicbody) {
      this.publicbody = publicbody
    },
    tokenUpdated(token) {
      this.$root.csrfToken = token
    },
    userUpdated(user) {
      this.user = user
    },
    requestMade(data) {
      this.alreadyRequested[data.id] = true
    },
    detailFetched(data) {
      this.publicbody = data.publicbody
      this.publicbodies = data.publicbodies.objects
      this.locations = this.locations.map((f) => {
        if (f.ident === data.ident) {
          f.publicbody = data.publicbody
          f.publicbodies = data.publicbodies.objects
          f.makeRequestURL = data.makeRequestURL
          f.full = true
          return f
        }
        return f
      })
    },
    startRequest(data) {
      this.showRequestForm = data
    },
    requestFormClosed() {
      this.showRequestForm = null
    },
    setLocator(data) {
      if (this.locatorModal === null) {
        this.locatorModal = new Modal(this.$refs.locator.$el)
        this.$refs.locator.$el.addEventListener('hidden.bs.modal', () => {
          this.setLocator(false)
        })
      }
      this.showLocator = data
      if (data) {
        this.locatorModal.show()
      } else {
        this.locatorModal.hide()
      }
    },
    coordinatesChosen(latlng) {
      const center = L.latLng(latlng)
      if (!this.maxBounds.contains(center)) {
        this.geolocationDisabled = true
        this.locatorErrorMessage =
          'Dein Ort scheint nicht in Deutschland zu sein!'
        this.setLocator(true)
        return
      }
      this.geolocationDisabled = false
      this.locatorErrorMessage = ''
      this.locationKnown = true
      this.map.setView(center, DETAIL_ZOOM_LEVEL)
      this.search({ coordinates: center })
      this.preventMapMoved()
    },
    locationChosen(location) {
      let url = `/api/v1/georegion/?name=${location}&limit=1`
      if (location.match(/^\d{5}$/)) {
        window.localStorage.setItem('froide-campaign:postcode', location)
        url = `/api/v1/georegion/?kind=zipcode&name=${location}&limit=1`
      }
      window
        .fetch(url)
        .then((response) => {
          return response.json()
        })
        .then((data) => {
          if (data.meta.total_count === 0) {
            return
          }
          const id = data.objects[0].id
          const url = `/api/v1/georegion/${id}/`
          window
            .fetch(url)
            .then((response) => {
              return response.json()
            })
            .then((data) => {
              this.locationKnown = true
              const geoRegion = data
              let bounds = bbox(geoRegion.geom)
              bounds = L.latLngBounds([
                [bounds[1], bounds[0]],
                [bounds[3], bounds[2]]
              ])
              const coords = geoRegion.centroid.coordinates
              const center = L.latLng([coords[1], coords[0]])
              this.map.fitBounds(bounds)
              this.search({ coordinates: center, bounds })
              this.preventMapMoved()
            })
        })
    },
    locationCreated(data) {
      data.full = false
      this.locations.push(data)
      this.startRequest(data)
    },
    setNewPlace(show) {
      this.showNewPlace = show

      if (this.newPlaceModal === null) {
        this.newPlaceModal = new Modal(this.$refs.newvenue.$el)
        this.$refs.newvenue.$el.addEventListener('hidden.bs.modal', () => {
          this.setNewPlace(false)
        })
      }
      this.showNewVenue = show
      if (show) {
        this.newPlaceModal.show()
      } else {
        this.newPlaceModal.hide()
      }
    },
    recordMapPosition() {
      const latlng = this.map.getCenter()
      this.center = [latlng.lat, latlng.lng]
      const zoom = this.map.getZoom()
      if (!canUseLocalStorage(window)) {
        return
      }
      window.localStorage.setItem('froide-campaign:zoom', zoom)
      window.localStorage.setItem(
        'froide-campaign:center',
        JSON.stringify(latlng)
      )
    },
    mapHasMoved() {
      if (this.autoMoved || this.ignoreMapFilter || this.onlyFeatured) {
        return
      }
      this.mapMoved = true
      this.search()
    },
    clearSearch() {
      this.query = ''
      this.search()
    },
    preventMapMoved() {
      this.autoMoved = true
      if (this.autoMovedTimeout !== null) {
        window.clearTimeout(this.autoMovedTimeout)
      }
      this.autoMovedTimeout = window.setTimeout(() => {
        this.autoMoved = false
        this.autoMovedTimeout = null
      }, 1500)
    },
    openFilter() {
      this.showFilter = !this.showFilter
    },
    userSearch() {
      if (this.query.match(/^\d{5}$/)) {
        const p = this.query
        this.query = ''
        return this.postcodeChosen(p)
      }
      this.search()
    },
    getFeatured(options = {}) {
      this.search()
    },
    search(options = {}) {
      this.map.closePopup()
      this.map.eachLayer((layer) => {
        if (layer.options.pane === 'tooltipPane') {
          layer.removeFrom(this.map)
        }
      })
      this.mapMoved = false
      this.error = false
      this.searching = true
      this.hasSearched = false
      this.searchEmpty = false
      this.lastQuery = this.query
      this.searchCenter = this.map.getCenter()

      const bounds = this.map.getBounds()

      let radius = Math.min(
        this.map.distance(bounds.getNorthEast(), bounds.getNorthWest()),
        this.map.distance(bounds.getNorthEast(), bounds.getSouthEast())
      )
      radius = Math.max(Math.round(Math.min(radius, 100000) / 100) * 100, 500)
      const reqCoords = latlngToGrid(this.searchCenter, radius)
      let locationParam = ''
      if (
        !this.ignoreMapFilter &&
        !this.onlyFeatured &&
        this.map.getZoom() > 7
      ) {
        locationParam = `lat=${reqCoords.lat}&lng=${reqCoords.lng}&radius=${radius}&zoom=${this.zoom}`
      }
      let onlyRequested = ''
      if (this.onlyRequested) {
        onlyRequested = '&requested=1'
      }
      let onlyFeatured = ''
      if (this.onlyFeatured) {
        onlyFeatured = '&featured=1'
      }
      window
        .fetch(
          `/api/v1/campaigninformationobject/?campaign=${
            this.config.campaignId
          }&q=${encodeURIComponent(
            this.query
          )}${onlyRequested}${onlyFeatured}&${locationParam}`
        )
        .then((response) => {
          return response.json()
        })
        .then(this.searchDone(options))
    },
    searchDone(options) {
      return (data) => {
        this.searching = false
        this.hasSearched = true
        data = data.objects
        if (data.error) {
          console.warn('Error requesting the API')
        } else {
          this.searchEmpty = data.length === 0
          this.locations = data
          const bounds = L.latLngBounds(this.locations)
          if (!this.maxBounds.contains(bounds)) {
            this.locatorErrorMessage =
              'Dein Ort scheint nicht in Deutschland zu sein!'
            this.setLocator(true)
            return
          }
          this.preventMapMoved()
        }
      }
    },
    isStacked() {
      return (this.stacked = window.innerWidth < 768)
    },
    setDetail(data) {
      this.showDetail = data
    },
    getStatus(location) {
      if (location.foirequests.length > 0) {
        if (location.resolution === 'successful') {
          return 'success'
        }
        if (location.resolution === 'refused') {
          return 'failure'
        }
        if (location.resolution === 'user_withdrew') {
          return 'withdrawn'
        }
        return 'pending'
      }
      return 'normal'
    },
    getMarker(status, featured) {
      const iconSize = [25, 41]
      let glyph = ''
      if (featured) {
        glyph = this.config.featured_icon
          ? this.config.featured_icon
          : 'fa-exclamation'
      }

      return L.icon.glyph({
        className: 'campaign-marker-icon',
        prefix: 'fa',
        glyph,
        iconUrl: this.getIconUrl(status),
        iconSize
      })
    },
    getStatusColor(status) {
      return COLORS[status]
    },
    getStatusString(status) {
      if (status) {
        return STATUS_STRINGS[status]
      }
    },
    getIconUrl(status) {
      return getPinURL(COLORS[status])
    },
    handleSidebarScroll(evt, el) {
      if (this.modalActive) {
        return
      }
      if (L.Browser.safari) {
        /* FIXME: Ugly workaround for render bug in latest safari */
        this.$refs.campaignMap.style.top = 'unset'
        window.requestAnimationFrame(() => {
          this.$refs.campaignMap.style.top = 0
        })
      }
      const listTop = this.$refs.campaignList.getBoundingClientRect().top
      if (listTop < this.dividerSwitchHeight) {
        if (!this.listShown) {
          this.showFilter = false
        }
        this.listShown = true
      } else {
        this.listShown = false
      }
      const mapRect = this.$refs.campaignMap.getBoundingClientRect()
      const mapTop = mapRect.top
      const isMapTop = mapTop <= 0
      if (isMapTop !== this.isMapTop) {
        window.setTimeout(() => {
          this.map.invalidateSize()
          this.preventMapMoved()
        }, 1000)
        this.preventMapMoved()
      }
      this.isMapTop = isMapTop
      if (!this.stacked) {
        if (!isMapTop) {
          this.mapHeight = Math.max(window.innerHeight - mapTop, MIN_MAP_HEIGHT)
        } else {
          this.mapHeight = null
        }
      }
    }
  }
}
</script>

<style lang="scss" scoped>
$icon-normal: #007bff;
$icon-pending: #ffc107;
$icon-success: #28a745;
$icon-failure: #dc3545;

.icon-normal {
  fill: $icon-normal;
}
.icon-normal.selected {
  fill: darken($icon-normal, 30%);
}

.icon-pending {
  fill: $icon-pending;
}
.icon-pending.selected {
  fill: darken($icon-pending, 30%);
}

.icon-success {
  fill: $icon-normal;
}
.icon-success.selected {
  fill: darken($icon-success, 30%);
}

.icon-failure {
  fill: $icon-failure;
}
.icon-failure.selected {
  fill: darken($icon-failure, 30%);
}

.campaign-wrapper {
  position: relative;
}

.campaign-map-embed {
  border: 1px solid #eee;
  padding: 0 10px 10px;
  height: 100vh;
  overflow: scroll;

  &.modal-active {
    overflow: hidden;
  }
}

@media screen and (min-width: 768px) {
  .campaign-map-embed {
    padding: 0;
  }
}

.campaign-map-container {
  position: relative;
  padding-bottom: 1rem;
}

.searchbar {
  position: -webkit-sticky;
  position: sticky;
  top: 0;
  z-index: 2050;
  background-color: var(--bs-body-bg);
  margin: 0 -15px;
}

.searchbar-inner {
  padding: 0;
}

.map-search {
  position: absolute;
  top: 0;
  right: 0;
  z-index: 2000;
  width: 50%;
  transition: width 0.8s ease-out;
  margin-top: 1rem;
  margin-right: 1rem;

  .btn {
    color: var(--bs-body);
    background-color: var(--bs-body-bg);
  }
  .btn:hover,
  .btn:active {
    background-color: var(--bs-secondary-bg-subtle);
  }
}

.map-search-full {
  width: 80%;
}

@media screen and (max-width: 960px) {
  .map-search {
    width: 60%;
  }
  .map-search-full {
    width: 90%;
  }
}

.redo-search {
  position: absolute;
  z-index: 2000;
  width: auto;

  top: 0;
  left: 0;
  right: 0;
  text-align: center;
  margin-left: auto;
  margin-right: auto;
  margin-top: 1rem;

  pointer-events: none;
  .btn {
    pointer-events: auto;
  }
}

@media screen and (min-width: 768px) {
  .redo-search {
    left: 0;
    width: 30%;
    text-align: left;
    margin-left: 1rem;
    .btn {
      font-size: 0.85rem;
    }
  }
}

@media screen and (min-width: 768px) {
  .searchbar-inner {
    padding: 0 15px;
  }
}

.map-column {
  position: -webkit-sticky;
  position: sticky;
  top: 38px;

  padding-right: 0;
  padding-left: 0;
}

@media screen and (min-width: 768px) {
  .map-column {
    padding-right: 15px;
    padding-left: 5px;
  }
}

.map-container {
  width: 100%;
  height: 60vh;
  position: relative;
  overflow: hidden;
}

.sidebar {
  background-color: var(--bs-body-bg);
}

.sidebar.modal-active {
  height: 90vh;
  overflow: hidden;
}

.is-embed {
  .searchbar {
    padding: 10px 0 0;
  }
  .map-column {
    top: 53px;
  }
  .divider-column {
    top: 47px;
  }
}

@media screen and (min-width: 768px) {
  .map-container {
    height: 80vh;
    position: sticky;
    top: 0;
    transition: height 0.8s;
  }

  .is-embed {
    .map-container {
      margin-top: 1rem;
      height: calc(100vh - 2em - 2px);
    }
    .sidebar {
      height: calc(100vh - 2em - 2px);
      overflow: scroll;
    }
  }
}

.map-full-height {
  height: 100vh;
}

.sidebar-column {
  transform: translate3d(0px, 0px, 0px);
  z-index: 1045;
  margin-top: -1px;
  padding-right: 0;
  padding-left: 0;
}

@media screen and (min-width: 768px) {
  .sidebar-column {
    padding-right: 0px;
    padding-left: calc(var(--bs-gutter-x) * 0.5);
  }
}

.divider-column {
  background-color: var(--bs-body-bg);
  border-bottom: 2px solid var(--bs-tertiary-bg-subtle);
  padding: 0.25rem 0;
  z-index: 2025;
  position: sticky;
  top: 37px;
  padding: 6px 0 6px;
  margin-top: 4px;
  text-align: center;
  cursor: pointer;
}

.divider-button {
  margin: 0;
  a {
    padding: 0.25rem 0.5rem;
    background: var(--bs-tertiary-bg-subtle);
    color: var(--bs-body);
    border-radius: 5px;
  }
}

.clearable-input {
  position: relative;
  flex: 1 1 auto;
  width: 1%;
  border-top-end-radius: 0;
  border-bottom-end-radius: 0;
  margin-bottom: 0;
}
.clearer {
  position: absolute;
  right: 10px;
  top: 30%;
  color: #999;
  cursor: pointer;
}
.search-query-active {
  background-color: var(--bs-primary-bg-subtle);
}

.new-venue-area {
  text-align: center;
  padding: 15px 0;
}

.switch-filter {
  display: flex;
  justify-content: flex-end;
  padding: 15px;
  background-color: var(--bs-body-bg);
}

.color-legend {
  margin-bottom: 0;
  padding: 0.5rem;
  background-color: var(--bs-body-bg);
  color: var(--bs-body);
  list-style: none;
}

.color-legend li {
  background-repeat: no-repeat;
  padding-left: 1.5rem;
}

.color-legend li span {
  color: var(--bs-body);
}
</style>

<style global>
.leaflet-popup-content-wrapper,
.leaflet-popup-tip,
.leaflet-bar a {
  background: var(--bs-body-bg);
  color: var(--bs-body);
}
.leaflet-bar a.leaflet-disabled {
  background: var(--bs-body-bg);
}
.leaflet-container {
  background-color: var(--bs-secondary-bg);
}
.leaflet-container .leaflet-control-attribution,
.leaflet-container .leaflet-control-attribution a {
  background: var(--bs-body-bg);
  color: var(--bs-secondary);
}
</style>
