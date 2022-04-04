;(function () {
  window.addEventListener(
    'message',
    function (e) {
      if (
        e.origin !== 'https://media.frag-den-staat.de' &&
        e.origin !== 'https://fragdenstaat.de' &&
        e.origin !== 'http://localhost:8000'
      ) {
        return
      }

      const iframeId = e.data[0]
      const iframe = document.getElementById(iframeId)
      const data = e.data[2]
      iframe.style.height = data + 'px'
    },
    false
  )
})()
