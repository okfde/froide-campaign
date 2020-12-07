<template>
  <div>
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
      @publicBodyChanged="updatePublicBody"
      @detailfetched="detailFetched"
      @requestmade="requestMade"
      @userupdated="userUpdated"
      @tokenupdated="tokenUpdated"
      @close="requestFormClosed"
    ></campaign-request>

    <div v-show="!showRequestForm">
      <div v-if="!this.settings.input_field" >
        <h5>
          Filter
        </h5>
        <input
          type="search"
          v-model="search"
          @keyup="searchObjects"
          :placeholder="i18n.search"
          class="form-control mb-4"
        />
      </div>

      <div v-if="this.settings.input_field == 'topf-secret-fleisch'" class="embed-responsive embed-responsive-21by9 d-inline-flex" style="overflow: unset !important; color: #000;">
        <div class="d-flex flex-column justify-content-around align-items-center w-100 rounded-circle shadow py-2 px-5" style="border: 2px #000 solid;">
          <p class="h4 font-weight-bolder">DE</p>
          <div class="input-group">
            <input v-model="search" @keyup="searchObjects" placeholder="BY 1234" class="form-control text-center h4" style="color: #000;"/>
          </div>
          <p class="h4 font-weight-bolder">EG</p>
        </div>
      </div>

      <div class="mb-3">
        <div v-if="!this.settings.hide_status_filter">
          <CampaignListTag
            v-for="res in resolutions"
            :key="res"
            :active="res === resolution"
            :status="res"
            :isButton="true"
            @click="setResolutionFilter(res)"
          >

            {{ i18n.resolutions[res] }}
          </CampaignListTag>
        </div>
        <div v-if="!this.settings.hide_tag_filters">
          <CampaignListTag
            v-for="tag in config.tags"
            :key="tag"
            :active="currentTag === tag"
            @click="setTagFilter(tag)"
            :isButton="true"
          >
            #{{ tag }}
          </CampaignListTag>
        </div>
      </div>

      <transition-group name="list">
        <CampaignListItem
          v-for="object in objects"
          :key="object.id"
          :object="object"
          :currentTag="currentTag"
          :language="language"
          class="list-item"
          @filter="setTagFilter"
          @startRequest="startRequest"
        />

        <div
          class="text-center my-5 py-5"
          v-if="objects.length === 0"
          key="noResults"
        >
          <p v-if="hasSearched" class="text-secondary">{{ i18n.noResults }}</p>
        </div>
      </transition-group>
      <div
        class="row justify-content-center mb-5"
        v-if="this.meta.next"
      >
          <button @click="fetch" class="btn btn-light">Load more</button>
      </div>
    </div>
  </div>
</template>

<script>
import CampaignListTag from './campaign-list-tag'
import CampaignListItem from './campaign-list-item'
import Fuse from 'fuse.js'
import i18n from '../../i18n/campaign-list.json'
import CampaignRequest from './campaign-request'

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
      alreadyRequested: {},
      user: this.userInfo,
      hasSearched: false,
      search: '',
      objects: [],
      baseUrl: `/api/v1/campaigninformationobject/?campaign=${this.config.campaignId}&limit=${this.settings.limit}`,
      nextUrl: `/api/v1/campaigninformationobject/?campaign=${this.config.campaignId}&limit=${this.settings.limit}`,
      meta: [],
      currentTag: '',
      resolution: null,
      resolutions: ['normal', 'pending', 'successful', 'refused'],
      showRequestForm: null,
      publicbody: {},
      publicbodies: [],
    }
  },
  mounted() {
    if (!this.settings.show_list_after_search) {
      this.fetch()
    }
  },
  computed: {
    i18n() {
      return i18n[this.language]
    },
    hideNewsletterCheckbox () {
      return (this.settings.hide_newsletter_checkbox) ? this.settings.hide_newsletter_checkbox : false
    },
  },
  methods: {
    userUpdated (user) {
      this.user = user
    },
    detailFetched (data) {
      this.publicbody = data.publicbody
      this.publicbodies = data.publicbodies.results
      this.objects = this.objects.map((f) => {
        if (f.ident === data.ident) {
          f.publicbody = data.publicbody
          f.publicbodies = data.publicbodies.results
          f.makeRequestURL = data.makeRequestURL
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
      return url + `&search=${this.search}&status=${this.resolution}&tag=${this.currentTag}`
    },
    setResolutionFilter(name) {
      if (this.resolution === name) {
        this.resolution = null
      } else {
        this.resolution = name
      }
      this.updateData()
    },
    setTagFilter(tag) {
      if (this.currentTag == tag) {
        this.currentTag = ''
      } else {
        this.currentTag = tag
      }
      this.updateData()
    },
    searchObjects() {
      setTimeout(() => {
        this.updateData()
      }, 200)
    },
    updateData() {
      window
        .fetch(
          this.getUrlWithParams(this.baseUrl)
        )
        .then(response => response.json())
        .then(data => {
          this.meta = data.meta
          this.nextUrl = data.meta.next
          this.objects = data.objects
          this.hasSearched = true
      })
    },
    fetch() {
      window
        .fetch(
          this.getUrlWithParams(this.nextUrl)
        )
        .then(response => response.json())
        .then(data => {
          this.meta = data.meta
          this.nextUrl = data.meta.next
          this.objects.push(...data.objects)
        })
    }
  }
}
</script>

<style lang="scss" scoped>
.list-item {
  transition: all 0.3s ease;
}

.list-enter, .list-leave-to {
  opacity: 0;
}

.list-leave-active {
  position: relative;
}
</style>