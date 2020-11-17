<template>
  <div class="min-vh-100">
    <h5>
      Filter
    </h5>

    <input
      type="search"
      v-model="search"
      @keyup="searchObjects"
      :placeholder="i18n.search"
      class="form-control my-4"
    />

    <div class="mb-3">
      <CampaignListTag
        v-for="res in resolutions"
        :key="res"
        :active="res === resolution"
        :status="res"
        @click="setResolutionFilter(res)"
      >
        {{ i18n.resolutions[res] }}
      </CampaignListTag>
      <div v-if="!this.settings.hide_tag_filters">
        <CampaignListTag
          v-for="tag in config.tags"
          :key="tag"
          :active="currenTag === tag"
          @click="setTagFilter(tag)"
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
        :currentTag="currenTag"
        :language="language"
        class="list-item"
        @filter="setTagFilter"
      />

      <div
        class="text-center my-5 py-5"
        v-if="objects.length === 0"
        key="noResults"
      >
        <p class="text-secondary">{{ i18n.noResults }}</p>
      </div>
    </transition-group>
    <div
      class="row justify-content-center mb-5"
      v-if="this.meta.next"
    >
        <button @click="fetch" class="btn btn-light">Load more</button>
    </div>
  </div>
</template>

<script>
import CampaignListTag from './campaign-list-tag'
import CampaignListItem from './campaign-list-item'
import Fuse from 'fuse.js'
import i18n from '../../i18n/campaign-list.json'

export default {
  name: 'campaign-list',
  components: { CampaignListTag, CampaignListItem },
  props: {
    config: Object,
    settings: Object,
    language: {
      type: String,
      default: 'de'
    }
  },
  data() {
    return {
      search: '',
      objects: [],
      baseUrl: `/api/v1/campaigninformationobject/?campaign=${this.config.campaignId}&limit=${this.settings.limit}`,
      nextUrl: `/api/v1/campaigninformationobject/?campaign=${this.config.campaignId}&limit=${this.settings.limit}`,
      meta: [],
      currenTag: '',
      resolution: null,
      resolutions: ['normal', 'pending', 'successful', 'refused']
    }
  },
  mounted() {
    this.fetch()
  },
  computed: {
    i18n() {
      return i18n[this.language]
    }
  },
  methods: {
    setResolutionFilter(name) {
      if (this.resolution === name) {
        this.resolution = null
      } else {
        this.resolution = name
      }
      window
        .fetch(
          this.baseUrl + `&search=${this.search}&status=${this.resolution}&tag=${this.currenTag}`
        )
        .then(response => response.json())
        .then(data => {
          this.meta = data.meta
          this.nextUrl = data.meta.next
          this.objects = data.objects
      })
    },
    setTagFilter(tag) {
      this.currenTag = tag
      window
        .fetch(
          this.baseUrl + `&search=${this.search}&status=${this.resolution}&tag=${this.currenTag}`
        )
        .then(response => response.json())
        .then(data => {
          this.meta = data.meta
          this.nextUrl = data.meta.next
          this.objects = data.objects
      })
    },
    searchObjects() {
      setTimeout(() => {
        window
          .fetch(
            this.baseUrl + `&search=${this.search}&status=${this.resolution}&tag=${this.currenTag}`
          )
          .then(response => response.json())
          .then(data => {
            this.meta = data.meta
            this.nextUrl = data.meta.next
            this.objects = data.objects
        })
      }, 200)
    },
    fetch() {
      window
        .fetch(
          this.nextUrl + `&search=${this.search}&status=${this.resolution}`
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