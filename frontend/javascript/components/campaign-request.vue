<template>
  <div id="campaign-request" ref="campaignRequest" class="container mt-5 mb-5">
    <div class="row">
      <div class="col-12">
        <div v-if="fetching" class="loading">
          <CampaignLoader />
        </div>
        <CampaignRecommend
          v-else-if="showMaxRequestWarning"
          :user="userInfo"
          :request-count="userRequestCount"
          @close="$emit('close')" />
        <template v-else>
          <button class="btn btn-sm btn-secondary" @click="$emit('close')">
            &lt; {{ messages.back }}
          </button>
          <div class="row justify-content-md-end mt-5">
            <CampaignChoosePublicbody
              v-if="!fetching && publicbodiesOptions.length > 1"
              :publicbodies="publicbodiesOptions"
              :publicbody="publicbody"
              @public-body-changed="updatePublicBody" />
          </div>
          <div class="mt-5" v-if="!fetching && !publibodiesOptions && publicbody">
            <div class="fs-3">
              {{ config.i18n.toPublicBody.replace('${name}', publicbody.name) }}
              <a :href="publicbody.site_url" target="_blank">
                <span class="fa fa-info-circle" />
              </a>
            </div>
            <div
              v-if="defaultLaw?.request_note_html"
              class="alert alert-warning my-2"
              v-html="defaultLaw.request_note_html"
              />
            <div
              v-if="publicbody?.request_note_html"
              class="alert alert-warning my-2"
              v-html="publicbody.request_note_html"
              />
          </div>
          <!-- <template v-if="!canRequest">
            <p>Dieser Betrieb wurde zwischenzeitlich schon angefragt.</p>
            <button class="btn btn-secondary" @click="$emit('close')">
              zurück
            </button>
          </template> -->
          <form
            method="post"
            :action="config.url.makeRequest"
            target="_blank"
            enctype="multipart/form-data"
            @submit="formSubmit">
            <input
              type="hidden"
              name="csrfmiddlewaretoken"
              :value="csrfToken" />
            <input
              v-model="params.redirect_url"
              type="hidden"
              name="redirect_url" />
            <input v-model="params.ref" type="hidden" name="reference" />
            <!-- TODO is privateRequests ever true? if so, use froide/request-public.vue? -->
            <input
              v-if="!privateRequests"
              type="hidden"
              name="public"
              value="True" />
            <input
              v-for="k in hideParams"
              :key="k"
              type="hidden"
              :name="k"
              value="1" />
            <RequestForm
              v-if="!fetching"
              :publicbodies="[publicbody]"
              :request-form="requestForm"
              :user="userInfo"
              :default-law="defaultLaw"
              :user-form="userForm"
              :proof-form-initial="proofForm"
              :proof-required="proofRequired"
              :initial-subject="subject"
              :initial-body="body"
              :show-draft="!hideParams.includes('hide_draft')"
              :hide-publicbody-chooser="hideParams.includes('hide_publicbody')"
              :hide-full-text="hideParams.includes('hide_full_text')"
              :hide-editing="hideParams.includes('hide_editing')"
              :law-type="lawType"
              :config="config"
              :submitting="submitting" />
            <div class="card mb-3">
              <div class="card-body">
                <UserCreateAccount
                  v-if="!userInfo"
                  :user="user"
                  :config="config"
                  :request-form="requestForm"
                  :user-form="userForm"
                  :default-law="defaultLaw"
                  :address-help-text="addressHelpText"
                  :address-required="addressRequired"
                  :use-pseudonym="false"
                  >
                  <template #userPublicPreamble>
                    <span v-html="userForm.fields.private.help_text" />
                  </template>
                </UserCreateAccount>
                <UserConfirmation
                  :form="userForm"
                  />
              </div>
            </div>
            <div v-if="!hideNewsletterCheckbox" class="row">
              <div class="col-md-12">
                <div class="card mb-3">
                  <div class="card-body">
                    <div class="mb-3 row">
                      <div class="col-lg-9">
                        <div class="form-check">
                          <label class="form-check-label">
                            <input
                              id="id_subscribe"
                              v-model="userHasSubscription"
                              type="checkbox"
                              name="subscribe"
                              class="form-check-input"
                              :value="userHasSubscription" />
                            <span v-if="subscribeText">{{
                              subscribeText
                            }}</span>
                            <span v-else
                              >Bitte senden Sie mir Informationen zu dieser
                              Kampagne per E-mail</span
                            >
                          </label>
                        </div>
                      </div>
                    </div>
                    <p v-if="extraText" class="mb-0" v-html="extraText" />
                  </div>
                </div>
              </div>
            </div>
            <div class="text-end">
              <button
                type="submit"
                class="btn btn-lg btn-success"
                @click="submitting = true"
                :disabled="submitted">
                <i class="fa fa-angle-double-right" aria-hidden="true" />
                <template v-if="buttonText">{{ buttonText }}</template>
                <template v-else>{{ messages.sendRequest }}</template>
              </button>
            </div>
          </form>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import CampaignChoosePublicbody from './campaign-choose-publicbody.vue'
