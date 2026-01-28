<template>
  <div class="d-flex mb-3">
    <div class="card flex-1 w-100">
      <div class="card-body d-flex flex-column">
        <h5>{{ object.title }}</h5>
        <div
          v-if="object.subtitle || object.address || object.categories"
          class="d-flex mt-1">
          <div v-if="object.subtitle || object.address" class="mb-3">
            <p class="text-muted mb-0">
              {{ object.subtitle }}
            </p>
            <small v-if="object.address" class="text-muted">{{
              object.address
            }}</small>
          </div>
          <div v-if="object.categories" class="ms-auto text-end">
            <h5>
              <CampaignListTag
                v-for="category in object.categories"
                :key="category.id"
                :active="currentCategory === category.id"
                @click="$emit('setCategoryFilter', category.id)">
                #{{ category.title }}
              </CampaignListTag>
            </h5>
          </div>
        </div>
        <div class="row mt-auto">
          <div class="col">
            <button v-if="isReserved" class="btn btn-disabled" disabled>
              {{ i18n.requestReserved }}
            </button>
            <a
              v-else-if="hasNoRequest"
              :href="object.request_url"
              class="btn btn-outline-primary"
              @click.prevent.stop="$emit('startRequest', object)">
              {{ i18n.request }}
            </a>
            <button
              v-else-if="
                object.readable === undefined ? false : !object.readable
              "
              class="btn btn-disabled"
              disabled>
              {{ i18n.requestNotPublic }}
            </button>
            <div v-else>
              <a
                :href="'/a/' + object.foirequest"
                target="_blank"
                class="btn"
                :class="btnClass">
                {{ i18n.viewRequest }}
              </a>
              <a
                v-if="allowMultipleRequests"
                :href="object.request_url"
                class="btn btn-link"
                @click.prevent.stop="$emit('startRequest', object)">
                {{ i18n.requestAgain }}
              </a>
            </div>
          </div>
          <div
            v-if="object.follow && object.follow.can_follow !== false"
            class="col">
            <CampaignFollow
              :follow="object.follow"
              @followed="$emit('followed', $event)"
              @unfollowed="$emit('unfollowed')" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CampaignListTag from './campaign-list-tag'
import CampaignFollow from './campaign-follow.vue'
import i18n from '../../i18n/campaign-list.json'

export default {
  components: { CampaignListTag, CampaignFollow },
  props: {
    object: Object,
    currentCategory: Number,
    language: String,
    allowMultipleRequests: Boolean,
    reservations: {
      type: Map,
      default: null
    },
    clientId: {
      type: String,
      default: null
    }
  },
  computed: {
    i18n() {
      return i18n[this.language]
    },
    hasNoRequest() {
      return this.object.resolution === 'normal'
    },
    btnClass() {
      if (this.object.resolution === 'pending') {
        return 'btn-outline-secondary'
      } else if (this.object.resolution === 'successful') {
        return 'btn-outline-success'
      } else if (this.object.resolution === 'refused') {
        return 'btn-outline-danger'
      } else if (this.object.resolution === 'withdrawn') {
        return 'btn-outline-info'
      }
      return 'btn-outline-primary'
    },
    isReserved() {
      if (!this.reservations) {
        return false
      }
      const someClientId = this.reservations.get('' + this.object.id)
      return !!(someClientId && someClientId !== this.clientId)
    }
  }
}
</script>
