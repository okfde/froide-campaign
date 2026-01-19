import '../styles/main.scss'

import { createAppWithProps } from 'froide/frontend/javascript/lib/vue-helper'

import store from 'froide/frontend/javascript/store'

import CampaignMap from './components/campaign-map'

function createCampaignMap(selector) {
  createAppWithProps(selector, CampaignMap).use(store).mount(selector)
}

document.addEventListener('DOMContentLoaded', function () {
  createCampaignMap('#campaign-map-component')
})

export default {
  createCampaignMap
}
