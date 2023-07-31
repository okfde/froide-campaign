import '../styles/main.scss'

import { createAppWithProps } from 'froide/frontend/javascript/lib/vue-helper'

import CampaignQuestionaire from './components/campaign-questionaire'

function createCampaignQuestionaire(selector) {
  createAppWithProps(selector, CampaignQuestionaire).mount(selector)
}

document.addEventListener('DOMContentLoaded', function () {
  createCampaignQuestionaire('#campaign-questionaire-component')
})

export default {
  createCampaignQuestionaire
}
