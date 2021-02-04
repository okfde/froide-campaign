var CampaignDetailMixin = {
  methods: {
    getDetail (data, campaignId) {
      this.fetching = true
      window.fetch(`/api/v1/campaigninformationobject/${data.ident}/?campaign=${campaignId}&lat=${data.lat}&lng=${data.lng}&name=${encodeURIComponent(data.name)}&address=${encodeURIComponent(data.address)}&city=${data.city ? encodeURIComponent(data.city) : ''}&language=${document.documentElement.lang}`)
        .then((response) => {
          return response.json()
        }).then((data) => {
          if (data.error) {
            console.warn('Error requesting the API')
          }
          if (!this.userInfo) {
            this.getUser().then((user) => {
              if (user.id) {
                this.$emit('userupdated', user)
                this.getCSRFToken().then((token) => {
                  this.$emit('tokenupdated', token)
                  this.fetching = false
                  this.$emit('detailfetched', data)
                })
              } else {
                this.fetching = false
                this.$emit('detailfetched', data)
              }
            })
            return
          }
          this.fetching = false
          this.$emit('detailfetched', data)
        })
    },
    getUser () {
      return window.fetch('/api/v1/user/')
        .then((response) => {
          return response.json()
        })
    },
    getCSRFToken () {
      return window.fetch('.').then((response) => {
        return response.text()
      }).then((text) => {
        let match = text.match(/name="csrfmiddlewaretoken" value="([^"]+)"/)
        return match[1]
      })
    }
  }
}

export default CampaignDetailMixin
