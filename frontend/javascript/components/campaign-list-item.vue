<template>
  <div class="d-flex mb-3">
    <div class="card flex-1 w-100">
      <div class="card-body d-flex flex-column">
        <h5>{{ object.title }}</h5>
        <div class="d-flex mt-1">
          <div v-if="object.subtitle || object.address" class="mb-3">
            <p class="text-muted mb-0">
              {{ object.subtitle }}
            </p>
            <small v-if="object.address" class="text-muted">{{
              object.address
            }}</small>
          </div>
          <div class="ms-auto text-end">
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
              class="btn btn-normal"
              @click.prevent.stop="$emit('startRequest', object)">
              {{ i18n.request }}
            </a>
            <button
              v-else-if="object.public === undefined ? false : !object.public"
              class="btn btn-disabled"
              disabled>
              {{ i18n.requestNotPublic }}
            </button>
            <div v-else>
              <a
                :href="'/a/' + object.foirequest"
                target="_blank"
                class="btn"
                :class="[`btn-${object.resolution}`]">
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
            <campaign-follow
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

<style lang="scss" scoped>
@import 'froide/frontend/styles/variables';
@import 'froide/frontend/styles/color-contrast';

/* FIXME: use colors from variables */
$normal: $primary;
$pending: $warning;
$successful: $success;
$refused: $danger;
$withdrawn: $blue-800;

.btn-normal {
  background-color: $normal;
  border-color: $normal;
  box-shadow: none;
  color: color-contrast($normal);
}

.btn-pending {
  background-color: $pending;
  border-color: $pending;
  box-shadow: none;
  background-color: $pending;
  color: color-contrast($pending);
}

.btn-successful {
  background-color: $successful;
  border-color: $successful;
  box-shadow: none;
  background-color: $successful;
  color: color-contrast($successful);
}

.btn-refused {
  background-color: $refused;
  border-color: $refused;
  box-shadow: none;
  background-color: $refused;
  color: color-contrast($refused);
}

.btn-withdrawn {
  background-color: $withdrawn;
  border-color: $withdrawn;
  box-shadow: none;
  background-color: $withdrawn;
  color: color-contrast($withdrawn);
}
</style>
