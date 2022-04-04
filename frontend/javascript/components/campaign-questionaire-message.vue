<template>
  <div class="card mt-3">
    <div class="card-header">
      <h4>
        <small>{{ date }}, {{ message.sender }}</small
        ><br />
        {{ message.subject }}
      </h4>
    </div>
    <div class="card-body">
      <div class="content" @mouseup="checkSelection" ref="content"></div>
      <template v-if="attachment">
        <div v-if="attachment.is_pdf" class="container-sm-full">
          <iframe
            :src="pdfViewerUrl"
            frameborder="0"
            style="width: 100%; height: 90vh; border: 0"></iframe>
        </div>
        <embed
          v-else
          :src="attachment.file_url"
          style="max-width: 100%"
          :type="attachment.filetype" />
      </template>
    </div>
  </div>
</template>

<script>
const DATE_RE = /(\d{1,2})\.(\d{1,2})(\.\d{2,4})?/g

export default {
  name: 'campaign-questionair-message',
  props: {
    config: {
      type: Object
    },
    message: {
      type: Object
    },
    request: {
      type: Object
    }
  },
  data() {
    return {
      attachment: null,
      reportdate: ''
    }
  },
  mounted() {
    this.attachmentList.forEach((att) => this.loadAttachment(att))
  },
  computed: {
    attachmentList() {
      return this.message.attachments.filter((att) => att.approved)
    },
    date() {
      const date = this.message.timestamp.split('T')[0].split('-')
      date.reverse()
      return date.join('.')
    },
    pdfViewerUrl() {
      // embed PDF file directly into iframe
      return this.attachment.file_url
    },
    attachmentRedactionUrl() {
      return `/anfrage/${this.request.slug}/redact/${this.attachment.id}/`
    },
    dateList() {
      const already = {}
      const result = []
      let match
      do {
        match = DATE_RE.exec(this.message.content)
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
    checkSelection() {
      const selection = window.getSelection()
      this.setDate(selection.toString())
    }
  }
}
</script>
