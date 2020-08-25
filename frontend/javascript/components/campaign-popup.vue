<template>
  <div class="campaign-popup" :id="'popup-' + itemId">
    <div class="row">
      <div class="col-12">
        <h4 class="venue-name">{{ data.title }}</h4>
      </div>
    </div>
    <div class="row">
      <div class="col-12">
        <div v-if="hasRequests" class="request-status">
          <p :style="{ color: color }">
            {{ status }}
          </p>
          <p>
            <a v-for="fr in data.foirequests" :key="fr"
              :href="'/a/' + fr"
              target="_blank"
            >
              zur Anfrage&nbsp;&rarr;
            </a>
          </p>
        </div>
        <a class="btn btn-primary btn-sm make-request-btn" :href="data.request_url"  target="_blank">
          Anfrage<br class="d-block d-sm-none"/>
          erstellen&nbsp;&rarr;
        </a>
      </div>
    </div>
  </div>
</template>

<script>
import CampaignItemMixin from '../lib/mixin'

export default {
  name: 'campaign-popup',
  mixins: [CampaignItemMixin],
  props: {
    color: {
      type: String
    },
    status: {
      type: String
    },
    data: {
      type: Object
    }
  }
}
</script>

<style lang="scss" scoped>

.venue-name {
  min-width: 240px;
}

.image-column {
  padding: 0 5px;
}

.info-column {
  padding: 0 5px;
}

.venue-img {
  height: 70px;
  width: 100%;
  object-fit: cover;
}

.venue-address {
  color: #687683;
  font-size: 1rem;
  display: inline-block;
  margin: 0 0 0.5rem;
  white-space: pre-line;
}

.to-request-button {
  display: block;
  font-size: 1rem;
  color: #28a745;
}

.make-request-btn {
  color: white;
  white-space: normal !important;
}

.request-status {
  font-size: 0.9rem;
}

</style>
