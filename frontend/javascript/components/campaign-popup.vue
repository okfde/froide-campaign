<template>
  <div class="campaign-popup" :id="'popup-' + itemId">
    <div class="row">
      <div class="col-12">
        <h4 class="venue-name">{{ data.title }}</h4>
        <p v-if="data.subtitle">{{ data.subtitle }}</p>
        <p v-if="data.address" class="venue-address">{{ data.address }}</p>
      </div>
    </div>
    <div class="row">
      <div class="col">
        <h5>
          <CampaignListTag
            v-for="(tag, i) in data.tags"
            :key="i"
            :isButton="false"
          >
            #{{ tag }}
          </CampaignListTag>
        </h5>
      </div>
    </div>
    <div class="row">
      <div class="col-12">
        <div v-if="status !== 'normal'" class="request-status">
          <p :style="{'color':color}">
              {{ statusString }}
          </p>
          <p>
            <a :href="'/a/' + data.foirequest" target="_blank">zur Anfrage&nbsp;&rarr;</a>
          </p>
        </div>
        <p v-if="status == 'normal' || status === 'withdrawn'">
          <a v-if="buttonText" @click.prevent.stop="startRequest" class="btn btn-primary btn-sm make-request-btn text-white" target="_blank">
            <br class="d-block d-sm-none"/>
            {{this.buttonText}}&nbsp;&rarr;
          </a>
          <a v-else @click.prevent.stop="startRequest" class="btn btn-primary btn-sm make-request-btn text-white" target="_blank">
            Ort<br class="d-block d-sm-none"/>
            anfragen&nbsp;&rarr;
          </a>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import CampaignItemMixin from '../lib/mixin'
import CampaignListTag from './campaign-list-tag'

export default {
  name: 'campaign-popup',
  mixins: [CampaignItemMixin],
  components: { CampaignListTag },
  props: {
    buttonText: {
      type: String
    },
    color: {
      type: String
    },
    status: {
      type: String
    },
    statusString: {
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
