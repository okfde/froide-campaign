<template>
  <form class="form-group">
    <label class="my-1 mr-2" for="changePublicbodySelect"
      >Behörde ändern:</label
    >
    <select
      class="form-control form-control-sm"
      id="ichangePublicbodySelect"
      @change="onChangePublicBody($event)">
      <option
        v-for="(pb, index) in publicbodies"
        :key="index"
        :value="index"
        :selected="publicbody.name === pb.name">
        {{ pb.name }}
      </option>
    </select>
  </form>
</template>

<script>
export default {
  name: 'campaign-choose-publicbody',
  props: {
    publicbodies: {
      type: Array
    },
    publicbody: {
      type: Object
    }
  },
  methods: {
    onChangePublicBody(event) {
      const value = event.target.value
      const publicbody = this.publicbodies[value]
      this.$emit('publicBodyChanged', publicbody)
    }
  }
}
</script>

<style lang="scss" scoped></style>
