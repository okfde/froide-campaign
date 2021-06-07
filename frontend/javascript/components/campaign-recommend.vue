<template>
  <div>
    <div class="row justify-content-center mt-5">
      <div class="col-md-9">
        <h1
          v-if="user"
          class="text-center"
        >
          {{ i18n.holdOn }}, {{ userName }}!
        </h1>
        <h1
          v-else
          class="text-center"
        >
          {{ i18n.holdOn }}!
        </h1>

        <p class="lead">
          <template v-if="requestCount == 1">
            {{ i18n.alreadyMadeOneRequest }}
          </template>
          <template v-else>
            {{ i18n.alreadyMadeSomeRequest }}
          </template>
        </p>

        <p>
          {{ i18n.requestLimitExplanation }}
        </p>

        <h3>{{ i18n.getSupport }}</h3>
        <p>
          {{ i18n.tellFriends }}
        </p>
      </div>
    </div>
    <div class="row justify-content-center">
      <div
        v-if="canShare"
        class="col-md-4 mt-3 text-center"
      >
        <button
          class="btn btn-primary"
          @click="share"
        >
          <span
            class="fa fa-share-square-o"
            aria-hidden="true"
          />
          &nbsp;{{ i18n.shareNow }}
        </button>
      </div>

      <div class="col-md-4 mt-3 text-center">
        <a
          :href="whatsAppLink"
          class="btn btn-success"
        >
          <span
            class="fa fa-whatsapp"
            aria-hidden="true"
          />
          &nbsp;{{ i18n.viaWhatsapp }}
        </a>
      </div>

      <div class="col-md-4 mt-3 text-center">
        <a
          :href="mailLink"
          class="btn btn-secondary"
        >
          <span
            class="fa fa-envelope"
            aria-hidden="true"
          />
          &nbsp;{{ i18n.viaMail }}
        </a>
      </div>
    </div>

    <p class="text-center mt-5 mb-3">
      {{ i18n.socialMedia }}
    </p>

    <div class="text-center">
      <a
        class="btn btn-info sharing__link -twitter"
        rel="noopener"
        target="_blank"
        :href="twitterLink"
      >
        <i class="fa fa-twitter" />
        Twitter
      </a>
      <a
        class="btn btn-primary sharing__link -facebook"
        rel="noopener"
        target="_blank"
        :href="facebookLink"
      >
        <i class="fa fa-facebook" />
        Facebook
      </a>
    </div>

    <hr>

    <div class="row justify-content-center mt-5">
      <div class="col-md-8">
        <p class="text-center">
          <button
            class="btn btn-secondary"
            @click="$emit('close')"
          >
            {{ i18n.backToOverview }}
          </button>
        </p>
      </div>
    </div>
  </div>
</template>

<script>

import campaign_i18n from '../../i18n/campaign-request.json'

export default {
  name: 'CampaignRecommend',
  props: {
    requestCount: {
      type: Number,
      required: true
    },
    user: {
      type: Object,
      required: true
    },
  },
  computed: {
    i18n () {
      let language = document.documentElement.lang
      return campaign_i18n[language]
    },
    userName () {
      if (this.user) {
        return `${this.user.first_name} ${this.user.last_name}`
      }
      return ''
    },
    socialUrl () {
      let url = document.location.href
      if (url.indexOf('?') !== -1) {
        return url + '&social=1'
      }
      return url + '?social=1'
    },
    canShare () {
      return !!navigator.canShare
    },
    socialText () {
      return `${this.i18n.socialText}\n\n${this.socialUrl}`
    },
    smsLink () {
      return `sms:?&body=${encodeURIComponent(this.socialText)}`
    },
    whatsAppLink () {
      return `whatsapp://send?text=${encodeURIComponent(this.socialText)}`
    },
    mailLink () {
      let subject = encodeURIComponent(this.i18n.socialSubject)
      return `mailto:?Subject=${subject}&Body=${encodeURIComponent(this.socialText)}`
    },
    twitterLink () {
      return `https://twitter.com/share?text=${encodeURIComponent(this.socialText)}&amp;url=${encodeURIComponent(this.socialUrl)}&amp;via=fragdenstaat`
    },
    facebookLink () {
      return `https://www.facebook.com/sharer.php?u=${encodeURIComponent(this.socialUrl)}`
    }
  },
  methods: {
    share () {
      navigator.share({
        title: this.i18n.socialSubject,
        text: this.i18n.socialText,
        url: this.socialUrl
      })
    },
    close () {
      this.$emit('close')
    }
  }
}
</script>