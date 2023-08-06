var browser_name = null;
var browser_lang = 'en';
var translations = {}

function get_browser_name() {
	if (browser_name!=null) {
		return browser_name;
	}
	rwebkit = /(webkit)[ \/]([\w.]+)/;
	rchrome = /(chrome)[ \/]([\w.]+)/;
	ropera = /(opera)(?:.*version)?[ \/]([\w.]+)/;
	rmsie = /(msie) ([\w.]+)/;
	rmozilla = /(mozilla)(?:.*? rv:([\w.]+))?/;
	ua = navigator.userAgent.toLowerCase();
	browser_name = 'unknown';
	if (rchrome.exec(ua)) {
		browser_name = 'chrome';
	}
	else if (ropera.exec(ua)) {
		browser_name = 'opera';
	}
	else if (rmsie.exec(ua)) {
		browser_name = 'msie';
	}
	else if (rwebkit.exec(ua)) {
		browser_name = 'safari';
	}
	else if (rmozilla.exec(ua)) {
		browser_name = 'mozilla';
	}
	return browser_name;
}

var STARTING = 1;
var WAITING = 2;
var LOADING = 3;
var DONE = 4;
var script_load_info = {};

function _script_status(url) {
	if (typeof(script_load_info[url])=="undefined") {
		return null;
	}
	return script_load_info[url].status;
}
function _set_script_status(url,status,options) {
	if (typeof(script_load_info[url])=="undefined") {
		script_load_info[url] = {status: status, options: {}}
	}
	script_load_info[url].status = status;
	if (options!=null) {
		script_load_info[url].options = options;
	}
}
function _check_script_deps_satisfied(url) {
	if (typeof(script_load_info[url])=="undefined") {
		return null;
	}
	for (var didx in script_load_info[url].options.dependencies) {
		dep_url = script_load_info[url].options.dependencies[didx];
		if (_script_status(dep_url)!=DONE) {
			return false;
		}
	}
	return true;
}

function _start_dep_satisfied_script_loads() {
	for (var url in script_load_info) {
		var script_load = script_load_info[url];
		if (script_load.status==WAITING && _check_script_deps_satisfied(url)) {
			_load_script(url,script_load.options);
		}
	}
}

function _load_script(url,options) {
	if (typeof(transdeps)!="undefined") {
		var new_deps = false;
		if (typeof(transdeps[url])!=undefined) {
			for (var dep in transdeps[url]) {
				if (script_load_info[url].options.dependencies.indexOf("translations/"+browser_lang+"/"+transdeps[url][dep]+".js")>-1) {
					continue;
				}
				script_load_info[url].options.dependencies.push("translations/"+browser_lang+"/"+transdeps[url][dep]+".js");
				new_deps = true;
				loadScript("translations/"+browser_lang+"/"+transdeps[url][dep]+".js");
			}
		}
		if (new_deps==true) {
			_start_dep_satisfied_script_loads();
			return;
		}
	}
	_set_script_status(url,LOADING);
	//console.debug("loading: " + url)
	var head = document.getElementsByTagName('head')[0];
	var script = document.createElement('script');
	script.setAttribute("id",options.id);
	script.type = 'text/javascript';
	script.src = url;

	// then bind the event to the callback function 
	// there are several events for cross browser compatibility
	var bname = get_browser_name();
	
	if (bname=="msie") {
		script.onreadystatechange = function(x) {
			if (this.readyState=='loaded' || this.readyState=='complete') {
				_set_script_status(url,DONE);
				if (options.callback) {
					options.callback(options.id);
				}
				_start_dep_satisfied_script_loads();
			}
		}
	}
	else {
		script.onload = function() {
			//console.debug("Done: " + url)
			_set_script_status(url,DONE);
			if (options.callback) {
				options.callback(options.id);
			}
			_start_dep_satisfied_script_loads();
		}
	}
	// fire the loading
	head.appendChild(script);
}

function loadScript(url, options) {
	// adding the script tag to the head as suggested before
	if (options==null) {
		options = {};
	}
	var def_options = {
		id: null,
		callback: null,
		dependencies: []
	}
	if (typeof(options.id)=="undefined") {
		options.id = def_options.id;
	}
	if (typeof(options.callback)=="undefined") {
		options.callback = def_options.callback;
	}
	if (typeof(options.dependencies)=="undefined") {
		options.dependencies = def_options.dependencies;
	}
	if (_script_status('translations/translation_handler.js')==null) {
		_load_script('translations/translation_handler.js',{
			id:null,
			dependencies:[],
			callback: function() {
			}
		});
	}
	options.dependencies.push('translations/translation_handler.js');
	if (_script_status(url)!=null) {
		return null;
	}
	_set_script_status(url,STARTING,options);
	if (!_check_script_deps_satisfied(url)) {
		_set_script_status(url,WAITING);
	}
	else {
		_load_script(url, options);
	}
}

function setLanguage(lang) {
	browser_lang = lang;
}

function pysite_translate(source,context,comment) {
	if (typeof(translations[context])!="undefined") {
		if (typeof(translations[context][source])!="undefined") {
			if (typeof(translations[context][source][(comment==null?"":comment)])!="undefined") {
				return translations[context][source][(comment==null?"":comment)];
			}
		}
	}
	return "#" + source;
}

function pysite_tr_common(source,comment) {
	return pysite_translate(source,"common",comment);
}

function pysite_tr(source,comment) {
	var context = (new Error).stack.match(/[^//]+\.js/g)[1].slice(0,-3);
	return pysite_translate(source,context,comment);
}
