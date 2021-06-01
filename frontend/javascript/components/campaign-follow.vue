<template>
  <div v-if="canFollow">
    <button v-if="follows || justFollowed" class="input-large btn btn-block btn-sm" :class="{'hover-btn-danger': !justFollowed}" @click.stop="unfollow">
      <span v-if="!justFollowed" class="on-hover">
        <i class="fa fa-remove" aria-hidden="true"></i>
        {{ i18n.unfollow }}
      </span>
      <span :class="{'on-display': !justFollowed}">
        <i class="fa fa-star" aria-hidden="true"></i>
        {{ i18n.followed }}
      </span>
    </button>
    <button v-else class="input-large btn hover-btn-success btn-block btn-sm" @click.stop="doFollow">
      <span class="on-hover">
        <i class="fa fa-star" aria-hidden="true"></i>
        {{ i18n.follow_q }}
      </span>
      <span class="on-display">
        <i class="fa fa-star-o" aria-hidden="true"></i>
        {{ i18n.follow_q }}
      </span>
    </button>
  </div>
</template>

<script>

import {postData} from '../lib/utils.js'

import i18n from '../../i18n/campaign-follow.json';

export default {
  name: 'campaign-follow',
  props: {
    follow: {
      type: Object
    }
  },
  data () {
    return {
      working: false,
      justFollowed: false
    }
  },
  computed: {
    i18n() {
      return i18n[document.documentElement.lang];
    },
    canFollow () {
      return !this.unknown && this.follow.canFollow !== false
    },
    follows () {
      return !this.unknown && this.follow.follows === true
    },
    unknown () {
      return this.follow === undefined
    },
    requestId () {
      if (this.unknown) {
        return null
      }
      let parts = this.follow.request.split('/')
      return parseInt(parts[parts.length - 2])
    }
  },
  methods: {
    showEmailFollow () {
      window.open(
        `/benachrichtigen/${this.requestId}/follow/embed/`,
        'follow_window',
        'menubar=no,location=yes,resizable=yes,scrollbars=yes,status=yes,height=450,width=500'
      );
    },
    doFollow () {
      if (this.follow.can_follow === null) {
        this.showEmailFollow()
        return
      }
      this.justFollowed = true
      postData(
        '/api/v1/following/',
        {'request': this.requestId},
        this.$root.csrfToken
      ).then((data) => {
        this.$emit('followed', data['url'])
        window.setTimeout(() => this.justFollowed = false, 2000)
      })
    },
    unfollow () {
      if (this.justFollowed) {
        return
      }
      window.fetch(this.follow.resource_uri, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          'X-CSRFToken': this.$root.csrfToken
        }
      }).then(() => {
        this.$emit('unfollowed')
      })
    }
  }
}
</script>
