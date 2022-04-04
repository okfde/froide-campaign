<template>
  <div :class="{ 'mx-n3': settings.twoColumns }">
    <campaign-request
      v-if="showRequestForm"
      :config="requestConfig"
      :button-text="config.button_text"
      :request-form="requestForm"
      :user-info="user"
      :user-form="userForm"
      :data="showRequestForm"
      :current-url="''"
      :campaign-id="config.campaignId"
      :law-type="config.lawType"
      :extra-text="config.requestExtraText"
      :hide-newsletter-checkbox="hideNewsletterCheckbox"
      :subscribe-text="config.subscribe_text"
      :has-subscription="config.hasSubscription"
      :publicbody="publicbody"
      :publicbodies="[publicbody]"
      :publicbodies-options="publicbodies"
      :local-request-count="localRequestCount"
      :max-requests-per-user="maxRequestsPerUser"
      :address-required="settings.addressRequired"
      :private-requests="config.privateRequests"
      @publicBodyChanged="updatePublicBody"
      @detailfetched="detailFetched"
      @requestmade="requestMade"
      @userupdated="userUpdated"
      @tokenupdated="tokenUpdated"
      @close="requestFormClosed" />

    <div v-show="!showRequestForm">
      <div
        v-if="!settings.input_field"
        ref="searchTop"
        class="container mx-auto"
        :class="[settings.twoColumns ? 'col-md-12' : 'col-md-5']">
        <h5>Filter</h5>
        <input
          v-model="search"
          type="search"
          :placeholder="i18n.search"
          class="form-control mb-3"
          @keyup="searchObjects" />
      </div>

      <div
        v-if="settings.input_field === 'topf-secret-fleisch'"
        class="fleisch-form-background">
        <div class="container">
          <div class="col-md-5 mx-auto">
            <div
              class="fleisch-form-container embed-responsive embed-responsive-21by9">
              <div class="fleisch-form shadow">
                <p class="h4 font-weight-bolder">DE</p>
                <div class="input-group">
                  <input
                    v-model="search"
                    placeholder="BY 1234"
                    class="form-control text-center h4"
                    @keyup="searchObjects" />
                </div>
                <p class="h4 font-weight-bolder">EG</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div
        class="container mx-auto mb-3"
        :class="[settings.twoColumns ? 'col-md-12' : 'col-md-5']">
        <div v-if="!settings.hide_status_filter">
          <CampaignListTag
            v-for="res in resolutions"
            :key="res"
            :active="res === resolution"
            :status="res"
            @click="setResolutionFilter(res)">
            {{ i18n.resolutions[res] }}
          </CampaignListTag>
        </div>
        <div v-if="!settings.hide_tag_filters">
          <CampaignListTag
            v-for="category in config.categories"
            :key="category.id"
            :active="currentCategory === category.id"
            @click="setCategoryFilter(category.id)">
            #{{ category.title }}
          </CampaignListTag>
        </div>

        <transition-group
          name="list"
          tag="div"
          class="row mt-3 mx-0"
          :class="{ 'mx-n2': settings.twoColumns }">
          <CampaignListItem
            v-for="object in objects"
            :key="object.ident"
            :object="object"
            :current-category="currentCategory"
            :allow-multiple-requests="allowMultipleRequests"
            :language="language"
            :reservations="reservations"
            :client-id="clientId"
            class="list-item"
            :class="[settings.twoColumns ? 'col-md-6 px-2' : 'w-100']"
            @startRequest="startRequest"
            @setCategoryFilter="setCategoryFilter"
            @followed="followedRequest(object, $event)"
            @unfollowed="object.follow.follows = false" />

          <div
            v-if="!loading && hasSearched && objects.length === 0"
            key="noResults"
            class="text-center my-5 py-5 w-100">
            <p class="text-secondary" v-html="i18n.noResults" />
          </div>
          <div v-if="loading" key="loading" class="text-center my-5 py-5 w-100">
            <div class="spinner-border" role="status">
              <span class="sr-only">Loading...</span>
            </div>
          </div>
        </transition-group>
        <div
          v-if="!loading && (nextUrl || lastSearchWasRandom)"
          class="row justify-content-center mb-5">
          <button class="btn btn-light" @click="fetch">
            <template v-if="nextUrl">
              {{ i18n.loadMore }}
            </template>
            <template v-else>
              {{ i18n.loadRandom }}
            </template>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import deepmerge from 'deepmerge'
import debounce from 'lodash.debounce'
import Vue from 'vue'

import CampaignListTag from './campaign-list-tag'
import CampaignListItem from './campaign-list-item'
import i18n from '../../i18n/campaign-list.json'
import CampaignRequest from './campaign-request'
import Room from 'froide/frontend/javascript/lib/websocket.ts'

function uuidv4() {
  return ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, (c) =>
    (
      c ^
      (crypto.getRandomValues(new Uint8Array(1))[0] & (15 >> (c / 4)))
    ).toString(16)
  )
}

