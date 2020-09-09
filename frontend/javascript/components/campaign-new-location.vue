<template>
  <div class="modal-mask" @click.self="$emit('close')">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h4 class="modal-title">
            Details des fehlenden Ortes
          </h4>
          <button type="button" class="close" aria-label="Close" @click="$emit('close')">
             <span aria-hidden="true">&times;</span>
           </button>
        </div>
        <div class="modal-body">
          <div class="row">
            <div class="col-12">
              <template v-if="error">
                <div class="alert alert-danger">
                  <p>Ein Fehler ist aufgetreten. Der Ort kann nicht angefragt werden.</p>
                </div>
              </template>
              <form v-else @submit="formSubmit">
                <p>
                  Falls der Ort, zu dem Sie eine Anfrage erstellen wollen, nicht gelistet wird,
                  können Sie hier die Details des Ortes eintragen.
                </p>
                <div class="form-group">
                  <label for="new-venue-title">Der Name des Ortes</label>
                  <input v-model="title" type="text" class="form-control" id="new-venue-title" aria-describedby="new-venue-title-help" placeholder="Name" required>
                </div>
                <div class="form-group">
                  <label for="new-venue-address">Adresse</label>
                  <input v-model="address" type="text" class="form-control" id="new-venue-address" placeholder="z.B. Hauptstr. 5" required>
                </div>
                <div class="row">
                  <div class="col">
                    <div class="form-group">
                      <label for="new-venue-plz">PLZ</label>
                      <input v-model="postcode" id="new-venue-plz" type="text" class="form-control" pattern="[0-9]{5}" required>
                    </div>
                  </div>
                  <div class="col">
                    <div class="form-group">
                      <label for="new-venue-ort">Ort</label>
                      <input v-model="city" id="new-venue-ort" type="text" class="form-control" placeholder="z.B. Berlin" required>
                    </div>
                  </div>
                </div>
                <p class="text-right">
                  <button type="submit" class="btn btn-primary">
                    Ort finden und Anfrage stellen
                  </button>
                </p>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>

import {postData} from '../lib/utils.js'

export default {
  name: 'campaign-new-location',
  mounted () {
  },
  props: {
    campaignId: {
      type: Number
    }
  },
  data () {
    return {
      fetching: false,
      error: false,
      title: '',
      address: '',
      postcode: '',
      city: '',
    }
  },
  methods: {
    formSubmit (e) {
      e.preventDefault()
      this.findDetail()
    },
    findDetail () {
      this.fetching = true
      postData('/api/v1/campaigninformationobject/', {
        campaign: this.campaignId,
        title: this.title,
        address: `${this.address}\n${this.postcode} ${this.city}`,
      }, this.$root.csrfToken).then((data) => {
        this.fetching = false
        if (data.error) {
          console.warn(data.message)
          this.error = true
          return
        }
        this.$emit('locationcreated', data)
        this.$emit('close')
      })
    }
  }
}
</script>

<style lang="scss" scoped>
  .modal-mask {
    position: absolute;
    z-index: 9998;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, .5);
    display: flex;
    transition: opacity .3s ease;
  }
  .is-embed .modal-mask {
    top: 10px;
  }
  .loading {
    padding-top: 3em 0;
    background-color: #fff;
    text-align: center;
  }

  .loading img {
    width: 10%;
  }
</style>
