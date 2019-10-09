(function(){
  window.addEventListener("message", function(e) {
    if (e.origin !== "https://fragdenstaat.de" && e.origin !== "http://localhost:8000") {return;}

    var iframeId = e.data[0];
    var iframe = document.getElementById(iframeId);
    var data      = e.data[2];
    iframe.style.height = data + 'px';
  }, false)
}())
