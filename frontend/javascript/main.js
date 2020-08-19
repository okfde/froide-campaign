import '../styles/main.scss'

import Vue from 'vue'
import VueLazyload from 'vue-lazyload'

import {renderComponent} from 'froide/frontend/javascript/lib/vue-helper'

import CampaignMap from './components/campaign-map'

Vue.use(VueLazyload, {
  lazyComponent: true
})

Vue.config.productionTip = false

function createCampaignMap (selector) {
  /* eslint-disable no-new */
  new Vue({
    components: { CampaignMap },
    render: renderComponent(selector, CampaignMap)
  }).$mount(selector)
}

document.addEventListener('DOMContentLoaded', function () {
  createCampaignMap('#campaign-map-component')
})

export default {
  createCampaignMap
}
