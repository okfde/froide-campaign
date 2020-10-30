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

    <div
      class="card mb-2"
      v-for="object in filteredObjects"
      :key="object.ident"
    >
      <div class="card-body">
        <h5>{{ object.title }}</h5>
        <div class="row mt-3">
          <div class="col">
            <small class="text-muted">{{ object.context.ident }}</small>
          </div>
          <div class="col text-right">
            <h5>
              <CampaignListTag
                v-for="(tag, i) in object.context.tags"
                :key="i"
                :active="tagFilters.includes(tag)"
                @click="setTagFilter(tag)"
              >
                #{{ tag }}
              </CampaignListTag>
            </h5>
          </div>
        </div>
        <div class="row mt-3">
          <div class="col">
            <a
              v-if="object.resolution === 'normal'"
              :href="object.request_url"
              class="btn btn-normal text-white"
            >
              Anfragen
            </a>
            <a
              v-else
              :href="'/a/' + object.foirequest"
              class="btn text-white"
              :class="[`btn-${object.resolution}`]"
            >
              Anfrage ansehen
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CampaignListTag from './campaign-list-tag';

export default {
  name: 'campaign-list',
  components: { CampaignListTag },
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
$normal: #007bff;
$pending: #ffc107;
$successful: #28a745;
$refused: #dc3545;

.btn-normal {
  background-color: $normal;
  border-color: $normal;
  box-shadow: none;
}

.btn-pending {
  background-color: $pending;
  border-color: $pending;
  box-shadow: none;
  background-color: $pending;
}

.btn-successful {
  background-color: $successful;
  border-color: $successful;
  box-shadow: none;
  background-color: $successful;
}

.btn-refused {
  background-color: $refused;
  border-color: $refused;
  box-shadow: none;
  background-color: $refused;
}
</style>