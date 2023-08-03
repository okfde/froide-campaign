<template>
  <span
    v-for="choice in filter.choices"
    :key="choice.value"
    class="flex badge rounded-pill mb-1 me-1 cursor-pointer"
    :class="[
      {
        'text-bg-dark': value === choice.value,
        'text-bg-light': value !== choice.value
      }
    ]"
    @click="setChoice(choice.value)"
    aria-role="button">
    {{ choice.label[lang] }}
  </span>
</template>

<script>
export default {
  props: {
    filter: {
      type: Object,
      required: true
    },
    value: {
      type: String,
      default: null
    }
  },
  emits: ['input'],
  computed: {
    lang() {
      return document.documentElement.lang
    },
    label() {
      return this.filter.label[this.lang]
    }
  },
  methods: {
    setChoice(choiceValue) {
      if (choiceValue === this.value) {
        choiceValue = undefined
      }
      this.$emit('input', {
        id: this.filter.id,
        value: choiceValue
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.badge {
  cursor: pointer;
}
</style>
