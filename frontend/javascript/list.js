import '../styles/main.scss'

import Vue from 'vue'
import VueLazyload from 'vue-lazyload'

import {renderComponent} from 'froide/frontend/javascript/lib/vue-helper'

import CampaignList from './components/campaign-list'

Vue.use(VueLazyload, {
  lazyComponent: true
})

Vue.config.productionTip = false

function createCampaignList (selector) {
  /* eslint-disable no-new */
  new Vue({
    components: { CampaignList },
    render: renderComponent(selector, CampaignList)
  }).$mount(selector)
}

document.addEventListener('DOMContentLoaded', function () {
    createCampaignList('#campaign-list-component')
})

export default {
    createCampaignList
}
