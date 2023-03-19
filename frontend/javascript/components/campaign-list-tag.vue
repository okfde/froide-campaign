<template>
  <span
    class="flex badge rounded-pill mb-1 me-1"
    :class="[
      { 'text-bg-dark': active, 'text-bg-light': !active },
      status && 'filter-badge-' + status
    ]"
    v-bind="$attrs"
    aria-role="button">
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
@import '~froide/frontend/styles/variables.scss';

$normal: $secondary;
$pending: $primary;
$successful: $success;
$refused: $danger;

.badge {
  font-size: 0.8rem;
  font-weight: normal;
  cursor: pointer;
}

.filter-badge {
  content: '';
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
