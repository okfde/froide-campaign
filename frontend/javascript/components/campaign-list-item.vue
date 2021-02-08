<template>
  <div class="card mb-2">
    <div class="card-body">
      <h5>{{ object.title }}</h5>
      <div class="row mt-3">
        <div class="col">
          <p class="text-muted">{{ object.subtitle }}</p>
          <small class="text-muted">{{ object.address }}</small>
        </div>
        <div class="col text-right">
          <h5>
            <CampaignListTag
              v-for="(category) in object.categories"
              :key="category.id"
              :active="currentCategory === category.id.toString()"
              :isButton="false">
              #{{ category.title }}
            </CampaignListTag>
          </h5>
        </div>
      </div>
      <div class="row mt-1">
        <div class="col">
          <a
            v-if="object.resolution === 'normal'"
            @click.prevent.stop="$emit('startRequest', object)"
            class="btn btn-normal text-white"
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
              @click.prevent.stop="$emit('startRequest', object)"
              class="btn btn-link"
              >
              {{ i18n.requestAgain }}
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CampaignListTag from './campaign-list-tag';
import i18n from '../../i18n/campaign-list.json';

export default {
  props: {
    object: Object,
    currentCategory: String,
    language: String,
    allowMultipleRequests: Boolean
  },
  components: { CampaignListTag },
  computed: {
    i18n() {
      return i18n[this.language];
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