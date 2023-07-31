import '../styles/main.scss'

import { createAppWithProps } from 'froide/frontend/javascript/lib/vue-helper'

import CampaignList from './components/campaign-list'

function createCampaignList(selector) {
  createAppWithProps(selector, CampaignList).mount(selector)
}

document.addEventListener('DOMContentLoaded', function () {
  createCampaignList('#campaign-list-component')
})

export default {
  createCampaignList
}
