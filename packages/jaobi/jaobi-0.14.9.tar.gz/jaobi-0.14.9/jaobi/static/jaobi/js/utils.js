var utils = (utils || {})
	, win = window;

utils.ajax = function(opts) {

  function createCORSRequest(method, url, async) {
    var xhr = new XMLHttpRequest();
    if ("withCredentials" in xhr) {
      // Check if the XMLHttpRequest object has a "withCredentials" property.
      // "withCredentials" only exists on XMLHTTPRequest2 objects.
      xhr.open(method, url, async);
    } else if (typeof XDomainRequest != "undefined") {
      // Otherwise, check if XDomainRequest.
      // XDomainRequest only exists in IE, and is IE's way of making CORS requests.
      xhr = new XDomainRequest();
      xhr.open(method, url, async);
    } else {
      // Otherwise, CORS is not supported by the browser.
      xhr = null;
    }
    return xhr;
  }

  if (!opts.type) opts.type = "GET";
  opts.type = opts.type.toUpperCase();
  if (opts.data) {
    var req = "";
    for(opt in opts.data) {
      req += opt + "=" + encodeURIComponent(opts.data[opt]) + "&"
    }
    opts.data = req;
    if (opts.type.match(/(GET)/ig)) {
      opts.url += "?"+opts.data;
    };
  };

  var xhr = createCORSRequest(opts.type,opts.url,(opts.async || true));
  if (opts.type.match(/(PUT|POST|DELETE|UPDATE)/ig)) {
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  }
  if (!xhr) return; //CORS not supported by the browser
  xhr.onreadystatechange = function(){
    if (xhr.readyState == 4) {
      var res = xhr.responseText;
      if (res.substr(0,1) == "{") res = JSON.parse(res);
      opts[(xhr.status >= 500)?"error":"success"](res);
    };
  };
  xhr.send(opts.data);
};

utils.log = function() {
  if (console) {
    console.log.apply(console, arguments);
  };
};

utils.isNumeric = function(n) { 
  return !isNaN(parseFloat(n)) && isFinite(n); 
};

utils.isEmptyObject = function(n) {
  return !Boolean(Object.keys(n).length);
};

utils.clone = function(obj) {
  return JSON.parse(JSON.stringify(obj));
};

utils.addEvent = function(event, callback) {
  if (win.attachEvent) {
    win.attachEvent('on'+event,function() {
      callback();
    })
  } else if (win.addEventListener) {
    win.addEventListener(event,function() {
      callback();
    },false);
  };
}



// John Resig - http://ejohn.org/ - MIT Licensed
utils.tmpl = function tmpl(str, data){
  var fn = new Function("obj",
      "var p=[],print=function(){p.push.apply(p,arguments);};" +
      "with(obj){p.push('" +
      str
        .replace(/[\r\t\n]/g, " ")
        .split("<%").join("\t")
        .replace(/((^|%>)[^\t]*)'/g, "$1\r")
        .replace(/\t=(.*?)%>/g, "',$1,'")
        .split("\t").join("');")
        .split("%>").join("p.push('")
        .split("\r").join("\\'")
    + "');}return p.join('');");
  return data ? fn( data ) : fn;
};


