var jaobi = (jaobi || {})
    , doc = document
	, win = window;

win._jaobi = {}; //privates
// $param_name = optional parameter.

//base
(function(o){

  function set_config(config) {
    o.confs = win.extend({
       version            : "0.2.1"
      ,JAOBI_API_URL      : 'http://jaobi.com/api/'
      ,JAOBI_CONSUMER_URL : false
      ,COOKIE_NAME        : 'jaobi_consumer'
      ,CONSUMPTION_COOKIE : 'jaobi_consumption'
      ,ACCESS_COOKIE      : 'jaobi_old_access'
      ,THEMES_COOKIE      : 'jaobi_preferred_themes'
      ,CONTENT_URI	  : null
      ,widget_col_size    : 200
      ,MAX_ACCESS_DATA    : 300
      ,similar_consumers  : 5
      ,default_suggestions: 10
      ,auto_send          : true
      ,contentID          : false
      ,log                : false
      ,API_KEY            : null
      ,use_local          : true
      ,send_only_once     : false
      ,auto_create_widget : true
    }, config);

    if (o.confs.JAOBI_CONSUMER_URL == false){
      o.confs.JAOBI_CONSUMER_URL = o.confs.JAOBI_API_URL.replace(
	'/api/', '/interfone/consumer_server.html');
    }

  }
  if (typeof JAOBI_CONFIGS == "undefined") JAOBI_CONFIGS = {};
  set_config(JAOBI_CONFIGS);

  //base methods
  win._jaobi.eventListeners = {};

  o.callee = function(callback,args){
	if(typeof callback == "function") {
	  callback.apply(undefined, args);
	} else {
	  throw new Exception('param "callback" is required!');
	}
  };

  o.call = function(eventType, args){
    var listeners = win._jaobi.eventListeners[eventType];
    if (listeners) {
      for (var i = listeners.length - 1; i >= 0; i--) {
        listeners[i](args);
      };
    };
  };

  o.on = function(eventType, callback){
    if (!win._jaobi.eventListeners[eventType]) win._jaobi.eventListeners[eventType] = [];
    var listeners = win._jaobi.eventListeners[eventType];
    if (o.confs[eventType]) {
      callback(o.confs[eventType]);
    };
    if (typeof callback == "function") {
      listeners.push(callback);
    };
  };

  o.is_accessed = function(url) {
    if (interphone_get_local(o.confs.ACCESS_COOKIE,"all")) {
      var urls = interphone_get_local(o.confs.ACCESS_COOKIE,"all").split("|");
      return (urls.indexOf(url) != -1); //interphone define Array.indexOf for IE8
    } else {
      return false;
    };
  }

  o.set_access = function(url) {
    var urls = interphone_get_local(o.confs.ACCESS_COOKIE,"all");
    urls = (urls || "").split("|");
    urls.unshift(url);
    urls.splice(o.confs.MAX_ACCESS_DATA,urls.length);
    urls = urls.join("|");
    interphone_set_local(o.confs.ACCESS_COOKIE,urls,"all")
    return url;
  }

})(jaobi);


