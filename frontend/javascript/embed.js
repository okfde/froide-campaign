import '../styles/embed.scss'

function resize() {
  const height = document.getElementsByTagName('html')[0].scrollHeight
  window.parent.postMessage(
    ['froide-campaign-' + window.Froide.campaignPageId, 'setHeight', height],
    '*'
  )
}

document.addEventListener('DOMContentLoaded', getRandom)
document.addEventListener('resize', resize)

const searchForm = document.getElementById('searchform')
searchForm.addEventListener('submit', getSearch)

function getJson(url) {
  return new Promise((resolve, reject) => {
    const request = new window.XMLHttpRequest()
    request.open('GET', url, true)
    request.onload = function () {
      if (request.status >= 400) {
        return reject(request.responseText)
      }
      resolve(JSON.parse(request.responseText))
    }
    request.onerror = function () {
      reject(request.statusText)
    }

    request.send()
  })
}

function renderResults(results, emptyMessage) {
  if (results.length === 0) {
    return `<p>${emptyMessage}</p>`
  } else {
    return results
      .map(
        (r) => `<div class="row request-row">
      <div class="col-9">
        <h6>
          ${r.description}<br/>
          <small>${r.publicbody_name}</small>
        </h6>
      </div>
      <div class="col mr-auto">
        <a href="${r.request_url}" rel="noopener" class="btn btn-primary btn-block">
          ${window.Froide.i18n.requestThis}
        </a>
      </div>
    </div>`
      )
      .join('\n')
  }
}

function getSearch(e) {
  e.preventDefault()
  const requestList = document.getElementById('request-list')
  requestList.className = 'requests-loading'

  const searchQuery = document.getElementById('search-input').value

  let query = window.Froide.campaignIds.map((m) => `campaign=${m}`).join('&')
  query += '&q=' + encodeURIComponent(searchQuery)
  const url = `${window.Froide.urls.campaigninformationobjectSearch}?${query}`
  getJson(url).then((results) => {
    const html = renderResults(results, window.Froide.i18n.noResults)
    requestList.className = ''
    document.getElementById('request-list').innerHTML = html
    resize()
  })
}

function getRandom() {
  const moreButton = document.getElementById('load-more')
  moreButton.disabled = true
  const requestList = document.getElementById('request-list')
  requestList.className = 'requests-loading'
  const query = window.Froide.campaignIds.map((m) => `campaign=${m}`).join('&')
  const url = `${window.Froide.urls.campaigninformationobjectRandom}?${query}`
  getJson(url).then((results) => {
    const html = renderResults(results, window.Froide.i18n.noRequestLeft)
    moreButton.disabled = false
    requestList.className = ''
    document.getElementById('request-list').innerHTML = html
    resize()
  })
}

window.Froide.getRandom = getRandom
