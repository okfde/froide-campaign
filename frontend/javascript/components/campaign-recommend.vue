<template>
  <div>
    <div class="row justify-content-center mt-5">
      <div class="col-md-9">
        <h1 v-if="user" class="text-center">
          {{ i18n.holdOn }}, {{ userName }}!
        </h1>
        <h1 v-else class="text-center">{{ i18n.holdOn }}!</h1>

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
      <div v-if="canShare" class="col-md-4 mt-3 text-center">
        <button class="btn btn-primary" @click="share">
          <span class="fa fa-share-square-o" aria-hidden="true" />
          &nbsp;{{ i18n.shareNow }}
        </button>
      </div>

      <div class="col-md-4 mt-3 text-center">
        <a :href="whatsAppLink" class="btn btn-success">
          <span class="fa fa-whatsapp" aria-hidden="true" />
          &nbsp;{{ i18n.viaWhatsapp }}
        </a>
      </div>

      <div class="col-md-4 mt-3 text-center">
        <a :href="mailLink" class="btn btn-secondary">
          <span class="fa fa-envelope" aria-hidden="true" />
          &nbsp;{{ i18n.viaMail }}
        </a>
      </div>
    </div>

    <p class="text-center mt-5 mb-3">
      {{ i18n.socialMedia }}
    </p>

    <div class="text-center">
      <a
        class="btn btn-share-bluesky me-3"
        rel="noopener"
        target="_blank"
        :href="blueskyLink"
        ><svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 512 512"
          class="img-text"
        >
          <path
            d="M111.8 62.2C170.2 105.9 233 194.7 256 242.4c23-47.6 85.8-136.4 144.2-180.2c42.1-31.6 110.3-56 110.3 21.8c0 15.5-8.9 130.5-14.1 149.2C478.2 298 412 314.6 353.1 304.5c102.9 17.5 129.1 75.5 72.5 133.5c-107.4 110.2-154.3-27.6-166.3-62.9l0 0c-1.7-4.9-2.6-7.8-3.3-7.8s-1.6 3-3.3 7.8l0 0c-12 35.3-59 173.1-166.3 62.9c-56.5-58-30.4-116 72.5-133.5C100 314.6 33.8 298 15.7 233.1C10.4 214.4 1.5 99.4 1.5 83.9c0-77.8 68.2-53.4 110.3-21.8z"
            fill="currentColor"
          />
        </svg>
        Bluesky
      </a>
      <a
        class="btn btn-share-facebook"
        rel="noopener"
        target="_blank"
        :href="facebookLink">
        <i class="fa fa-facebook" />
        Facebook
      </a>
    </div>

    <hr />

    <div class="row justify-content-center mt-5">
      <div class="col-md-8">
        <p class="text-center">
          <button class="btn btn-secondary" @click="$emit('close')">
            {{ i18n.backToOverview }}
          </button>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import campaignI18n from '../../i18n/campaign-request.json'

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
    }
  },
  computed: {
    i18n() {
      const language = document.documentElement.lang
      return campaignI18n[language]
    },
    userName() {
      if (this.user) {
        return `${this.user.first_name} ${this.user.last_name}`
      }
      return ''
    },
    socialUrl() {
      const url = document.location.href
      if (url.indexOf('?') !== -1) {
        return url + '&social=1'
      }
      return url + '?social=1'
    },
    canShare() {
      return !!navigator.canShare
    },
    socialText() {
      return `${this.i18n.socialText}\n\n${this.socialUrl}`
    },
    smsLink() {
      return `sms:?&body=${encodeURIComponent(this.socialText)}`
    },
    whatsAppLink() {
      return `whatsapp://send?text=${encodeURIComponent(this.socialText)}`
    },
    mailLink() {
      const subject = encodeURIComponent(this.i18n.socialSubject)
      return `mailto:?Subject=${subject}&Body=${encodeURIComponent(
        this.socialText
      )}`
    },
    blueskyLink() {
      return `https://bsky.app/intent/compose?text=${encodeURIComponent(
        this.socialText + ' - ' + this.socialUrl
      )}`
    },
    facebookLink() {
      return `https://www.facebook.com/sharer.php?u=${encodeURIComponent(
        this.socialUrl
      )}`
    }
  },
  methods: {
    share() {
      navigator.share({
        title: this.i18n.socialSubject,
        text: this.i18n.socialText,
        url: this.socialUrl
      })
    },
    close() {
      this.$emit('close')
    }
  }
}
</script>
