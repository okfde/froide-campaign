import {renderDate, getRequestStatus} from '../lib/utils'


var CampaignItemMixin = {
  computed: {
    itemId () {
      return this.data.id
    },
    hasRequests () {
      return this.data.foirequests.length > 0
    }
  },
  methods: {
    setDetail () {
      this.$emit('detail', this.data)
    },
    startRequest () {
      this.$emit('startRequest', this.data)
    }
  }
}

export default CampaignItemMixin
