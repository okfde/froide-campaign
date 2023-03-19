import '../styles/main.scss'

import VueLazyload from 'vue-lazyload'

import { createAppWithProps } from 'froide/frontend/javascript/lib/vue-helper'

import CampaignMap from './components/campaign-map'

function createCampaignMap(selector) {
  createAppWithProps(selector, CampaignMap).use(VueLazyload).mount(selector)
}

document.addEventListener('DOMContentLoaded', function () {
  createCampaignMap('#campaign-map-component')
})

export default {
  createCampaignMap
}
