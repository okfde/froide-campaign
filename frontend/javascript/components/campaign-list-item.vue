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
              v-for="(tag, i) in object.context.context_as_json.categories"
              :key="i"
              :active="currentTag === tag"
              @click="$emit('filter', tag)"
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
            {{ i18n.request }}
          </a>
          <a
            v-else
            :href="'/a/' + object.foirequest"
            class="btn text-white"
            :class="[`btn-${object.resolution}`]"
          >
            {{ i18n.viewRequest }}
          </a>
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
    currentTag: String,
    language: String
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