import RequestForm from 'froide/frontend/javascript/components/makerequest/request-form.vue'
import StoreValueMixin from 'froide/frontend/javascript/components/makerequest/lib/store-values-mixin'
import UserCreateAccount from 'froide/frontend/javascript/components/makerequest/user-create-account.vue'
import UserConfirmation from 'froide/frontend/javascript/components/makerequest/user-confirmation.vue'
import { selectBestLaw } from 'froide/frontend/javascript/lib/law-select'
import campaignI18n from '../../i18n/campaign-request.json'

import CampaignLoader from './campaign-loader'
import CampaignRecommend from './campaign-recommend'
import CampaignDetailMixin from '../lib/detailmixin'
import CampaignItemMixin from '../lib/mixin.js'

export default {
  name: 'CampaignRequest',
  components: {
    RequestForm,
    CampaignLoader,
    UserCreateAccount,
    UserConfirmation,
    CampaignChoosePublicbody,
    CampaignRecommend
  },
  mixins: [CampaignDetailMixin, CampaignItemMixin, StoreValueMixin],
  props: {
    buttonText: {
      type: String
    },
    data: {
      type: Object
    },
    config: {
      type: Object
    },
    requestForm: {
      type: Object
    },
    userInfo: {
      type: Object,
      default: null
    },
    userForm: {
      type: Object,
      default: null
    },
    proofForm: {
      type: Object,
      default: null
    },
    proofRequired: {
      type: Boolean,
      default: false
    },
    currentUrl: {
      type: String
    },
    lawType: {
      type: String
    },
    extraText: {
      type: String
    },
    hideNewsletterCheckbox: {
      type: Boolean
    },
    subscribeText: {
      type: String
    },
    hasSubscription: {
      type: Boolean
    },
    campaignId: {
      type: Number
    },
    publicbody: {
      type: Object
    },
    publicbodies: {
      type: Array
    },
    publicbodiesOptions: {
      type: Array
    },
    maxRequestsPerUser: {
      type: Number,
      default: 0
    },
    localRequestCount: {
      type: Number,
      default: 0
    },
    addressRequired: {
      type: Boolean,
      default: true
    },
    privateRequests: {
      type: Boolean,
      default: false
    }
  },
  data() {
    const language = document.documentElement.lang
    const messages = campaignI18n[language]
    let text = messages.addressInfo
    if (this.lawType === 'VIG') {
      text =
        text +
        '<strong class="text-danger">' +
        messages.warningVIG +
        '</strong>'
    }

    return {
      pbScope: 'campaign-',
      fetching: !this.data.full,
      submitting: false,
      submitted: false,
      addressHelpText: text,
      userHasSubscription: this.hasSubscription,
      language,
      messages
    }
  },
  created() {
    this.initAllStoreValues()
  },
  computed: {
    csrfToken() {
      return this.$root.csrfToken
    },
    showMaxRequestWarning() {
      return (
        this.maxRequestsPerUser > 0 &&
        ((this.userInfo &&
          this.data.userRequestCount >= this.maxRequestsPerUser) ||
          (!this.userInfo && this.localRequestCount >= this.maxRequestsPerUser))
      )
    },
    userRequestCount() {
      if (this.userInfo) {
        return this.data.userRequestCount
      }
      return this.localRequestCount
    },
    params() {
      const params = {}
      if (!this.data.makeRequestURL) {
        return {}
      }
      this.data.makeRequestURL
        .split('?')[1]
        .split('&')
        .forEach((pair) => {
          pair = pair.split('=')
          params[pair[0]] = decodeURIComponent(pair[1])
        })
      return params
    },
    subject() {
      return this.params.subject.replace('\n', ' ') || ''
    },
    body() {
      return this.params.body || ''
    },
    hideParams() {
      const a = []
      for (const k in this.params) {
        if (k.match(/hide_\w+/)) {
          a.push(k)
        }
      }
      return a
    },
    defaultLaw() {
      return selectBestLaw(this.publicbody.laws, this.lawType)
    }
  },
  mounted() {
    this.$refs.campaignRequest.scrollIntoView(true)
    if (!this.data.full) {
      this.getDetail(this.data, this.campaignId)
    }
  },
  methods: {
    updatePublicBody(publicbody) {
      this.$emit('publicBodyChanged', publicbody)
    },
    close() {
      this.$emit('close')
    },
    formSubmit() {
      this.submitted = true
      window.setTimeout(() => {
        this.$emit('requestmade', this.data)
        this.$emit('close')
      }, 300)
    }
  }
}
</script>

<style lang="scss" scoped>
.loading {
  height: 100vh;
  padding-top: 30%;
  background-color: var(--bs-body-bg);
  // animation: blinker 0.8s linear infinite;
  text-align: center;
}

.loading img {
  width: 10%;
}

@keyframes blinker {
  50% {
    opacity: 0.25;
  }
}
</style>
