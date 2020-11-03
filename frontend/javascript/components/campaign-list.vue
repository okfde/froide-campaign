<template>
  <div class="min-vh-100">
    <h5>
      Filter
    </h5>

    <input
      type="search"
      v-model="search"
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
      <CampaignListTag
        v-for="tag in allTags"
        :key="tag"
        :active="tagFilters.includes(tag)"
        @click="setTagFilter(tag)"
      >
        #{{ tag }}
      </CampaignListTag>
    </div>

    <transition-group name="list">
      <CampaignListItem
        v-for="object in filteredObjects"
        :key="object.ident"
        :object="object"
        :tagFilters="tagFilters"
        :language="language"
        class="list-item"
        @filter="setTagFilter"
      />

      <div
        class="text-center my-5 py-5"
        v-if="filteredObjects.length === 0"
        key="noResults"
      >
        <p class="text-secondary">{{ i18n.noResults }}</p>
      </div>
    </transition-group>
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
      tagFilters: [],
      resolution: null,
      resolutions: ['normal', 'pending', 'successful', 'refused']
    }
  },
  mounted() {
    this.fetch()
  },
  computed: {
    filteredObjects() {
      const filtered =  this.objects
        .filter(object => {
          const resolution = !this.resolution || this.resolution === object.resolution
          const tag = this.tagFilters.length === 0 || this.tagFilters.some(t => object.context.tags.includes(t))

          return resolution && tag
        })
        .map(object => ({
          ...object,
          title: (object.context.intl[this.language] || object).title
        }))

      if (this.search.length < 2) return filtered

      const fuse = new Fuse(filtered, {
        keys: this.settings.fuseKeys || ['title'],
        sort: true
      })

      return fuse.search(this.search)
    },
    allTags() {
      const tags = new Set()
      this.objects
        .map(object => object.context.tags)
        .flat()
        .forEach(tag => tags.add(tag))
      
      return [...tags].sort().filter(Boolean)
    },
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
    },
    setTagFilter(tag) {
      if (this.tagFilters.includes(tag)) {
        const i = this.tagFilters.findIndex(t => t === tag)
        this.tagFilters.splice(i, 1)
      } else {
        this.tagFilters.push(tag)
      }
    },
    fetch() {
      window
        .fetch(
          `/api/v1/campaigninformationobject/search/?campaign=${this.config.campaignId}&limit=off`
        )
        .then(response => response.json())
        .then(data => {
          this.objects = data
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