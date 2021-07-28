<template>
  <div :class="{ 'mx-n3': settings.twoColumns }">
    <campaign-request v-if="showRequestForm"
      :config="requestConfig"
      :buttonText="config.button_text"
      :request-form="requestForm"
      :user-info="user"
      :user-form="userForm"
      :data="showRequestForm"
      :current-url="''"
      :campaignId="config.campaignId"
      :lawType="config.lawType"
      :extraText="config.requestExtraText"
      :hideNewsletterCheckbox="hideNewsletterCheckbox"
      :subscribeText="config.subscribe_text"
      :hasSubscription="config.hasSubscription"
      :publicbody="publicbody"
      :publicbodies="[publicbody]"
      :publicbodiesOptions="publicbodies"
      :localRequestCount="localRequestCount"
      :maxRequestsPerUser="maxRequestsPerUser"
      @publicBodyChanged="updatePublicBody"
      @detailfetched="detailFetched"
      @requestmade="requestMade"
      @userupdated="userUpdated"
      @tokenupdated="tokenUpdated"
      @close="requestFormClosed"
    ></campaign-request>

    <div v-show="!showRequestForm">
      <div
        v-if="!this.settings.input_field"
        class="container mx-auto"
        ref="searchTop"
        :class="[settings.twoColumns ? 'col-md-12' : 'col-md-5']"
      >
        <h5>
          Filter
        </h5>
        <input
          type="search"
          v-model="search"
          @keyup="searchObjects"
          :placeholder="i18n.search"
          class="form-control mb-3"
        />
      </div>

      <div class="fleisch-form-background" v-if="this.settings.input_field == 'topf-secret-fleisch'">
        <div class="container">
          <div class="col-md-5 mx-auto">
            <div
              class="fleisch-form-container embed-responsive embed-responsive-21by9"
            >
              <div class="fleisch-form shadow">
                <p class="h4 font-weight-bolder">DE</p>
                <div class="input-group">
                  <input v-model="search" @keyup="searchObjects" placeholder="BY 1234" class="form-control text-center h4"/>
                </div>
                <p class="h4 font-weight-bolder">EG</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div
        class="container mx-auto mb-3"
        :class="[settings.twoColumns ? 'col-md-12' : 'col-md-5']"
      >
        <div v-if="!this.settings.hide_status_filter">
          <CampaignListTag
            v-for="res in resolutions"
            :key="res"
            :active="res === resolution"
            :status="res"
            @click="setResolutionFilter(res)"
          >

            {{ i18n.resolutions[res] }}
          </CampaignListTag>
        </div>
        <div v-if="!this.settings.hide_tag_filters">
          <CampaignListTag
            v-for="category in config.categories"
            :key="category.id"
            :active="currentCategory === category.id"
            @click="setCategoryFilter(category.id)"
          >
            #{{ category.title }}
          </CampaignListTag>
        </div>

        <transition-group
          name="list"
          tag="div"
          class="row mt-3 mx-0"
          :class="{ 'mx-n2': settings.twoColumns}"
        >
          <CampaignListItem
            v-for="object in objects"
            :key="object.ident"
            :object="object"
            :currentCategory="currentCategory"
            :allowMultipleRequests="allowMultipleRequests"
            :language="language"
            class="list-item"
            :class="[settings.twoColumns ? 'col-md-6 px-2' : 'w-100']"
            @startRequest="startRequest"
            @setCategoryFilter="setCategoryFilter"
            @followed="followedRequest(object, $event)"
            @unfollowed="object.follow.follows = false"
          />

          <div
            class="text-center my-5 py-5 w-100"
            v-if="!loading && hasSearched && objects.length === 0"
            key="noResults"
          >
            <p class="text-secondary" v-html="i18n.noResults" />
          </div>
          <div
            class="text-center my-5 py-5 w-100"
            v-if="loading"
            key="loading"
          >
            <div class="spinner-border" role="status">
              <span class="sr-only">Loading...</span>
            </div>
          </div>
        </transition-group>
        <div
          class="row justify-content-center mb-5"
          v-if="!loading && (nextUrl || lastSearchWasRandom)"
        >
            <button @click="fetch" class="btn btn-light">
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
import Room from "froide/frontend/javascript/lib/websocket.ts"

