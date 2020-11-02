<template>
  <div>
    <h5>
      Filter
    </h5>

    <div class="mb-3">
      <CampaignListTag
        v-for="res in Object.keys(resolutions)"
        :key="res"
        :active="res === resolution"
        :status="res"
        @click="setResolutionFilter(res)"
      >
        {{ resolutions[res] }}
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
        class="list-item"
        @filter="setTagFilter"
      />
    </transition-group>
  </div>
</template>

<script>
import CampaignListTag from './campaign-list-tag';
import CampaignListItem from './campaign-list-item';

export default {
  name: 'campaign-list',
  components: { CampaignListTag, CampaignListItem },
  props: {
    config: {
      type: Object,
    },
  },
  data() {
    return {
      objects: [],
      tagFilters: [],
      resolution: null,
      resolutions: {
        normal: 'Noch nicht angefragt',
        pending: 'Anfrage läuft',
        successful: 'Anfrage erfolgreich',
        refused: 'Anfrage abgelehnt',
      },
    };
  },
  mounted() {
    this.fetch();
  },
  computed: {
    filteredObjects() {
      return this.objects.filter(object => {
        const resolution = !this.resolution || this.resolution === object.resolution
        const tag = this.tagFilters.length === 0 || this.tagFilters.some(t => object.context.tags.includes(t))

        return resolution && tag
      })
    },
    allTags() {
      const tags = new Set()
      this.objects
        .map(object => object.context.tags)
        .flat()
        .forEach(tag => tags.add(tag))
      
      return [...tags].sort()
    }
  },
  methods: {
    setResolutionFilter(name) {
      if (this.resolution === name) {
        this.resolution = null;
      } else {
        this.resolution = name;
      }
    },
    setTagFilter(tag) {
      if (this.tagFilters.includes(tag)) {
        const i = this.tagFilters.findIndex(t => t === tag);
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
        .then((response) => {
          return response.json();
        })
        .then((data) => {
          this.objects = data;
        });
    },
  },
};
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