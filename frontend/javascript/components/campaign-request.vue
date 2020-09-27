<template>
  <div class="container mb-5">
    <div class="row">
      <div class="col-12">
        <div v-if="fetching" class="loading">
          <campaign-loader></campaign-loader>
        </div>
        <template v-else>
          <div class="text-right">
            <button class="btn btn-sm btn-light" @click="$emit('close')">
              zurück
            </button>
          </div>
          <!-- <template v-if="!canRequest">
            <p>Dieser Betrieb wurde zwischenzeitlich schon angefragt.</p>
            <button class="btn btn-secondary" @click="$emit('close')">
              zurück
            </button>
          </template> -->
          <form method="post" @submit="formSubmit" :action="config.url.makeRequest" target="_blank">
            <input type="hidden" name="csrfmiddlewaretoken" :value="csrfToken"/>

            <input type="hidden" name="redirect_url" v-model="params.redirect"/>
            <input type="hidden" name="reference" v-model="params.ref"/>
            <input type="hidden" name="public" value="1"/>
            <input type="hidden" v-for="k in hideParams" :key="k" :name="k" value="1"/>

            <request-form v-if="!fetching"
              :publicbodies="publicbodies"
              :request-form="requestForm"
              :user="userInfo"
              :default-law="defaultLaw"
              :user-form="userForm"
              :initial-subject="subject"
              :initial-body="body"
              :show-draft="false"
              :hide-publicbody-chooser="true"
              :hide-full-text="true"
              :hide-editing="true"
              :law-type="lawType"
              :use-pseudonym="false"
              :config="config"
            ></request-form>
            <user-registration
              :form="userForm"
              :config="config"
              :user="userInfo"
              :default-law="defaultLaw"
              :address-help-text="addressHelpText"
              :address-required="true"
            ></user-registration>
            <user-terms v-if="!userInfo"
              :form="userForm"
            ></user-terms>
            <div class="row">
              <div class="col-md-12">
                <div class="card mb-3">
                  <div class="card-body">
                    <div class="form-group row">
                      <div class="col-lg-9">
                        <div class="form-check">
                          <label class="form-check-label">
                            <input type="checkbox" name="subscribe" id="id_subscribe" class="form-check-input" :value="userHasSubscription" v-model="userHasSubscription">
                            <span v-if="this.subscribeText">{{ this.subscribeText }}</span>
                            <span v-else>Bitte senden Sie mir Informationen zu dieser Kampagne per E-mail</span>
                          </label>
                        </div>
                      </div>
                    </div>
                    <p v-if="this.extraText" v-html="this.extraText" class="mb-0"></p>
                  </div>
                </div>
              </div>
            </div>
            <div class="text-right">
              <button v-if="buttonText" type="submit" class="btn btn-lg btn-success" :disabled="submitting">
                <i class="fa fa-angle-double-right" aria-hidden="true"></i>
                {{ this.buttonText }}
              </button>
              <button v-else type="submit" class="btn btn-lg btn-success" :disabled="submitting">
                <i class="fa fa-angle-double-right" aria-hidden="true"></i>
                Anfrage abschicken
              </button>
            </div>
          </form>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import RequestForm from 'froide/frontend/javascript/components/makerequest/request-form.vue'
import UserRegistration from 'froide/frontend/javascript/components/makerequest/user-registration.vue'
import UserTerms from 'froide/frontend/javascript/components/makerequest/user-terms.vue'
import {selectBestLaw} from 'froide/frontend/javascript/lib/law-select'

import CampaignLoader from './campaign-loader'
import CampaignDetailMixin from '../lib/detailmixin'
import CampaignItemMixin from '../lib/mixin.js'
import {postData} from '../lib/utils.js'

const MAX_REQUEST_COUNT = 3

export default {
  name: 'campaign-request',
  mixins: [CampaignDetailMixin, CampaignItemMixin],
  components: {
    RequestForm,
    CampaignLoader,
    UserTerms,
    UserRegistration
  },
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
    currentUrl: {
      type: String
    },
    lawType: {
      type: String
    },
    extraText: {
      type: String
    },
    subscribeText: {
      type: String
    },
    hasSubscription: {
      type: Boolean
    },
    campaignId: {
      type: Number
    }
  },
  mounted () {
    if (!this.data.full) {
      this.getDetail(this.data, this.campaignId)
    }
  },
  data () {
    return {
      fetching: !this.data.full,
      closedWarning: false,
      submitting: false,
      userHasSubscription: this.hasSubscription,
      addressHelpText: 'Ihre Adresse wird nicht öffentlich angezeigt.'
    }
  },
  computed: {
    csrfToken () {
      return this.$root.csrfToken
    },
    publicbodies () {
      return [this.data.publicbody]
    },
    publicBody () {
      return this.data.publicbody
    },
    showWarning () {
      return this.userInfo && this.data.userRequestCount >= MAX_REQUEST_COUNT && !this.closedWarning
    },
    userRequestCount () {
      return this.data.userRequestCount
    },
    params () {
      let params = {}
      if (!this.data.makeRequestURL) {
        return {}
      }
      this.data.makeRequestURL.split('?')[1].split('&').forEach((pair) => {
        pair = pair.split('=')
        params[pair[0]] = decodeURIComponent(pair[1])
      })
      return params
    },
    subject () {
      return this.params.subject || ''
    },
    body () {
      return this.params.body || ''
    },
    hideParams () {
      var a = []
      for (let k in this.params) {
        if (k.match(/hide_\w+/)) {
          a.push(k)
        }
      }
      return a
    },
    defaultLaw () {
      return selectBestLaw(this.publicBody.laws, this.lawType)
    }
  },
  methods: {
    close () {
      this.$emit('close')
    },
    formSubmit () {
      this.submitting = true
      window.setTimeout(() => {
        let email
        let inputs = document.getElementsByTagName('input')

        for(let i = 0; i < inputs.length; i++) {
          if(inputs[i].name == 'user_email') {
            email = inputs[i].value
          }
        }
        postData('/api/v1/campaigninformationobject/subscribe/', {
          subscribe: this.userHasSubscription,
          campaign: this.campaignId,
          email: email
        }, this.$root.csrfToken).then((data) => {
          if (data.error) {
            console.warn(data.message)
            this.error = true
          }
          this.$emit('requestmade', this.data)
          this.$emit('close')
        })
      }, 300)
    }
  }
}
</script>


<style lang="scss" scoped>
  .loading {
    height: 100vh;
    padding-top: 30%;
    background-color: #fff;
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