function getQueryVariable(variable) {
  const query = window.location.search.substring(1)
  const vars = query.split('&')
  for (let i = 0; i < vars.length; i++) {
    const pair = vars[i].split('=')
    if (decodeURIComponent(pair[0]) === variable) {
      return decodeURIComponent(pair[1].replace(/\+/g, '%20'))
    }
  }
}

function canUseLocalStorage(window) {
  try {
    const key = '__canary_key__'
    window.localStorage.setItem(key, key)
    window.localStorage.removeItem(key)
    return true
  } catch {
    return false
  }
}

function renderDate(date) {
  const d = new Date(date)
  return `${d.getDate()}.${d.getMonth() + 1}.${d.getFullYear()}`
}

function getPlaceStatus(place) {
  if (place.requests.length === 0) {
    return 'normal'
  }
  return getRequestStatus(place.last_status, place.last_resolution)
}

const PINS = {}

function getPinURL(color) {
  if (PINS[color] === undefined) {
    const svg = `<?xml version="1.0" encoding="UTF-8"?><svg viewBox="0 0 8.9999998 11.800001" xml:space="preserve" xmlns="http://www.w3.org/2000/svg"> <defs><filter id="a" x="-.10828" y="-.086222" width="1.2166" height="1.1724" color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation="0.388"/></filter></defs> <path d="m4.5 0.90339c1.1 0 2.2 0.5 3 1.3 0.8 0.9 1.3 1.9 1.3 3.1s-0.5 2.5-1.3 3.3l-3 3.1-3-3.1c-0.8-0.8-1.3-2-1.3-3.3 0-1.2 0.4-2.2 1.3-3.1 0.8-0.8 1.9-1.3 3-1.3z" fill="#646464" fill-opacity=".39216" filter="url(#a)"/> <path fill="${color}" d="m4.5 0.2c1.1 0 2.2 0.5 3 1.3 0.8 0.9 1.3 1.9 1.3 3.1s-0.5 2.5-1.3 3.3l-3 3.1-3-3.1c-0.8-0.8-1.3-2-1.3-3.3 0-1.2 0.4-2.2 1.3-3.1 0.8-0.8 1.9-1.3 3-1.3z"/> </svg>`
    // return `data:image/svg+xml;utf8,` + svg.replace(/#/g, '%23')
    PINS[color] = window.URL.createObjectURL(
      new window.Blob([svg], { type: 'image/svg+xml' })
    )
  }
  return PINS[color]
}

const COLORS = {
  normal: '#007bff',
  pending: '#ffc107',
  success: '#6db750',
  failure: '#dc3545',
  withdrawn: '#007bff'
}

const STATUS_STRINGS = {
  normal: 'Jetzt anfragen!',
  pending: 'Anfrage läuft',
  success: 'Anfrage erfolgreich',
  failure: 'Anfrage abgelehnt',
  withdrawn: 'Anfrage zurückgezogen'
}

function getRequestStatus(status, resolution) {
  if (status === 'resolved') {
    if (resolution === 'successful' || resolution === 'partially_successful') {
      return 'success'
    } else if (resolution === 'refused') {
      return 'failure'
    } else if (
      resolution === 'user_withdrew' ||
      resolution === 'user_withdrew_costs'
    ) {
      return 'withdrawn'
    } else {
      return 'complete'
    }
  } else if (
    status === 'awaiting_response' ||
    status === 'awaiting_user_confirmation'
  ) {
    return 'pending'
  }
  return 'normal'
}

function latlngToGrid(latlng) {
  return {
    lat: Math.round(latlng.lat * 1000) / 1000,
    lng: Math.round(latlng.lng * 1000) / 1000
  }
}

function handleErrors(response) {
  if (!response.ok) {
    throw response
  }
  return response
}

function postData(url = '', data = {}, csrfToken) {
  return window
    .fetch(url, {
      method: 'POST',
      cache: 'no-cache',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify(data)
    })
    .then(handleErrors)
    .then((response) => response.json())
    .catch((error) =>
      error.text().then((errormessage) => {
        return {
          error: true,
          message: errormessage
        }
      })
    )
}

export {
  postData,
  getQueryVariable,
  canUseLocalStorage,
  renderDate,
  getPlaceStatus,
  getRequestStatus,
  getPinURL,
  COLORS,
  STATUS_STRINGS,
  latlngToGrid
}
