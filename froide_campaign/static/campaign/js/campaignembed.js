(function webpackUniversalModuleDefinition(root, factory) {
	if(typeof exports === 'object' && typeof module === 'object')
		module.exports = factory();
	else if(typeof define === 'function' && define.amd)
		define([], factory);
	else if(typeof exports === 'object')
		exports["campaignembed"] = factory();
	else
		root["Froide"] = root["Froide"] || {}, root["Froide"]["components"] = root["Froide"]["components"] || {}, root["Froide"]["components"]["campaignembed"] = factory();
})(typeof self !== 'undefined' ? self : this, function() {
return /******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, {
/******/ 				configurable: false,
/******/ 				enumerable: true,
/******/ 				get: getter
/******/ 			});
/******/ 		}
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = 0);
/******/ })
/************************************************************************/
/******/ ([
/* 0 */
/***/ (function(module, exports, __webpack_require__) {

module.exports = __webpack_require__(1);


/***/ }),
/* 1 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


__webpack_require__(2);

function resize() {
  var height = document.getElementsByTagName('html')[0].scrollHeight;
  window.parent.postMessage(['froide-campaign-' + window.Froide.campaignPageId, 'setHeight', height], '*');
}

document.addEventListener('DOMContentLoaded', getRandom);
document.addEventListener('resize', resize);

var searchForm = document.getElementById('searchform');
searchForm.addEventListener('submit', getSearch);

function getJson(url) {
  return new Promise(function (resolve, reject) {
    var request = new window.XMLHttpRequest();
    request.open('GET', url, true);
    request.onload = function () {
      if (request.status >= 400) {
        return reject(request.responseText);
      }
      resolve(JSON.parse(request.responseText));
    };
    request.onerror = function () {
      reject(request.statusText);
    };

    request.send();
  });
}

function renderResults(results, emptyMessage) {
  if (results.length === 0) {
    return '<p>' + emptyMessage + '</p>';
  } else {
    return results.map(function (r) {
      return '<div class="row request-row">\n      <div class="col-9">\n        <h6>\n          ' + r.description + '<br/>\n          <small>' + r.publicbody_name + '</small>\n        </h6>\n      </div>\n      <div class="col mr-auto">\n        <a href="' + r.request_url + '" rel="noopener" class="btn btn-primary btn-block">\n          ' + window.Froide.i18n.requestThis + '\n        </a>\n      </div>\n    </div>';
    }).join('\n');
  }
}

function getSearch(e) {
  e.preventDefault();
  var requestList = document.getElementById('request-list');
  requestList.className = 'requests-loading';

  var searchQuery = document.getElementById('search-input').value;

  var query = window.Froide.campaignIds.map(function (m) {
    return 'campaign=' + m;
  }).join('&');
  query += '&q=' + encodeURIComponent(searchQuery);
  var url = window.Froide.urls.campaigninformationobjectSearch + '?' + query;
  getJson(url).then(function (results) {
    var html = renderResults(results, window.Froide.i18n.noResults);
    requestList.className = '';
    document.getElementById('request-list').innerHTML = html;
    resize();
  });
}

function getRandom() {
  var moreButton = document.getElementById('load-more');
  moreButton.disabled = true;
  var requestList = document.getElementById('request-list');
  requestList.className = 'requests-loading';
  var query = window.Froide.campaignIds.map(function (m) {
    return 'campaign=' + m;
  }).join('&');
  var url = window.Froide.urls.campaigninformationobjectRandom + '?' + query;
  getJson(url).then(function (results) {
    var html = renderResults(results, window.Froide.i18n.noRequestLeft);
    moreButton.disabled = false;
    requestList.className = '';
    document.getElementById('request-list').innerHTML = html;
    resize();
  });
}

window.Froide.getRandom = getRandom;

/***/ }),
/* 2 */
/***/ (function(module, exports) {

// removed by extract-text-webpack-plugin

/***/ })
/******/ ]);
});
//# sourceMappingURL=campaignembed.js.map