// consumer
(function(o){
  o.consumer = {};
  var api_url = o.confs.JAOBI_API_URL + "consumer/";
  var server;

  function retrieve_id(id, callback) {
    o.confs.consumerID = id
    if (o.confs.JAOBI_CONSUMER_URL) {
      server.set(o.confs.COOKIE_NAME,o.confs.consumerID,"all")
    } else {
      interphone_set_local(o.confs.COOKIE_NAME,o.confs.consumerID,"all");
    };
    if (o.confs.log) utils.log('consumer created successfully');
    o.call("consumerID",o.confs.consumerID);
    callback(o.confs.consumerID);
  }

  function create_id(callback) {
    utils.ajax({
      url: api_url + 'create',
      data: {'api_key': o.confs.API_KEY},
      type: 'PUT',
      success: function(response){
        retrieve_id(response.id, callback)
      },
      error: function(response){
        if (o.confs.log) utils.log('error creating consumer');
        callback(false,response);
      }
    });
  }

  o.consumer.getID = function(callback) {
    var id = interphone_get_local(o.confs.COOKIE_NAME,"all");
    if (o.confs.use_local && id && id != 'undefined' && id !="!storage" && id != "storage") {
      callback(id);
      if (o.confs.log) utils.log('consumer already created');
    } else {
      if (o.confs.JAOBI_CONSUMER_URL) {
        server = new interphone({
          on_ready: function(inter) {
            server.get(o.confs.COOKIE_NAME,"all");
          },
          on_data: function(key,val,type){
            if (key == o.confs.COOKIE_NAME) {
              if (!val) {
                create_id(callback);
              } else {
                retrieve_id(val,callback)
              };
            };
          },
          closed: true,
          serverUrl: o.confs.JAOBI_CONSUMER_URL
        })
      } else {
        create_id(callback);
      };
    };
  };

  o.consumer.sendAccess = function($url,$callback){
    var attempts = 0;
    if (typeof $url == "function") {
      $callback = $url;
      $url = false;
	}

	$url = $url || o.confs.CONTENT_URI || win.location.href;

    if (o.confs.send_only_once && o.is_accessed($url)) {
      if (typeof $callback == "function") $callback("ok");
      return;
    };
    function send_URL(contentID) {
      o.consumer.getID(function(consumerID){
        utils.ajax({
          type: 'PUT',
          url: o.confs.JAOBI_API_URL + 'contentconsumption/',
          data: {
            'content__url': $url,
            'consumer__id': consumerID,
	    'referrer': document.referrer,
            'consumed': true,
	    'api_key': o.confs.API_KEY,
          },
          success: function(response){
            o.set_access($url)

            if (typeof $callback == "function") $callback(response);
            if (o.confs.log) utils.log('sendAccess ok');
          },
          error: function(response){
            if (attempts < 0) {
              attempts ++;
              // o.content.createContent($url,function(contentID){
              //   send_URL($url);
              // })
            } else {
              if (typeof $callback == "function") $callback(false,response);
              if (o.confs.log) utils.log('sendAccess ERROR');
            };
          }
        });
      })
    };
    send_URL($url);
  };

  o.consumer.sendAccessFinished = function($url,$callback){

    if (typeof $url == "function") {
      $callback = $url;
      $url = false;
    }

    $url = $url || o.confs.CONTENT_URI || win.location.href;

    if (o.confs.send_only_once && o.is_accessed($url)) {
      if (typeof $callback == "function") $callback("ok");
      return;
    };
    function send_URL_Finished(contentID) {
      o.consumer.getID(function(consumerID){
        utils.ajax({
          type: 'PUT',
          url: o.confs.JAOBI_API_URL + 'contentconsumption/consumption-finished',
          data: {
            'content__url': $url,
            'consumer__id': consumerID,
	    'api_key': o.confs.API_KEY,
          },
          success: function(response){
            o.set_access($url)
            if (typeof $callback == "function") $callback(response);
            if (o.confs.log) utils.log('sendAccessFinished ok');
          },
          error: function(response){
            if (attempts < 0) {
              attempts ++;
              // o.content.createContent($url,function(contentID){
              //   send_URL($url);
              // })
            } else {
              if (typeof $callback == "function") $callback(false,response);
              if (o.confs.log) utils.log('sendAccess ERROR');
            };
          }
        });
      })
    };
    send_URL_Finished($url);
  };

  o.consumer.getSimilarConsumers = function($quantity){
    if (!$quantity) $quantity = o.confs.similar_consumers;
    function orderClassifiedConsumers(classified_consumers){
      var ordered_consumers = new Array();
      for (var consumer in classified_consumers){
        ordered_consumers.push([consumer, classified_consumers[consumer]]);
      }
      ordered_consumers.sort(function(a, b){
        return b[1] - a[1];
      });
      return ordered_consumers;
    };

    var recorded = interphone_get_local(o.confs.CONSUMPTION_COOKIE,"storage");
    if (recorded) recorded = JSON.parse(recorded)
    var consumers = (recorded || {});

    var similar_consumers = orderClassifiedConsumers(consumers);
    var similar_ids = new Array();
    for (var i = 0; i < similar_consumers.length; i++){
      similar_ids.push(similar_consumers[i][0]);
      if ( i + 1 >= $quantity){
        break;
      }
    }
    return similar_ids;
  };

  o.consumer.getSuggestions = function($quantity,callback) {

    if (typeof $quantity == "function") {
      callback = $quantity;
      $quantity = o.confs.default_suggestions;
    } else {
      $quantity = $quantity || o.confs.default_suggestions;
	  callback = callback || function(){};
	};


    o.consumer.getID(function(consumer_id) {
      var url = api_url + 'behavioral-suggestions';
      var similar_consumers = o.consumer.getSimilarConsumers();
      var query_str = '?consumer_id=' + consumer_id + '&quantity=' + $quantity;
	  query_str += '&content_uri='+ o.confs.CONTENT_URI;
      for (var index in similar_consumers){
        query_str += '&s=' + similar_consumers[index];
      };
      utils.ajax({
        url: api_url + 'behavioral-suggestions' + query_str + '&api_key=' + o.confs.API_KEY,
        success: function(response){
          callback(response);
        }
      });
    })
  };

  o.consumer.getPreferredThemes = function($callback) {
    // retrieve preferred themes from server
    o.consumer.getID(function(consumer_id){
      var url = api_url + 'preferred-themes';
      utils.ajax({
		url: url,
		data: {
		  'api_key': o.confs.API_KEY,
		  'consumer_id': consumer_id
		},
		success: function(response){
		  interphone_set_local(
		    o.confs.THEMES_COOKIE, JSON.stringify(response.items), "all");
		  if($callback){$callback(response)};
		}
      });
    });
  };

  o.consumer.preferredThemes = function(){
    // get preferred themes from cookie
    var themes = interphone_get_local(o.confs.THEMES_COOKIE, "all");
    if (themes){
      themes = JSON.parse(themes);
    }
    return themes;
  }


})(jaobi);


