import '../styles/main.scss'

import Vue from 'vue'
import VueLazyload from 'vue-lazyload'

import {renderComponent} from 'froide/frontend/javascript/lib/vue-helper'

import CampaignQuestionaire from './components/campaign-questionaire'

Vue.use(VueLazyload, {
  lazyComponent: true
})

Vue.config.productionTip = false

function createCampaignQuestionaire (selector) {
  /* eslint-disable no-new */
  new Vue({
    components: { CampaignQuestionaire },
    render: renderComponent(selector, CampaignQuestionaire)
  }).$mount(selector)
}

document.addEventListener('DOMContentLoaded', function () {
    createCampaignQuestionaire('#campaign-questionaire-component')
})

export default {
    createCampaignQuestionaire
}
