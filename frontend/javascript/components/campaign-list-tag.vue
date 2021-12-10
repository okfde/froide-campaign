<template>
  <span
    class="flex badge badge-pill badge-light mb-1 mr-1"
    :class="[{ 'badge-dark': active }, status && 'filter-badge-' + status]"
    v-on="$listeners"
    aria-role="button"
  >
    <slot />
  </span>
</template>

<script>
export default {
  props: {
    active: Boolean,
    status: String
  }
}
</script>

<style lang="scss" scoped>
$normal: #007bff;
$pending: #ffc107;
$successful: #28a745;
$refused: #dc3545;

.badge {
  font-size: 0.8rem;
  font-weight: normal;
  cursor: pointer;
}

.filter-badge {
  content: "";
  display: inline-block;
  width: 0.5rem;
  height: 0.5rem;
  -moz-border-radius: 100%;
  -webkit-border-radius: 100%;
  border-radius: 100%;
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