// widget
(function(o){
  var company_link = '<a target="_blank" class="jaobi_logo" href="#jaobi">jao.bi</a>'
  o.widget = {};
  o.widget.all = {};
  o.widget.options = {
     selector: '[data-jaobi]'
    ,quantity: 3
    ,loading: '<div class="loading">loading...</div>'
    ,template: '<ul class="jaobi_list">' + company_link
           +'<% for (var j = 0; j < i.length; j++) { %>'
              +'<li'
                +' data-origin="<%= i[j].origin %>"'
                +' data-producer="<%= i[j].producer %>"'
                +' data-publication_date="<%= i[j].publication_date %>"'
              +'>'
                +'<a href="<%= i[j].url %>">'
                  +'<% if(i[j].image) { %>'
                    +'<img src="<%= i[j].image %>" />'
                  +'<% } %>'
                  +'<% if(i[j].title) { %>'
                    +'<h3><%= i[j].title %></h3>'
                  +'<% } %>'
                  +'<% if(i[j].description) { %>'
                    +'<p><%= i[j].description %></p>'
                  +'<% } %>'
                +'</a>'
              +'</li>'
           +'<% } %>'
           +'</ul>'
  };


  o.widget.include_css = function() {
    var has_css = doc.getElementById("jaobi_css_base");
    if (!has_css) {
      var css = ""
        css += ".jaobi_list {"
          css += "position: relative;"
          css += "font-style: sans-serif;"
          css += "display: inline-block;"
          // css += "display: none;"
          css += "list-style-type: none;"
          css += "padding: 0;"
          css += "margin: 0;"
          css += "background-color: transparent;"
          css += "-webkit-background-size: "+o.confs.widget_col_size+"px;"
          css += "-moz-background-size: "+o.confs.widget_col_size+"px;"
          css += "o-background-size: "+o.confs.widget_col_size+"px;"
          css += "background-size: "+o.confs.widget_col_size+"px;"
          css += "background-image: -webkit-linear-gradient(0, transparent 99.5%, rgba(0, 0, 0, .10) 50%);"
          css += "background-image: -moz-linear-gradient(0px 50%, transparent 99.5%, rgba(0, 0, 0, 0.10) 50%);"
          css += "background-image: -ms-linear-gradient(0, transparent 99.5%, rgba(0, 0, 0, .10) 50%);"
          css += "background-image: -o-linear-gradient(0, transparent 99.5%, rgba(0, 0, 0, .10) 50%); "
          css += "border-left: 1px solid transparent;"
          // filter: progid:DXImageTransform.Microsoft.gradient(GradientType=1,startColorstr='#FFFFFF',endColorstr='#F5F5F5');
          // -ms-filter: "progid:DXImageTransform.Microsoft.gradient(GradientType=1,startColorstr='#FFFFFF',endColorstr='#F5F5F5')";
        css += "}"
        css += ".jaobi_list .jaobi_logo {"
          css += "position: absolute;"
          css += "color: gray;"
          css += "padding: 1px 4px;"
          css += "font-size: 8px;"
          css += "font-family: monospace;"
          css += "text-decoration: none;"
          css += "bottom: 0px;"
          css += "right: 0px;"
        css += "}"
        css += ".jaobi_list li img {"
          css += "width: 100%;"
        css += "}"
        css += ".jaobi_list li {"
          css += "display: inline-block;"
          css += "vertical-align: top;"
          css += "padding: 0px 10px 10px 10px;"
          css += "width: 180px;"
        css += "}"
        css += ".jaobi_list li .loading {"
          css += "display: inline-block;"
        css += "}"
        css += ".jaobi_list li a {"
          css += "color: #333;"
          css += "display: inline-block;"
          css += "text-decoration: none;"
        css += "}"
        css += ".jaobi_list li a:hover, .jaobi_logo:hover {"
          css += "text-decoration: underline;"
        css += "}"
      head = doc.head || doc.getElementsByTagName('head')[0],
      style = doc.createElement('style');
      style.type = 'text/css';
      style.id = "jaobi_css_base";
      if (style.styleSheet){
        style.styleSheet.cssText = css;
      } else {
        style.appendChild(doc.createTextNode(css));
      }
      head.insertBefore(style, head.firstChild);
    };
  }

  function generate_widget(defaults,items,callback) {
    var div = doc.createElement('div');
    div.innerHTML = utils.tmpl(defaults.template,{i: items});
    var widget = div.firstChild;
    widget.id = 'xxxxxx2-yxxx-xxxx-yxxx'.to_id()
    callback(widget);
  };

  o.widget.update = function($selector, $callback) {
    if (typeof $selector == "function") {
      $callback = $selector;
      $selector = false;
    };
    var count = 0;
    var total = 0;
    if ($selector) {
      o.widget.create({selector: $selector, loading: false},$callback);
    } else {
      for (sel in o.widget.all) { total ++; };
      for (sel in o.widget.all) {
        o.widget.create({selector: sel, loading: false}, function(){
          count ++;
          if (count == total && $callback) $callback(o.widget.all);
        });
      };
    };
  };

  o.widget.get = function($selector) {
    return $selector?o.widget.all[$selector]:o.widget.all;
  }

  o.widget.remove = function($selector) {
    if ($selector) {
      var el = doc.querySelectorAll($selector);
      if (el.length > 0) el[0].innerHTML = "";
      delete o.widget.all[$selector];
    } else {
      for (sel in o.widget.all) {
        var el = doc.querySelectorAll(sel);
        for (var i = 0; i < el.length; i++) {
          el[i].innerHTML = "";
        };
        delete o.widget.all[sel];
      };
    };
  }

  o.widget.create = function($opts,$callback) {
    if (typeof $opts == "string") {
      $opts = {selector: $opts};
    } else if (typeof $opts == "function") {
      $callback = $opts;
      $opts = undefined;
    }
    var general_defaults = utils.clone(o.widget.options);
    var defaults = win.extend(general_defaults,($opts || {}));
    var sel = defaults.selector;
    o.widget.all[sel] = [];
    var boxes = doc.querySelectorAll(sel)
    var todo = [];
    var total = 0;
    for (var i = boxes.length - 1; i >= 0; i--) {
      var attrbs = {};
      for (var j = 0; j < boxes[i].attributes.length; j++) {
        var attrib = boxes[i].attributes[j];
        var val = attrib.value;
        attrbs[attrib.name.replace("data-","")] = utils.isNumeric(val)?Number(val):val;
      };
      var user_defaults = utils.clone(defaults);
      var item_defaults = win.extend(user_defaults,attrbs);
      if (item_defaults.loading) boxes[i].innerHTML = item_defaults.loading;
      total += item_defaults.quantity;
      todo.unshift({box: boxes[i],defaults: item_defaults})
    };
    var rest = total;
    if (total > 0) {
      o.consumer.getSuggestions(total, function(res){
        o.content.getLastConsumers(total, function(){});
	if (res && res.items) {
	  for (var i = 0; i < todo.length; i++) {
	    var quant = todo[i].defaults.quantity;
	    rest -= quant;
	    var items = res.items.splice(0,quant);
	    generate_widget(todo[i].defaults, items, function(widget){
	      todo[i].box.innerHTML = "";
	      todo[i].box.appendChild(widget);

	      //record box into selector.
	      o.widget.all[sel].push(todo[i].box);

	      if (rest < 1) {
		if (typeof $callback != "undefined") {
                  $callback(o.widget.all[sel]);
                }
	      };
	    })
	  };
	} else {
	  if (typeof $callback != "undefined") $callback(false);
	};
      });
    };
  };

  o.widget.create_all = function(callback) {
    o.widget.include_css();
    o.widget.create(callback);
  };

  if (o.confs.auto_create_widget){
     utils.addEvent("load",o.widget.create_all);
  }

})(jaobi);


