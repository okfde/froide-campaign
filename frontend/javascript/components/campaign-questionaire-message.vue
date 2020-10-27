<template>
  <div class="card mt-3">
    <div class="card-header">
        <h4>
        <small>{{ date }}, {{ message.sender }}</small><br/>
        {{ message.subject }}
      </h4>
    </div>
    <div class="card-body">
      <div class="content" @mouseup="checkSelection" ref="content">{{ message.content}}</div>
        <div v-for="att in attachmentList" :key="att.id" class="mb-3">
            <span>{{ att.name }}  <button class="btn btn-light btn-sm" @click.prevent="loadAttachment(att)">Ansehen</button></span>
        </div>
      <template v-if="attachment">
        <div v-if="attachment.is_pdf" class="container-sm-full">
          <iframe :src="pdfViewerUrl" frameborder="0" style="width: 100%; height: 90vh; border: 0;"></iframe>
        </div>
        <embed v-else :src="attachment.file_url" style="max-width: 100%;" :type="attachment.filetype"/>
      </template>

    </div>
  </div>
</template>

<script>
const DATE_RE = /(\d{1,2})\.(\d{1,2})(\.\d{2,4})?/g
const DATE_ONLY_RE = /^(\d{1,2})\.(\d{1,2})(?:\.(\d{2,4}))?$/

function isValidDate(d) {
  return d instanceof Date && !isNaN(d)
}

function leftpad(str) {
  str = '' + str
  const pad = "00"
  return pad.substring(0, pad.length - str.length) + str
}

function makeDate(str) {
  const match = DATE_ONLY_RE.exec(str)
  if (match === null) {
    return null
  }
  let year = match[3]
  if (!year) {
    year = 2019
  } else {
    year = parseInt(year, 10)
    if (year < 25) {
      year += 2000
    }
  }
  const d = new Date(year, parseInt(match[2], 10) - 1, parseInt(match[1], 10))
  if (!isValidDate(d)) {
    return null
  }
  return d
}

export default {
    name: "campaign-questionair-message",
    props: {
    config: {
      type: Object
    },
    message: {
      type: Object
    },
    request: {
      type: Object
    },
  },
  data () {
    return {
      attachment: null,
      reportdate: ''
    }
  },
  computed: {
    attachmentList () {
      return this.message.attachments.filter((att) => att.approved)
    },
    date () {
      let date = this.message.timestamp.split('T')[0].split('-')
      date.reverse()
      return date.join('.')
    },
    pdfViewerUrl () {
      return `${this.config.viewerUrl}?file=${encodeURIComponent(this.attachment.file_url)}`
    },
    attachmentRedactionUrl () {
        return `/anfrage/${this.request.slug}/redact/${this.attachment.id}/`
    },
    dateList () {
      const already = {}
      const result = []
      let match;
      do {
        match = DATE_RE.exec(this.message.content);
        if (match && already[match[0]] === undefined) {
          already[match[0]] = true
          result.push(match[0])
        }
      } while (match)
      return result
    }
  },
  methods: {
    loadAttachment(att) {
      this.attachment = att
    },
    checkSelection () {
      const selection = window.getSelection()
      const selectionRange = selection.getRangeAt(0)
      this.setDate(selection.toString())
    }
  }
}
</script>