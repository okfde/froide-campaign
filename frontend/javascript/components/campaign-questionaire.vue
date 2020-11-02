<template>
  <div class="container-fluid my-5">
    <div class="row justify-content-center">
      <div class="col-md-4 text-center">
        <h4 v-if="request">
            Anfrage: {{ request.title }} <br>
            <small>An: {{ currentObject.publicbody_name }}</small>
          </h4>
          <button
              @click.prevent="next"
              class="btn btn-secondary mb-2"
              v-if="objectListIndex < maxIndex"
            >
              Überspringen
          </button>
          <button
              @click.prevent="next"
              class="btn btn-light mb-2"
              v-if="objectListIndex == maxIndex"
              disabled
            >
              Überspringen
          </button><br>
          <small  v-if="objectListIndex == maxIndex">Kein weiteren Anfragen mehr! Vielen Dank!</small>
      </div>
    </div>
    <div class="row my-5">
      <div class="col-7">
        <div v-if="loading" class="spinner-border" role="status">
          <span class="sr-only">Loading...</span>
        </div>
        <div v-if="request">
          <p v-if="description" v-html="description"></p>
          <campaign-questionair-message
          v-for="message in this.filteredMessages()"
          :key="message.id"
          :request="request"
          :message="message"
          :config="config"
          ></campaign-questionair-message>
        </div>
      </div>
      <div class="col-5">
        <div class="sticky-top">
          <h4>Fragen:</h4>
          <form>
            <div
              class="form-group"
              v-for="(answer, index) in answers"
              :key="index"
            >
              <label>{{ answer.question }}<span v-if="answer.required">*</span></label>
              <select v-if="answer.options.length > 1" select class="form-control" v-model="answer.answer">
                <option v-for="(option, index) in answer.options" :key=index :selected="index === 0">{{ option }}</option>
              </select>
              <input v-if="answer.options.length === 1" :class="answer.error ? 'form-control is-invalid' : 'form-control'" type="text" v-model="answer.answer" />
              <small v-if="answer.helptext" class="text-muted">{{ answer.helptext }}</small>
              <div v-if="answer.error" class="invalid-feedback">Bitte beantworten Sie diese Frage.</div>
            </div>
            <button
              type="submit"
              @click.prevent="submitAnswersAndNext"
              class="btn btn-primary pull-right"
              v-if="objectListIndex < maxIndex"
            >
              Absenden und weiter
            </button>
            <button
              type="submit"
              @click.prevent="submitAnswers"
              class="btn btn-light mb-2 mr-2 pull-right"
            >
              Absenden
            </button>
          </form>
          <div v-if="showSuccess" class="alert alert-success mt-3" role="alert">
          Antworten erfolgreich gespeichert!
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { postData } from "../lib/utils.js";
import {getData } from 'froide/frontend/javascript/lib/api.js'
import CampaignQuestionairMessage from './campaign-questionaire-message'
export default {
  name: "campaign-questionaire",
  components: {
    CampaignQuestionairMessage
  },
  props: {
    questionaire: {
      type: String
    },
    informationobjects: {
      type: Array,
    },
    questions: {
      type: Array,
    },
    config: {
      type: Object
    }
  },
  mounted () {
    this.getNextRequest()
  },
  data() {
    let objectListIndex = 0
    let currentObject = this.informationobjects[objectListIndex]
    this.$root.csrfToken = document.querySelector(
      "[name=csrfmiddlewaretoken]"
    ).value

    return {
      answers: this.getEmptyAnswerSet(),
      objectListIndex: objectListIndex,
      currentObject: currentObject,
      loading: true,
      request: null,
      showSuccess: false,
      reportId: null,
      hasError: false,
      maxIndex: this.informationobjects.length -1
    }
  },
  methods: {
    getEmptyAnswerSet () {
      let answers = this.questions.map((question) => {
        return {
          questionId: question.id,
          question: question.text,
          options: question.options,
          required: question.required,
          answer: (question.options.length > 1) ? question.options[0] : '',
          helptext: question.helptext,
          error: ''
        }
      })
      return answers
    },
    filteredMessages () {
      return this.request.messages.filter( message => message.sender_public_body !== null)
    },
    getNextRequest () {
      let id = this.currentObject.foirequest
      getData(`/api/v1/request/${id}/`).then((data) => {
          this.request = data
          this.loading = false
          this.answers = this.getEmptyAnswerSet()
        }
      )
    },
    next: function (event) {
      let objectListIndex  = this.objectListIndex + 1
      this.objectListIndex  = objectListIndex
      this.currentObject = this.informationobjects[objectListIndex]
      this.getNextRequest()
    },
    submitAnswers: function () {
      this.hasError  = false
      this.validateData()
      if (!this.hasError) {
        postData(
          "/api/v1/campaigninformationobject/report/", {
            questionaire: this.questionaire,
            informationObject: this.currentObject.id,
            answers: this.answers,
            report: this.reportId
          },
          this.$root.csrfToken
        ).then((data) => {
          if (data.error) {
            console.warn(data.message)
            this.error = true
          }
          this.reportId = data.report
          this.showSuccess = true
          setTimeout(() => this.showSuccess  = false, 600);
        })
      }
    },
    validateData: function() {
      let answers = this.answers.map((answer, index) => {
        let required = answer.required
        let currentAnswer = answer.answer
        return {
          questionId: answer.questionId,
          question: answer.question,
          options: answer.options,
          required: answer.required,
          answer: currentAnswer,
          error: (required && currentAnswer === '') ? true : false,
          helptext: answer.helptext
        }
      })
      this.answers = answers
      this.answers.forEach( answer => {
        if (answer.error) {
          this.hasError  = true
        }
      })
    },
    submitAnswersAndNext: function () {
      this.hasError  = false
      this.validateData()
      if (!this.hasError) {
        postData(
          "/api/v1/campaigninformationobject/report/", {
            questionaire: this.questionaire,
            informationObject: this.currentObject.id,
            answers: this.answers,
            report: this.reportId
          },
          this.$root.csrfToken
        ).then((data) => {
          if (data.error) {
            console.warn(data.message)
            this.error = true
          }
          this.answers = this.getEmptyAnswerSet()
          let objectListIndex  = this.objectListIndex + 1
          this.objectListIndex  = objectListIndex
          this.currentObject = this.informationobjects[objectListIndex]
          this.getNextRequest()
        })
      }
    }
  }
}
</script>

<style lang="scss" scoped>
</style>