import {renderDate, getRequestStatus} from '../lib/utils'

const DAYS_BETWEEN_REQUEST = 90

var CampaignItemMixin = {
  computed: {
    itemId () {
      return this.data.id
    },
    hasRequest () {
      return this.data.foirequest !== null
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
