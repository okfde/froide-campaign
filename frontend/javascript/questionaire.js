import '../styles/main.scss'

import VueLazyload from 'vue-lazyload'

import { createAppWithProps } from 'froide/frontend/javascript/lib/vue-helper'

import CampaignQuestionaire from './components/campaign-questionaire'

function createCampaignQuestionaire(selector) {
  createAppWithProps(selector, CampaignQuestionaire)
    .use(VueLazyload)
    .mount(selector)
}

document.addEventListener('DOMContentLoaded', function () {
  createCampaignQuestionaire('#campaign-questionaire-component')
})

export default {
  createCampaignQuestionaire
}
