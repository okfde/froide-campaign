import '../styles/main.scss'

import { createAppWithProps } from 'froide/frontend/javascript/lib/vue-helper'

import store from 'froide/frontend/javascript/store'

import CampaignList from './components/campaign-list'

function createCampaignList(selector) {
  createAppWithProps(selector, CampaignList).use(store).mount(selector)
}

document.addEventListener('DOMContentLoaded', function () {
  createCampaignList('#campaign-list-component')
})

export default {
  createCampaignList
}
