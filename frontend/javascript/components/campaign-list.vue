<template>
  <div>
    <h5>
      Filter<br />
      <span v-for="(res, index) in Object.keys(resolutions)"
            type="button"
            :key="index"
            :class="[{'badge-dark': res === resolution}, 'filter-badge-' + res]"
            class="badge badge-pill badge-light mb-1 mr-1"
            @click="setFilter(res)"
            >{{ resolutions[res] }}
      </span>
    </h5>
    <div class="card mb-2" v-for="(object, index) in filteredObjects" :key="index">
      <div class="card-body">
        <h5>{{ object.title }}</h5>
        <div class="row mt-3">
          <div class="col">
            <small class="text-muted">{{ object.ident }}</small>
          </div>
          <!-- <div class="col text-right">
            <h5>
              <span class="badge badge-pill badge-light mb-1 mr-1">#{{ object.context.committee }}</span>
            </h5>
          </div> -->
        </div>
        <div class="row mt-3">
          <div class="col">
            <a v-if="object.resolution === 'normal'" :href="object.request_url" class="btn btn-normal text-white">Anfragen</a>
            <a v-if="object.resolution === 'pending'" :href="'/a/' + object.foirequest" class="btn btn-pending text-white">Anfrage ansehen</a>
            <a v-if="object.resolution === 'successful'" :href="'/a/' + object.foirequest" class="btn btn-successful text-white">Anfrage ansehen</a>
            <a v-if="object.resolution === 'refused'" :href="'/a/' + object.foirequest" class="btn btn-refused text-white">Anfrage ansehen</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>

export default {
  name: "campaign-list",
  props: {
    config: {
      type: Object,
    }
  },
  data() {
    return {
      objects: null,
      filteredObjects: null,
      resolution: null,
      resolutions: {
        normal: 'Noch nicht angefragt',
        pending: 'Anfrage läuft',
        successful: 'Anfrage erfolgreich',
        refused: 'Anfrage abgelehnt'
      }
    }
  },
  mounted() {
    this.fetch()
  },
  methods: {
    setFilter (name) {
      if (this.resolution === name) {
        this.resolution  = null
      } else {
        this.resolution = name
      }
      this.search()
    },
    filter (data) {
      let filteredData = []
      data.forEach((object, i) => {
        if (this.isInFilter(object)) {
          filteredData.push(object)
        }
      })
      return filteredData
    },
    isInFilter (object) {
      return (!this.resolution || this.resolution == object.resolution)
    },
    search () {
      this.filteredObjects = this.filter(this.objects)
    },
    fetch () {
      window
        .fetch(
          `/api/v1/campaigninformationobject/search/?campaign=${this.config.campaignId}&limit=off`
        )
        .then((response) => {
          return response.json()
        })
        .then((data) => {
          this.objects = data
          this.filteredObjects = this.filter(data)
        })
    }
  }
}
</script>

<style lang="scss" scoped>
  $normal: #007bff;
  $pending: #ffc107;
  $successful: #28a745;
  $refused: #dc3545;

  .btn-normal {
    background-color:$normal;
    border-color:$normal;
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

  .filter-badge {
    content: '';
    display: inline-block;
    width: 12px;
    height: 12px;
    -moz-border-radius: 6px;
    -webkit-border-radius: 6px;
    border-radius: 6px;
    margin-right: 0.2rem;
  }

  .filter-badge-normal:before {
    @extend .filter-badge;
    background-color: $normal;
  }

  .filter-badge-pending:before {
    @extend .filter-badge;
    background-color: $pending;
  }

  .filter-badge-successful:before {
    @extend .filter-badge;
    background-color: $successful;
  }

  .filter-badge-refused:before {
    @extend .filter-badge;
    background-color: $refused;
  }

</style>