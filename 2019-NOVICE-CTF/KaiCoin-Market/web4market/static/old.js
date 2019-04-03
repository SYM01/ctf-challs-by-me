!function(e){function n(){}function t(e,n){return function(){e.apply(n,arguments)}}function o(e){if("object"!=typeof this)throw new TypeError("Promises must be constructed via new");if("function"!=typeof e)throw new TypeError("not a function");this._state=0,this._handled=!1,this._value=void 0,this._deferreds=[],s(e,this)}function i(e,n){for(;3===e._state;)e=e._value;return 0===e._state?void e._deferreds.push(n):(e._handled=!0,void o._immediateFn(function(){var t=1===e._state?n.onFulfilled:n.onRejected;if(null===t)return void(1===e._state?r:u)(n.promise,e._value);var o;try{o=t(e._value)}catch(i){return void u(n.promise,i)}r(n.promise,o)}))}function r(e,n){try{if(n===e)throw new TypeError("A promise cannot be resolved with itself.");if(n&&("object"==typeof n||"function"==typeof n)){var i=n.then;if(n instanceof o)return e._state=3,e._value=n,void f(e);if("function"==typeof i)return void s(t(i,n),e)}e._state=1,e._value=n,f(e)}catch(r){u(e,r)}}function u(e,n){e._state=2,e._value=n,f(e)}function f(e){2===e._state&&0===e._deferreds.length&&o._immediateFn(function(){e._handled||o._unhandledRejectionFn(e._value)});for(var n=0,t=e._deferreds.length;n<t;n++)i(e,e._deferreds[n]);e._deferreds=null}function c(e,n,t){this.onFulfilled="function"==typeof e?e:null,this.onRejected="function"==typeof n?n:null,this.promise=t}function s(e,n){var t=!1;try{e(function(e){t||(t=!0,r(n,e))},function(e){t||(t=!0,u(n,e))})}catch(o){if(t)return;t=!0,u(n,o)}}var a=setTimeout;o.prototype["catch"]=function(e){return this.then(null,e)},o.prototype.then=function(e,t){var o=new this.constructor(n);return i(this,new c(e,t,o)),o},o.all=function(e){var n=Array.prototype.slice.call(e);return new o(function(e,t){function o(r,u){try{if(u&&("object"==typeof u||"function"==typeof u)){var f=u.then;if("function"==typeof f)return void f.call(u,function(e){o(r,e)},t)}n[r]=u,0===--i&&e(n)}catch(c){t(c)}}if(0===n.length)return e([]);for(var i=n.length,r=0;r<n.length;r++)o(r,n[r])})},o.resolve=function(e){return e&&"object"==typeof e&&e.constructor===o?e:new o(function(n){n(e)})},o.reject=function(e){return new o(function(n,t){t(e)})},o.race=function(e){return new o(function(n,t){for(var o=0,i=e.length;o<i;o++)e[o].then(n,t)})},o._immediateFn="function"==typeof setImmediate&&function(e){setImmediate(e)}||function(e){a(e,0)},o._unhandledRejectionFn=function(e){"undefined"!=typeof console&&console&&console.warn("Possible Unhandled Promise Rejection:",e)},o._setImmediateFn=function(e){o._immediateFn=e},o._setUnhandledRejectionFn=function(e){o._unhandledRejectionFn=e},"undefined"!=typeof module&&module.exports?module.exports=o:e.Promise||(e.Promise=o)}(this);
(function(self) {
    'use strict';
  
    if (self.fetch) {
      return
    }
  
    var support = {
      searchParams: 'URLSearchParams' in self,
      iterable: 'Symbol' in self && 'iterator' in Symbol,
      blob: 'FileReader' in self && 'Blob' in self && (function() {
        try {
          new Blob()
          return true
        } catch(e) {
          return false
        }
      })(),
      formData: 'FormData' in self,
      arrayBuffer: 'ArrayBuffer' in self
    }
  
    if (support.arrayBuffer) {
      var viewClasses = [
        '[object Int8Array]',
        '[object Uint8Array]',
        '[object Uint8ClampedArray]',
        '[object Int16Array]',
        '[object Uint16Array]',
        '[object Int32Array]',
        '[object Uint32Array]',
        '[object Float32Array]',
        '[object Float64Array]'
      ]
  
      var isDataView = function(obj) {
        return obj && DataView.prototype.isPrototypeOf(obj)
      }
  
      var isArrayBufferView = ArrayBuffer.isView || function(obj) {
        return obj && viewClasses.indexOf(Object.prototype.toString.call(obj)) > -1
      }
    }
  
    function normalizeName(name) {
      if (typeof name !== 'string') {
        name = String(name)
      }
      if (/[^a-z0-9\-#$%&'*+.\^_`|~]/i.test(name)) {
        throw new TypeError('Invalid character in header field name')
      }
      return name.toLowerCase()
    }
  
    function normalizeValue(value) {
      if (typeof value !== 'string') {
        value = String(value)
      }
      return value
    }
  
    // Build a destructive iterator for the value list
    function iteratorFor(items) {
      var iterator = {
        next: function() {
          var value = items.shift()
          return {done: value === undefined, value: value}
        }
      }
  
      if (support.iterable) {
        iterator[Symbol.iterator] = function() {
          return iterator
        }
      }
  
      return iterator
    }
  
    function Headers(headers) {
      this.map = {}
  
      if (headers instanceof Headers) {
        headers.forEach(function(value, name) {
          this.append(name, value)
        }, this)
      } else if (Array.isArray(headers)) {
        headers.forEach(function(header) {
          this.append(header[0], header[1])
        }, this)
      } else if (headers) {
        Object.getOwnPropertyNames(headers).forEach(function(name) {
          this.append(name, headers[name])
        }, this)
      }
    }
  
    Headers.prototype.append = function(name, value) {
      name = normalizeName(name)
      value = normalizeValue(value)
      var oldValue = this.map[name]
      this.map[name] = oldValue ? oldValue+','+value : value
    }
  
    Headers.prototype['delete'] = function(name) {
      delete this.map[normalizeName(name)]
    }
  
    Headers.prototype.get = function(name) {
      name = normalizeName(name)
      return this.has(name) ? this.map[name] : null
    }
  
    Headers.prototype.has = function(name) {
      return this.map.hasOwnProperty(normalizeName(name))
    }
  
    Headers.prototype.set = function(name, value) {
      this.map[normalizeName(name)] = normalizeValue(value)
    }
  
    Headers.prototype.forEach = function(callback, thisArg) {
      for (var name in this.map) {
        if (this.map.hasOwnProperty(name)) {
          callback.call(thisArg, this.map[name], name, this)
        }
      }
    }
  
    Headers.prototype.keys = function() {
      var items = []
      this.forEach(function(value, name) { items.push(name) })
      return iteratorFor(items)
    }
  
    Headers.prototype.values = function() {
      var items = []
      this.forEach(function(value) { items.push(value) })
      return iteratorFor(items)
    }
  
    Headers.prototype.entries = function() {
      var items = []
      this.forEach(function(value, name) { items.push([name, value]) })
      return iteratorFor(items)
    }
  
    if (support.iterable) {
      Headers.prototype[Symbol.iterator] = Headers.prototype.entries
    }
  
    function consumed(body) {
      if (body.bodyUsed) {
        return Promise.reject(new TypeError('Already read'))
      }
      body.bodyUsed = true
    }
  
    function fileReaderReady(reader) {
      return new Promise(function(resolve, reject) {
        reader.onload = function() {
          resolve(reader.result)
        }
        reader.onerror = function() {
          reject(reader.error)
        }
      })
    }
  
    function readBlobAsArrayBuffer(blob) {
      var reader = new FileReader()
      var promise = fileReaderReady(reader)
      reader.readAsArrayBuffer(blob)
      return promise
    }
  
    function readBlobAsText(blob) {
      var reader = new FileReader()
      var promise = fileReaderReady(reader)
      reader.readAsText(blob)
      return promise
    }
  
    function readArrayBufferAsText(buf) {
      var view = new Uint8Array(buf)
      var chars = new Array(view.length)
  
      for (var i = 0; i < view.length; i++) {
        chars[i] = String.fromCharCode(view[i])
      }
      return chars.join('')
    }
  
    function bufferClone(buf) {
      if (buf.slice) {
        return buf.slice(0)
      } else {
        var view = new Uint8Array(buf.byteLength)
        view.set(new Uint8Array(buf))
        return view.buffer
      }
    }
  
    function Body() {
      this.bodyUsed = false
  
      this._initBody = function(body) {
        this._bodyInit = body
        if (!body) {
          this._bodyText = ''
        } else if (typeof body === 'string') {
          this._bodyText = body
        } else if (support.blob && Blob.prototype.isPrototypeOf(body)) {
          this._bodyBlob = body
        } else if (support.formData && FormData.prototype.isPrototypeOf(body)) {
          this._bodyFormData = body
        } else if (support.searchParams && URLSearchParams.prototype.isPrototypeOf(body)) {
          this._bodyText = body.toString()
        } else if (support.arrayBuffer && support.blob && isDataView(body)) {
          this._bodyArrayBuffer = bufferClone(body.buffer)
          // IE 10-11 can't handle a DataView body.
          this._bodyInit = new Blob([this._bodyArrayBuffer])
        } else if (support.arrayBuffer && (ArrayBuffer.prototype.isPrototypeOf(body) || isArrayBufferView(body))) {
          this._bodyArrayBuffer = bufferClone(body)
        } else {
          throw new Error('unsupported BodyInit type')
        }
  
        if (!this.headers.get('content-type')) {
          if (typeof body === 'string') {
            this.headers.set('content-type', 'text/plain;charset=UTF-8')
          } else if (this._bodyBlob && this._bodyBlob.type) {
            this.headers.set('content-type', this._bodyBlob.type)
          } else if (support.searchParams && URLSearchParams.prototype.isPrototypeOf(body)) {
            this.headers.set('content-type', 'application/x-www-form-urlencoded;charset=UTF-8')
          }
        }
      }
  
      if (support.blob) {
        this.blob = function() {
          var rejected = consumed(this)
          if (rejected) {
            return rejected
          }
  
          if (this._bodyBlob) {
            return Promise.resolve(this._bodyBlob)
          } else if (this._bodyArrayBuffer) {
            return Promise.resolve(new Blob([this._bodyArrayBuffer]))
          } else if (this._bodyFormData) {
            throw new Error('could not read FormData body as blob')
          } else {
            return Promise.resolve(new Blob([this._bodyText]))
          }
        }
  
        this.arrayBuffer = function() {
          if (this._bodyArrayBuffer) {
            return consumed(this) || Promise.resolve(this._bodyArrayBuffer)
          } else {
            return this.blob().then(readBlobAsArrayBuffer)
          }
        }
      }
  
      this.text = function() {
        var rejected = consumed(this)
        if (rejected) {
          return rejected
        }
  
        if (this._bodyBlob) {
          return readBlobAsText(this._bodyBlob)
        } else if (this._bodyArrayBuffer) {
          return Promise.resolve(readArrayBufferAsText(this._bodyArrayBuffer))
        } else if (this._bodyFormData) {
          throw new Error('could not read FormData body as text')
        } else {
          return Promise.resolve(this._bodyText)
        }
      }
  
      if (support.formData) {
        this.formData = function() {
          return this.text().then(decode)
        }
      }
  
      this.json = function() {
        return this.text().then(JSON.parse)
      }
  
      return this
    }
  
    // HTTP methods whose capitalization should be normalized
    var methods = ['DELETE', 'GET', 'HEAD', 'OPTIONS', 'POST', 'PUT']
  
    function normalizeMethod(method) {
      var upcased = method.toUpperCase()
      return (methods.indexOf(upcased) > -1) ? upcased : method
    }
  
    function Request(input, options) {
      options = options || {}
      var body = options.body
  
      if (input instanceof Request) {
        if (input.bodyUsed) {
          throw new TypeError('Already read')
        }
        this.url = input.url
        this.credentials = input.credentials
        if (!options.headers) {
          this.headers = new Headers(input.headers)
        }
        this.method = input.method
        this.mode = input.mode
        if (!body && input._bodyInit != null) {
          body = input._bodyInit
          input.bodyUsed = true
        }
      } else {
        this.url = String(input)
      }
  
      this.credentials = options.credentials || this.credentials || 'omit'
      if (options.headers || !this.headers) {
        this.headers = new Headers(options.headers)
      }
      this.method = normalizeMethod(options.method || this.method || 'GET')
      this.mode = options.mode || this.mode || null
      this.referrer = null
  
      if ((this.method === 'GET' || this.method === 'HEAD') && body) {
        throw new TypeError('Body not allowed for GET or HEAD requests')
      }
      this._initBody(body)
    }
  
    Request.prototype.clone = function() {
      return new Request(this, { body: this._bodyInit })
    }
  
    function decode(body) {
      var form = new FormData()
      body.trim().split('&').forEach(function(bytes) {
        if (bytes) {
          var split = bytes.split('=')
          var name = split.shift().replace(/\+/g, ' ')
          var value = split.join('=').replace(/\+/g, ' ')
          form.append(decodeURIComponent(name), decodeURIComponent(value))
        }
      })
      return form
    }
  
    function parseHeaders(rawHeaders) {
      var headers = new Headers()
      // Replace instances of \r\n and \n followed by at least one space or horizontal tab with a space
      // https://tools.ietf.org/html/rfc7230#section-3.2
      var preProcessedHeaders = rawHeaders.replace(/\r?\n[\t ]+/g, ' ')
      preProcessedHeaders.split(/\r?\n/).forEach(function(line) {
        var parts = line.split(':')
        var key = parts.shift().trim()
        if (key) {
          var value = parts.join(':').trim()
          headers.append(key, value)
        }
      })
      return headers
    }
  
    Body.call(Request.prototype)
  
    function Response(bodyInit, options) {
      if (!options) {
        options = {}
      }
  
      this.type = 'default'
      this.status = options.status === undefined ? 200 : options.status
      this.ok = this.status >= 200 && this.status < 300
      this.statusText = 'statusText' in options ? options.statusText : 'OK'
      this.headers = new Headers(options.headers)
      this.url = options.url || ''
      this._initBody(bodyInit)
    }
  
    Body.call(Response.prototype)
  
    Response.prototype.clone = function() {
      return new Response(this._bodyInit, {
        status: this.status,
        statusText: this.statusText,
        headers: new Headers(this.headers),
        url: this.url
      })
    }
  
    Response.error = function() {
      var response = new Response(null, {status: 0, statusText: ''})
      response.type = 'error'
      return response
    }
  
    var redirectStatuses = [301, 302, 303, 307, 308]
  
    Response.redirect = function(url, status) {
      if (redirectStatuses.indexOf(status) === -1) {
        throw new RangeError('Invalid status code')
      }
  
      return new Response(null, {status: status, headers: {location: url}})
    }
  
    self.Headers = Headers
    self.Request = Request
    self.Response = Response
  
    self.fetch = function(input, init) {
      return new Promise(function(resolve, reject) {
        var request = new Request(input, init)
        var xhr = new XMLHttpRequest()
  
        xhr.onload = function() {
          var options = {
            status: xhr.status,
            statusText: xhr.statusText,
            headers: parseHeaders(xhr.getAllResponseHeaders() || '')
          }
          options.url = 'responseURL' in xhr ? xhr.responseURL : options.headers.get('X-Request-URL')
          var body = 'response' in xhr ? xhr.response : xhr.responseText
          resolve(new Response(body, options))
        }
  
        xhr.onerror = function() {
          reject(new TypeError('Network request failed'))
        }
  
        xhr.ontimeout = function() {
          reject(new TypeError('Network request failed'))
        }
  
        xhr.open(request.method, request.url, true)
  
        if (request.credentials === 'include') {
          xhr.withCredentials = true
        } else if (request.credentials === 'omit') {
          xhr.withCredentials = false
        }
  
        if ('responseType' in xhr && support.blob) {
          xhr.responseType = 'blob'
        }
  
        request.headers.forEach(function(value, name) {
          xhr.setRequestHeader(name, value)
        })
  
        xhr.send(typeof request._bodyInit === 'undefined' ? null : request._bodyInit)
      })
    }
    self.fetch.polyfill = true
  })(typeof self !== 'undefined' ? self : this);