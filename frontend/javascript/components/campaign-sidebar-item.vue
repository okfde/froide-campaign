<template>
  <div class="sidebar-item" :id="'sidebar-' + itemId">
    <div class="sidebar-item-inner">
      <div class="container-fluid">
        <div class="row">
          <div class="col info-column">
            <h5 v-if="data.title" class="venue-name">
              {{ data.title }}
            </h5>
            <div v-else class="venue-name-dummy dummy dummy-blinker"></div>
            <p v-if="data.subtitle">{{ data.subtitle }}</p>
            <p v-if="data.address" class="venue-address">{{ data.address }}</p>
          </div>
          <div class="col text-right">
            <h5>
              <CampaignListTag
                v-for="(category, i) in data.categories"
                :key="i"
                :isButton="false">
                #{{ category.title }}
              </CampaignListTag>
            </h5>
          </div>
        </div>
        <div class="row">
          <div class="col-12">
            <div v-if="status !== 'normal'" class="request-status">
              <p :style="{ color: color }">
                {{ statusString }} <br />
                <a :href="'/a/' + data.foirequest" target="_blank"
                  >zur Anfrage&nbsp;&rarr;</a
                >
              </p>
              <p v-if="allowMultipleRequests">
                <a
                  @click.prevent.stop="startRequest"
                  class="btn btn-primary btn-sm make-request-btn text-white"
                  target="_blank">
                  erneut<br class="d-block d-sm-none" />
                  anfragen&nbsp;&rarr;
                </a>
              </p>
            </div>
            <p v-if="status === 'normal' || status === 'withdrawn'">
              <a
                v-if="buttonText"
                @click.prevent.stop="startRequest"
                class="btn btn-primary btn-sm make-request-btn text-white"
                target="_blank">
                <br class="d-block d-sm-none" />
                {{ this.buttonText }}&nbsp;&rarr;
              </a>
              <a
                v-else
                @click.prevent.stop="startRequest"
                class="btn btn-primary btn-sm make-request-btn text-white"
                target="_blank">
                Ort<br class="d-block d-sm-none" />
                anfragen&nbsp;&rarr;
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CampaignItemMixin from '../lib/mixin'
import CampaignListTag from './campaign-list-tag'

export default {
  name: 'campaign-sidebar-item',
  mixins: [CampaignItemMixin],
  components: { CampaignListTag },
  props: {
    color: {
      type: String
    },
    buttonText: {
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
    },
    allowMultipleRequests: {
      type: Boolean
    }
  }
}
</script>

<style lang="scss" scoped>
.sidebar-item {
  padding: 0;
  width: 100%;
}

.sidebar-item-inner {
  padding: 1rem 0 1rem;
  border-bottom: 2px solid #eee;
}

.sidebar-item:first-child .sidebar-item-inner {
  padding-top: 0.5rem;
}

@media screen and (min-width: 768px) {
  .sidebar-item:first-child .sidebar-item-inner {
    padding-top: 1rem;
  }
}

.sidebar-item:last-child .sidebar-item-inner {
  border-bottom: 0px;
}

.image-column {
  padding: 0 5px 0 5px;
  min-width: 110px;
}

@media screen and (min-width: 768px) {
  .image-column {
    padding: 0 5px 0 5px;
  }
}

@media screen and (min-width: 768px) {
  .map-container {
    height: 80vh;
  }
  .sidebar {
    height: 80vh;
    overflow-y: scroll;
  }
}

.image-column-inner,
.image-column-inner-link {
  display: block;
  background-color: #eee;
  padding: 0;
}

.image-column-inner:hover,
.image-column-inner-link:hover {
  text-decoration: none;
}

.image-column-inner-link {
  cursor: pointer;
}

.info-column {
  padding-left: 15px;
  padding-right: 10px;
}

.venue-address {
  font-size: 0.8em;
  color: #687683;
  display: inline-block;
  white-space: pre-line;
}

.dummy {
  background-color: #ddd;
  display: block;
}
.dummy-blinker {
  animation: blinker 0.8s linear infinite;
}

@keyframes blinker {
  50% {
    opacity: 0.25;
  }
}

.dummy-provider {
  height: 9.5rem;
  width: 100%;
}

.venue-name-dummy {
  height: 2rem;
  width: 80%;
}

.venue-address-dummy {
  margin: 1rem 0;
  height: 3rem;
  width: 40%;
}

.dummy-actions {
  margin-top: 1rem;
  height: 2rem;
  width: 80%;
}

.highlighted {
  background-color: #fffbbf;
}

.venue-img {
  height: 70px;
  width: 100%;
  object-fit: cover;
}

.dummy-image {
  height: 70px;
  width: 100%;
  background-color: #aaa;
}

.make-request-btn {
  white-space: normal !important;
}

.request-status {
  font-size: 0.9rem;
}

.image-column-provider {
  padding: 0 0.5rem;
}

.provider-logo {
  background-repeat: no-repeat;
  background-size: contain;
  display: block;
  margin: 0.25rem 0 0;
  width: 60px;
  height: 32px;
}

.foursquare-logo {
  height: 10px;
}

.review-count {
  font-size: 0.7rem;
  display: block;
  margin: 0.25rem 0 0;
  padding: 0 0 0.25rem;
  color: #888;
  text-decoration: none;
}

.request-status {
  font-size: 0.9rem;
}
</style>