export default {
  name: 'campaign-list',
  components: { CampaignListTag, CampaignListItem, CampaignRequest },
  props: {
    config: Object,
    settings: Object,
    requestConfig: Object,
    requestForm: Object,
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
    this.$root.csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value
    return {
      allowMultipleRequests: this.settings.allow_multiple_requests ? this.settings.allow_multiple_requests: false,
      alreadyRequested: {},
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
  mounted() {
    if (!this.settings.show_list_after_search) {
      this.nextUrl = this.getUrlWithParams(this.baseUrl)
      this.fetch()
    }
    if (this.settings.live) {
      try {
        this.room = new Room(`/ws/campaign/live/${this.config.campaignId}/`)
        this.room.connect()
          .on('request_made', (event) => {
            if (this.objects.length === 0) {
              return
            }
            this.objects = this.objects.map(o => {
              if (o.ident === event.data.ident) {
                return event.data
              }
              return o
            })
          })
      } catch (e) {
        console.error(e)
      }
    }
  },
  computed: {
    i18n() {
      const settings = this.settings || {}
      const messages = deepmerge(i18n, settings.overwrite_messages || {})

      return messages[this.language]
    },
    hideNewsletterCheckbox () {
      return (this.settings.hide_newsletter_checkbox) ? this.settings.hide_newsletter_checkbox : true
    },
    maxRequestsPerUser () {
      return this.settings.maxRequestsPerUser || 0
    },
    searchParameters () {
      let defaults = [
        ['search', this.search],
        ['status', this.resolution],
        ['category', this.currentCategory],
      ]
      return defaults.filter(d => !!d[1])
    },
    hasSearchParameters () {
      return this.searchParameters.length > 0
    },
    lastSearchWasRandom () {
      return this.lastSearch && this.lastSearch.indexOf('order=random') !== -1
    },
    localRequestCount () {
      let count = 0
      for (let x in this.alreadyRequested) {
        count += 1
      }
      return count
    }
  },
  methods: {
    userUpdated (user) {
      this.user = user
    },
    detailFetched (data) {
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
    requestMade (data) {
      this.alreadyRequested[data.id] = true
    },
    updatePublicBody (publicbody) {
      this.publicbody = publicbody
    },
    tokenUpdated (token) {
      this.$root.csrfToken = token
    },
    startRequest (data) {
      this.showRequestForm = data
    },
    requestFormClosed () {
      this.showRequestForm = null
    },
    getUrlWithParams (url) {
      let query = this.searchParameters
      if (query.length === 0 && this.settings.order) {
        query = [['order', this.settings.order]]
      }
      let queryString = query.map(p => `${p[0]}=${encodeURIComponent(p[1])}`).join('&')
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
      if (this.currentCategory == category) {
        this.currentCategory = null
      } else {
        this.currentCategory = category
      }
      this.updateData()
    },
    searchObjects: debounce(function () {
      this.updateData()
    }, 400),
    updateData (url = null) {
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
      this.abortController = new AbortController();
      this.lastSearch = url
      this.loading = true
      window.fetch(url, {signal: this.abortController.signal})
        .then(response => response.json())
        .then(data => {
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
      }).catch(e => {
        console.warn(`Fetch 1 error: ${e.message}`);
      });
    },
    fetch() {
      if (this.nextUrl === null) {
        this.hasSearched = false
      }
      return this.updateData(this.nextUrl)
    },
    getFollowers () {
      let requestIds = this.objects.map(m => m.foirequest).filter(x => !!x)
      let requests = requestIds.join(',')
      window.fetch(`/api/v1/following/?request=${requests}`)
        .then((response) => {
          return response.json()
        }).then((data) => {
          let requestMapping = new Map()
          this.objects.forEach((o, i) => {
            if (o.foirequest) {
              requestMapping.set(o.foirequest, i)
            }
          })
          data.objects.forEach((followObj) => {
            let parts = followObj.request.split('/')
            let requestId = parseInt(parts[parts.length - 2])

            let objIndex = requestMapping.get(requestId)
            let obj = this.objects[objIndex]
            if (obj) {
              Vue.set(obj, 'follow', followObj)
            }
          })
        })
    },
    followedRequest (data, resourceUri) {
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
  transition-timing-function: cubic-bezier(0.0, 0.0, 0.2, 1);;
}

.list-leave-active {
  transition-timing-function: cubic-bezier(0.4, 0.0, 1, 1);
}

.list-enter, .list-leave-to {
  transform: scale(0);
  opacity: 0;
  position: relative;
}

.list-leave-move {
  position: relative;
  transition-timing-function: cubic-bezier(0.4, 0.0, 0.2, 1);;
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