// content
(function(o){
  o.content = {};
  var api_url = o.confs.JAOBI_API_URL + 'content/';
  var url = o.confs.CONTENT_URI || win.location.href.replace(win.location.search, '');

  o.content.createContent = function($url,$callback) {
    var title = doc.title || 'title'
    if (typeof $url == "function") {
      $callback = $url;
      $url = url;
    } else {
      title = 'title';
    };
    var data = {
      'url': $url,
      'title': title,
      'api_key': o.confs.API_KEY,
      }
    utils.ajax({
      type: 'PUT',
      url: api_url,
      data: data,
      success: function(response){
        if (o.confs.log) utils.log('createContent ok');
        o.confs.contentID = response['id'];
        if (typeof $callback == "function") $callback(o.confs.contentID);
      },
      error: function(response){
        if (o.confs.log) utils.log('createContent error');
        if (typeof $callback == "function") $callback(false,response);
      },
    });
  };

  o.content.getID = function(callback){
    if(o.confs.contentID && callback) {
      callback(o.confs.contentID);
      return;
    };
    utils.ajax({
      url: api_url,
      data: {'url': url,
	     'api_key': o.confs.API_KEY},
      success: function(response){
        if (o.confs.log) utils.log('getContentId ok');
        o.confs.contentID = response.id;
        o.call("contentID",o.confs.contentID);
        callback(o.confs.contentID);
      },
      error: function(response){
        // o.content.createContent(function(res){
        //   callback(false);
        // });
      },
    });
  };

  o.content.getLastConsumers = function($quantity, callback){
    if (typeof $quantity == "function") {
      callback = $quantity;
      $quantity = o.confs.default_suggestions;
    }

    var recorded = interphone_get_local(o.confs.CONSUMPTION_COOKIE,"all");
    if (recorded) recorded = JSON.parse(recorded)
    var consumers = (recorded || {});

    function classifyConsumers(last_consumers){
      var last_consumers = last_consumers || [];
      for (var i = 0; i < last_consumers.length; i++){
        var consumer = last_consumers[i];
        var count = consumers[consumer.id] || 0;
        count++;
        consumers[consumer.id] = count;
      }
      interphone_set_local(o.confs.CONSUMPTION_COOKIE,JSON.stringify(consumers),"all");
      return consumers;
    };

    if (o.is_accessed(url) && !utils.isEmptyObject(consumers) ) {
      callback(consumers);
    } else {
      utils.ajax({
        url: api_url + 'last-consumers',
        data: {
          'url': url,
          'quantity': $quantity,
		  'api_key': o.confs.API_KEY,
        },
        success: function(response){
          callback(classifyConsumers(response.items));
        },
      });
    };

  };

})(jaobi);


//auto-start
(function(o){
  o.confs.auto_init = function() {
    o.confs.start = "starting...";
    o.call("start",o.confs.start);
    function ready() {
      o.call("ready", o.confs.ready)
    }
    if (o.confs.auto_send) {
      o.consumer.sendAccess(function(res){
        o.confs.ready = res;
        ready();
      });
    } else {
      ready();
    };
  };
  o.confs.test_envy = function(){
    if (!win.interphone || !win.utils) {
      if (console) console.log("interphone.js and utils.js are necessary!");
      return false;
    } else {
      return true;
    };
  }
  if (!o.confs.test_envy()) return;
  o.confs.auto_init();

  window.onunload = function(){
    o.consumer.sendAccessFinished(function(res){
      ready();

    });
  }
})(jaobi);
