<template>
  <div class="d-flex mb-3">
    <div class="card flex-1 w-100">
      <div class="card-body d-flex flex-column">
        <h5>{{ object.title }}</h5>
        <div class="d-flex mt-1">
          <div class="mb-3">
            <p class="text-muted mb-0">
              {{ object.subtitle }}
            </p>
            <small class="text-muted">{{ object.address }}</small>
          </div>
          <div class="ml-auto text-right">
            <h5>
              <CampaignListTag
                v-for="(category) in object.categories"
                :key="category.id"
                :active="currentCategory === category.id"
                @click="$emit('setCategoryFilter', category.id)"
              >
                #{{ category.title }}
              </CampaignListTag>
            </h5>
          </div>
        </div>
        <div class="row mt-auto">
          <div class="col">
            <a
              v-if="hasNoRequest"
              :href="object.makeRequestURL"
              class="btn btn-normal text-white"
              @click.prevent.stop="$emit('startRequest', object)"
            >
              {{ i18n.request }}
            </a>
            <div v-else>
              <a
                :href="'/a/' + object.foirequest"
                target="_blank"
                class="btn text-white"
                :class="[`btn-${object.resolution}`]"
              >
                {{ i18n.viewRequest }}
              </a>
              <a
                v-if="allowMultipleRequests"
                :href="object.makeRequestURL"
                class="btn btn-link"
                @click.prevent.stop="$emit('startRequest', object)"
              >
                {{ i18n.requestAgain }}
              </a>
            </div>
          </div>
          <div
            v-if="object.follow"
            class="col"
          >
            <campaign-follow
              :follow="object.follow"
              @followed="$emit('followed', $event)"
              @unfollowed="$emit('unfollowed')"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CampaignListTag from './campaign-list-tag';
import CampaignFollow from './campaign-follow.vue'
import i18n from '../../i18n/campaign-list.json';

export default {
  components: { CampaignListTag, CampaignFollow },
  props: {
    object: Object,
    currentCategory: Number,
    language: String,
    allowMultipleRequests: Boolean
  },
  computed: {
    i18n() {
      return i18n[this.language];
    },
    hasNoRequest () {
      return this.object.resolution === 'normal'
    }
  }
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