<template>
  <div class="modal fade" tabindex="-1">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h4 class="modal-title">Details des fehlenden Ortes</h4>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
            @click="$emit('close')" />
        </div>
        <div class="modal-body">
          <div class="row">
            <div class="col-12">
              <template v-if="error">
                <div class="alert alert-danger">
                  <p>
                    Ein Fehler ist aufgetreten. Der Ort kann nicht angefragt
                    werden.
                  </p>
                </div>
              </template>
              <form v-else @submit="formSubmit">
                <p>
                  Falls der Ort, zu dem Sie eine Anfrage erstellen wollen, nicht
                  gelistet wird, können Sie hier die Details des Ortes
                  eintragen.
                </p>
                <div class="mb-3">
                  <label for="new-venue-title">Der Name des Ortes</label>
                  <input
                    v-model="title"
                    type="text"
                    class="form-control"
                    id="new-venue-title"
                    aria-describedby="new-venue-title-help"
                    placeholder="Name"
                    required />
                </div>
                <div class="mb-3">
                  <label for="new-venue-address">Adresse</label>
                  <input
                    v-model="address"
                    type="text"
                    class="form-control"
                    id="new-venue-address"
                    placeholder="z.B. Hauptstr. 5"
                    required />
                </div>
                <div class="row">
                  <div class="col">
                    <div class="mb-3">
                      <label for="new-venue-plz">PLZ</label>
                      <input
                        v-model="postcode"
                        id="new-venue-plz"
                        type="text"
                        class="form-control"
                        pattern="[0-9]{5}"
                        required />
                    </div>
                  </div>
                  <div class="col">
                    <div class="mb-3">
                      <label for="new-venue-ort">Ort</label>
                      <input
                        v-model="city"
                        id="new-venue-ort"
                        type="text"
                        class="form-control"
                        placeholder="z.B. Berlin"
                        required />
                    </div>
                  </div>
                </div>
                <p class="text-end">
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
import { postData } from '../lib/utils.js'

export default {
  name: 'CampaignNewLocation',
  props: {
    campaignId: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      fetching: false,
      error: false,
      title: '',
      address: '',
      postcode: '',
      city: ''
    }
  },
  methods: {
    formSubmit(e) {
      e.preventDefault()
      this.findDetail()
    },
    findDetail() {
      this.fetching = true
      postData(
        '/api/v1/campaigninformationobject/',
        {
          campaign: this.campaignId,
          title: this.title,
          address: `${this.address}\n${this.postcode} ${this.city}`
        },
        this.$root.csrfToken
      ).then((data) => {
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
.loading {
  padding-top: 3em 0;
  background-color: var(--bs-body-bg);
  text-align: center;
}

.loading img {
  width: 10%;
}
</style>