export default {
  name: 'CampaignList',
  components: { CampaignListTag, CampaignListItem, CampaignRequest },
  props: {
    config: {
      type: Object,
      required: true
    },
    settings: {
      type: Object,
      required: true
    },
    requestConfig: {
      type: Object,
      required: true
    },
    requestForm: {
      type: Object,
      required: true
    },
    userInfo: {
      type: Object,
      default: null
    },
    userForm: {
      type: Object,
      default: null
    },
    language: {
      type: String,
      default: 'de'
    }
  },
  data() {
    this.$root.csrfToken = document.querySelector(
      '[name=csrfmiddlewaretoken]'
    ).value
    return {
      allowMultipleRequests: this.settings.allow_multiple_requests
        ? this.settings.allow_multiple_requests
        : false,
      alreadyRequested: new Set(),
      reservations: new Map(),
      user: this.userInfo,
      hasSearched: false,
      loading: false,
      search: '',
      objects: [],
      baseUrl: `/api/v1/campaigninformationobject/?campaign=${this.config.campaignId}&limit=${this.settings.limit}&featured=${this.settings.featured_only}&language=${this.language}`,
      nextUrl: '',
      meta: [],
      currentCategory: null,
      resolution: null,
      resolutions: ['normal', 'pending', 'successful', 'refused'],
      showRequestForm: null,
      publicbody: {},
      publicbodies: [],
      room: null,
      lastSearch: null
    }
  },
  computed: {
    i18n() {
      const settings = this.settings || {}
      const messages = deepmerge(i18n, settings.overwrite_messages || {})

      return messages[this.language]
    },
    hideNewsletterCheckbox() {
      return this.settings.hide_newsletter_checkbox
        ? this.settings.hide_newsletter_checkbox
        : true
    },
    maxRequestsPerUser() {
      return this.settings.maxRequestsPerUser || 0
    },
    searchParameters() {
      const defaults = [
        ['search', this.search],
        ['status', this.resolution],
        ['category', this.currentCategory]
      ]
      return defaults.filter((d) => !!d[1])
    },
    hasSearchParameters() {
      return this.searchParameters.length > 0
    },
    lastSearchWasRandom() {
      return this.lastSearch && this.lastSearch.indexOf('order=random') !== -1
    },
    localRequestCount() {
      return this.alreadyRequested.size
    }
  },
  created() {
    this.clientId = null
    try {
      const key = 'campaign_temp_client_id'
      const clientId = window.localStorage.getItem(key)
      if (!clientId) {
        this.clientId = uuidv4()
        localStorage.setItem(key, this.clientId)
      } else {
        this.clientId = clientId
      }
    } catch {
      // eslint-disable-next-line no-console
      console.error('Could not access localstorage')
    }
  },
  mounted() {
    if (!this.settings.show_list_after_search) {
      this.nextUrl = this.getUrlWithParams(this.baseUrl)
      this.fetch()
    }
    this.reservationTimeout = null
    if (this.settings.live) {
      try {
        this.room = new Room(`/ws/campaign/live/${this.config.campaignId}/`)
        this.room
          .connect()
          .on('request_made', (event) => {
            if (this.objects.length === 0) {
              return
            }
            this.objects = this.objects.map((o) => {
              if (o.ident === event.data.ident) {
                return event.data
              }
              return o
            })
          })
          .on('reservations', (event) => {
            if (this.objects.length === 0) {
              return
            }
            this.reservations = new Map()
            event.reservations.forEach((keyValue) =>
              this.reservations.set(keyValue[0], keyValue[1])
            )
            if (this.reservationTimeout) {
              window.clearTimeout(this.reservationTimeout)
            }
            this.reservationTimeout = window.setTimeout(() => {
              this.room.send({
                type: 'request_reservations'
              })
            }, (event.timeout || 5 * 60) * 1000)
          })
      } catch (e) {
        // eslint-disable-next-line no-console
        console.error(e)
      }
    }
  },
  methods: {
    userUpdated(user) {
      this.user = user
    },
    detailFetched(data) {
      this.publicbody = data.publicbody
      this.publicbodies = data.publicbodies.objects
      this.objects = this.objects.map((f) => {
        if (f.ident === data.ident) {
          f.publicbody = data.publicbody
          f.publicbodies = data.publicbodies.objects
          f.makeRequestURL = data.makeRequestURL
          f.userRequestCount = data.userRequestCount
          f.full = true
          return f
        }
        return f
      })
    },
    requestMade(data) {
      this.alreadyRequested.add(data.id)
    },
    updatePublicBody(publicbody) {
      this.publicbody = publicbody
    },
    tokenUpdated(token) {
      this.$root.csrfToken = token
    },
    startRequest(data) {
      if (this.clientId) {
        this.room.send({
          type: 'reserve',
          obj_id: '' + data.id,
          client_id: this.clientId
        })
      }
      this.showRequestForm = data
    },
    requestFormClosed() {
      if (this.clientId) {
        if (this.alreadyRequested.has(this.showRequestForm.id)) {
          // Request has been sent, reserve item again
          // until request has come through
          this.room.send({
            type: 'reserve',
            obj_id: '' + this.showRequestForm.id,
            client_id: this.clientId
          })
        } else {
          this.room.send({
            type: 'unreserve',
            obj_id: '' + this.showRequestForm.id,
            client_id: this.clientId
          })
        }
      }
      this.showRequestForm = null
    },
    getUrlWithParams(url) {
      let query = this.searchParameters
      if (query.length === 0 && this.settings.order) {
        query = [['order', this.settings.order]]
      }
      const queryString = query
        .map((p) => `${p[0]}=${encodeURIComponent(p[1])}`)
        .join('&')
      return `${url}&${queryString}`
    },
    setResolutionFilter(name) {
      if (this.resolution === name) {
        this.resolution = null
      } else {
        this.resolution = name
      }
      this.updateData()
    },
    setCategoryFilter(category) {
      if (this.currentCategory === category) {
        this.currentCategory = null
      } else {
        this.currentCategory = category
      }
      this.updateData()
    },
    searchObjects: debounce(function () {
      this.updateData()
    }, 400),
    updateData(url = null) {
      if (url === null) {
        url = this.getUrlWithParams(this.baseUrl)
      }
      if (this.lastSearch === url && !this.lastSearchWasRandom) {
        return
      }
      if (url.indexOf('offset=') === -1 && this.objects.length > 0) {
        // we are not paging
        this.objects = []
        this.$refs.searchTop.scrollIntoView()
      }
      if (this.abortController) {
        this.abortController.abort()
      }
      this.abortController = new AbortController()
      this.lastSearch = url
      this.loading = true
      window
        .fetch(url, { signal: this.abortController.signal })
        .then((response) => response.json())
        .then((data) => {
          this.loading = false
          this.meta = data.meta
          if (this.lastSearchWasRandom) {
            this.nextUrl = null
            this.objects = data.objects
          } else if (this.lastSearch.indexOf('offset=') !== -1) {
            this.nextUrl = data.meta.next
            this.objects.push(...data.objects)
          } else {
            this.objects = data.objects
            this.nextUrl = data.meta.next
          }
          this.hasSearched = true
          this.abortController = null
          this.getFollowers()
        })
        .catch((e) => {
          // eslint-disable-next-line no-console
          console.warn(`Fetch 1 error: ${e.message}`)
        })
    },
    fetch() {
      if (this.nextUrl === null) {
        this.hasSearched = false
      }
      return this.updateData(this.nextUrl)
    },
    getFollowers() {
      const requestIds = this.objects
        .map((m) => m.foirequest)
        .filter((x) => !!x)
      if (requestIds.length === 0) {
        return
      }
      const requests = requestIds.join(',')
      window
        .fetch(`/api/v1/following/?request=${requests}`)
        .then((response) => {
          return response.json()
        })
        .then((data) => {
          const requestMapping = new Map()
          this.objects.forEach((o, i) => {
            if (o.foirequest) {
              requestMapping.set(o.foirequest, i)
            }
          })
          data.objects.forEach((followObj) => {
            const parts = followObj.request.split('/')
            const requestId = parseInt(parts[parts.length - 2])

            const objIndex = requestMapping.get(requestId)
            const obj = this.objects[objIndex]
            if (obj) {
              Vue.set(obj, 'follow', followObj)
            }
          })
        })
    },
    followedRequest(data, resourceUri) {
      data.follow.follows = true
      data.follow.resource_uri = resourceUri
    }
  }
}
</script>

<style lang="scss" scoped>
.list-item {
  transition: all 0.3s;
}

.list-enter-active {
  transition-timing-function: cubic-bezier(0, 0, 0.2, 1);
}

.list-leave-active {
  transition-timing-function: cubic-bezier(0.4, 0, 1, 1);
}

.list-enter,
.list-leave-to {
  transform: scale(0);
  opacity: 0;
  position: relative;
}

.list-leave-move {
  position: relative;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}

.fleisch-form-background {
  padding: 2rem 0;
  margin-bottom: 1rem;
  background-image: url('../../img/fleisch-backdrop.jpg');
  background-size: cover;
}

.fleisch-form-container {
  display: inline-flex;
  overflow: hidden;
  color: #000;

  .fleisch-form {
    display: flex;
    flex-direction: column;
    justify-content: space-evenly;
    align-items: center;
    width: 100%;
    border: 2px #000 solid;
    padding: 0.5rem 3rem;
    border-radius: 50%;
    background-color: #fff;

    input {
      color: #000;
    }
  }
}
</style>
