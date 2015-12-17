/*! jQuery v1.11.1 | (c) 2005, 2014 jQuery Foundation, Inc. | jquery.org/license */
!function(a,b){"object"==typeof module&&"object"==typeof module.exports?module.exports=a.document?b(a,!0):function(a){if(!a.document)throw new Error("jQuery requires a window with a document");return b(a)}:b(a)}("undefined"!=typeof window?window:this,function(a,b){var c=[],d=c.slice,e=c.concat,f=c.push,g=c.indexOf,h={},i=h.toString,j=h.hasOwnProperty,k={},l="1.11.1",m=function(a,b){return new m.fn.init(a,b)},n=/^[\s\uFEFF\xA0]+|[\s\uFEFF\xA0]+$/g,o=/^-ms-/,p=/-([\da-z])/gi,q=function(a,b){return b.toUpperCase()};m.fn=m.prototype={jquery:l,constructor:m,selector:"",length:0,toArray:function(){return d.call(this)},get:function(a){return null!=a?0>a?this[a+this.length]:this[a]:d.call(this)},pushStack:function(a){var b=m.merge(this.constructor(),a);return b.prevObject=this,b.context=this.context,b},each:function(a,b){return m.each(this,a,b)},map:function(a){return this.pushStack(m.map(this,function(b,c){return a.call(b,c,b)}))},slice:function(){return this.pushStack(d.apply(this,arguments))},first:function(){return this.eq(0)},last:function(){return this.eq(-1)},eq:function(a){var b=this.length,c=+a+(0>a?b:0);return this.pushStack(c>=0&&b>c?[this[c]]:[])},end:function(){return this.prevObject||this.constructor(null)},push:f,sort:c.sort,splice:c.splice},m.extend=m.fn.extend=function(){var a,b,c,d,e,f,g=arguments[0]||{},h=1,i=arguments.length,j=!1;for("boolean"==typeof g&&(j=g,g=arguments[h]||{},h++),"object"==typeof g||m.isFunction(g)||(g={}),h===i&&(g=this,h--);i>h;h++)if(null!=(e=arguments[h]))for(d in e)a=g[d],c=e[d],g!==c&&(j&&c&&(m.isPlainObject(c)||(b=m.isArray(c)))?(b?(b=!1,f=a&&m.isArray(a)?a:[]):f=a&&m.isPlainObject(a)?a:{},g[d]=m.extend(j,f,c)):void 0!==c&&(g[d]=c));return g},m.extend({expando:"jQuery"+(l+Math.random()).replace(/\D/g,""),isReady:!0,error:function(a){throw new Error(a)},noop:function(){},isFunction:function(a){return"function"===m.type(a)},isArray:Array.isArray||function(a){return"array"===m.type(a)},isWindow:function(a){return null!=a&&a==a.window},isNumeric:function(a){return!m.isArray(a)&&a-parseFloat(a)>=0},isEmptyObject:function(a){var b;for(b in a)return!1;return!0},isPlainObject:function(a){var b;if(!a||"object"!==m.type(a)||a.nodeType||m.isWindow(a))return!1;try{if(a.constructor&&!j.call(a,"constructor")&&!j.call(a.constructor.prototype,"isPrototypeOf"))return!1}catch(c){return!1}if(k.ownLast)for(b in a)return j.call(a,b);for(b in a);return void 0===b||j.call(a,b)},type:function(a){return null==a?a+"":"object"==typeof a||"function"==typeof a?h[i.call(a)]||"object":typeof a},globalEval:function(b){b&&m.trim(b)&&(a.execScript||function(b){a.eval.call(a,b)})(b)},camelCase:function(a){return a.replace(o,"ms-").replace(p,q)},nodeName:function(a,b){return a.nodeName&&a.nodeName.toLowerCase()===b.toLowerCase()},each:function(a,b,c){var d,e=0,f=a.length,g=r(a);if(c){if(g){for(;f>e;e++)if(d=b.apply(a[e],c),d===!1)break}else for(e in a)if(d=b.apply(a[e],c),d===!1)break}else if(g){for(;f>e;e++)if(d=b.call(a[e],e,a[e]),d===!1)break}else for(e in a)if(d=b.call(a[e],e,a[e]),d===!1)break;return a},trim:function(a){return null==a?"":(a+"").replace(n,"")},makeArray:function(a,b){var c=b||[];return null!=a&&(r(Object(a))?m.merge(c,"string"==typeof a?[a]:a):f.call(c,a)),c},inArray:function(a,b,c){var d;if(b){if(g)return g.call(b,a,c);for(d=b.length,c=c?0>c?Math.max(0,d+c):c:0;d>c;c++)if(c in b&&b[c]===a)return c}return-1},merge:function(a,b){var c=+b.length,d=0,e=a.length;while(c>d)a[e++]=b[d++];if(c!==c)while(void 0!==b[d])a[e++]=b[d++];return a.length=e,a},grep:function(a,b,c){for(var d,e=[],f=0,g=a.length,h=!c;g>f;f++)d=!b(a[f],f),d!==h&&e.push(a[f]);return e},map:function(a,b,c){var d,f=0,g=a.length,h=r(a),i=[];if(h)for(;g>f;f++)d=b(a[f],f,c),null!=d&&i.push(d);else for(f in a)d=b(a[f],f,c),null!=d&&i.push(d);return e.apply([],i)},guid:1,proxy:function(a,b){var c,e,f;return"string"==typeof b&&(f=a[b],b=a,a=f),m.isFunction(a)?(c=d.call(arguments,2),e=function(){return a.apply(b||this,c.concat(d.call(arguments)))},e.guid=a.guid=a.guid||m.guid++,e):void 0},now:function(){return+new Date},support:k}),m.each("Boolean Number String Function Array Date RegExp Object Error".split(" "),function(a,b){h["[object "+b+"]"]=b.toLowerCase()});function r(a){var b=a.length,c=m.type(a);return"function"===c||m.isWindow(a)?!1:1===a.nodeType&&b?!0:"array"===c||0===b||"number"==typeof b&&b>0&&b-1 in a}var s=function(a){var b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u="sizzle"+-new Date,v=a.document,w=0,x=0,y=gb(),z=gb(),A=gb(),B=function(a,b){return a===b&&(l=!0),0},C="undefined",D=1<<31,E={}.hasOwnProperty,F=[],G=F.pop,H=F.push,I=F.push,J=F.slice,K=F.indexOf||function(a){for(var b=0,c=this.length;c>b;b++)if(this[b]===a)return b;return-1},L="checked|selected|async|autofocus|autoplay|controls|defer|disabled|hidden|ismap|loop|multiple|open|readonly|required|scoped",M="[\\x20\\t\\r\\n\\f]",N="(?:\\\\.|[\\w-]|[^\\x00-\\xa0])+",O=N.replace("w","w#"),P="\\["+M+"*("+N+")(?:"+M+"*([*^$|!~]?=)"+M+"*(?:'((?:\\\\.|[^\\\\'])*)'|\"((?:\\\\.|[^\\\\\"])*)\"|("+O+"))|)"+M+"*\\]",Q=":("+N+")(?:\\((('((?:\\\\.|[^\\\\'])*)'|\"((?:\\\\.|[^\\\\\"])*)\")|((?:\\\\.|[^\\\\()[\\]]|"+P+")*)|.*)\\)|)",R=new RegExp("^"+M+"+|((?:^|[^\\\\])(?:\\\\.)*)"+M+"+$","g"),S=new RegExp("^"+M+"*,"+M+"*"),T=new RegExp("^"+M+"*([>+~]|"+M+")"+M+"*"),U=new RegExp("="+M+"*([^\\]'\"]*?)"+M+"*\\]","g"),V=new RegExp(Q),W=new RegExp("^"+O+"$"),X={ID:new RegExp("^#("+N+")"),CLASS:new RegExp("^\\.("+N+")"),TAG:new RegExp("^("+N.replace("w","w*")+")"),ATTR:new RegExp("^"+P),PSEUDO:new RegExp("^"+Q),CHILD:new RegExp("^:(only|first|last|nth|nth-last)-(child|of-type)(?:\\("+M+"*(even|odd|(([+-]|)(\\d*)n|)"+M+"*(?:([+-]|)"+M+"*(\\d+)|))"+M+"*\\)|)","i"),bool:new RegExp("^(?:"+L+")$","i"),needsContext:new RegExp("^"+M+"*[>+~]|:(even|odd|eq|gt|lt|nth|first|last)(?:\\("+M+"*((?:-\\d)?\\d*)"+M+"*\\)|)(?=[^-]|$)","i")},Y=/^(?:input|select|textarea|button)$/i,Z=/^h\d$/i,$=/^[^{]+\{\s*\[native \w/,_=/^(?:#([\w-]+)|(\w+)|\.([\w-]+))$/,ab=/[+~]/,bb=/'|\\/g,cb=new RegExp("\\\\([\\da-f]{1,6}"+M+"?|("+M+")|.)","ig"),db=function(a,b,c){var d="0x"+b-65536;return d!==d||c?b:0>d?String.fromCharCode(d+65536):String.fromCharCode(d>>10|55296,1023&d|56320)};try{I.apply(F=J.call(v.childNodes),v.childNodes),F[v.childNodes.length].nodeType}catch(eb){I={apply:F.length?function(a,b){H.apply(a,J.call(b))}:function(a,b){var c=a.length,d=0;while(a[c++]=b[d++]);a.length=c-1}}}function fb(a,b,d,e){var f,h,j,k,l,o,r,s,w,x;if((b?b.ownerDocument||b:v)!==n&&m(b),b=b||n,d=d||[],!a||"string"!=typeof a)return d;if(1!==(k=b.nodeType)&&9!==k)return[];if(p&&!e){if(f=_.exec(a))if(j=f[1]){if(9===k){if(h=b.getElementById(j),!h||!h.parentNode)return d;if(h.id===j)return d.push(h),d}else if(b.ownerDocument&&(h=b.ownerDocument.getElementById(j))&&t(b,h)&&h.id===j)return d.push(h),d}else{if(f[2])return I.apply(d,b.getElementsByTagName(a)),d;if((j=f[3])&&c.getElementsByClassName&&b.getElementsByClassName)return I.apply(d,b.getElementsByClassName(j)),d}if(c.qsa&&(!q||!q.test(a))){if(s=r=u,w=b,x=9===k&&a,1===k&&"object"!==b.nodeName.toLowerCase()){o=g(a),(r=b.getAttribute("id"))?s=r.replace(bb,"\\$&"):b.setAttribute("id",s),s="[id='"+s+"'] ",l=o.length;while(l--)o[l]=s+qb(o[l]);w=ab.test(a)&&ob(b.parentNode)||b,x=o.join(",")}if(x)try{return I.apply(d,w.querySelectorAll(x)),d}catch(y){}finally{r||b.removeAttribute("id")}}}return i(a.replace(R,"$1"),b,d,e)}function gb(){var a=[];function b(c,e){return a.push(c+" ")>d.cacheLength&&delete b[a.shift()],b[c+" "]=e}return b}function hb(a){return a[u]=!0,a}function ib(a){var b=n.createElement("div");try{return!!a(b)}catch(c){return!1}finally{b.parentNode&&b.parentNode.removeChild(b),b=null}}function jb(a,b){var c=a.split("|"),e=a.length;while(e--)d.attrHandle[c[e]]=b}function kb(a,b){var c=b&&a,d=c&&1===a.nodeType&&1===b.nodeType&&(~b.sourceIndex||D)-(~a.sourceIndex||D);if(d)return d;if(c)while(c=c.nextSibling)if(c===b)return-1;return a?1:-1}function lb(a){return function(b){var c=b.nodeName.toLowerCase();return"input"===c&&b.type===a}}function mb(a){return function(b){var c=b.nodeName.toLowerCase();return("input"===c||"button"===c)&&b.type===a}}function nb(a){return hb(function(b){return b=+b,hb(function(c,d){var e,f=a([],c.length,b),g=f.length;while(g--)c[e=f[g]]&&(c[e]=!(d[e]=c[e]))})})}function ob(a){return a&&typeof a.getElementsByTagName!==C&&a}c=fb.support={},f=fb.isXML=function(a){var b=a&&(a.ownerDocument||a).documentElement;return b?"HTML"!==b.nodeName:!1},m=fb.setDocument=function(a){var b,e=a?a.ownerDocument||a:v,g=e.defaultView;return e!==n&&9===e.nodeType&&e.documentElement?(n=e,o=e.documentElement,p=!f(e),g&&g!==g.top&&(g.addEventListener?g.addEventListener("unload",function(){m()},!1):g.attachEvent&&g.attachEvent("onunload",function(){m()})),c.attributes=ib(function(a){return a.className="i",!a.getAttribute("className")}),c.getElementsByTagName=ib(function(a){return a.appendChild(e.createComment("")),!a.getElementsByTagName("*").length}),c.getElementsByClassName=$.test(e.getElementsByClassName)&&ib(function(a){return a.innerHTML="<div class='a'></div><div class='a i'></div>",a.firstChild.className="i",2===a.getElementsByClassName("i").length}),c.getById=ib(function(a){return o.appendChild(a).id=u,!e.getElementsByName||!e.getElementsByName(u).length}),c.getById?(d.find.ID=function(a,b){if(typeof b.getElementById!==C&&p){var c=b.getElementById(a);return c&&c.parentNode?[c]:[]}},d.filter.ID=function(a){var b=a.replace(cb,db);return function(a){return a.getAttribute("id")===b}}):(delete d.find.ID,d.filter.ID=function(a){var b=a.replace(cb,db);return function(a){var c=typeof a.getAttributeNode!==C&&a.getAttributeNode("id");return c&&c.value===b}}),d.find.TAG=c.getElementsByTagName?function(a,b){return typeof b.getElementsByTagName!==C?b.getElementsByTagName(a):void 0}:function(a,b){var c,d=[],e=0,f=b.getElementsByTagName(a);if("*"===a){while(c=f[e++])1===c.nodeType&&d.push(c);return d}return f},d.find.CLASS=c.getElementsByClassName&&function(a,b){return typeof b.getElementsByClassName!==C&&p?b.getElementsByClassName(a):void 0},r=[],q=[],(c.qsa=$.test(e.querySelectorAll))&&(ib(function(a){a.innerHTML="<select msallowclip=''><option selected=''></option></select>",a.querySelectorAll("[msallowclip^='']").length&&q.push("[*^$]="+M+"*(?:''|\"\")"),a.querySelectorAll("[selected]").length||q.push("\\["+M+"*(?:value|"+L+")"),a.querySelectorAll(":checked").length||q.push(":checked")}),ib(function(a){var b=e.createElement("input");b.setAttribute("type","hidden"),a.appendChild(b).setAttribute("name","D"),a.querySelectorAll("[name=d]").length&&q.push("name"+M+"*[*^$|!~]?="),a.querySelectorAll(":enabled").length||q.push(":enabled",":disabled"),a.querySelectorAll("*,:x"),q.push(",.*:")})),(c.matchesSelector=$.test(s=o.matches||o.webkitMatchesSelector||o.mozMatchesSelector||o.oMatchesSelector||o.msMatchesSelector))&&ib(function(a){c.disconnectedMatch=s.call(a,"div"),s.call(a,"[s!='']:x"),r.push("!=",Q)}),q=q.length&&new RegExp(q.join("|")),r=r.length&&new RegExp(r.join("|")),b=$.test(o.compareDocumentPosition),t=b||$.test(o.contains)?function(a,b){var c=9===a.nodeType?a.documentElement:a,d=b&&b.parentNode;return a===d||!(!d||1!==d.nodeType||!(c.contains?c.contains(d):a.compareDocumentPosition&&16&a.compareDocumentPosition(d)))}:function(a,b){if(b)while(b=b.parentNode)if(b===a)return!0;return!1},B=b?function(a,b){if(a===b)return l=!0,0;var d=!a.compareDocumentPosition-!b.compareDocumentPosition;return d?d:(d=(a.ownerDocument||a)===(b.ownerDocument||b)?a.compareDocumentPosition(b):1,1&d||!c.sortDetached&&b.compareDocumentPosition(a)===d?a===e||a.ownerDocument===v&&t(v,a)?-1:b===e||b.ownerDocument===v&&t(v,b)?1:k?K.call(k,a)-K.call(k,b):0:4&d?-1:1)}:function(a,b){if(a===b)return l=!0,0;var c,d=0,f=a.parentNode,g=b.parentNode,h=[a],i=[b];if(!f||!g)return a===e?-1:b===e?1:f?-1:g?1:k?K.call(k,a)-K.call(k,b):0;if(f===g)return kb(a,b);c=a;while(c=c.parentNode)h.unshift(c);c=b;while(c=c.parentNode)i.unshift(c);while(h[d]===i[d])d++;return d?kb(h[d],i[d]):h[d]===v?-1:i[d]===v?1:0},e):n},fb.matches=function(a,b){return fb(a,null,null,b)},fb.matchesSelector=function(a,b){if((a.ownerDocument||a)!==n&&m(a),b=b.replace(U,"='$1']"),!(!c.matchesSelector||!p||r&&r.test(b)||q&&q.test(b)))try{var d=s.call(a,b);if(d||c.disconnectedMatch||a.document&&11!==a.document.nodeType)return d}catch(e){}return fb(b,n,null,[a]).length>0},fb.contains=function(a,b){return(a.ownerDocument||a)!==n&&m(a),t(a,b)},fb.attr=function(a,b){(a.ownerDocument||a)!==n&&m(a);var e=d.attrHandle[b.toLowerCase()],f=e&&E.call(d.attrHandle,b.toLowerCase())?e(a,b,!p):void 0;return void 0!==f?f:c.attributes||!p?a.getAttribute(b):(f=a.getAttributeNode(b))&&f.specified?f.value:null},fb.error=function(a){throw new Error("Syntax error, unrecognized expression: "+a)},fb.uniqueSort=function(a){var b,d=[],e=0,f=0;if(l=!c.detectDuplicates,k=!c.sortStable&&a.slice(0),a.sort(B),l){while(b=a[f++])b===a[f]&&(e=d.push(f));while(e--)a.splice(d[e],1)}return k=null,a},e=fb.getText=function(a){var b,c="",d=0,f=a.nodeType;if(f){if(1===f||9===f||11===f){if("string"==typeof a.textContent)return a.textContent;for(a=a.firstChild;a;a=a.nextSibling)c+=e(a)}else if(3===f||4===f)return a.nodeValue}else while(b=a[d++])c+=e(b);return c},d=fb.selectors={cacheLength:50,createPseudo:hb,match:X,attrHandle:{},find:{},relative:{">":{dir:"parentNode",first:!0}," ":{dir:"parentNode"},"+":{dir:"previousSibling",first:!0},"~":{dir:"previousSibling"}},preFilter:{ATTR:function(a){return a[1]=a[1].replace(cb,db),a[3]=(a[3]||a[4]||a[5]||"").replace(cb,db),"~="===a[2]&&(a[3]=" "+a[3]+" "),a.slice(0,4)},CHILD:function(a){return a[1]=a[1].toLowerCase(),"nth"===a[1].slice(0,3)?(a[3]||fb.error(a[0]),a[4]=+(a[4]?a[5]+(a[6]||1):2*("even"===a[3]||"odd"===a[3])),a[5]=+(a[7]+a[8]||"odd"===a[3])):a[3]&&fb.error(a[0]),a},PSEUDO:function(a){var b,c=!a[6]&&a[2];return X.CHILD.test(a[0])?null:(a[3]?a[2]=a[4]||a[5]||"":c&&V.test(c)&&(b=g(c,!0))&&(b=c.indexOf(")",c.length-b)-c.length)&&(a[0]=a[0].slice(0,b),a[2]=c.slice(0,b)),a.slice(0,3))}},filter:{TAG:function(a){var b=a.replace(cb,db).toLowerCase();return"*"===a?function(){return!0}:function(a){return a.nodeName&&a.nodeName.toLowerCase()===b}},CLASS:function(a){var b=y[a+" "];return b||(b=new RegExp("(^|"+M+")"+a+"("+M+"|$)"))&&y(a,function(a){return b.test("string"==typeof a.className&&a.className||typeof a.getAttribute!==C&&a.getAttribute("class")||"")})},ATTR:function(a,b,c){return function(d){var e=fb.attr(d,a);return null==e?"!="===b:b?(e+="","="===b?e===c:"!="===b?e!==c:"^="===b?c&&0===e.indexOf(c):"*="===b?c&&e.indexOf(c)>-1:"$="===b?c&&e.slice(-c.length)===c:"~="===b?(" "+e+" ").indexOf(c)>-1:"|="===b?e===c||e.slice(0,c.length+1)===c+"-":!1):!0}},CHILD:function(a,b,c,d,e){var f="nth"!==a.slice(0,3),g="last"!==a.slice(-4),h="of-type"===b;return 1===d&&0===e?function(a){return!!a.parentNode}:function(b,c,i){var j,k,l,m,n,o,p=f!==g?"nextSibling":"previousSibling",q=b.parentNode,r=h&&b.nodeName.toLowerCase(),s=!i&&!h;if(q){if(f){while(p){l=b;while(l=l[p])if(h?l.nodeName.toLowerCase()===r:1===l.nodeType)return!1;o=p="only"===a&&!o&&"nextSibling"}return!0}if(o=[g?q.firstChild:q.lastChild],g&&s){k=q[u]||(q[u]={}),j=k[a]||[],n=j[0]===w&&j[1],m=j[0]===w&&j[2],l=n&&q.childNodes[n];while(l=++n&&l&&l[p]||(m=n=0)||o.pop())if(1===l.nodeType&&++m&&l===b){k[a]=[w,n,m];break}}else if(s&&(j=(b[u]||(b[u]={}))[a])&&j[0]===w)m=j[1];else while(l=++n&&l&&l[p]||(m=n=0)||o.pop())if((h?l.nodeName.toLowerCase()===r:1===l.nodeType)&&++m&&(s&&((l[u]||(l[u]={}))[a]=[w,m]),l===b))break;return m-=e,m===d||m%d===0&&m/d>=0}}},PSEUDO:function(a,b){var c,e=d.pseudos[a]||d.setFilters[a.toLowerCase()]||fb.error("unsupported pseudo: "+a);return e[u]?e(b):e.length>1?(c=[a,a,"",b],d.setFilters.hasOwnProperty(a.toLowerCase())?hb(function(a,c){var d,f=e(a,b),g=f.length;while(g--)d=K.call(a,f[g]),a[d]=!(c[d]=f[g])}):function(a){return e(a,0,c)}):e}},pseudos:{not:hb(function(a){var b=[],c=[],d=h(a.replace(R,"$1"));return d[u]?hb(function(a,b,c,e){var f,g=d(a,null,e,[]),h=a.length;while(h--)(f=g[h])&&(a[h]=!(b[h]=f))}):function(a,e,f){return b[0]=a,d(b,null,f,c),!c.pop()}}),has:hb(function(a){return function(b){return fb(a,b).length>0}}),contains:hb(function(a){return function(b){return(b.textContent||b.innerText||e(b)).indexOf(a)>-1}}),lang:hb(function(a){return W.test(a||"")||fb.error("unsupported lang: "+a),a=a.replace(cb,db).toLowerCase(),function(b){var c;do if(c=p?b.lang:b.getAttribute("xml:lang")||b.getAttribute("lang"))return c=c.toLowerCase(),c===a||0===c.indexOf(a+"-");while((b=b.parentNode)&&1===b.nodeType);return!1}}),target:function(b){var c=a.location&&a.location.hash;return c&&c.slice(1)===b.id},root:function(a){return a===o},focus:function(a){return a===n.activeElement&&(!n.hasFocus||n.hasFocus())&&!!(a.type||a.href||~a.tabIndex)},enabled:function(a){return a.disabled===!1},disabled:function(a){return a.disabled===!0},checked:function(a){var b=a.nodeName.toLowerCase();return"input"===b&&!!a.checked||"option"===b&&!!a.selected},selected:function(a){return a.parentNode&&a.parentNode.selectedIndex,a.selected===!0},empty:function(a){for(a=a.firstChild;a;a=a.nextSibling)if(a.nodeType<6)return!1;return!0},parent:function(a){return!d.pseudos.empty(a)},header:function(a){return Z.test(a.nodeName)},input:function(a){return Y.test(a.nodeName)},button:function(a){var b=a.nodeName.toLowerCase();return"input"===b&&"button"===a.type||"button"===b},text:function(a){var b;return"input"===a.nodeName.toLowerCase()&&"text"===a.type&&(null==(b=a.getAttribute("type"))||"text"===b.toLowerCase())},first:nb(function(){return[0]}),last:nb(function(a,b){return[b-1]}),eq:nb(function(a,b,c){return[0>c?c+b:c]}),even:nb(function(a,b){for(var c=0;b>c;c+=2)a.push(c);return a}),odd:nb(function(a,b){for(var c=1;b>c;c+=2)a.push(c);return a}),lt:nb(function(a,b,c){for(var d=0>c?c+b:c;--d>=0;)a.push(d);return a}),gt:nb(function(a,b,c){for(var d=0>c?c+b:c;++d<b;)a.push(d);return a})}},d.pseudos.nth=d.pseudos.eq;for(b in{radio:!0,checkbox:!0,file:!0,password:!0,image:!0})d.pseudos[b]=lb(b);for(b in{submit:!0,reset:!0})d.pseudos[b]=mb(b);function pb(){}pb.prototype=d.filters=d.pseudos,d.setFilters=new pb,g=fb.tokenize=function(a,b){var c,e,f,g,h,i,j,k=z[a+" "];if(k)return b?0:k.slice(0);h=a,i=[],j=d.preFilter;while(h){(!c||(e=S.exec(h)))&&(e&&(h=h.slice(e[0].length)||h),i.push(f=[])),c=!1,(e=T.exec(h))&&(c=e.shift(),f.push({value:c,type:e[0].replace(R," ")}),h=h.slice(c.length));for(g in d.filter)!(e=X[g].exec(h))||j[g]&&!(e=j[g](e))||(c=e.shift(),f.push({value:c,type:g,matches:e}),h=h.slice(c.length));if(!c)break}return b?h.length:h?fb.error(a):z(a,i).slice(0)};function qb(a){for(var b=0,c=a.length,d="";c>b;b++)d+=a[b].value;return d}function rb(a,b,c){var d=b.dir,e=c&&"parentNode"===d,f=x++;return b.first?function(b,c,f){while(b=b[d])if(1===b.nodeType||e)return a(b,c,f)}:function(b,c,g){var h,i,j=[w,f];if(g){while(b=b[d])if((1===b.nodeType||e)&&a(b,c,g))return!0}else while(b=b[d])if(1===b.nodeType||e){if(i=b[u]||(b[u]={}),(h=i[d])&&h[0]===w&&h[1]===f)return j[2]=h[2];if(i[d]=j,j[2]=a(b,c,g))return!0}}}function sb(a){return a.length>1?function(b,c,d){var e=a.length;while(e--)if(!a[e](b,c,d))return!1;return!0}:a[0]}function tb(a,b,c){for(var d=0,e=b.length;e>d;d++)fb(a,b[d],c);return c}function ub(a,b,c,d,e){for(var f,g=[],h=0,i=a.length,j=null!=b;i>h;h++)(f=a[h])&&(!c||c(f,d,e))&&(g.push(f),j&&b.push(h));return g}function vb(a,b,c,d,e,f){return d&&!d[u]&&(d=vb(d)),e&&!e[u]&&(e=vb(e,f)),hb(function(f,g,h,i){var j,k,l,m=[],n=[],o=g.length,p=f||tb(b||"*",h.nodeType?[h]:h,[]),q=!a||!f&&b?p:ub(p,m,a,h,i),r=c?e||(f?a:o||d)?[]:g:q;if(c&&c(q,r,h,i),d){j=ub(r,n),d(j,[],h,i),k=j.length;while(k--)(l=j[k])&&(r[n[k]]=!(q[n[k]]=l))}if(f){if(e||a){if(e){j=[],k=r.length;while(k--)(l=r[k])&&j.push(q[k]=l);e(null,r=[],j,i)}k=r.length;while(k--)(l=r[k])&&(j=e?K.call(f,l):m[k])>-1&&(f[j]=!(g[j]=l))}}else r=ub(r===g?r.splice(o,r.length):r),e?e(null,g,r,i):I.apply(g,r)})}function wb(a){for(var b,c,e,f=a.length,g=d.relative[a[0].type],h=g||d.relative[" "],i=g?1:0,k=rb(function(a){return a===b},h,!0),l=rb(function(a){return K.call(b,a)>-1},h,!0),m=[function(a,c,d){return!g&&(d||c!==j)||((b=c).nodeType?k(a,c,d):l(a,c,d))}];f>i;i++)if(c=d.relative[a[i].type])m=[rb(sb(m),c)];else{if(c=d.filter[a[i].type].apply(null,a[i].matches),c[u]){for(e=++i;f>e;e++)if(d.relative[a[e].type])break;return vb(i>1&&sb(m),i>1&&qb(a.slice(0,i-1).concat({value:" "===a[i-2].type?"*":""})).replace(R,"$1"),c,e>i&&wb(a.slice(i,e)),f>e&&wb(a=a.slice(e)),f>e&&qb(a))}m.push(c)}return sb(m)}function xb(a,b){var c=b.length>0,e=a.length>0,f=function(f,g,h,i,k){var l,m,o,p=0,q="0",r=f&&[],s=[],t=j,u=f||e&&d.find.TAG("*",k),v=w+=null==t?1:Math.random()||.1,x=u.length;for(k&&(j=g!==n&&g);q!==x&&null!=(l=u[q]);q++){if(e&&l){m=0;while(o=a[m++])if(o(l,g,h)){i.push(l);break}k&&(w=v)}c&&((l=!o&&l)&&p--,f&&r.push(l))}if(p+=q,c&&q!==p){m=0;while(o=b[m++])o(r,s,g,h);if(f){if(p>0)while(q--)r[q]||s[q]||(s[q]=G.call(i));s=ub(s)}I.apply(i,s),k&&!f&&s.length>0&&p+b.length>1&&fb.uniqueSort(i)}return k&&(w=v,j=t),r};return c?hb(f):f}return h=fb.compile=function(a,b){var c,d=[],e=[],f=A[a+" "];if(!f){b||(b=g(a)),c=b.length;while(c--)f=wb(b[c]),f[u]?d.push(f):e.push(f);f=A(a,xb(e,d)),f.selector=a}return f},i=fb.select=function(a,b,e,f){var i,j,k,l,m,n="function"==typeof a&&a,o=!f&&g(a=n.selector||a);if(e=e||[],1===o.length){if(j=o[0]=o[0].slice(0),j.length>2&&"ID"===(k=j[0]).type&&c.getById&&9===b.nodeType&&p&&d.relative[j[1].type]){if(b=(d.find.ID(k.matches[0].replace(cb,db),b)||[])[0],!b)return e;n&&(b=b.parentNode),a=a.slice(j.shift().value.length)}i=X.needsContext.test(a)?0:j.length;while(i--){if(k=j[i],d.relative[l=k.type])break;if((m=d.find[l])&&(f=m(k.matches[0].replace(cb,db),ab.test(j[0].type)&&ob(b.parentNode)||b))){if(j.splice(i,1),a=f.length&&qb(j),!a)return I.apply(e,f),e;break}}}return(n||h(a,o))(f,b,!p,e,ab.test(a)&&ob(b.parentNode)||b),e},c.sortStable=u.split("").sort(B).join("")===u,c.detectDuplicates=!!l,m(),c.sortDetached=ib(function(a){return 1&a.compareDocumentPosition(n.createElement("div"))}),ib(function(a){return a.innerHTML="<a href='#'></a>","#"===a.firstChild.getAttribute("href")})||jb("type|href|height|width",function(a,b,c){return c?void 0:a.getAttribute(b,"type"===b.toLowerCase()?1:2)}),c.attributes&&ib(function(a){return a.innerHTML="<input/>",a.firstChild.setAttribute("value",""),""===a.firstChild.getAttribute("value")})||jb("value",function(a,b,c){return c||"input"!==a.nodeName.toLowerCase()?void 0:a.defaultValue}),ib(function(a){return null==a.getAttribute("disabled")})||jb(L,function(a,b,c){var d;return c?void 0:a[b]===!0?b.toLowerCase():(d=a.getAttributeNode(b))&&d.specified?d.value:null}),fb}(a);m.find=s,m.expr=s.selectors,m.expr[":"]=m.expr.pseudos,m.unique=s.uniqueSort,m.text=s.getText,m.isXMLDoc=s.isXML,m.contains=s.contains;var t=m.expr.match.needsContext,u=/^<(\w+)\s*\/?>(?:<\/\1>|)$/,v=/^.[^:#\[\.,]*$/;function w(a,b,c){if(m.isFunction(b))return m.grep(a,function(a,d){return!!b.call(a,d,a)!==c});if(b.nodeType)return m.grep(a,function(a){return a===b!==c});if("string"==typeof b){if(v.test(b))return m.filter(b,a,c);b=m.filter(b,a)}return m.grep(a,function(a){return m.inArray(a,b)>=0!==c})}m.filter=function(a,b,c){var d=b[0];return c&&(a=":not("+a+")"),1===b.length&&1===d.nodeType?m.find.matchesSelector(d,a)?[d]:[]:m.find.matches(a,m.grep(b,function(a){return 1===a.nodeType}))},m.fn.extend({find:function(a){var b,c=[],d=this,e=d.length;if("string"!=typeof a)return this.pushStack(m(a).filter(function(){for(b=0;e>b;b++)if(m.contains(d[b],this))return!0}));for(b=0;e>b;b++)m.find(a,d[b],c);return c=this.pushStack(e>1?m.unique(c):c),c.selector=this.selector?this.selector+" "+a:a,c},filter:function(a){return this.pushStack(w(this,a||[],!1))},not:function(a){return this.pushStack(w(this,a||[],!0))},is:function(a){return!!w(this,"string"==typeof a&&t.test(a)?m(a):a||[],!1).length}});var x,y=a.document,z=/^(?:\s*(<[\w\W]+>)[^>]*|#([\w-]*))$/,A=m.fn.init=function(a,b){var c,d;if(!a)return this;if("string"==typeof a){if(c="<"===a.charAt(0)&&">"===a.charAt(a.length-1)&&a.length>=3?[null,a,null]:z.exec(a),!c||!c[1]&&b)return!b||b.jquery?(b||x).find(a):this.constructor(b).find(a);if(c[1]){if(b=b instanceof m?b[0]:b,m.merge(this,m.parseHTML(c[1],b&&b.nodeType?b.ownerDocument||b:y,!0)),u.test(c[1])&&m.isPlainObject(b))for(c in b)m.isFunction(this[c])?this[c](b[c]):this.attr(c,b[c]);return this}if(d=y.getElementById(c[2]),d&&d.parentNode){if(d.id!==c[2])return x.find(a);this.length=1,this[0]=d}return this.context=y,this.selector=a,this}return a.nodeType?(this.context=this[0]=a,this.length=1,this):m.isFunction(a)?"undefined"!=typeof x.ready?x.ready(a):a(m):(void 0!==a.selector&&(this.selector=a.selector,this.context=a.context),m.makeArray(a,this))};A.prototype=m.fn,x=m(y);var B=/^(?:parents|prev(?:Until|All))/,C={children:!0,contents:!0,next:!0,prev:!0};m.extend({dir:function(a,b,c){var d=[],e=a[b];while(e&&9!==e.nodeType&&(void 0===c||1!==e.nodeType||!m(e).is(c)))1===e.nodeType&&d.push(e),e=e[b];return d},sibling:function(a,b){for(var c=[];a;a=a.nextSibling)1===a.nodeType&&a!==b&&c.push(a);return c}}),m.fn.extend({has:function(a){var b,c=m(a,this),d=c.length;return this.filter(function(){for(b=0;d>b;b++)if(m.contains(this,c[b]))return!0})},closest:function(a,b){for(var c,d=0,e=this.length,f=[],g=t.test(a)||"string"!=typeof a?m(a,b||this.context):0;e>d;d++)for(c=this[d];c&&c!==b;c=c.parentNode)if(c.nodeType<11&&(g?g.index(c)>-1:1===c.nodeType&&m.find.matchesSelector(c,a))){f.push(c);break}return this.pushStack(f.length>1?m.unique(f):f)},index:function(a){return a?"string"==typeof a?m.inArray(this[0],m(a)):m.inArray(a.jquery?a[0]:a,this):this[0]&&this[0].parentNode?this.first().prevAll().length:-1},add:function(a,b){return this.pushStack(m.unique(m.merge(this.get(),m(a,b))))},addBack:function(a){return this.add(null==a?this.prevObject:this.prevObject.filter(a))}});function D(a,b){do a=a[b];while(a&&1!==a.nodeType);return a}m.each({parent:function(a){var b=a.parentNode;return b&&11!==b.nodeType?b:null},parents:function(a){return m.dir(a,"parentNode")},parentsUntil:function(a,b,c){return m.dir(a,"parentNode",c)},next:function(a){return D(a,"nextSibling")},prev:function(a){return D(a,"previousSibling")},nextAll:function(a){return m.dir(a,"nextSibling")},prevAll:function(a){return m.dir(a,"previousSibling")},nextUntil:function(a,b,c){return m.dir(a,"nextSibling",c)},prevUntil:function(a,b,c){return m.dir(a,"previousSibling",c)},siblings:function(a){return m.sibling((a.parentNode||{}).firstChild,a)},children:function(a){return m.sibling(a.firstChild)},contents:function(a){return m.nodeName(a,"iframe")?a.contentDocument||a.contentWindow.document:m.merge([],a.childNodes)}},function(a,b){m.fn[a]=function(c,d){var e=m.map(this,b,c);return"Until"!==a.slice(-5)&&(d=c),d&&"string"==typeof d&&(e=m.filter(d,e)),this.length>1&&(C[a]||(e=m.unique(e)),B.test(a)&&(e=e.reverse())),this.pushStack(e)}});var E=/\S+/g,F={};function G(a){var b=F[a]={};return m.each(a.match(E)||[],function(a,c){b[c]=!0}),b}m.Callbacks=function(a){a="string"==typeof a?F[a]||G(a):m.extend({},a);var b,c,d,e,f,g,h=[],i=!a.once&&[],j=function(l){for(c=a.memory&&l,d=!0,f=g||0,g=0,e=h.length,b=!0;h&&e>f;f++)if(h[f].apply(l[0],l[1])===!1&&a.stopOnFalse){c=!1;break}b=!1,h&&(i?i.length&&j(i.shift()):c?h=[]:k.disable())},k={add:function(){if(h){var d=h.length;!function f(b){m.each(b,function(b,c){var d=m.type(c);"function"===d?a.unique&&k.has(c)||h.push(c):c&&c.length&&"string"!==d&&f(c)})}(arguments),b?e=h.length:c&&(g=d,j(c))}return this},remove:function(){return h&&m.each(arguments,function(a,c){var d;while((d=m.inArray(c,h,d))>-1)h.splice(d,1),b&&(e>=d&&e--,f>=d&&f--)}),this},has:function(a){return a?m.inArray(a,h)>-1:!(!h||!h.length)},empty:function(){return h=[],e=0,this},disable:function(){return h=i=c=void 0,this},disabled:function(){return!h},lock:function(){return i=void 0,c||k.disable(),this},locked:function(){return!i},fireWith:function(a,c){return!h||d&&!i||(c=c||[],c=[a,c.slice?c.slice():c],b?i.push(c):j(c)),this},fire:function(){return k.fireWith(this,arguments),this},fired:function(){return!!d}};return k},m.extend({Deferred:function(a){var b=[["resolve","done",m.Callbacks("once memory"),"resolved"],["reject","fail",m.Callbacks("once memory"),"rejected"],["notify","progress",m.Callbacks("memory")]],c="pending",d={state:function(){return c},always:function(){return e.done(arguments).fail(arguments),this},then:function(){var a=arguments;return m.Deferred(function(c){m.each(b,function(b,f){var g=m.isFunction(a[b])&&a[b];e[f[1]](function(){var a=g&&g.apply(this,arguments);a&&m.isFunction(a.promise)?a.promise().done(c.resolve).fail(c.reject).progress(c.notify):c[f[0]+"With"](this===d?c.promise():this,g?[a]:arguments)})}),a=null}).promise()},promise:function(a){return null!=a?m.extend(a,d):d}},e={};return d.pipe=d.then,m.each(b,function(a,f){var g=f[2],h=f[3];d[f[1]]=g.add,h&&g.add(function(){c=h},b[1^a][2].disable,b[2][2].lock),e[f[0]]=function(){return e[f[0]+"With"](this===e?d:this,arguments),this},e[f[0]+"With"]=g.fireWith}),d.promise(e),a&&a.call(e,e),e},when:function(a){var b=0,c=d.call(arguments),e=c.length,f=1!==e||a&&m.isFunction(a.promise)?e:0,g=1===f?a:m.Deferred(),h=function(a,b,c){return function(e){b[a]=this,c[a]=arguments.length>1?d.call(arguments):e,c===i?g.notifyWith(b,c):--f||g.resolveWith(b,c)}},i,j,k;if(e>1)for(i=new Array(e),j=new Array(e),k=new Array(e);e>b;b++)c[b]&&m.isFunction(c[b].promise)?c[b].promise().done(h(b,k,c)).fail(g.reject).progress(h(b,j,i)):--f;return f||g.resolveWith(k,c),g.promise()}});var H;m.fn.ready=function(a){return m.ready.promise().done(a),this},m.extend({isReady:!1,readyWait:1,holdReady:function(a){a?m.readyWait++:m.ready(!0)},ready:function(a){if(a===!0?!--m.readyWait:!m.isReady){if(!y.body)return setTimeout(m.ready);m.isReady=!0,a!==!0&&--m.readyWait>0||(H.resolveWith(y,[m]),m.fn.triggerHandler&&(m(y).triggerHandler("ready"),m(y).off("ready")))}}});function I(){y.addEventListener?(y.removeEventListener("DOMContentLoaded",J,!1),a.removeEventListener("load",J,!1)):(y.detachEvent("onreadystatechange",J),a.detachEvent("onload",J))}function J(){(y.addEventListener||"load"===event.type||"complete"===y.readyState)&&(I(),m.ready())}m.ready.promise=function(b){if(!H)if(H=m.Deferred(),"complete"===y.readyState)setTimeout(m.ready);else if(y.addEventListener)y.addEventListener("DOMContentLoaded",J,!1),a.addEventListener("load",J,!1);else{y.attachEvent("onreadystatechange",J),a.attachEvent("onload",J);var c=!1;try{c=null==a.frameElement&&y.documentElement}catch(d){}c&&c.doScroll&&!function e(){if(!m.isReady){try{c.doScroll("left")}catch(a){return setTimeout(e,50)}I(),m.ready()}}()}return H.promise(b)};var K="undefined",L;for(L in m(k))break;k.ownLast="0"!==L,k.inlineBlockNeedsLayout=!1,m(function(){var a,b,c,d;c=y.getElementsByTagName("body")[0],c&&c.style&&(b=y.createElement("div"),d=y.createElement("div"),d.style.cssText="position:absolute;border:0;width:0;height:0;top:0;left:-9999px",c.appendChild(d).appendChild(b),typeof b.style.zoom!==K&&(b.style.cssText="display:inline;margin:0;border:0;padding:1px;width:1px;zoom:1",k.inlineBlockNeedsLayout=a=3===b.offsetWidth,a&&(c.style.zoom=1)),c.removeChild(d))}),function(){var a=y.createElement("div");if(null==k.deleteExpando){k.deleteExpando=!0;try{delete a.test}catch(b){k.deleteExpando=!1}}a=null}(),m.acceptData=function(a){var b=m.noData[(a.nodeName+" ").toLowerCase()],c=+a.nodeType||1;return 1!==c&&9!==c?!1:!b||b!==!0&&a.getAttribute("classid")===b};var M=/^(?:\{[\w\W]*\}|\[[\w\W]*\])$/,N=/([A-Z])/g;function O(a,b,c){if(void 0===c&&1===a.nodeType){var d="data-"+b.replace(N,"-$1").toLowerCase();if(c=a.getAttribute(d),"string"==typeof c){try{c="true"===c?!0:"false"===c?!1:"null"===c?null:+c+""===c?+c:M.test(c)?m.parseJSON(c):c}catch(e){}m.data(a,b,c)}else c=void 0}return c}function P(a){var b;for(b in a)if(("data"!==b||!m.isEmptyObject(a[b]))&&"toJSON"!==b)return!1;return!0}function Q(a,b,d,e){if(m.acceptData(a)){var f,g,h=m.expando,i=a.nodeType,j=i?m.cache:a,k=i?a[h]:a[h]&&h;
if(k&&j[k]&&(e||j[k].data)||void 0!==d||"string"!=typeof b)return k||(k=i?a[h]=c.pop()||m.guid++:h),j[k]||(j[k]=i?{}:{toJSON:m.noop}),("object"==typeof b||"function"==typeof b)&&(e?j[k]=m.extend(j[k],b):j[k].data=m.extend(j[k].data,b)),g=j[k],e||(g.data||(g.data={}),g=g.data),void 0!==d&&(g[m.camelCase(b)]=d),"string"==typeof b?(f=g[b],null==f&&(f=g[m.camelCase(b)])):f=g,f}}function R(a,b,c){if(m.acceptData(a)){var d,e,f=a.nodeType,g=f?m.cache:a,h=f?a[m.expando]:m.expando;if(g[h]){if(b&&(d=c?g[h]:g[h].data)){m.isArray(b)?b=b.concat(m.map(b,m.camelCase)):b in d?b=[b]:(b=m.camelCase(b),b=b in d?[b]:b.split(" ")),e=b.length;while(e--)delete d[b[e]];if(c?!P(d):!m.isEmptyObject(d))return}(c||(delete g[h].data,P(g[h])))&&(f?m.cleanData([a],!0):k.deleteExpando||g!=g.window?delete g[h]:g[h]=null)}}}m.extend({cache:{},noData:{"applet ":!0,"embed ":!0,"object ":"clsid:D27CDB6E-AE6D-11cf-96B8-444553540000"},hasData:function(a){return a=a.nodeType?m.cache[a[m.expando]]:a[m.expando],!!a&&!P(a)},data:function(a,b,c){return Q(a,b,c)},removeData:function(a,b){return R(a,b)},_data:function(a,b,c){return Q(a,b,c,!0)},_removeData:function(a,b){return R(a,b,!0)}}),m.fn.extend({data:function(a,b){var c,d,e,f=this[0],g=f&&f.attributes;if(void 0===a){if(this.length&&(e=m.data(f),1===f.nodeType&&!m._data(f,"parsedAttrs"))){c=g.length;while(c--)g[c]&&(d=g[c].name,0===d.indexOf("data-")&&(d=m.camelCase(d.slice(5)),O(f,d,e[d])));m._data(f,"parsedAttrs",!0)}return e}return"object"==typeof a?this.each(function(){m.data(this,a)}):arguments.length>1?this.each(function(){m.data(this,a,b)}):f?O(f,a,m.data(f,a)):void 0},removeData:function(a){return this.each(function(){m.removeData(this,a)})}}),m.extend({queue:function(a,b,c){var d;return a?(b=(b||"fx")+"queue",d=m._data(a,b),c&&(!d||m.isArray(c)?d=m._data(a,b,m.makeArray(c)):d.push(c)),d||[]):void 0},dequeue:function(a,b){b=b||"fx";var c=m.queue(a,b),d=c.length,e=c.shift(),f=m._queueHooks(a,b),g=function(){m.dequeue(a,b)};"inprogress"===e&&(e=c.shift(),d--),e&&("fx"===b&&c.unshift("inprogress"),delete f.stop,e.call(a,g,f)),!d&&f&&f.empty.fire()},_queueHooks:function(a,b){var c=b+"queueHooks";return m._data(a,c)||m._data(a,c,{empty:m.Callbacks("once memory").add(function(){m._removeData(a,b+"queue"),m._removeData(a,c)})})}}),m.fn.extend({queue:function(a,b){var c=2;return"string"!=typeof a&&(b=a,a="fx",c--),arguments.length<c?m.queue(this[0],a):void 0===b?this:this.each(function(){var c=m.queue(this,a,b);m._queueHooks(this,a),"fx"===a&&"inprogress"!==c[0]&&m.dequeue(this,a)})},dequeue:function(a){return this.each(function(){m.dequeue(this,a)})},clearQueue:function(a){return this.queue(a||"fx",[])},promise:function(a,b){var c,d=1,e=m.Deferred(),f=this,g=this.length,h=function(){--d||e.resolveWith(f,[f])};"string"!=typeof a&&(b=a,a=void 0),a=a||"fx";while(g--)c=m._data(f[g],a+"queueHooks"),c&&c.empty&&(d++,c.empty.add(h));return h(),e.promise(b)}});var S=/[+-]?(?:\d*\.|)\d+(?:[eE][+-]?\d+|)/.source,T=["Top","Right","Bottom","Left"],U=function(a,b){return a=b||a,"none"===m.css(a,"display")||!m.contains(a.ownerDocument,a)},V=m.access=function(a,b,c,d,e,f,g){var h=0,i=a.length,j=null==c;if("object"===m.type(c)){e=!0;for(h in c)m.access(a,b,h,c[h],!0,f,g)}else if(void 0!==d&&(e=!0,m.isFunction(d)||(g=!0),j&&(g?(b.call(a,d),b=null):(j=b,b=function(a,b,c){return j.call(m(a),c)})),b))for(;i>h;h++)b(a[h],c,g?d:d.call(a[h],h,b(a[h],c)));return e?a:j?b.call(a):i?b(a[0],c):f},W=/^(?:checkbox|radio)$/i;!function(){var a=y.createElement("input"),b=y.createElement("div"),c=y.createDocumentFragment();if(b.innerHTML="  <link/><table></table><a href='/a'>a</a><input type='checkbox'/>",k.leadingWhitespace=3===b.firstChild.nodeType,k.tbody=!b.getElementsByTagName("tbody").length,k.htmlSerialize=!!b.getElementsByTagName("link").length,k.html5Clone="<:nav></:nav>"!==y.createElement("nav").cloneNode(!0).outerHTML,a.type="checkbox",a.checked=!0,c.appendChild(a),k.appendChecked=a.checked,b.innerHTML="<textarea>x</textarea>",k.noCloneChecked=!!b.cloneNode(!0).lastChild.defaultValue,c.appendChild(b),b.innerHTML="<input type='radio' checked='checked' name='t'/>",k.checkClone=b.cloneNode(!0).cloneNode(!0).lastChild.checked,k.noCloneEvent=!0,b.attachEvent&&(b.attachEvent("onclick",function(){k.noCloneEvent=!1}),b.cloneNode(!0).click()),null==k.deleteExpando){k.deleteExpando=!0;try{delete b.test}catch(d){k.deleteExpando=!1}}}(),function(){var b,c,d=y.createElement("div");for(b in{submit:!0,change:!0,focusin:!0})c="on"+b,(k[b+"Bubbles"]=c in a)||(d.setAttribute(c,"t"),k[b+"Bubbles"]=d.attributes[c].expando===!1);d=null}();var X=/^(?:input|select|textarea)$/i,Y=/^key/,Z=/^(?:mouse|pointer|contextmenu)|click/,$=/^(?:focusinfocus|focusoutblur)$/,_=/^([^.]*)(?:\.(.+)|)$/;function ab(){return!0}function bb(){return!1}function cb(){try{return y.activeElement}catch(a){}}m.event={global:{},add:function(a,b,c,d,e){var f,g,h,i,j,k,l,n,o,p,q,r=m._data(a);if(r){c.handler&&(i=c,c=i.handler,e=i.selector),c.guid||(c.guid=m.guid++),(g=r.events)||(g=r.events={}),(k=r.handle)||(k=r.handle=function(a){return typeof m===K||a&&m.event.triggered===a.type?void 0:m.event.dispatch.apply(k.elem,arguments)},k.elem=a),b=(b||"").match(E)||[""],h=b.length;while(h--)f=_.exec(b[h])||[],o=q=f[1],p=(f[2]||"").split(".").sort(),o&&(j=m.event.special[o]||{},o=(e?j.delegateType:j.bindType)||o,j=m.event.special[o]||{},l=m.extend({type:o,origType:q,data:d,handler:c,guid:c.guid,selector:e,needsContext:e&&m.expr.match.needsContext.test(e),namespace:p.join(".")},i),(n=g[o])||(n=g[o]=[],n.delegateCount=0,j.setup&&j.setup.call(a,d,p,k)!==!1||(a.addEventListener?a.addEventListener(o,k,!1):a.attachEvent&&a.attachEvent("on"+o,k))),j.add&&(j.add.call(a,l),l.handler.guid||(l.handler.guid=c.guid)),e?n.splice(n.delegateCount++,0,l):n.push(l),m.event.global[o]=!0);a=null}},remove:function(a,b,c,d,e){var f,g,h,i,j,k,l,n,o,p,q,r=m.hasData(a)&&m._data(a);if(r&&(k=r.events)){b=(b||"").match(E)||[""],j=b.length;while(j--)if(h=_.exec(b[j])||[],o=q=h[1],p=(h[2]||"").split(".").sort(),o){l=m.event.special[o]||{},o=(d?l.delegateType:l.bindType)||o,n=k[o]||[],h=h[2]&&new RegExp("(^|\\.)"+p.join("\\.(?:.*\\.|)")+"(\\.|$)"),i=f=n.length;while(f--)g=n[f],!e&&q!==g.origType||c&&c.guid!==g.guid||h&&!h.test(g.namespace)||d&&d!==g.selector&&("**"!==d||!g.selector)||(n.splice(f,1),g.selector&&n.delegateCount--,l.remove&&l.remove.call(a,g));i&&!n.length&&(l.teardown&&l.teardown.call(a,p,r.handle)!==!1||m.removeEvent(a,o,r.handle),delete k[o])}else for(o in k)m.event.remove(a,o+b[j],c,d,!0);m.isEmptyObject(k)&&(delete r.handle,m._removeData(a,"events"))}},trigger:function(b,c,d,e){var f,g,h,i,k,l,n,o=[d||y],p=j.call(b,"type")?b.type:b,q=j.call(b,"namespace")?b.namespace.split("."):[];if(h=l=d=d||y,3!==d.nodeType&&8!==d.nodeType&&!$.test(p+m.event.triggered)&&(p.indexOf(".")>=0&&(q=p.split("."),p=q.shift(),q.sort()),g=p.indexOf(":")<0&&"on"+p,b=b[m.expando]?b:new m.Event(p,"object"==typeof b&&b),b.isTrigger=e?2:3,b.namespace=q.join("."),b.namespace_re=b.namespace?new RegExp("(^|\\.)"+q.join("\\.(?:.*\\.|)")+"(\\.|$)"):null,b.result=void 0,b.target||(b.target=d),c=null==c?[b]:m.makeArray(c,[b]),k=m.event.special[p]||{},e||!k.trigger||k.trigger.apply(d,c)!==!1)){if(!e&&!k.noBubble&&!m.isWindow(d)){for(i=k.delegateType||p,$.test(i+p)||(h=h.parentNode);h;h=h.parentNode)o.push(h),l=h;l===(d.ownerDocument||y)&&o.push(l.defaultView||l.parentWindow||a)}n=0;while((h=o[n++])&&!b.isPropagationStopped())b.type=n>1?i:k.bindType||p,f=(m._data(h,"events")||{})[b.type]&&m._data(h,"handle"),f&&f.apply(h,c),f=g&&h[g],f&&f.apply&&m.acceptData(h)&&(b.result=f.apply(h,c),b.result===!1&&b.preventDefault());if(b.type=p,!e&&!b.isDefaultPrevented()&&(!k._default||k._default.apply(o.pop(),c)===!1)&&m.acceptData(d)&&g&&d[p]&&!m.isWindow(d)){l=d[g],l&&(d[g]=null),m.event.triggered=p;try{d[p]()}catch(r){}m.event.triggered=void 0,l&&(d[g]=l)}return b.result}},dispatch:function(a){a=m.event.fix(a);var b,c,e,f,g,h=[],i=d.call(arguments),j=(m._data(this,"events")||{})[a.type]||[],k=m.event.special[a.type]||{};if(i[0]=a,a.delegateTarget=this,!k.preDispatch||k.preDispatch.call(this,a)!==!1){h=m.event.handlers.call(this,a,j),b=0;while((f=h[b++])&&!a.isPropagationStopped()){a.currentTarget=f.elem,g=0;while((e=f.handlers[g++])&&!a.isImmediatePropagationStopped())(!a.namespace_re||a.namespace_re.test(e.namespace))&&(a.handleObj=e,a.data=e.data,c=((m.event.special[e.origType]||{}).handle||e.handler).apply(f.elem,i),void 0!==c&&(a.result=c)===!1&&(a.preventDefault(),a.stopPropagation()))}return k.postDispatch&&k.postDispatch.call(this,a),a.result}},handlers:function(a,b){var c,d,e,f,g=[],h=b.delegateCount,i=a.target;if(h&&i.nodeType&&(!a.button||"click"!==a.type))for(;i!=this;i=i.parentNode||this)if(1===i.nodeType&&(i.disabled!==!0||"click"!==a.type)){for(e=[],f=0;h>f;f++)d=b[f],c=d.selector+" ",void 0===e[c]&&(e[c]=d.needsContext?m(c,this).index(i)>=0:m.find(c,this,null,[i]).length),e[c]&&e.push(d);e.length&&g.push({elem:i,handlers:e})}return h<b.length&&g.push({elem:this,handlers:b.slice(h)}),g},fix:function(a){if(a[m.expando])return a;var b,c,d,e=a.type,f=a,g=this.fixHooks[e];g||(this.fixHooks[e]=g=Z.test(e)?this.mouseHooks:Y.test(e)?this.keyHooks:{}),d=g.props?this.props.concat(g.props):this.props,a=new m.Event(f),b=d.length;while(b--)c=d[b],a[c]=f[c];return a.target||(a.target=f.srcElement||y),3===a.target.nodeType&&(a.target=a.target.parentNode),a.metaKey=!!a.metaKey,g.filter?g.filter(a,f):a},props:"altKey bubbles cancelable ctrlKey currentTarget eventPhase metaKey relatedTarget shiftKey target timeStamp view which".split(" "),fixHooks:{},keyHooks:{props:"char charCode key keyCode".split(" "),filter:function(a,b){return null==a.which&&(a.which=null!=b.charCode?b.charCode:b.keyCode),a}},mouseHooks:{props:"button buttons clientX clientY fromElement offsetX offsetY pageX pageY screenX screenY toElement".split(" "),filter:function(a,b){var c,d,e,f=b.button,g=b.fromElement;return null==a.pageX&&null!=b.clientX&&(d=a.target.ownerDocument||y,e=d.documentElement,c=d.body,a.pageX=b.clientX+(e&&e.scrollLeft||c&&c.scrollLeft||0)-(e&&e.clientLeft||c&&c.clientLeft||0),a.pageY=b.clientY+(e&&e.scrollTop||c&&c.scrollTop||0)-(e&&e.clientTop||c&&c.clientTop||0)),!a.relatedTarget&&g&&(a.relatedTarget=g===a.target?b.toElement:g),a.which||void 0===f||(a.which=1&f?1:2&f?3:4&f?2:0),a}},special:{load:{noBubble:!0},focus:{trigger:function(){if(this!==cb()&&this.focus)try{return this.focus(),!1}catch(a){}},delegateType:"focusin"},blur:{trigger:function(){return this===cb()&&this.blur?(this.blur(),!1):void 0},delegateType:"focusout"},click:{trigger:function(){return m.nodeName(this,"input")&&"checkbox"===this.type&&this.click?(this.click(),!1):void 0},_default:function(a){return m.nodeName(a.target,"a")}},beforeunload:{postDispatch:function(a){void 0!==a.result&&a.originalEvent&&(a.originalEvent.returnValue=a.result)}}},simulate:function(a,b,c,d){var e=m.extend(new m.Event,c,{type:a,isSimulated:!0,originalEvent:{}});d?m.event.trigger(e,null,b):m.event.dispatch.call(b,e),e.isDefaultPrevented()&&c.preventDefault()}},m.removeEvent=y.removeEventListener?function(a,b,c){a.removeEventListener&&a.removeEventListener(b,c,!1)}:function(a,b,c){var d="on"+b;a.detachEvent&&(typeof a[d]===K&&(a[d]=null),a.detachEvent(d,c))},m.Event=function(a,b){return this instanceof m.Event?(a&&a.type?(this.originalEvent=a,this.type=a.type,this.isDefaultPrevented=a.defaultPrevented||void 0===a.defaultPrevented&&a.returnValue===!1?ab:bb):this.type=a,b&&m.extend(this,b),this.timeStamp=a&&a.timeStamp||m.now(),void(this[m.expando]=!0)):new m.Event(a,b)},m.Event.prototype={isDefaultPrevented:bb,isPropagationStopped:bb,isImmediatePropagationStopped:bb,preventDefault:function(){var a=this.originalEvent;this.isDefaultPrevented=ab,a&&(a.preventDefault?a.preventDefault():a.returnValue=!1)},stopPropagation:function(){var a=this.originalEvent;this.isPropagationStopped=ab,a&&(a.stopPropagation&&a.stopPropagation(),a.cancelBubble=!0)},stopImmediatePropagation:function(){var a=this.originalEvent;this.isImmediatePropagationStopped=ab,a&&a.stopImmediatePropagation&&a.stopImmediatePropagation(),this.stopPropagation()}},m.each({mouseenter:"mouseover",mouseleave:"mouseout",pointerenter:"pointerover",pointerleave:"pointerout"},function(a,b){m.event.special[a]={delegateType:b,bindType:b,handle:function(a){var c,d=this,e=a.relatedTarget,f=a.handleObj;return(!e||e!==d&&!m.contains(d,e))&&(a.type=f.origType,c=f.handler.apply(this,arguments),a.type=b),c}}}),k.submitBubbles||(m.event.special.submit={setup:function(){return m.nodeName(this,"form")?!1:void m.event.add(this,"click._submit keypress._submit",function(a){var b=a.target,c=m.nodeName(b,"input")||m.nodeName(b,"button")?b.form:void 0;c&&!m._data(c,"submitBubbles")&&(m.event.add(c,"submit._submit",function(a){a._submit_bubble=!0}),m._data(c,"submitBubbles",!0))})},postDispatch:function(a){a._submit_bubble&&(delete a._submit_bubble,this.parentNode&&!a.isTrigger&&m.event.simulate("submit",this.parentNode,a,!0))},teardown:function(){return m.nodeName(this,"form")?!1:void m.event.remove(this,"._submit")}}),k.changeBubbles||(m.event.special.change={setup:function(){return X.test(this.nodeName)?(("checkbox"===this.type||"radio"===this.type)&&(m.event.add(this,"propertychange._change",function(a){"checked"===a.originalEvent.propertyName&&(this._just_changed=!0)}),m.event.add(this,"click._change",function(a){this._just_changed&&!a.isTrigger&&(this._just_changed=!1),m.event.simulate("change",this,a,!0)})),!1):void m.event.add(this,"beforeactivate._change",function(a){var b=a.target;X.test(b.nodeName)&&!m._data(b,"changeBubbles")&&(m.event.add(b,"change._change",function(a){!this.parentNode||a.isSimulated||a.isTrigger||m.event.simulate("change",this.parentNode,a,!0)}),m._data(b,"changeBubbles",!0))})},handle:function(a){var b=a.target;return this!==b||a.isSimulated||a.isTrigger||"radio"!==b.type&&"checkbox"!==b.type?a.handleObj.handler.apply(this,arguments):void 0},teardown:function(){return m.event.remove(this,"._change"),!X.test(this.nodeName)}}),k.focusinBubbles||m.each({focus:"focusin",blur:"focusout"},function(a,b){var c=function(a){m.event.simulate(b,a.target,m.event.fix(a),!0)};m.event.special[b]={setup:function(){var d=this.ownerDocument||this,e=m._data(d,b);e||d.addEventListener(a,c,!0),m._data(d,b,(e||0)+1)},teardown:function(){var d=this.ownerDocument||this,e=m._data(d,b)-1;e?m._data(d,b,e):(d.removeEventListener(a,c,!0),m._removeData(d,b))}}}),m.fn.extend({on:function(a,b,c,d,e){var f,g;if("object"==typeof a){"string"!=typeof b&&(c=c||b,b=void 0);for(f in a)this.on(f,b,c,a[f],e);return this}if(null==c&&null==d?(d=b,c=b=void 0):null==d&&("string"==typeof b?(d=c,c=void 0):(d=c,c=b,b=void 0)),d===!1)d=bb;else if(!d)return this;return 1===e&&(g=d,d=function(a){return m().off(a),g.apply(this,arguments)},d.guid=g.guid||(g.guid=m.guid++)),this.each(function(){m.event.add(this,a,d,c,b)})},one:function(a,b,c,d){return this.on(a,b,c,d,1)},off:function(a,b,c){var d,e;if(a&&a.preventDefault&&a.handleObj)return d=a.handleObj,m(a.delegateTarget).off(d.namespace?d.origType+"."+d.namespace:d.origType,d.selector,d.handler),this;if("object"==typeof a){for(e in a)this.off(e,b,a[e]);return this}return(b===!1||"function"==typeof b)&&(c=b,b=void 0),c===!1&&(c=bb),this.each(function(){m.event.remove(this,a,c,b)})},trigger:function(a,b){return this.each(function(){m.event.trigger(a,b,this)})},triggerHandler:function(a,b){var c=this[0];return c?m.event.trigger(a,b,c,!0):void 0}});function db(a){var b=eb.split("|"),c=a.createDocumentFragment();if(c.createElement)while(b.length)c.createElement(b.pop());return c}var eb="abbr|article|aside|audio|bdi|canvas|data|datalist|details|figcaption|figure|footer|header|hgroup|mark|meter|nav|output|progress|section|summary|time|video",fb=/ jQuery\d+="(?:null|\d+)"/g,gb=new RegExp("<(?:"+eb+")[\\s/>]","i"),hb=/^\s+/,ib=/<(?!area|br|col|embed|hr|img|input|link|meta|param)(([\w:]+)[^>]*)\/>/gi,jb=/<([\w:]+)/,kb=/<tbody/i,lb=/<|&#?\w+;/,mb=/<(?:script|style|link)/i,nb=/checked\s*(?:[^=]|=\s*.checked.)/i,ob=/^$|\/(?:java|ecma)script/i,pb=/^true\/(.*)/,qb=/^\s*<!(?:\[CDATA\[|--)|(?:\]\]|--)>\s*$/g,rb={option:[1,"<select multiple='multiple'>","</select>"],legend:[1,"<fieldset>","</fieldset>"],area:[1,"<map>","</map>"],param:[1,"<object>","</object>"],thead:[1,"<table>","</table>"],tr:[2,"<table><tbody>","</tbody></table>"],col:[2,"<table><tbody></tbody><colgroup>","</colgroup></table>"],td:[3,"<table><tbody><tr>","</tr></tbody></table>"],_default:k.htmlSerialize?[0,"",""]:[1,"X<div>","</div>"]},sb=db(y),tb=sb.appendChild(y.createElement("div"));rb.optgroup=rb.option,rb.tbody=rb.tfoot=rb.colgroup=rb.caption=rb.thead,rb.th=rb.td;function ub(a,b){var c,d,e=0,f=typeof a.getElementsByTagName!==K?a.getElementsByTagName(b||"*"):typeof a.querySelectorAll!==K?a.querySelectorAll(b||"*"):void 0;if(!f)for(f=[],c=a.childNodes||a;null!=(d=c[e]);e++)!b||m.nodeName(d,b)?f.push(d):m.merge(f,ub(d,b));return void 0===b||b&&m.nodeName(a,b)?m.merge([a],f):f}function vb(a){W.test(a.type)&&(a.defaultChecked=a.checked)}function wb(a,b){return m.nodeName(a,"table")&&m.nodeName(11!==b.nodeType?b:b.firstChild,"tr")?a.getElementsByTagName("tbody")[0]||a.appendChild(a.ownerDocument.createElement("tbody")):a}function xb(a){return a.type=(null!==m.find.attr(a,"type"))+"/"+a.type,a}function yb(a){var b=pb.exec(a.type);return b?a.type=b[1]:a.removeAttribute("type"),a}function zb(a,b){for(var c,d=0;null!=(c=a[d]);d++)m._data(c,"globalEval",!b||m._data(b[d],"globalEval"))}function Ab(a,b){if(1===b.nodeType&&m.hasData(a)){var c,d,e,f=m._data(a),g=m._data(b,f),h=f.events;if(h){delete g.handle,g.events={};for(c in h)for(d=0,e=h[c].length;e>d;d++)m.event.add(b,c,h[c][d])}g.data&&(g.data=m.extend({},g.data))}}function Bb(a,b){var c,d,e;if(1===b.nodeType){if(c=b.nodeName.toLowerCase(),!k.noCloneEvent&&b[m.expando]){e=m._data(b);for(d in e.events)m.removeEvent(b,d,e.handle);b.removeAttribute(m.expando)}"script"===c&&b.text!==a.text?(xb(b).text=a.text,yb(b)):"object"===c?(b.parentNode&&(b.outerHTML=a.outerHTML),k.html5Clone&&a.innerHTML&&!m.trim(b.innerHTML)&&(b.innerHTML=a.innerHTML)):"input"===c&&W.test(a.type)?(b.defaultChecked=b.checked=a.checked,b.value!==a.value&&(b.value=a.value)):"option"===c?b.defaultSelected=b.selected=a.defaultSelected:("input"===c||"textarea"===c)&&(b.defaultValue=a.defaultValue)}}m.extend({clone:function(a,b,c){var d,e,f,g,h,i=m.contains(a.ownerDocument,a);if(k.html5Clone||m.isXMLDoc(a)||!gb.test("<"+a.nodeName+">")?f=a.cloneNode(!0):(tb.innerHTML=a.outerHTML,tb.removeChild(f=tb.firstChild)),!(k.noCloneEvent&&k.noCloneChecked||1!==a.nodeType&&11!==a.nodeType||m.isXMLDoc(a)))for(d=ub(f),h=ub(a),g=0;null!=(e=h[g]);++g)d[g]&&Bb(e,d[g]);if(b)if(c)for(h=h||ub(a),d=d||ub(f),g=0;null!=(e=h[g]);g++)Ab(e,d[g]);else Ab(a,f);return d=ub(f,"script"),d.length>0&&zb(d,!i&&ub(a,"script")),d=h=e=null,f},buildFragment:function(a,b,c,d){for(var e,f,g,h,i,j,l,n=a.length,o=db(b),p=[],q=0;n>q;q++)if(f=a[q],f||0===f)if("object"===m.type(f))m.merge(p,f.nodeType?[f]:f);else if(lb.test(f)){h=h||o.appendChild(b.createElement("div")),i=(jb.exec(f)||["",""])[1].toLowerCase(),l=rb[i]||rb._default,h.innerHTML=l[1]+f.replace(ib,"<$1></$2>")+l[2],e=l[0];while(e--)h=h.lastChild;if(!k.leadingWhitespace&&hb.test(f)&&p.push(b.createTextNode(hb.exec(f)[0])),!k.tbody){f="table"!==i||kb.test(f)?"<table>"!==l[1]||kb.test(f)?0:h:h.firstChild,e=f&&f.childNodes.length;while(e--)m.nodeName(j=f.childNodes[e],"tbody")&&!j.childNodes.length&&f.removeChild(j)}m.merge(p,h.childNodes),h.textContent="";while(h.firstChild)h.removeChild(h.firstChild);h=o.lastChild}else p.push(b.createTextNode(f));h&&o.removeChild(h),k.appendChecked||m.grep(ub(p,"input"),vb),q=0;while(f=p[q++])if((!d||-1===m.inArray(f,d))&&(g=m.contains(f.ownerDocument,f),h=ub(o.appendChild(f),"script"),g&&zb(h),c)){e=0;while(f=h[e++])ob.test(f.type||"")&&c.push(f)}return h=null,o},cleanData:function(a,b){for(var d,e,f,g,h=0,i=m.expando,j=m.cache,l=k.deleteExpando,n=m.event.special;null!=(d=a[h]);h++)if((b||m.acceptData(d))&&(f=d[i],g=f&&j[f])){if(g.events)for(e in g.events)n[e]?m.event.remove(d,e):m.removeEvent(d,e,g.handle);j[f]&&(delete j[f],l?delete d[i]:typeof d.removeAttribute!==K?d.removeAttribute(i):d[i]=null,c.push(f))}}}),m.fn.extend({text:function(a){return V(this,function(a){return void 0===a?m.text(this):this.empty().append((this[0]&&this[0].ownerDocument||y).createTextNode(a))},null,a,arguments.length)},append:function(){return this.domManip(arguments,function(a){if(1===this.nodeType||11===this.nodeType||9===this.nodeType){var b=wb(this,a);b.appendChild(a)}})},prepend:function(){return this.domManip(arguments,function(a){if(1===this.nodeType||11===this.nodeType||9===this.nodeType){var b=wb(this,a);b.insertBefore(a,b.firstChild)}})},before:function(){return this.domManip(arguments,function(a){this.parentNode&&this.parentNode.insertBefore(a,this)})},after:function(){return this.domManip(arguments,function(a){this.parentNode&&this.parentNode.insertBefore(a,this.nextSibling)})},remove:function(a,b){for(var c,d=a?m.filter(a,this):this,e=0;null!=(c=d[e]);e++)b||1!==c.nodeType||m.cleanData(ub(c)),c.parentNode&&(b&&m.contains(c.ownerDocument,c)&&zb(ub(c,"script")),c.parentNode.removeChild(c));return this},empty:function(){for(var a,b=0;null!=(a=this[b]);b++){1===a.nodeType&&m.cleanData(ub(a,!1));while(a.firstChild)a.removeChild(a.firstChild);a.options&&m.nodeName(a,"select")&&(a.options.length=0)}return this},clone:function(a,b){return a=null==a?!1:a,b=null==b?a:b,this.map(function(){return m.clone(this,a,b)})},html:function(a){return V(this,function(a){var b=this[0]||{},c=0,d=this.length;if(void 0===a)return 1===b.nodeType?b.innerHTML.replace(fb,""):void 0;if(!("string"!=typeof a||mb.test(a)||!k.htmlSerialize&&gb.test(a)||!k.leadingWhitespace&&hb.test(a)||rb[(jb.exec(a)||["",""])[1].toLowerCase()])){a=a.replace(ib,"<$1></$2>");try{for(;d>c;c++)b=this[c]||{},1===b.nodeType&&(m.cleanData(ub(b,!1)),b.innerHTML=a);b=0}catch(e){}}b&&this.empty().append(a)},null,a,arguments.length)},replaceWith:function(){var a=arguments[0];return this.domManip(arguments,function(b){a=this.parentNode,m.cleanData(ub(this)),a&&a.replaceChild(b,this)}),a&&(a.length||a.nodeType)?this:this.remove()},detach:function(a){return this.remove(a,!0)},domManip:function(a,b){a=e.apply([],a);var c,d,f,g,h,i,j=0,l=this.length,n=this,o=l-1,p=a[0],q=m.isFunction(p);if(q||l>1&&"string"==typeof p&&!k.checkClone&&nb.test(p))return this.each(function(c){var d=n.eq(c);q&&(a[0]=p.call(this,c,d.html())),d.domManip(a,b)});if(l&&(i=m.buildFragment(a,this[0].ownerDocument,!1,this),c=i.firstChild,1===i.childNodes.length&&(i=c),c)){for(g=m.map(ub(i,"script"),xb),f=g.length;l>j;j++)d=i,j!==o&&(d=m.clone(d,!0,!0),f&&m.merge(g,ub(d,"script"))),b.call(this[j],d,j);if(f)for(h=g[g.length-1].ownerDocument,m.map(g,yb),j=0;f>j;j++)d=g[j],ob.test(d.type||"")&&!m._data(d,"globalEval")&&m.contains(h,d)&&(d.src?m._evalUrl&&m._evalUrl(d.src):m.globalEval((d.text||d.textContent||d.innerHTML||"").replace(qb,"")));i=c=null}return this}}),m.each({appendTo:"append",prependTo:"prepend",insertBefore:"before",insertAfter:"after",replaceAll:"replaceWith"},function(a,b){m.fn[a]=function(a){for(var c,d=0,e=[],g=m(a),h=g.length-1;h>=d;d++)c=d===h?this:this.clone(!0),m(g[d])[b](c),f.apply(e,c.get());return this.pushStack(e)}});var Cb,Db={};function Eb(b,c){var d,e=m(c.createElement(b)).appendTo(c.body),f=a.getDefaultComputedStyle&&(d=a.getDefaultComputedStyle(e[0]))?d.display:m.css(e[0],"display");return e.detach(),f}function Fb(a){var b=y,c=Db[a];return c||(c=Eb(a,b),"none"!==c&&c||(Cb=(Cb||m("<iframe frameborder='0' width='0' height='0'/>")).appendTo(b.documentElement),b=(Cb[0].contentWindow||Cb[0].contentDocument).document,b.write(),b.close(),c=Eb(a,b),Cb.detach()),Db[a]=c),c}!function(){var a;k.shrinkWrapBlocks=function(){if(null!=a)return a;a=!1;var b,c,d;return c=y.getElementsByTagName("body")[0],c&&c.style?(b=y.createElement("div"),d=y.createElement("div"),d.style.cssText="position:absolute;border:0;width:0;height:0;top:0;left:-9999px",c.appendChild(d).appendChild(b),typeof b.style.zoom!==K&&(b.style.cssText="-webkit-box-sizing:content-box;-moz-box-sizing:content-box;box-sizing:content-box;display:block;margin:0;border:0;padding:1px;width:1px;zoom:1",b.appendChild(y.createElement("div")).style.width="5px",a=3!==b.offsetWidth),c.removeChild(d),a):void 0}}();var Gb=/^margin/,Hb=new RegExp("^("+S+")(?!px)[a-z%]+$","i"),Ib,Jb,Kb=/^(top|right|bottom|left)$/;a.getComputedStyle?(Ib=function(a){return a.ownerDocument.defaultView.getComputedStyle(a,null)},Jb=function(a,b,c){var d,e,f,g,h=a.style;return c=c||Ib(a),g=c?c.getPropertyValue(b)||c[b]:void 0,c&&(""!==g||m.contains(a.ownerDocument,a)||(g=m.style(a,b)),Hb.test(g)&&Gb.test(b)&&(d=h.width,e=h.minWidth,f=h.maxWidth,h.minWidth=h.maxWidth=h.width=g,g=c.width,h.width=d,h.minWidth=e,h.maxWidth=f)),void 0===g?g:g+""}):y.documentElement.currentStyle&&(Ib=function(a){return a.currentStyle},Jb=function(a,b,c){var d,e,f,g,h=a.style;return c=c||Ib(a),g=c?c[b]:void 0,null==g&&h&&h[b]&&(g=h[b]),Hb.test(g)&&!Kb.test(b)&&(d=h.left,e=a.runtimeStyle,f=e&&e.left,f&&(e.left=a.currentStyle.left),h.left="fontSize"===b?"1em":g,g=h.pixelLeft+"px",h.left=d,f&&(e.left=f)),void 0===g?g:g+""||"auto"});function Lb(a,b){return{get:function(){var c=a();if(null!=c)return c?void delete this.get:(this.get=b).apply(this,arguments)}}}!function(){var b,c,d,e,f,g,h;if(b=y.createElement("div"),b.innerHTML="  <link/><table></table><a href='/a'>a</a><input type='checkbox'/>",d=b.getElementsByTagName("a")[0],c=d&&d.style){c.cssText="float:left;opacity:.5",k.opacity="0.5"===c.opacity,k.cssFloat=!!c.cssFloat,b.style.backgroundClip="content-box",b.cloneNode(!0).style.backgroundClip="",k.clearCloneStyle="content-box"===b.style.backgroundClip,k.boxSizing=""===c.boxSizing||""===c.MozBoxSizing||""===c.WebkitBoxSizing,m.extend(k,{reliableHiddenOffsets:function(){return null==g&&i(),g},boxSizingReliable:function(){return null==f&&i(),f},pixelPosition:function(){return null==e&&i(),e},reliableMarginRight:function(){return null==h&&i(),h}});function i(){var b,c,d,i;c=y.getElementsByTagName("body")[0],c&&c.style&&(b=y.createElement("div"),d=y.createElement("div"),d.style.cssText="position:absolute;border:0;width:0;height:0;top:0;left:-9999px",c.appendChild(d).appendChild(b),b.style.cssText="-webkit-box-sizing:border-box;-moz-box-sizing:border-box;box-sizing:border-box;display:block;margin-top:1%;top:1%;border:1px;padding:1px;width:4px;position:absolute",e=f=!1,h=!0,a.getComputedStyle&&(e="1%"!==(a.getComputedStyle(b,null)||{}).top,f="4px"===(a.getComputedStyle(b,null)||{width:"4px"}).width,i=b.appendChild(y.createElement("div")),i.style.cssText=b.style.cssText="-webkit-box-sizing:content-box;-moz-box-sizing:content-box;box-sizing:content-box;display:block;margin:0;border:0;padding:0",i.style.marginRight=i.style.width="0",b.style.width="1px",h=!parseFloat((a.getComputedStyle(i,null)||{}).marginRight)),b.innerHTML="<table><tr><td></td><td>t</td></tr></table>",i=b.getElementsByTagName("td"),i[0].style.cssText="margin:0;border:0;padding:0;display:none",g=0===i[0].offsetHeight,g&&(i[0].style.display="",i[1].style.display="none",g=0===i[0].offsetHeight),c.removeChild(d))}}}(),m.swap=function(a,b,c,d){var e,f,g={};for(f in b)g[f]=a.style[f],a.style[f]=b[f];e=c.apply(a,d||[]);for(f in b)a.style[f]=g[f];return e};var Mb=/alpha\([^)]*\)/i,Nb=/opacity\s*=\s*([^)]*)/,Ob=/^(none|table(?!-c[ea]).+)/,Pb=new RegExp("^("+S+")(.*)$","i"),Qb=new RegExp("^([+-])=("+S+")","i"),Rb={position:"absolute",visibility:"hidden",display:"block"},Sb={letterSpacing:"0",fontWeight:"400"},Tb=["Webkit","O","Moz","ms"];function Ub(a,b){if(b in a)return b;var c=b.charAt(0).toUpperCase()+b.slice(1),d=b,e=Tb.length;while(e--)if(b=Tb[e]+c,b in a)return b;return d}function Vb(a,b){for(var c,d,e,f=[],g=0,h=a.length;h>g;g++)d=a[g],d.style&&(f[g]=m._data(d,"olddisplay"),c=d.style.display,b?(f[g]||"none"!==c||(d.style.display=""),""===d.style.display&&U(d)&&(f[g]=m._data(d,"olddisplay",Fb(d.nodeName)))):(e=U(d),(c&&"none"!==c||!e)&&m._data(d,"olddisplay",e?c:m.css(d,"display"))));for(g=0;h>g;g++)d=a[g],d.style&&(b&&"none"!==d.style.display&&""!==d.style.display||(d.style.display=b?f[g]||"":"none"));return a}function Wb(a,b,c){var d=Pb.exec(b);return d?Math.max(0,d[1]-(c||0))+(d[2]||"px"):b}function Xb(a,b,c,d,e){for(var f=c===(d?"border":"content")?4:"width"===b?1:0,g=0;4>f;f+=2)"margin"===c&&(g+=m.css(a,c+T[f],!0,e)),d?("content"===c&&(g-=m.css(a,"padding"+T[f],!0,e)),"margin"!==c&&(g-=m.css(a,"border"+T[f]+"Width",!0,e))):(g+=m.css(a,"padding"+T[f],!0,e),"padding"!==c&&(g+=m.css(a,"border"+T[f]+"Width",!0,e)));return g}function Yb(a,b,c){var d=!0,e="width"===b?a.offsetWidth:a.offsetHeight,f=Ib(a),g=k.boxSizing&&"border-box"===m.css(a,"boxSizing",!1,f);if(0>=e||null==e){if(e=Jb(a,b,f),(0>e||null==e)&&(e=a.style[b]),Hb.test(e))return e;d=g&&(k.boxSizingReliable()||e===a.style[b]),e=parseFloat(e)||0}return e+Xb(a,b,c||(g?"border":"content"),d,f)+"px"}m.extend({cssHooks:{opacity:{get:function(a,b){if(b){var c=Jb(a,"opacity");return""===c?"1":c}}}},cssNumber:{columnCount:!0,fillOpacity:!0,flexGrow:!0,flexShrink:!0,fontWeight:!0,lineHeight:!0,opacity:!0,order:!0,orphans:!0,widows:!0,zIndex:!0,zoom:!0},cssProps:{"float":k.cssFloat?"cssFloat":"styleFloat"},style:function(a,b,c,d){if(a&&3!==a.nodeType&&8!==a.nodeType&&a.style){var e,f,g,h=m.camelCase(b),i=a.style;if(b=m.cssProps[h]||(m.cssProps[h]=Ub(i,h)),g=m.cssHooks[b]||m.cssHooks[h],void 0===c)return g&&"get"in g&&void 0!==(e=g.get(a,!1,d))?e:i[b];if(f=typeof c,"string"===f&&(e=Qb.exec(c))&&(c=(e[1]+1)*e[2]+parseFloat(m.css(a,b)),f="number"),null!=c&&c===c&&("number"!==f||m.cssNumber[h]||(c+="px"),k.clearCloneStyle||""!==c||0!==b.indexOf("background")||(i[b]="inherit"),!(g&&"set"in g&&void 0===(c=g.set(a,c,d)))))try{i[b]=c}catch(j){}}},css:function(a,b,c,d){var e,f,g,h=m.camelCase(b);return b=m.cssProps[h]||(m.cssProps[h]=Ub(a.style,h)),g=m.cssHooks[b]||m.cssHooks[h],g&&"get"in g&&(f=g.get(a,!0,c)),void 0===f&&(f=Jb(a,b,d)),"normal"===f&&b in Sb&&(f=Sb[b]),""===c||c?(e=parseFloat(f),c===!0||m.isNumeric(e)?e||0:f):f}}),m.each(["height","width"],function(a,b){m.cssHooks[b]={get:function(a,c,d){return c?Ob.test(m.css(a,"display"))&&0===a.offsetWidth?m.swap(a,Rb,function(){return Yb(a,b,d)}):Yb(a,b,d):void 0},set:function(a,c,d){var e=d&&Ib(a);return Wb(a,c,d?Xb(a,b,d,k.boxSizing&&"border-box"===m.css(a,"boxSizing",!1,e),e):0)}}}),k.opacity||(m.cssHooks.opacity={get:function(a,b){return Nb.test((b&&a.currentStyle?a.currentStyle.filter:a.style.filter)||"")?.01*parseFloat(RegExp.$1)+"":b?"1":""},set:function(a,b){var c=a.style,d=a.currentStyle,e=m.isNumeric(b)?"alpha(opacity="+100*b+")":"",f=d&&d.filter||c.filter||"";c.zoom=1,(b>=1||""===b)&&""===m.trim(f.replace(Mb,""))&&c.removeAttribute&&(c.removeAttribute("filter"),""===b||d&&!d.filter)||(c.filter=Mb.test(f)?f.replace(Mb,e):f+" "+e)}}),m.cssHooks.marginRight=Lb(k.reliableMarginRight,function(a,b){return b?m.swap(a,{display:"inline-block"},Jb,[a,"marginRight"]):void 0}),m.each({margin:"",padding:"",border:"Width"},function(a,b){m.cssHooks[a+b]={expand:function(c){for(var d=0,e={},f="string"==typeof c?c.split(" "):[c];4>d;d++)e[a+T[d]+b]=f[d]||f[d-2]||f[0];return e}},Gb.test(a)||(m.cssHooks[a+b].set=Wb)}),m.fn.extend({css:function(a,b){return V(this,function(a,b,c){var d,e,f={},g=0;if(m.isArray(b)){for(d=Ib(a),e=b.length;e>g;g++)f[b[g]]=m.css(a,b[g],!1,d);return f}return void 0!==c?m.style(a,b,c):m.css(a,b)},a,b,arguments.length>1)},show:function(){return Vb(this,!0)},hide:function(){return Vb(this)},toggle:function(a){return"boolean"==typeof a?a?this.show():this.hide():this.each(function(){U(this)?m(this).show():m(this).hide()})}});function Zb(a,b,c,d,e){return new Zb.prototype.init(a,b,c,d,e)}m.Tween=Zb,Zb.prototype={constructor:Zb,init:function(a,b,c,d,e,f){this.elem=a,this.prop=c,this.easing=e||"swing",this.options=b,this.start=this.now=this.cur(),this.end=d,this.unit=f||(m.cssNumber[c]?"":"px")
},cur:function(){var a=Zb.propHooks[this.prop];return a&&a.get?a.get(this):Zb.propHooks._default.get(this)},run:function(a){var b,c=Zb.propHooks[this.prop];return this.pos=b=this.options.duration?m.easing[this.easing](a,this.options.duration*a,0,1,this.options.duration):a,this.now=(this.end-this.start)*b+this.start,this.options.step&&this.options.step.call(this.elem,this.now,this),c&&c.set?c.set(this):Zb.propHooks._default.set(this),this}},Zb.prototype.init.prototype=Zb.prototype,Zb.propHooks={_default:{get:function(a){var b;return null==a.elem[a.prop]||a.elem.style&&null!=a.elem.style[a.prop]?(b=m.css(a.elem,a.prop,""),b&&"auto"!==b?b:0):a.elem[a.prop]},set:function(a){m.fx.step[a.prop]?m.fx.step[a.prop](a):a.elem.style&&(null!=a.elem.style[m.cssProps[a.prop]]||m.cssHooks[a.prop])?m.style(a.elem,a.prop,a.now+a.unit):a.elem[a.prop]=a.now}}},Zb.propHooks.scrollTop=Zb.propHooks.scrollLeft={set:function(a){a.elem.nodeType&&a.elem.parentNode&&(a.elem[a.prop]=a.now)}},m.easing={linear:function(a){return a},swing:function(a){return.5-Math.cos(a*Math.PI)/2}},m.fx=Zb.prototype.init,m.fx.step={};var $b,_b,ac=/^(?:toggle|show|hide)$/,bc=new RegExp("^(?:([+-])=|)("+S+")([a-z%]*)$","i"),cc=/queueHooks$/,dc=[ic],ec={"*":[function(a,b){var c=this.createTween(a,b),d=c.cur(),e=bc.exec(b),f=e&&e[3]||(m.cssNumber[a]?"":"px"),g=(m.cssNumber[a]||"px"!==f&&+d)&&bc.exec(m.css(c.elem,a)),h=1,i=20;if(g&&g[3]!==f){f=f||g[3],e=e||[],g=+d||1;do h=h||".5",g/=h,m.style(c.elem,a,g+f);while(h!==(h=c.cur()/d)&&1!==h&&--i)}return e&&(g=c.start=+g||+d||0,c.unit=f,c.end=e[1]?g+(e[1]+1)*e[2]:+e[2]),c}]};function fc(){return setTimeout(function(){$b=void 0}),$b=m.now()}function gc(a,b){var c,d={height:a},e=0;for(b=b?1:0;4>e;e+=2-b)c=T[e],d["margin"+c]=d["padding"+c]=a;return b&&(d.opacity=d.width=a),d}function hc(a,b,c){for(var d,e=(ec[b]||[]).concat(ec["*"]),f=0,g=e.length;g>f;f++)if(d=e[f].call(c,b,a))return d}function ic(a,b,c){var d,e,f,g,h,i,j,l,n=this,o={},p=a.style,q=a.nodeType&&U(a),r=m._data(a,"fxshow");c.queue||(h=m._queueHooks(a,"fx"),null==h.unqueued&&(h.unqueued=0,i=h.empty.fire,h.empty.fire=function(){h.unqueued||i()}),h.unqueued++,n.always(function(){n.always(function(){h.unqueued--,m.queue(a,"fx").length||h.empty.fire()})})),1===a.nodeType&&("height"in b||"width"in b)&&(c.overflow=[p.overflow,p.overflowX,p.overflowY],j=m.css(a,"display"),l="none"===j?m._data(a,"olddisplay")||Fb(a.nodeName):j,"inline"===l&&"none"===m.css(a,"float")&&(k.inlineBlockNeedsLayout&&"inline"!==Fb(a.nodeName)?p.zoom=1:p.display="inline-block")),c.overflow&&(p.overflow="hidden",k.shrinkWrapBlocks()||n.always(function(){p.overflow=c.overflow[0],p.overflowX=c.overflow[1],p.overflowY=c.overflow[2]}));for(d in b)if(e=b[d],ac.exec(e)){if(delete b[d],f=f||"toggle"===e,e===(q?"hide":"show")){if("show"!==e||!r||void 0===r[d])continue;q=!0}o[d]=r&&r[d]||m.style(a,d)}else j=void 0;if(m.isEmptyObject(o))"inline"===("none"===j?Fb(a.nodeName):j)&&(p.display=j);else{r?"hidden"in r&&(q=r.hidden):r=m._data(a,"fxshow",{}),f&&(r.hidden=!q),q?m(a).show():n.done(function(){m(a).hide()}),n.done(function(){var b;m._removeData(a,"fxshow");for(b in o)m.style(a,b,o[b])});for(d in o)g=hc(q?r[d]:0,d,n),d in r||(r[d]=g.start,q&&(g.end=g.start,g.start="width"===d||"height"===d?1:0))}}function jc(a,b){var c,d,e,f,g;for(c in a)if(d=m.camelCase(c),e=b[d],f=a[c],m.isArray(f)&&(e=f[1],f=a[c]=f[0]),c!==d&&(a[d]=f,delete a[c]),g=m.cssHooks[d],g&&"expand"in g){f=g.expand(f),delete a[d];for(c in f)c in a||(a[c]=f[c],b[c]=e)}else b[d]=e}function kc(a,b,c){var d,e,f=0,g=dc.length,h=m.Deferred().always(function(){delete i.elem}),i=function(){if(e)return!1;for(var b=$b||fc(),c=Math.max(0,j.startTime+j.duration-b),d=c/j.duration||0,f=1-d,g=0,i=j.tweens.length;i>g;g++)j.tweens[g].run(f);return h.notifyWith(a,[j,f,c]),1>f&&i?c:(h.resolveWith(a,[j]),!1)},j=h.promise({elem:a,props:m.extend({},b),opts:m.extend(!0,{specialEasing:{}},c),originalProperties:b,originalOptions:c,startTime:$b||fc(),duration:c.duration,tweens:[],createTween:function(b,c){var d=m.Tween(a,j.opts,b,c,j.opts.specialEasing[b]||j.opts.easing);return j.tweens.push(d),d},stop:function(b){var c=0,d=b?j.tweens.length:0;if(e)return this;for(e=!0;d>c;c++)j.tweens[c].run(1);return b?h.resolveWith(a,[j,b]):h.rejectWith(a,[j,b]),this}}),k=j.props;for(jc(k,j.opts.specialEasing);g>f;f++)if(d=dc[f].call(j,a,k,j.opts))return d;return m.map(k,hc,j),m.isFunction(j.opts.start)&&j.opts.start.call(a,j),m.fx.timer(m.extend(i,{elem:a,anim:j,queue:j.opts.queue})),j.progress(j.opts.progress).done(j.opts.done,j.opts.complete).fail(j.opts.fail).always(j.opts.always)}m.Animation=m.extend(kc,{tweener:function(a,b){m.isFunction(a)?(b=a,a=["*"]):a=a.split(" ");for(var c,d=0,e=a.length;e>d;d++)c=a[d],ec[c]=ec[c]||[],ec[c].unshift(b)},prefilter:function(a,b){b?dc.unshift(a):dc.push(a)}}),m.speed=function(a,b,c){var d=a&&"object"==typeof a?m.extend({},a):{complete:c||!c&&b||m.isFunction(a)&&a,duration:a,easing:c&&b||b&&!m.isFunction(b)&&b};return d.duration=m.fx.off?0:"number"==typeof d.duration?d.duration:d.duration in m.fx.speeds?m.fx.speeds[d.duration]:m.fx.speeds._default,(null==d.queue||d.queue===!0)&&(d.queue="fx"),d.old=d.complete,d.complete=function(){m.isFunction(d.old)&&d.old.call(this),d.queue&&m.dequeue(this,d.queue)},d},m.fn.extend({fadeTo:function(a,b,c,d){return this.filter(U).css("opacity",0).show().end().animate({opacity:b},a,c,d)},animate:function(a,b,c,d){var e=m.isEmptyObject(a),f=m.speed(b,c,d),g=function(){var b=kc(this,m.extend({},a),f);(e||m._data(this,"finish"))&&b.stop(!0)};return g.finish=g,e||f.queue===!1?this.each(g):this.queue(f.queue,g)},stop:function(a,b,c){var d=function(a){var b=a.stop;delete a.stop,b(c)};return"string"!=typeof a&&(c=b,b=a,a=void 0),b&&a!==!1&&this.queue(a||"fx",[]),this.each(function(){var b=!0,e=null!=a&&a+"queueHooks",f=m.timers,g=m._data(this);if(e)g[e]&&g[e].stop&&d(g[e]);else for(e in g)g[e]&&g[e].stop&&cc.test(e)&&d(g[e]);for(e=f.length;e--;)f[e].elem!==this||null!=a&&f[e].queue!==a||(f[e].anim.stop(c),b=!1,f.splice(e,1));(b||!c)&&m.dequeue(this,a)})},finish:function(a){return a!==!1&&(a=a||"fx"),this.each(function(){var b,c=m._data(this),d=c[a+"queue"],e=c[a+"queueHooks"],f=m.timers,g=d?d.length:0;for(c.finish=!0,m.queue(this,a,[]),e&&e.stop&&e.stop.call(this,!0),b=f.length;b--;)f[b].elem===this&&f[b].queue===a&&(f[b].anim.stop(!0),f.splice(b,1));for(b=0;g>b;b++)d[b]&&d[b].finish&&d[b].finish.call(this);delete c.finish})}}),m.each(["toggle","show","hide"],function(a,b){var c=m.fn[b];m.fn[b]=function(a,d,e){return null==a||"boolean"==typeof a?c.apply(this,arguments):this.animate(gc(b,!0),a,d,e)}}),m.each({slideDown:gc("show"),slideUp:gc("hide"),slideToggle:gc("toggle"),fadeIn:{opacity:"show"},fadeOut:{opacity:"hide"},fadeToggle:{opacity:"toggle"}},function(a,b){m.fn[a]=function(a,c,d){return this.animate(b,a,c,d)}}),m.timers=[],m.fx.tick=function(){var a,b=m.timers,c=0;for($b=m.now();c<b.length;c++)a=b[c],a()||b[c]!==a||b.splice(c--,1);b.length||m.fx.stop(),$b=void 0},m.fx.timer=function(a){m.timers.push(a),a()?m.fx.start():m.timers.pop()},m.fx.interval=13,m.fx.start=function(){_b||(_b=setInterval(m.fx.tick,m.fx.interval))},m.fx.stop=function(){clearInterval(_b),_b=null},m.fx.speeds={slow:600,fast:200,_default:400},m.fn.delay=function(a,b){return a=m.fx?m.fx.speeds[a]||a:a,b=b||"fx",this.queue(b,function(b,c){var d=setTimeout(b,a);c.stop=function(){clearTimeout(d)}})},function(){var a,b,c,d,e;b=y.createElement("div"),b.setAttribute("className","t"),b.innerHTML="  <link/><table></table><a href='/a'>a</a><input type='checkbox'/>",d=b.getElementsByTagName("a")[0],c=y.createElement("select"),e=c.appendChild(y.createElement("option")),a=b.getElementsByTagName("input")[0],d.style.cssText="top:1px",k.getSetAttribute="t"!==b.className,k.style=/top/.test(d.getAttribute("style")),k.hrefNormalized="/a"===d.getAttribute("href"),k.checkOn=!!a.value,k.optSelected=e.selected,k.enctype=!!y.createElement("form").enctype,c.disabled=!0,k.optDisabled=!e.disabled,a=y.createElement("input"),a.setAttribute("value",""),k.input=""===a.getAttribute("value"),a.value="t",a.setAttribute("type","radio"),k.radioValue="t"===a.value}();var lc=/\r/g;m.fn.extend({val:function(a){var b,c,d,e=this[0];{if(arguments.length)return d=m.isFunction(a),this.each(function(c){var e;1===this.nodeType&&(e=d?a.call(this,c,m(this).val()):a,null==e?e="":"number"==typeof e?e+="":m.isArray(e)&&(e=m.map(e,function(a){return null==a?"":a+""})),b=m.valHooks[this.type]||m.valHooks[this.nodeName.toLowerCase()],b&&"set"in b&&void 0!==b.set(this,e,"value")||(this.value=e))});if(e)return b=m.valHooks[e.type]||m.valHooks[e.nodeName.toLowerCase()],b&&"get"in b&&void 0!==(c=b.get(e,"value"))?c:(c=e.value,"string"==typeof c?c.replace(lc,""):null==c?"":c)}}}),m.extend({valHooks:{option:{get:function(a){var b=m.find.attr(a,"value");return null!=b?b:m.trim(m.text(a))}},select:{get:function(a){for(var b,c,d=a.options,e=a.selectedIndex,f="select-one"===a.type||0>e,g=f?null:[],h=f?e+1:d.length,i=0>e?h:f?e:0;h>i;i++)if(c=d[i],!(!c.selected&&i!==e||(k.optDisabled?c.disabled:null!==c.getAttribute("disabled"))||c.parentNode.disabled&&m.nodeName(c.parentNode,"optgroup"))){if(b=m(c).val(),f)return b;g.push(b)}return g},set:function(a,b){var c,d,e=a.options,f=m.makeArray(b),g=e.length;while(g--)if(d=e[g],m.inArray(m.valHooks.option.get(d),f)>=0)try{d.selected=c=!0}catch(h){d.scrollHeight}else d.selected=!1;return c||(a.selectedIndex=-1),e}}}}),m.each(["radio","checkbox"],function(){m.valHooks[this]={set:function(a,b){return m.isArray(b)?a.checked=m.inArray(m(a).val(),b)>=0:void 0}},k.checkOn||(m.valHooks[this].get=function(a){return null===a.getAttribute("value")?"on":a.value})});var mc,nc,oc=m.expr.attrHandle,pc=/^(?:checked|selected)$/i,qc=k.getSetAttribute,rc=k.input;m.fn.extend({attr:function(a,b){return V(this,m.attr,a,b,arguments.length>1)},removeAttr:function(a){return this.each(function(){m.removeAttr(this,a)})}}),m.extend({attr:function(a,b,c){var d,e,f=a.nodeType;if(a&&3!==f&&8!==f&&2!==f)return typeof a.getAttribute===K?m.prop(a,b,c):(1===f&&m.isXMLDoc(a)||(b=b.toLowerCase(),d=m.attrHooks[b]||(m.expr.match.bool.test(b)?nc:mc)),void 0===c?d&&"get"in d&&null!==(e=d.get(a,b))?e:(e=m.find.attr(a,b),null==e?void 0:e):null!==c?d&&"set"in d&&void 0!==(e=d.set(a,c,b))?e:(a.setAttribute(b,c+""),c):void m.removeAttr(a,b))},removeAttr:function(a,b){var c,d,e=0,f=b&&b.match(E);if(f&&1===a.nodeType)while(c=f[e++])d=m.propFix[c]||c,m.expr.match.bool.test(c)?rc&&qc||!pc.test(c)?a[d]=!1:a[m.camelCase("default-"+c)]=a[d]=!1:m.attr(a,c,""),a.removeAttribute(qc?c:d)},attrHooks:{type:{set:function(a,b){if(!k.radioValue&&"radio"===b&&m.nodeName(a,"input")){var c=a.value;return a.setAttribute("type",b),c&&(a.value=c),b}}}}}),nc={set:function(a,b,c){return b===!1?m.removeAttr(a,c):rc&&qc||!pc.test(c)?a.setAttribute(!qc&&m.propFix[c]||c,c):a[m.camelCase("default-"+c)]=a[c]=!0,c}},m.each(m.expr.match.bool.source.match(/\w+/g),function(a,b){var c=oc[b]||m.find.attr;oc[b]=rc&&qc||!pc.test(b)?function(a,b,d){var e,f;return d||(f=oc[b],oc[b]=e,e=null!=c(a,b,d)?b.toLowerCase():null,oc[b]=f),e}:function(a,b,c){return c?void 0:a[m.camelCase("default-"+b)]?b.toLowerCase():null}}),rc&&qc||(m.attrHooks.value={set:function(a,b,c){return m.nodeName(a,"input")?void(a.defaultValue=b):mc&&mc.set(a,b,c)}}),qc||(mc={set:function(a,b,c){var d=a.getAttributeNode(c);return d||a.setAttributeNode(d=a.ownerDocument.createAttribute(c)),d.value=b+="","value"===c||b===a.getAttribute(c)?b:void 0}},oc.id=oc.name=oc.coords=function(a,b,c){var d;return c?void 0:(d=a.getAttributeNode(b))&&""!==d.value?d.value:null},m.valHooks.button={get:function(a,b){var c=a.getAttributeNode(b);return c&&c.specified?c.value:void 0},set:mc.set},m.attrHooks.contenteditable={set:function(a,b,c){mc.set(a,""===b?!1:b,c)}},m.each(["width","height"],function(a,b){m.attrHooks[b]={set:function(a,c){return""===c?(a.setAttribute(b,"auto"),c):void 0}}})),k.style||(m.attrHooks.style={get:function(a){return a.style.cssText||void 0},set:function(a,b){return a.style.cssText=b+""}});var sc=/^(?:input|select|textarea|button|object)$/i,tc=/^(?:a|area)$/i;m.fn.extend({prop:function(a,b){return V(this,m.prop,a,b,arguments.length>1)},removeProp:function(a){return a=m.propFix[a]||a,this.each(function(){try{this[a]=void 0,delete this[a]}catch(b){}})}}),m.extend({propFix:{"for":"htmlFor","class":"className"},prop:function(a,b,c){var d,e,f,g=a.nodeType;if(a&&3!==g&&8!==g&&2!==g)return f=1!==g||!m.isXMLDoc(a),f&&(b=m.propFix[b]||b,e=m.propHooks[b]),void 0!==c?e&&"set"in e&&void 0!==(d=e.set(a,c,b))?d:a[b]=c:e&&"get"in e&&null!==(d=e.get(a,b))?d:a[b]},propHooks:{tabIndex:{get:function(a){var b=m.find.attr(a,"tabindex");return b?parseInt(b,10):sc.test(a.nodeName)||tc.test(a.nodeName)&&a.href?0:-1}}}}),k.hrefNormalized||m.each(["href","src"],function(a,b){m.propHooks[b]={get:function(a){return a.getAttribute(b,4)}}}),k.optSelected||(m.propHooks.selected={get:function(a){var b=a.parentNode;return b&&(b.selectedIndex,b.parentNode&&b.parentNode.selectedIndex),null}}),m.each(["tabIndex","readOnly","maxLength","cellSpacing","cellPadding","rowSpan","colSpan","useMap","frameBorder","contentEditable"],function(){m.propFix[this.toLowerCase()]=this}),k.enctype||(m.propFix.enctype="encoding");var uc=/[\t\r\n\f]/g;m.fn.extend({addClass:function(a){var b,c,d,e,f,g,h=0,i=this.length,j="string"==typeof a&&a;if(m.isFunction(a))return this.each(function(b){m(this).addClass(a.call(this,b,this.className))});if(j)for(b=(a||"").match(E)||[];i>h;h++)if(c=this[h],d=1===c.nodeType&&(c.className?(" "+c.className+" ").replace(uc," "):" ")){f=0;while(e=b[f++])d.indexOf(" "+e+" ")<0&&(d+=e+" ");g=m.trim(d),c.className!==g&&(c.className=g)}return this},removeClass:function(a){var b,c,d,e,f,g,h=0,i=this.length,j=0===arguments.length||"string"==typeof a&&a;if(m.isFunction(a))return this.each(function(b){m(this).removeClass(a.call(this,b,this.className))});if(j)for(b=(a||"").match(E)||[];i>h;h++)if(c=this[h],d=1===c.nodeType&&(c.className?(" "+c.className+" ").replace(uc," "):"")){f=0;while(e=b[f++])while(d.indexOf(" "+e+" ")>=0)d=d.replace(" "+e+" "," ");g=a?m.trim(d):"",c.className!==g&&(c.className=g)}return this},toggleClass:function(a,b){var c=typeof a;return"boolean"==typeof b&&"string"===c?b?this.addClass(a):this.removeClass(a):this.each(m.isFunction(a)?function(c){m(this).toggleClass(a.call(this,c,this.className,b),b)}:function(){if("string"===c){var b,d=0,e=m(this),f=a.match(E)||[];while(b=f[d++])e.hasClass(b)?e.removeClass(b):e.addClass(b)}else(c===K||"boolean"===c)&&(this.className&&m._data(this,"__className__",this.className),this.className=this.className||a===!1?"":m._data(this,"__className__")||"")})},hasClass:function(a){for(var b=" "+a+" ",c=0,d=this.length;d>c;c++)if(1===this[c].nodeType&&(" "+this[c].className+" ").replace(uc," ").indexOf(b)>=0)return!0;return!1}}),m.each("blur focus focusin focusout load resize scroll unload click dblclick mousedown mouseup mousemove mouseover mouseout mouseenter mouseleave change select submit keydown keypress keyup error contextmenu".split(" "),function(a,b){m.fn[b]=function(a,c){return arguments.length>0?this.on(b,null,a,c):this.trigger(b)}}),m.fn.extend({hover:function(a,b){return this.mouseenter(a).mouseleave(b||a)},bind:function(a,b,c){return this.on(a,null,b,c)},unbind:function(a,b){return this.off(a,null,b)},delegate:function(a,b,c,d){return this.on(b,a,c,d)},undelegate:function(a,b,c){return 1===arguments.length?this.off(a,"**"):this.off(b,a||"**",c)}});var vc=m.now(),wc=/\?/,xc=/(,)|(\[|{)|(}|])|"(?:[^"\\\r\n]|\\["\\\/bfnrt]|\\u[\da-fA-F]{4})*"\s*:?|true|false|null|-?(?!0\d)\d+(?:\.\d+|)(?:[eE][+-]?\d+|)/g;m.parseJSON=function(b){if(a.JSON&&a.JSON.parse)return a.JSON.parse(b+"");var c,d=null,e=m.trim(b+"");return e&&!m.trim(e.replace(xc,function(a,b,e,f){return c&&b&&(d=0),0===d?a:(c=e||b,d+=!f-!e,"")}))?Function("return "+e)():m.error("Invalid JSON: "+b)},m.parseXML=function(b){var c,d;if(!b||"string"!=typeof b)return null;try{a.DOMParser?(d=new DOMParser,c=d.parseFromString(b,"text/xml")):(c=new ActiveXObject("Microsoft.XMLDOM"),c.async="false",c.loadXML(b))}catch(e){c=void 0}return c&&c.documentElement&&!c.getElementsByTagName("parsererror").length||m.error("Invalid XML: "+b),c};var yc,zc,Ac=/#.*$/,Bc=/([?&])_=[^&]*/,Cc=/^(.*?):[ \t]*([^\r\n]*)\r?$/gm,Dc=/^(?:about|app|app-storage|.+-extension|file|res|widget):$/,Ec=/^(?:GET|HEAD)$/,Fc=/^\/\//,Gc=/^([\w.+-]+:)(?:\/\/(?:[^\/?#]*@|)([^\/?#:]*)(?::(\d+)|)|)/,Hc={},Ic={},Jc="*/".concat("*");try{zc=location.href}catch(Kc){zc=y.createElement("a"),zc.href="",zc=zc.href}yc=Gc.exec(zc.toLowerCase())||[];function Lc(a){return function(b,c){"string"!=typeof b&&(c=b,b="*");var d,e=0,f=b.toLowerCase().match(E)||[];if(m.isFunction(c))while(d=f[e++])"+"===d.charAt(0)?(d=d.slice(1)||"*",(a[d]=a[d]||[]).unshift(c)):(a[d]=a[d]||[]).push(c)}}function Mc(a,b,c,d){var e={},f=a===Ic;function g(h){var i;return e[h]=!0,m.each(a[h]||[],function(a,h){var j=h(b,c,d);return"string"!=typeof j||f||e[j]?f?!(i=j):void 0:(b.dataTypes.unshift(j),g(j),!1)}),i}return g(b.dataTypes[0])||!e["*"]&&g("*")}function Nc(a,b){var c,d,e=m.ajaxSettings.flatOptions||{};for(d in b)void 0!==b[d]&&((e[d]?a:c||(c={}))[d]=b[d]);return c&&m.extend(!0,a,c),a}function Oc(a,b,c){var d,e,f,g,h=a.contents,i=a.dataTypes;while("*"===i[0])i.shift(),void 0===e&&(e=a.mimeType||b.getResponseHeader("Content-Type"));if(e)for(g in h)if(h[g]&&h[g].test(e)){i.unshift(g);break}if(i[0]in c)f=i[0];else{for(g in c){if(!i[0]||a.converters[g+" "+i[0]]){f=g;break}d||(d=g)}f=f||d}return f?(f!==i[0]&&i.unshift(f),c[f]):void 0}function Pc(a,b,c,d){var e,f,g,h,i,j={},k=a.dataTypes.slice();if(k[1])for(g in a.converters)j[g.toLowerCase()]=a.converters[g];f=k.shift();while(f)if(a.responseFields[f]&&(c[a.responseFields[f]]=b),!i&&d&&a.dataFilter&&(b=a.dataFilter(b,a.dataType)),i=f,f=k.shift())if("*"===f)f=i;else if("*"!==i&&i!==f){if(g=j[i+" "+f]||j["* "+f],!g)for(e in j)if(h=e.split(" "),h[1]===f&&(g=j[i+" "+h[0]]||j["* "+h[0]])){g===!0?g=j[e]:j[e]!==!0&&(f=h[0],k.unshift(h[1]));break}if(g!==!0)if(g&&a["throws"])b=g(b);else try{b=g(b)}catch(l){return{state:"parsererror",error:g?l:"No conversion from "+i+" to "+f}}}return{state:"success",data:b}}m.extend({active:0,lastModified:{},etag:{},ajaxSettings:{url:zc,type:"GET",isLocal:Dc.test(yc[1]),global:!0,processData:!0,async:!0,contentType:"application/x-www-form-urlencoded; charset=UTF-8",accepts:{"*":Jc,text:"text/plain",html:"text/html",xml:"application/xml, text/xml",json:"application/json, text/javascript"},contents:{xml:/xml/,html:/html/,json:/json/},responseFields:{xml:"responseXML",text:"responseText",json:"responseJSON"},converters:{"* text":String,"text html":!0,"text json":m.parseJSON,"text xml":m.parseXML},flatOptions:{url:!0,context:!0}},ajaxSetup:function(a,b){return b?Nc(Nc(a,m.ajaxSettings),b):Nc(m.ajaxSettings,a)},ajaxPrefilter:Lc(Hc),ajaxTransport:Lc(Ic),ajax:function(a,b){"object"==typeof a&&(b=a,a=void 0),b=b||{};var c,d,e,f,g,h,i,j,k=m.ajaxSetup({},b),l=k.context||k,n=k.context&&(l.nodeType||l.jquery)?m(l):m.event,o=m.Deferred(),p=m.Callbacks("once memory"),q=k.statusCode||{},r={},s={},t=0,u="canceled",v={readyState:0,getResponseHeader:function(a){var b;if(2===t){if(!j){j={};while(b=Cc.exec(f))j[b[1].toLowerCase()]=b[2]}b=j[a.toLowerCase()]}return null==b?null:b},getAllResponseHeaders:function(){return 2===t?f:null},setRequestHeader:function(a,b){var c=a.toLowerCase();return t||(a=s[c]=s[c]||a,r[a]=b),this},overrideMimeType:function(a){return t||(k.mimeType=a),this},statusCode:function(a){var b;if(a)if(2>t)for(b in a)q[b]=[q[b],a[b]];else v.always(a[v.status]);return this},abort:function(a){var b=a||u;return i&&i.abort(b),x(0,b),this}};if(o.promise(v).complete=p.add,v.success=v.done,v.error=v.fail,k.url=((a||k.url||zc)+"").replace(Ac,"").replace(Fc,yc[1]+"//"),k.type=b.method||b.type||k.method||k.type,k.dataTypes=m.trim(k.dataType||"*").toLowerCase().match(E)||[""],null==k.crossDomain&&(c=Gc.exec(k.url.toLowerCase()),k.crossDomain=!(!c||c[1]===yc[1]&&c[2]===yc[2]&&(c[3]||("http:"===c[1]?"80":"443"))===(yc[3]||("http:"===yc[1]?"80":"443")))),k.data&&k.processData&&"string"!=typeof k.data&&(k.data=m.param(k.data,k.traditional)),Mc(Hc,k,b,v),2===t)return v;h=k.global,h&&0===m.active++&&m.event.trigger("ajaxStart"),k.type=k.type.toUpperCase(),k.hasContent=!Ec.test(k.type),e=k.url,k.hasContent||(k.data&&(e=k.url+=(wc.test(e)?"&":"?")+k.data,delete k.data),k.cache===!1&&(k.url=Bc.test(e)?e.replace(Bc,"$1_="+vc++):e+(wc.test(e)?"&":"?")+"_="+vc++)),k.ifModified&&(m.lastModified[e]&&v.setRequestHeader("If-Modified-Since",m.lastModified[e]),m.etag[e]&&v.setRequestHeader("If-None-Match",m.etag[e])),(k.data&&k.hasContent&&k.contentType!==!1||b.contentType)&&v.setRequestHeader("Content-Type",k.contentType),v.setRequestHeader("Accept",k.dataTypes[0]&&k.accepts[k.dataTypes[0]]?k.accepts[k.dataTypes[0]]+("*"!==k.dataTypes[0]?", "+Jc+"; q=0.01":""):k.accepts["*"]);for(d in k.headers)v.setRequestHeader(d,k.headers[d]);if(k.beforeSend&&(k.beforeSend.call(l,v,k)===!1||2===t))return v.abort();u="abort";for(d in{success:1,error:1,complete:1})v[d](k[d]);if(i=Mc(Ic,k,b,v)){v.readyState=1,h&&n.trigger("ajaxSend",[v,k]),k.async&&k.timeout>0&&(g=setTimeout(function(){v.abort("timeout")},k.timeout));try{t=1,i.send(r,x)}catch(w){if(!(2>t))throw w;x(-1,w)}}else x(-1,"No Transport");function x(a,b,c,d){var j,r,s,u,w,x=b;2!==t&&(t=2,g&&clearTimeout(g),i=void 0,f=d||"",v.readyState=a>0?4:0,j=a>=200&&300>a||304===a,c&&(u=Oc(k,v,c)),u=Pc(k,u,v,j),j?(k.ifModified&&(w=v.getResponseHeader("Last-Modified"),w&&(m.lastModified[e]=w),w=v.getResponseHeader("etag"),w&&(m.etag[e]=w)),204===a||"HEAD"===k.type?x="nocontent":304===a?x="notmodified":(x=u.state,r=u.data,s=u.error,j=!s)):(s=x,(a||!x)&&(x="error",0>a&&(a=0))),v.status=a,v.statusText=(b||x)+"",j?o.resolveWith(l,[r,x,v]):o.rejectWith(l,[v,x,s]),v.statusCode(q),q=void 0,h&&n.trigger(j?"ajaxSuccess":"ajaxError",[v,k,j?r:s]),p.fireWith(l,[v,x]),h&&(n.trigger("ajaxComplete",[v,k]),--m.active||m.event.trigger("ajaxStop")))}return v},getJSON:function(a,b,c){return m.get(a,b,c,"json")},getScript:function(a,b){return m.get(a,void 0,b,"script")}}),m.each(["get","post"],function(a,b){m[b]=function(a,c,d,e){return m.isFunction(c)&&(e=e||d,d=c,c=void 0),m.ajax({url:a,type:b,dataType:e,data:c,success:d})}}),m.each(["ajaxStart","ajaxStop","ajaxComplete","ajaxError","ajaxSuccess","ajaxSend"],function(a,b){m.fn[b]=function(a){return this.on(b,a)}}),m._evalUrl=function(a){return m.ajax({url:a,type:"GET",dataType:"script",async:!1,global:!1,"throws":!0})},m.fn.extend({wrapAll:function(a){if(m.isFunction(a))return this.each(function(b){m(this).wrapAll(a.call(this,b))});if(this[0]){var b=m(a,this[0].ownerDocument).eq(0).clone(!0);this[0].parentNode&&b.insertBefore(this[0]),b.map(function(){var a=this;while(a.firstChild&&1===a.firstChild.nodeType)a=a.firstChild;return a}).append(this)}return this},wrapInner:function(a){return this.each(m.isFunction(a)?function(b){m(this).wrapInner(a.call(this,b))}:function(){var b=m(this),c=b.contents();c.length?c.wrapAll(a):b.append(a)})},wrap:function(a){var b=m.isFunction(a);return this.each(function(c){m(this).wrapAll(b?a.call(this,c):a)})},unwrap:function(){return this.parent().each(function(){m.nodeName(this,"body")||m(this).replaceWith(this.childNodes)}).end()}}),m.expr.filters.hidden=function(a){return a.offsetWidth<=0&&a.offsetHeight<=0||!k.reliableHiddenOffsets()&&"none"===(a.style&&a.style.display||m.css(a,"display"))},m.expr.filters.visible=function(a){return!m.expr.filters.hidden(a)};var Qc=/%20/g,Rc=/\[\]$/,Sc=/\r?\n/g,Tc=/^(?:submit|button|image|reset|file)$/i,Uc=/^(?:input|select|textarea|keygen)/i;function Vc(a,b,c,d){var e;if(m.isArray(b))m.each(b,function(b,e){c||Rc.test(a)?d(a,e):Vc(a+"["+("object"==typeof e?b:"")+"]",e,c,d)});else if(c||"object"!==m.type(b))d(a,b);else for(e in b)Vc(a+"["+e+"]",b[e],c,d)}m.param=function(a,b){var c,d=[],e=function(a,b){b=m.isFunction(b)?b():null==b?"":b,d[d.length]=encodeURIComponent(a)+"="+encodeURIComponent(b)};if(void 0===b&&(b=m.ajaxSettings&&m.ajaxSettings.traditional),m.isArray(a)||a.jquery&&!m.isPlainObject(a))m.each(a,function(){e(this.name,this.value)});else for(c in a)Vc(c,a[c],b,e);return d.join("&").replace(Qc,"+")},m.fn.extend({serialize:function(){return m.param(this.serializeArray())},serializeArray:function(){return this.map(function(){var a=m.prop(this,"elements");return a?m.makeArray(a):this}).filter(function(){var a=this.type;return this.name&&!m(this).is(":disabled")&&Uc.test(this.nodeName)&&!Tc.test(a)&&(this.checked||!W.test(a))}).map(function(a,b){var c=m(this).val();return null==c?null:m.isArray(c)?m.map(c,function(a){return{name:b.name,value:a.replace(Sc,"\r\n")}}):{name:b.name,value:c.replace(Sc,"\r\n")}}).get()}}),m.ajaxSettings.xhr=void 0!==a.ActiveXObject?function(){return!this.isLocal&&/^(get|post|head|put|delete|options)$/i.test(this.type)&&Zc()||$c()}:Zc;var Wc=0,Xc={},Yc=m.ajaxSettings.xhr();a.ActiveXObject&&m(a).on("unload",function(){for(var a in Xc)Xc[a](void 0,!0)}),k.cors=!!Yc&&"withCredentials"in Yc,Yc=k.ajax=!!Yc,Yc&&m.ajaxTransport(function(a){if(!a.crossDomain||k.cors){var b;return{send:function(c,d){var e,f=a.xhr(),g=++Wc;if(f.open(a.type,a.url,a.async,a.username,a.password),a.xhrFields)for(e in a.xhrFields)f[e]=a.xhrFields[e];a.mimeType&&f.overrideMimeType&&f.overrideMimeType(a.mimeType),a.crossDomain||c["X-Requested-With"]||(c["X-Requested-With"]="XMLHttpRequest");for(e in c)void 0!==c[e]&&f.setRequestHeader(e,c[e]+"");f.send(a.hasContent&&a.data||null),b=function(c,e){var h,i,j;if(b&&(e||4===f.readyState))if(delete Xc[g],b=void 0,f.onreadystatechange=m.noop,e)4!==f.readyState&&f.abort();else{j={},h=f.status,"string"==typeof f.responseText&&(j.text=f.responseText);try{i=f.statusText}catch(k){i=""}h||!a.isLocal||a.crossDomain?1223===h&&(h=204):h=j.text?200:404}j&&d(h,i,j,f.getAllResponseHeaders())},a.async?4===f.readyState?setTimeout(b):f.onreadystatechange=Xc[g]=b:b()},abort:function(){b&&b(void 0,!0)}}}});function Zc(){try{return new a.XMLHttpRequest}catch(b){}}function $c(){try{return new a.ActiveXObject("Microsoft.XMLHTTP")}catch(b){}}m.ajaxSetup({accepts:{script:"text/javascript, application/javascript, application/ecmascript, application/x-ecmascript"},contents:{script:/(?:java|ecma)script/},converters:{"text script":function(a){return m.globalEval(a),a}}}),m.ajaxPrefilter("script",function(a){void 0===a.cache&&(a.cache=!1),a.crossDomain&&(a.type="GET",a.global=!1)}),m.ajaxTransport("script",function(a){if(a.crossDomain){var b,c=y.head||m("head")[0]||y.documentElement;return{send:function(d,e){b=y.createElement("script"),b.async=!0,a.scriptCharset&&(b.charset=a.scriptCharset),b.src=a.url,b.onload=b.onreadystatechange=function(a,c){(c||!b.readyState||/loaded|complete/.test(b.readyState))&&(b.onload=b.onreadystatechange=null,b.parentNode&&b.parentNode.removeChild(b),b=null,c||e(200,"success"))},c.insertBefore(b,c.firstChild)},abort:function(){b&&b.onload(void 0,!0)}}}});var _c=[],ad=/(=)\?(?=&|$)|\?\?/;m.ajaxSetup({jsonp:"callback",jsonpCallback:function(){var a=_c.pop()||m.expando+"_"+vc++;return this[a]=!0,a}}),m.ajaxPrefilter("json jsonp",function(b,c,d){var e,f,g,h=b.jsonp!==!1&&(ad.test(b.url)?"url":"string"==typeof b.data&&!(b.contentType||"").indexOf("application/x-www-form-urlencoded")&&ad.test(b.data)&&"data");return h||"jsonp"===b.dataTypes[0]?(e=b.jsonpCallback=m.isFunction(b.jsonpCallback)?b.jsonpCallback():b.jsonpCallback,h?b[h]=b[h].replace(ad,"$1"+e):b.jsonp!==!1&&(b.url+=(wc.test(b.url)?"&":"?")+b.jsonp+"="+e),b.converters["script json"]=function(){return g||m.error(e+" was not called"),g[0]},b.dataTypes[0]="json",f=a[e],a[e]=function(){g=arguments},d.always(function(){a[e]=f,b[e]&&(b.jsonpCallback=c.jsonpCallback,_c.push(e)),g&&m.isFunction(f)&&f(g[0]),g=f=void 0}),"script"):void 0}),m.parseHTML=function(a,b,c){if(!a||"string"!=typeof a)return null;"boolean"==typeof b&&(c=b,b=!1),b=b||y;var d=u.exec(a),e=!c&&[];return d?[b.createElement(d[1])]:(d=m.buildFragment([a],b,e),e&&e.length&&m(e).remove(),m.merge([],d.childNodes))};var bd=m.fn.load;m.fn.load=function(a,b,c){if("string"!=typeof a&&bd)return bd.apply(this,arguments);var d,e,f,g=this,h=a.indexOf(" ");return h>=0&&(d=m.trim(a.slice(h,a.length)),a=a.slice(0,h)),m.isFunction(b)?(c=b,b=void 0):b&&"object"==typeof b&&(f="POST"),g.length>0&&m.ajax({url:a,type:f,dataType:"html",data:b}).done(function(a){e=arguments,g.html(d?m("<div>").append(m.parseHTML(a)).find(d):a)}).complete(c&&function(a,b){g.each(c,e||[a.responseText,b,a])}),this},m.expr.filters.animated=function(a){return m.grep(m.timers,function(b){return a===b.elem}).length};var cd=a.document.documentElement;function dd(a){return m.isWindow(a)?a:9===a.nodeType?a.defaultView||a.parentWindow:!1}m.offset={setOffset:function(a,b,c){var d,e,f,g,h,i,j,k=m.css(a,"position"),l=m(a),n={};"static"===k&&(a.style.position="relative"),h=l.offset(),f=m.css(a,"top"),i=m.css(a,"left"),j=("absolute"===k||"fixed"===k)&&m.inArray("auto",[f,i])>-1,j?(d=l.position(),g=d.top,e=d.left):(g=parseFloat(f)||0,e=parseFloat(i)||0),m.isFunction(b)&&(b=b.call(a,c,h)),null!=b.top&&(n.top=b.top-h.top+g),null!=b.left&&(n.left=b.left-h.left+e),"using"in b?b.using.call(a,n):l.css(n)}},m.fn.extend({offset:function(a){if(arguments.length)return void 0===a?this:this.each(function(b){m.offset.setOffset(this,a,b)});var b,c,d={top:0,left:0},e=this[0],f=e&&e.ownerDocument;if(f)return b=f.documentElement,m.contains(b,e)?(typeof e.getBoundingClientRect!==K&&(d=e.getBoundingClientRect()),c=dd(f),{top:d.top+(c.pageYOffset||b.scrollTop)-(b.clientTop||0),left:d.left+(c.pageXOffset||b.scrollLeft)-(b.clientLeft||0)}):d},position:function(){if(this[0]){var a,b,c={top:0,left:0},d=this[0];return"fixed"===m.css(d,"position")?b=d.getBoundingClientRect():(a=this.offsetParent(),b=this.offset(),m.nodeName(a[0],"html")||(c=a.offset()),c.top+=m.css(a[0],"borderTopWidth",!0),c.left+=m.css(a[0],"borderLeftWidth",!0)),{top:b.top-c.top-m.css(d,"marginTop",!0),left:b.left-c.left-m.css(d,"marginLeft",!0)}}},offsetParent:function(){return this.map(function(){var a=this.offsetParent||cd;while(a&&!m.nodeName(a,"html")&&"static"===m.css(a,"position"))a=a.offsetParent;return a||cd})}}),m.each({scrollLeft:"pageXOffset",scrollTop:"pageYOffset"},function(a,b){var c=/Y/.test(b);m.fn[a]=function(d){return V(this,function(a,d,e){var f=dd(a);return void 0===e?f?b in f?f[b]:f.document.documentElement[d]:a[d]:void(f?f.scrollTo(c?m(f).scrollLeft():e,c?e:m(f).scrollTop()):a[d]=e)},a,d,arguments.length,null)}}),m.each(["top","left"],function(a,b){m.cssHooks[b]=Lb(k.pixelPosition,function(a,c){return c?(c=Jb(a,b),Hb.test(c)?m(a).position()[b]+"px":c):void 0})}),m.each({Height:"height",Width:"width"},function(a,b){m.each({padding:"inner"+a,content:b,"":"outer"+a},function(c,d){m.fn[d]=function(d,e){var f=arguments.length&&(c||"boolean"!=typeof d),g=c||(d===!0||e===!0?"margin":"border");return V(this,function(b,c,d){var e;return m.isWindow(b)?b.document.documentElement["client"+a]:9===b.nodeType?(e=b.documentElement,Math.max(b.body["scroll"+a],e["scroll"+a],b.body["offset"+a],e["offset"+a],e["client"+a])):void 0===d?m.css(b,c,g):m.style(b,c,d,g)},b,f?d:void 0,f,null)}})}),m.fn.size=function(){return this.length},m.fn.andSelf=m.fn.addBack,"function"==typeof define&&define.amd&&define("jquery",[],function(){return m});var ed=a.jQuery,fd=a.$;return m.noConflict=function(b){return a.$===m&&(a.$=fd),b&&a.jQuery===m&&(a.jQuery=ed),m},typeof b===K&&(a.jQuery=a.$=m),m});



// /*!
//  * jQuery JavaScript Library v1.5
//  * http://jquery.com/
//  *
//  * Copyright 2011, John Resig
//  * Dual licensed under the MIT or GPL Version 2 licenses.
//  * http://jquery.org/license
//  *
//  * Includes Sizzle.js
//  * http://sizzlejs.com/
//  * Copyright 2011, The Dojo Foundation
//  * Released under the MIT, BSD, and GPL Licenses.
//  *
//  * Date: Mon Jan 31 08:31:29 2011 -0500
//  */
// (function( window, undefined ) {

// // Use the correct document accordingly with window argument (sandbox)
// var document = window.document;
// var jQuery = (function() {

// // Define a local copy of jQuery
// var jQuery = function( selector, context ) {
// 		// The jQuery object is actually just the init constructor 'enhanced'
// 		return new jQuery.fn.init( selector, context, rootjQuery );
// 	},

// 	// Map over jQuery in case of overwrite
// 	_jQuery = window.jQuery,

// 	// Map over the $ in case of overwrite
// 	_$ = window.$,

// 	// A central reference to the root jQuery(document)
// 	rootjQuery,

// 	// A simple way to check for HTML strings or ID strings
// 	// (both of which we optimize for)
// 	quickExpr = /^(?:[^<]*(<[\w\W]+>)[^>]*$|#([\w\-]+)$)/,

// 	// Check if a string has a non-whitespace character in it
// 	rnotwhite = /\S/,

// 	// Used for trimming whitespace
// 	trimLeft = /^\s+/,
// 	trimRight = /\s+$/,

// 	// Check for digits
// 	rdigit = /\d/,

// 	// Match a standalone tag
// 	rsingleTag = /^<(\w+)\s*\/?>(?:<\/\1>)?$/,

// 	// JSON RegExp
// 	rvalidchars = /^[\],:{}\s]*$/,
// 	rvalidescape = /\\(?:["\\\/bfnrt]|u[0-9a-fA-F]{4})/g,
// 	rvalidtokens = /"[^"\\\n\r]*"|true|false|null|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?/g,
// 	rvalidbraces = /(?:^|:|,)(?:\s*\[)+/g,

// 	// Useragent RegExp
// 	rwebkit = /(webkit)[ \/]([\w.]+)/,
// 	ropera = /(opera)(?:.*version)?[ \/]([\w.]+)/,
// 	rmsie = /(msie) ([\w.]+)/,
// 	rmozilla = /(mozilla)(?:.*? rv:([\w.]+))?/,

// 	// Keep a UserAgent string for use with jQuery.browser
// 	userAgent = navigator.userAgent,

// 	// For matching the engine and version of the browser
// 	browserMatch,

// 	// Has the ready events already been bound?
// 	readyBound = false,

// 	// The deferred used on DOM ready
// 	readyList,

// 	// Promise methods
// 	promiseMethods = "then done fail isResolved isRejected promise".split( " " ),

// 	// The ready event handler
// 	DOMContentLoaded,

// 	// Save a reference to some core methods
// 	toString = Object.prototype.toString,
// 	hasOwn = Object.prototype.hasOwnProperty,
// 	push = Array.prototype.push,
// 	slice = Array.prototype.slice,
// 	trim = String.prototype.trim,
// 	indexOf = Array.prototype.indexOf,

// 	// [[Class]] -> type pairs
// 	class2type = {};

// jQuery.fn = jQuery.prototype = {
// 	constructor: jQuery,
// 	init: function( selector, context, rootjQuery ) {
// 		var match, elem, ret, doc;

// 		// Handle $(""), $(null), or $(undefined)
// 		if ( !selector ) {
// 			return this;
// 		}

// 		// Handle $(DOMElement)
// 		if ( selector.nodeType ) {
// 			this.context = this[0] = selector;
// 			this.length = 1;
// 			return this;
// 		}

// 		// The body element only exists once, optimize finding it
// 		if ( selector === "body" && !context && document.body ) {
// 			this.context = document;
// 			this[0] = document.body;
// 			this.selector = "body";
// 			this.length = 1;
// 			return this;
// 		}

// 		// Handle HTML strings
// 		if ( typeof selector === "string" ) {
// 			// Are we dealing with HTML string or an ID?
// 			match = quickExpr.exec( selector );

// 			// Verify a match, and that no context was specified for #id
// 			if ( match && (match[1] || !context) ) {

// 				// HANDLE: $(html) -> $(array)
// 				if ( match[1] ) {
// 					context = context instanceof jQuery ? context[0] : context;
// 					doc = (context ? context.ownerDocument || context : document);

// 					// If a single string is passed in and it's a single tag
// 					// just do a createElement and skip the rest
// 					ret = rsingleTag.exec( selector );

// 					if ( ret ) {
// 						if ( jQuery.isPlainObject( context ) ) {
// 							selector = [ document.createElement( ret[1] ) ];
// 							jQuery.fn.attr.call( selector, context, true );

// 						} else {
// 							selector = [ doc.createElement( ret[1] ) ];
// 						}

// 					} else {
// 						ret = jQuery.buildFragment( [ match[1] ], [ doc ] );
// 						selector = (ret.cacheable ? jQuery.clone(ret.fragment) : ret.fragment).childNodes;
// 					}

// 					return jQuery.merge( this, selector );

// 				// HANDLE: $("#id")
// 				} else {
// 					elem = document.getElementById( match[2] );

// 					// Check parentNode to catch when Blackberry 4.6 returns
// 					// nodes that are no longer in the document #6963
// 					if ( elem && elem.parentNode ) {
// 						// Handle the case where IE and Opera return items
// 						// by name instead of ID
// 						if ( elem.id !== match[2] ) {
// 							return rootjQuery.find( selector );
// 						}

// 						// Otherwise, we inject the element directly into the jQuery object
// 						this.length = 1;
// 						this[0] = elem;
// 					}

// 					this.context = document;
// 					this.selector = selector;
// 					return this;
// 				}

// 			// HANDLE: $(expr, $(...))
// 			} else if ( !context || context.jquery ) {
// 				return (context || rootjQuery).find( selector );

// 			// HANDLE: $(expr, context)
// 			// (which is just equivalent to: $(context).find(expr)
// 			} else {
// 				return this.constructor( context ).find( selector );
// 			}

// 		// HANDLE: $(function)
// 		// Shortcut for document ready
// 		} else if ( jQuery.isFunction( selector ) ) {
// 			return rootjQuery.ready( selector );
// 		}

// 		if (selector.selector !== undefined) {
// 			this.selector = selector.selector;
// 			this.context = selector.context;
// 		}

// 		return jQuery.makeArray( selector, this );
// 	},

// 	// Start with an empty selector
// 	selector: "",

// 	// The current version of jQuery being used
// 	jquery: "1.5",

// 	// The default length of a jQuery object is 0
// 	length: 0,

// 	// The number of elements contained in the matched element set
// 	size: function() {
// 		return this.length;
// 	},

// 	toArray: function() {
// 		return slice.call( this, 0 );
// 	},

// 	// Get the Nth element in the matched element set OR
// 	// Get the whole matched element set as a clean array
// 	get: function( num ) {
// 		return num == null ?

// 			// Return a 'clean' array
// 			this.toArray() :

// 			// Return just the object
// 			( num < 0 ? this[ this.length + num ] : this[ num ] );
// 	},

// 	// Take an array of elements and push it onto the stack
// 	// (returning the new matched element set)
// 	pushStack: function( elems, name, selector ) {
// 		// Build a new jQuery matched element set
// 		var ret = this.constructor();

// 		if ( jQuery.isArray( elems ) ) {
// 			push.apply( ret, elems );

// 		} else {
// 			jQuery.merge( ret, elems );
// 		}

// 		// Add the old object onto the stack (as a reference)
// 		ret.prevObject = this;

// 		ret.context = this.context;

// 		if ( name === "find" ) {
// 			ret.selector = this.selector + (this.selector ? " " : "") + selector;
// 		} else if ( name ) {
// 			ret.selector = this.selector + "." + name + "(" + selector + ")";
// 		}

// 		// Return the newly-formed element set
// 		return ret;
// 	},

// 	// Execute a callback for every element in the matched set.
// 	// (You can seed the arguments with an array of args, but this is
// 	// only used internally.)
// 	each: function( callback, args ) {
// 		return jQuery.each( this, callback, args );
// 	},

// 	ready: function( fn ) {
// 		// Attach the listeners
// 		jQuery.bindReady();

// 		// Add the callback
// 		readyList.done( fn );

// 		return this;
// 	},

// 	eq: function( i ) {
// 		return i === -1 ?
// 			this.slice( i ) :
// 			this.slice( i, +i + 1 );
// 	},

// 	first: function() {
// 		return this.eq( 0 );
// 	},

// 	last: function() {
// 		return this.eq( -1 );
// 	},

// 	slice: function() {
// 		return this.pushStack( slice.apply( this, arguments ),
// 			"slice", slice.call(arguments).join(",") );
// 	},

// 	map: function( callback ) {
// 		return this.pushStack( jQuery.map(this, function( elem, i ) {
// 			return callback.call( elem, i, elem );
// 		}));
// 	},

// 	end: function() {
// 		return this.prevObject || this.constructor(null);
// 	},

// 	// For internal use only.
// 	// Behaves like an Array's method, not like a jQuery method.
// 	push: push,
// 	sort: [].sort,
// 	splice: [].splice
// };

// // Give the init function the jQuery prototype for later instantiation
// jQuery.fn.init.prototype = jQuery.fn;

// jQuery.extend = jQuery.fn.extend = function() {
// 	 var options, name, src, copy, copyIsArray, clone,
// 		target = arguments[0] || {},
// 		i = 1,
// 		length = arguments.length,
// 		deep = false;

// 	// Handle a deep copy situation
// 	if ( typeof target === "boolean" ) {
// 		deep = target;
// 		target = arguments[1] || {};
// 		// skip the boolean and the target
// 		i = 2;
// 	}

// 	// Handle case when target is a string or something (possible in deep copy)
// 	if ( typeof target !== "object" && !jQuery.isFunction(target) ) {
// 		target = {};
// 	}

// 	// extend jQuery itself if only one argument is passed
// 	if ( length === i ) {
// 		target = this;
// 		--i;
// 	}

// 	for ( ; i < length; i++ ) {
// 		// Only deal with non-null/undefined values
// 		if ( (options = arguments[ i ]) != null ) {
// 			// Extend the base object
// 			for ( name in options ) {
// 				src = target[ name ];
// 				copy = options[ name ];

// 				// Prevent never-ending loop
// 				if ( target === copy ) {
// 					continue;
// 				}

// 				// Recurse if we're merging plain objects or arrays
// 				if ( deep && copy && ( jQuery.isPlainObject(copy) || (copyIsArray = jQuery.isArray(copy)) ) ) {
// 					if ( copyIsArray ) {
// 						copyIsArray = false;
// 						clone = src && jQuery.isArray(src) ? src : [];

// 					} else {
// 						clone = src && jQuery.isPlainObject(src) ? src : {};
// 					}

// 					// Never move original objects, clone them
// 					target[ name ] = jQuery.extend( deep, clone, copy );

// 				// Don't bring in undefined values
// 				} else if ( copy !== undefined ) {
// 					target[ name ] = copy;
// 				}
// 			}
// 		}
// 	}

// 	// Return the modified object
// 	return target;
// };

// jQuery.extend({
// 	noConflict: function( deep ) {
// 		window.$ = _$;

// 		if ( deep ) {
// 			window.jQuery = _jQuery;
// 		}

// 		return jQuery;
// 	},

// 	// Is the DOM ready to be used? Set to true once it occurs.
// 	isReady: false,

// 	// A counter to track how many items to wait for before
// 	// the ready event fires. See #6781
// 	readyWait: 1,

// 	// Handle when the DOM is ready
// 	ready: function( wait ) {
// 		// A third-party is pushing the ready event forwards
// 		if ( wait === true ) {
// 			jQuery.readyWait--;
// 		}

// 		// Make sure that the DOM is not already loaded
// 		if ( !jQuery.readyWait || (wait !== true && !jQuery.isReady) ) {
// 			// Make sure body exists, at least, in case IE gets a little overzealous (ticket #5443).
// 			if ( !document.body ) {
// 				return setTimeout( jQuery.ready, 1 );
// 			}

// 			// Remember that the DOM is ready
// 			jQuery.isReady = true;

// 			// If a normal DOM Ready event fired, decrement, and wait if need be
// 			if ( wait !== true && --jQuery.readyWait > 0 ) {
// 				return;
// 			}

// 			// If there are functions bound, to execute
// 			readyList.resolveWith( document, [ jQuery ] );

// 			// Trigger any bound ready events
// 			if ( jQuery.fn.trigger ) {
// 				jQuery( document ).trigger( "ready" ).unbind( "ready" );
// 			}
// 		}
// 	},

// 	bindReady: function() {
// 		if ( readyBound ) {
// 			return;
// 		}

// 		readyBound = true;

// 		// Catch cases where $(document).ready() is called after the
// 		// browser event has already occurred.
// 		if ( document.readyState === "complete" ) {
// 			// Handle it asynchronously to allow scripts the opportunity to delay ready
// 			return setTimeout( jQuery.ready, 1 );
// 		}

// 		// Mozilla, Opera and webkit nightlies currently support this event
// 		if ( document.addEventListener ) {
// 			// Use the handy event callback
// 			document.addEventListener( "DOMContentLoaded", DOMContentLoaded, false );

// 			// A fallback to window.onload, that will always work
// 			window.addEventListener( "load", jQuery.ready, false );

// 		// If IE event model is used
// 		} else if ( document.attachEvent ) {
// 			// ensure firing before onload,
// 			// maybe late but safe also for iframes
// 			document.attachEvent("onreadystatechange", DOMContentLoaded);

// 			// A fallback to window.onload, that will always work
// 			window.attachEvent( "onload", jQuery.ready );

// 			// If IE and not a frame
// 			// continually check to see if the document is ready
// 			var toplevel = false;

// 			try {
// 				toplevel = window.frameElement == null;
// 			} catch(e) {}

// 			if ( document.documentElement.doScroll && toplevel ) {
// 				doScrollCheck();
// 			}
// 		}
// 	},

// 	// See test/unit/core.js for details concerning isFunction.
// 	// Since version 1.3, DOM methods and functions like alert
// 	// aren't supported. They return false on IE (#2968).
// 	isFunction: function( obj ) {
// 		return jQuery.type(obj) === "function";
// 	},

// 	isArray: Array.isArray || function( obj ) {
// 		return jQuery.type(obj) === "array";
// 	},

// 	// A crude way of determining if an object is a window
// 	isWindow: function( obj ) {
// 		return obj && typeof obj === "object" && "setInterval" in obj;
// 	},

// 	isNaN: function( obj ) {
// 		return obj == null || !rdigit.test( obj ) || isNaN( obj );
// 	},

// 	type: function( obj ) {
// 		return obj == null ?
// 			String( obj ) :
// 			class2type[ toString.call(obj) ] || "object";
// 	},

// 	isPlainObject: function( obj ) {
// 		// Must be an Object.
// 		// Because of IE, we also have to check the presence of the constructor property.
// 		// Make sure that DOM nodes and window objects don't pass through, as well
// 		if ( !obj || jQuery.type(obj) !== "object" || obj.nodeType || jQuery.isWindow( obj ) ) {
// 			return false;
// 		}

// 		// Not own constructor property must be Object
// 		if ( obj.constructor &&
// 			!hasOwn.call(obj, "constructor") &&
// 			!hasOwn.call(obj.constructor.prototype, "isPrototypeOf") ) {
// 			return false;
// 		}

// 		// Own properties are enumerated firstly, so to speed up,
// 		// if last one is own, then all properties are own.

// 		var key;
// 		for ( key in obj ) {}

// 		return key === undefined || hasOwn.call( obj, key );
// 	},

// 	isEmptyObject: function( obj ) {
// 		for ( var name in obj ) {
// 			return false;
// 		}
// 		return true;
// 	},

// 	error: function( msg ) {
// 		throw msg;
// 	},

// 	parseJSON: function( data ) {
// 		if ( typeof data !== "string" || !data ) {
// 			return null;
// 		}

// 		// Make sure leading/trailing whitespace is removed (IE can't handle it)
// 		data = jQuery.trim( data );

// 		// Make sure the incoming data is actual JSON
// 		// Logic borrowed from http://json.org/json2.js
// 		if ( rvalidchars.test(data.replace(rvalidescape, "@")
// 			.replace(rvalidtokens, "]")
// 			.replace(rvalidbraces, "")) ) {

// 			// Try to use the native JSON parser first
// 			return window.JSON && window.JSON.parse ?
// 				window.JSON.parse( data ) :
// 				(new Function("return " + data))();

// 		} else {
// 			jQuery.error( "Invalid JSON: " + data );
// 		}
// 	},

// 	// Cross-browser xml parsing
// 	// (xml & tmp used internally)
// 	parseXML: function( data , xml , tmp ) {

// 		if ( window.DOMParser ) { // Standard
// 			tmp = new DOMParser();
// 			xml = tmp.parseFromString( data , "text/xml" );
// 		} else { // IE
// 			xml = new ActiveXObject( "Microsoft.XMLDOM" );
// 			xml.async = "false";
// 			xml.loadXML( data );
// 		}

// 		tmp = xml.documentElement;

// 		if ( ! tmp || ! tmp.nodeName || tmp.nodeName === "parsererror" ) {
// 			jQuery.error( "Invalid XML: " + data );
// 		}

// 		return xml;
// 	},

// 	noop: function() {},

// 	// Evalulates a script in a global context
// 	globalEval: function( data ) {
// 		if ( data && rnotwhite.test(data) ) {
// 			// Inspired by code by Andrea Giammarchi
// 			// http://webreflection.blogspot.com/2007/08/global-scope-evaluation-and-dom.html
// 			var head = document.getElementsByTagName("head")[0] || document.documentElement,
// 				script = document.createElement("script");

// 			script.type = "text/javascript";

// 			if ( jQuery.support.scriptEval() ) {
// 				script.appendChild( document.createTextNode( data ) );
// 			} else {
// 				script.text = data;
// 			}

// 			// Use insertBefore instead of appendChild to circumvent an IE6 bug.
// 			// This arises when a base node is used (#2709).
// 			head.insertBefore( script, head.firstChild );
// 			head.removeChild( script );
// 		}
// 	},

// 	nodeName: function( elem, name ) {
// 		return elem.nodeName && elem.nodeName.toUpperCase() === name.toUpperCase();
// 	},

// 	// args is for internal usage only
// 	each: function( object, callback, args ) {
// 		var name, i = 0,
// 			length = object.length,
// 			isObj = length === undefined || jQuery.isFunction(object);

// 		if ( args ) {
// 			if ( isObj ) {
// 				for ( name in object ) {
// 					if ( callback.apply( object[ name ], args ) === false ) {
// 						break;
// 					}
// 				}
// 			} else {
// 				for ( ; i < length; ) {
// 					if ( callback.apply( object[ i++ ], args ) === false ) {
// 						break;
// 					}
// 				}
// 			}

// 		// A special, fast, case for the most common use of each
// 		} else {
// 			if ( isObj ) {
// 				for ( name in object ) {
// 					if ( callback.call( object[ name ], name, object[ name ] ) === false ) {
// 						break;
// 					}
// 				}
// 			} else {
// 				for ( var value = object[0];
// 					i < length && callback.call( value, i, value ) !== false; value = object[++i] ) {}
// 			}
// 		}

// 		return object;
// 	},

// 	// Use native String.trim function wherever possible
// 	trim: trim ?
// 		function( text ) {
// 			return text == null ?
// 				"" :
// 				trim.call( text );
// 		} :

// 		// Otherwise use our own trimming functionality
// 		function( text ) {
// 			return text == null ?
// 				"" :
// 				text.toString().replace( trimLeft, "" ).replace( trimRight, "" );
// 		},

// 	// results is for internal usage only
// 	makeArray: function( array, results ) {
// 		var ret = results || [];

// 		if ( array != null ) {
// 			// The window, strings (and functions) also have 'length'
// 			// The extra typeof function check is to prevent crashes
// 			// in Safari 2 (See: #3039)
// 			// Tweaked logic slightly to handle Blackberry 4.7 RegExp issues #6930
// 			var type = jQuery.type(array);

// 			if ( array.length == null || type === "string" || type === "function" || type === "regexp" || jQuery.isWindow( array ) ) {
// 				push.call( ret, array );
// 			} else {
// 				jQuery.merge( ret, array );
// 			}
// 		}

// 		return ret;
// 	},

// 	inArray: function( elem, array ) {
// 		if ( array.indexOf ) {
// 			return array.indexOf( elem );
// 		}

// 		for ( var i = 0, length = array.length; i < length; i++ ) {
// 			if ( array[ i ] === elem ) {
// 				return i;
// 			}
// 		}

// 		return -1;
// 	},

// 	merge: function( first, second ) {
// 		var i = first.length,
// 			j = 0;

// 		if ( typeof second.length === "number" ) {
// 			for ( var l = second.length; j < l; j++ ) {
// 				first[ i++ ] = second[ j ];
// 			}

// 		} else {
// 			while ( second[j] !== undefined ) {
// 				first[ i++ ] = second[ j++ ];
// 			}
// 		}

// 		first.length = i;

// 		return first;
// 	},

// 	grep: function( elems, callback, inv ) {
// 		var ret = [], retVal;
// 		inv = !!inv;

// 		// Go through the array, only saving the items
// 		// that pass the validator function
// 		for ( var i = 0, length = elems.length; i < length; i++ ) {
// 			retVal = !!callback( elems[ i ], i );
// 			if ( inv !== retVal ) {
// 				ret.push( elems[ i ] );
// 			}
// 		}

// 		return ret;
// 	},

// 	// arg is for internal usage only
// 	map: function( elems, callback, arg ) {
// 		var ret = [], value;

// 		// Go through the array, translating each of the items to their
// 		// new value (or values).
// 		for ( var i = 0, length = elems.length; i < length; i++ ) {
// 			value = callback( elems[ i ], i, arg );

// 			if ( value != null ) {
// 				ret[ ret.length ] = value;
// 			}
// 		}

// 		// Flatten any nested arrays
// 		return ret.concat.apply( [], ret );
// 	},

// 	// A global GUID counter for objects
// 	guid: 1,

// 	proxy: function( fn, proxy, thisObject ) {
// 		if ( arguments.length === 2 ) {
// 			if ( typeof proxy === "string" ) {
// 				thisObject = fn;
// 				fn = thisObject[ proxy ];
// 				proxy = undefined;

// 			} else if ( proxy && !jQuery.isFunction( proxy ) ) {
// 				thisObject = proxy;
// 				proxy = undefined;
// 			}
// 		}

// 		if ( !proxy && fn ) {
// 			proxy = function() {
// 				return fn.apply( thisObject || this, arguments );
// 			};
// 		}

// 		// Set the guid of unique handler to the same of original handler, so it can be removed
// 		if ( fn ) {
// 			proxy.guid = fn.guid = fn.guid || proxy.guid || jQuery.guid++;
// 		}

// 		// So proxy can be declared as an argument
// 		return proxy;
// 	},

// 	// Mutifunctional method to get and set values to a collection
// 	// The value/s can be optionally by executed if its a function
// 	access: function( elems, key, value, exec, fn, pass ) {
// 		var length = elems.length;

// 		// Setting many attributes
// 		if ( typeof key === "object" ) {
// 			for ( var k in key ) {
// 				jQuery.access( elems, k, key[k], exec, fn, value );
// 			}
// 			return elems;
// 		}

// 		// Setting one attribute
// 		if ( value !== undefined ) {
// 			// Optionally, function values get executed if exec is true
// 			exec = !pass && exec && jQuery.isFunction(value);

// 			for ( var i = 0; i < length; i++ ) {
// 				fn( elems[i], key, exec ? value.call( elems[i], i, fn( elems[i], key ) ) : value, pass );
// 			}

// 			return elems;
// 		}

// 		// Getting an attribute
// 		return length ? fn( elems[0], key ) : undefined;
// 	},

// 	now: function() {
// 		return (new Date()).getTime();
// 	},

// 	// Create a simple deferred (one callbacks list)
// 	_Deferred: function() {
// 		var // callbacks list
// 			callbacks = [],
// 			// stored [ context , args ]
// 			fired,
// 			// to avoid firing when already doing so
// 			firing,
// 			// flag to know if the deferred has been cancelled
// 			cancelled,
// 			// the deferred itself
// 			deferred  = {

// 				// done( f1, f2, ...)
// 				done: function() {
// 					if ( !cancelled ) {
// 						var args = arguments,
// 							i,
// 							length,
// 							elem,
// 							type,
// 							_fired;
// 						if ( fired ) {
// 							_fired = fired;
// 							fired = 0;
// 						}
// 						for ( i = 0, length = args.length; i < length; i++ ) {
// 							elem = args[ i ];
// 							type = jQuery.type( elem );
// 							if ( type === "array" ) {
// 								deferred.done.apply( deferred, elem );
// 							} else if ( type === "function" ) {
// 								callbacks.push( elem );
// 							}
// 						}
// 						if ( _fired ) {
// 							deferred.resolveWith( _fired[ 0 ], _fired[ 1 ] );
// 						}
// 					}
// 					return this;
// 				},

// 				// resolve with given context and args
// 				resolveWith: function( context, args ) {
// 					if ( !cancelled && !fired && !firing ) {
// 						firing = 1;
// 						try {
// 							while( callbacks[ 0 ] ) {
// 								callbacks.shift().apply( context, args );
// 							}
// 						}
// 						finally {
// 							fired = [ context, args ];
// 							firing = 0;
// 						}
// 					}
// 					return this;
// 				},

// 				// resolve with this as context and given arguments
// 				resolve: function() {
// 					deferred.resolveWith( jQuery.isFunction( this.promise ) ? this.promise() : this, arguments );
// 					return this;
// 				},

// 				// Has this deferred been resolved?
// 				isResolved: function() {
// 					return !!( firing || fired );
// 				},

// 				// Cancel
// 				cancel: function() {
// 					cancelled = 1;
// 					callbacks = [];
// 					return this;
// 				}
// 			};

// 		return deferred;
// 	},

// 	// Full fledged deferred (two callbacks list)
// 	Deferred: function( func ) {
// 		var deferred = jQuery._Deferred(),
// 			failDeferred = jQuery._Deferred(),
// 			promise;
// 		// Add errorDeferred methods, then and promise
// 		jQuery.extend( deferred, {
// 			then: function( doneCallbacks, failCallbacks ) {
// 				deferred.done( doneCallbacks ).fail( failCallbacks );
// 				return this;
// 			},
// 			fail: failDeferred.done,
// 			rejectWith: failDeferred.resolveWith,
// 			reject: failDeferred.resolve,
// 			isRejected: failDeferred.isResolved,
// 			// Get a promise for this deferred
// 			// If obj is provided, the promise aspect is added to the object
// 			promise: function( obj , i /* internal */ ) {
// 				if ( obj == null ) {
// 					if ( promise ) {
// 						return promise;
// 					}
// 					promise = obj = {};
// 				}
// 				i = promiseMethods.length;
// 				while( i-- ) {
// 					obj[ promiseMethods[ i ] ] = deferred[ promiseMethods[ i ] ];
// 				}
// 				return obj;
// 			}
// 		} );
// 		// Make sure only one callback list will be used
// 		deferred.then( failDeferred.cancel, deferred.cancel );
// 		// Unexpose cancel
// 		delete deferred.cancel;
// 		// Call given func if any
// 		if ( func ) {
// 			func.call( deferred, deferred );
// 		}
// 		return deferred;
// 	},

// 	// Deferred helper
// 	when: function( object ) {
// 		var args = arguments,
// 			length = args.length,
// 			deferred = length <= 1 && object && jQuery.isFunction( object.promise ) ?
// 				object :
// 				jQuery.Deferred(),
// 			promise = deferred.promise(),
// 			resolveArray;

// 		if ( length > 1 ) {
// 			resolveArray = new Array( length );
// 			jQuery.each( args, function( index, element ) {
// 				jQuery.when( element ).then( function( value ) {
// 					resolveArray[ index ] = arguments.length > 1 ? slice.call( arguments, 0 ) : value;
// 					if( ! --length ) {
// 						deferred.resolveWith( promise, resolveArray );
// 					}
// 				}, deferred.reject );
// 			} );
// 		} else if ( deferred !== object ) {
// 			deferred.resolve( object );
// 		}
// 		return promise;
// 	},

// 	// Use of jQuery.browser is frowned upon.
// 	// More details: http://docs.jquery.com/Utilities/jQuery.browser
// 	uaMatch: function( ua ) {
// 		ua = ua.toLowerCase();

// 		var match = rwebkit.exec( ua ) ||
// 			ropera.exec( ua ) ||
// 			rmsie.exec( ua ) ||
// 			ua.indexOf("compatible") < 0 && rmozilla.exec( ua ) ||
// 			[];

// 		return { browser: match[1] || "", version: match[2] || "0" };
// 	},

// 	sub: function() {
// 		function jQuerySubclass( selector, context ) {
// 			return new jQuerySubclass.fn.init( selector, context );
// 		}
// 		jQuery.extend( true, jQuerySubclass, this );
// 		jQuerySubclass.superclass = this;
// 		jQuerySubclass.fn = jQuerySubclass.prototype = this();
// 		jQuerySubclass.fn.constructor = jQuerySubclass;
// 		jQuerySubclass.subclass = this.subclass;
// 		jQuerySubclass.fn.init = function init( selector, context ) {
// 			if ( context && context instanceof jQuery && !(context instanceof jQuerySubclass) ) {
// 				context = jQuerySubclass(context);
// 			}

// 			return jQuery.fn.init.call( this, selector, context, rootjQuerySubclass );
// 		};
// 		jQuerySubclass.fn.init.prototype = jQuerySubclass.fn;
// 		var rootjQuerySubclass = jQuerySubclass(document);
// 		return jQuerySubclass;
// 	},

// 	browser: {}
// });

// // Create readyList deferred
// readyList = jQuery._Deferred();

// // Populate the class2type map
// jQuery.each("Boolean Number String Function Array Date RegExp Object".split(" "), function(i, name) {
// 	class2type[ "[object " + name + "]" ] = name.toLowerCase();
// });

// browserMatch = jQuery.uaMatch( userAgent );
// if ( browserMatch.browser ) {
// 	jQuery.browser[ browserMatch.browser ] = true;
// 	jQuery.browser.version = browserMatch.version;
// }

// // Deprecated, use jQuery.browser.webkit instead
// if ( jQuery.browser.webkit ) {
// 	jQuery.browser.safari = true;
// }

// if ( indexOf ) {
// 	jQuery.inArray = function( elem, array ) {
// 		return indexOf.call( array, elem );
// 	};
// }

// // IE doesn't match non-breaking spaces with \s
// if ( rnotwhite.test( "\xA0" ) ) {
// 	trimLeft = /^[\s\xA0]+/;
// 	trimRight = /[\s\xA0]+$/;
// }

// // All jQuery objects should point back to these
// rootjQuery = jQuery(document);

// // Cleanup functions for the document ready method
// if ( document.addEventListener ) {
// 	DOMContentLoaded = function() {
// 		document.removeEventListener( "DOMContentLoaded", DOMContentLoaded, false );
// 		jQuery.ready();
// 	};

// } else if ( document.attachEvent ) {
// 	DOMContentLoaded = function() {
// 		// Make sure body exists, at least, in case IE gets a little overzealous (ticket #5443).
// 		if ( document.readyState === "complete" ) {
// 			document.detachEvent( "onreadystatechange", DOMContentLoaded );
// 			jQuery.ready();
// 		}
// 	};
// }

// // The DOM ready check for Internet Explorer
// function doScrollCheck() {
// 	if ( jQuery.isReady ) {
// 		return;
// 	}

// 	try {
// 		// If IE is used, use the trick by Diego Perini
// 		// http://javascript.nwbox.com/IEContentLoaded/
// 		document.documentElement.doScroll("left");
// 	} catch(e) {
// 		setTimeout( doScrollCheck, 1 );
// 		return;
// 	}

// 	// and execute any waiting functions
// 	jQuery.ready();
// }

// // Expose jQuery to the global object
// return (window.jQuery = window.$ = jQuery);

// })();


// (function() {

// 	jQuery.support = {};

// 	var div = document.createElement("div");

// 	div.style.display = "none";
// 	div.innerHTML = "   <link/><table></table><a href='/a' style='color:red;float:left;opacity:.55;'>a</a><input type='checkbox'/>";

// 	var all = div.getElementsByTagName("*"),
// 		a = div.getElementsByTagName("a")[0],
// 		select = document.createElement("select"),
// 		opt = select.appendChild( document.createElement("option") );

// 	// Can't get basic test support
// 	if ( !all || !all.length || !a ) {
// 		return;
// 	}

// 	jQuery.support = {
// 		// IE strips leading whitespace when .innerHTML is used
// 		leadingWhitespace: div.firstChild.nodeType === 3,

// 		// Make sure that tbody elements aren't automatically inserted
// 		// IE will insert them into empty tables
// 		tbody: !div.getElementsByTagName("tbody").length,

// 		// Make sure that link elements get serialized correctly by innerHTML
// 		// This requires a wrapper element in IE
// 		htmlSerialize: !!div.getElementsByTagName("link").length,

// 		// Get the style information from getAttribute
// 		// (IE uses .cssText insted)
// 		style: /red/.test( a.getAttribute("style") ),

// 		// Make sure that URLs aren't manipulated
// 		// (IE normalizes it by default)
// 		hrefNormalized: a.getAttribute("href") === "/a",

// 		// Make sure that element opacity exists
// 		// (IE uses filter instead)
// 		// Use a regex to work around a WebKit issue. See #5145
// 		opacity: /^0.55$/.test( a.style.opacity ),

// 		// Verify style float existence
// 		// (IE uses styleFloat instead of cssFloat)
// 		cssFloat: !!a.style.cssFloat,

// 		// Make sure that if no value is specified for a checkbox
// 		// that it defaults to "on".
// 		// (WebKit defaults to "" instead)
// 		checkOn: div.getElementsByTagName("input")[0].value === "on",

// 		// Make sure that a selected-by-default option has a working selected property.
// 		// (WebKit defaults to false instead of true, IE too, if it's in an optgroup)
// 		optSelected: opt.selected,

// 		// Will be defined later
// 		deleteExpando: true,
// 		optDisabled: false,
// 		checkClone: false,
// 		_scriptEval: null,
// 		noCloneEvent: true,
// 		boxModel: null,
// 		inlineBlockNeedsLayout: false,
// 		shrinkWrapBlocks: false,
// 		reliableHiddenOffsets: true
// 	};

// 	// Make sure that the options inside disabled selects aren't marked as disabled
// 	// (WebKit marks them as diabled)
// 	select.disabled = true;
// 	jQuery.support.optDisabled = !opt.disabled;

// 	jQuery.support.scriptEval = function() {
// 		if ( jQuery.support._scriptEval === null ) {
// 			var root = document.documentElement,
// 				script = document.createElement("script"),
// 				id = "script" + jQuery.now();

// 			script.type = "text/javascript";
// 			try {
// 				script.appendChild( document.createTextNode( "window." + id + "=1;" ) );
// 			} catch(e) {}

// 			root.insertBefore( script, root.firstChild );

// 			// Make sure that the execution of code works by injecting a script
// 			// tag with appendChild/createTextNode
// 			// (IE doesn't support this, fails, and uses .text instead)
// 			if ( window[ id ] ) {
// 				jQuery.support._scriptEval = true;
// 				delete window[ id ];
// 			} else {
// 				jQuery.support._scriptEval = false;
// 			}

// 			root.removeChild( script );
// 			// release memory in IE
// 			root = script = id  = null;
// 		}

// 		return jQuery.support._scriptEval;
// 	};

// 	// Test to see if it's possible to delete an expando from an element
// 	// Fails in Internet Explorer
// 	try {
// 		delete div.test;

// 	} catch(e) {
// 		jQuery.support.deleteExpando = false;
// 	}

// 	if ( div.attachEvent && div.fireEvent ) {
// 		div.attachEvent("onclick", function click() {
// 			// Cloning a node shouldn't copy over any
// 			// bound event handlers (IE does this)
// 			jQuery.support.noCloneEvent = false;
// 			div.detachEvent("onclick", click);
// 		});
// 		div.cloneNode(true).fireEvent("onclick");
// 	}

// 	div = document.createElement("div");
// 	div.innerHTML = "<input type='radio' name='radiotest' checked='checked'/>";

// 	var fragment = document.createDocumentFragment();
// 	fragment.appendChild( div.firstChild );

// 	// WebKit doesn't clone checked state correctly in fragments
// 	jQuery.support.checkClone = fragment.cloneNode(true).cloneNode(true).lastChild.checked;

// 	// Figure out if the W3C box model works as expected
// 	// document.body must exist before we can do this
// 	jQuery(function() {
// 		var div = document.createElement("div"),
// 			body = document.getElementsByTagName("body")[0];

// 		// Frameset documents with no body should not run this code
// 		if ( !body ) {
// 			return;
// 		}

// 		div.style.width = div.style.paddingLeft = "1px";
// 		body.appendChild( div );
// 		jQuery.boxModel = jQuery.support.boxModel = div.offsetWidth === 2;

// 		if ( "zoom" in div.style ) {
// 			// Check if natively block-level elements act like inline-block
// 			// elements when setting their display to 'inline' and giving
// 			// them layout
// 			// (IE < 8 does this)
// 			div.style.display = "inline";
// 			div.style.zoom = 1;
// 			jQuery.support.inlineBlockNeedsLayout = div.offsetWidth === 2;

// 			// Check if elements with layout shrink-wrap their children
// 			// (IE 6 does this)
// 			div.style.display = "";
// 			div.innerHTML = "<div style='width:4px;'></div>";
// 			jQuery.support.shrinkWrapBlocks = div.offsetWidth !== 2;
// 		}

// 		div.innerHTML = "<table><tr><td style='padding:0;border:0;display:none'></td><td>t</td></tr></table>";
// 		var tds = div.getElementsByTagName("td");

// 		// Check if table cells still have offsetWidth/Height when they are set
// 		// to display:none and there are still other visible table cells in a
// 		// table row; if so, offsetWidth/Height are not reliable for use when
// 		// determining if an element has been hidden directly using
// 		// display:none (it is still safe to use offsets if a parent element is
// 		// hidden; don safety goggles and see bug #4512 for more information).
// 		// (only IE 8 fails this test)
// 		jQuery.support.reliableHiddenOffsets = tds[0].offsetHeight === 0;

// 		tds[0].style.display = "";
// 		tds[1].style.display = "none";

// 		// Check if empty table cells still have offsetWidth/Height
// 		// (IE < 8 fail this test)
// 		jQuery.support.reliableHiddenOffsets = jQuery.support.reliableHiddenOffsets && tds[0].offsetHeight === 0;
// 		div.innerHTML = "";

// 		body.removeChild( div ).style.display = "none";
// 		div = tds = null;
// 	});

// 	// Technique from Juriy Zaytsev
// 	// http://thinkweb2.com/projects/prototype/detecting-event-support-without-browser-sniffing/
// 	var eventSupported = function( eventName ) {
// 		var el = document.createElement("div");
// 		eventName = "on" + eventName;

// 		// We only care about the case where non-standard event systems
// 		// are used, namely in IE. Short-circuiting here helps us to
// 		// avoid an eval call (in setAttribute) which can cause CSP
// 		// to go haywire. See: https://developer.mozilla.org/en/Security/CSP
// 		if ( !el.attachEvent ) {
// 			return true;
// 		}

// 		var isSupported = (eventName in el);
// 		if ( !isSupported ) {
// 			el.setAttribute(eventName, "return;");
// 			isSupported = typeof el[eventName] === "function";
// 		}
// 		el = null;

// 		return isSupported;
// 	};

// 	jQuery.support.submitBubbles = eventSupported("submit");
// 	jQuery.support.changeBubbles = eventSupported("change");

// 	// release memory in IE
// 	div = all = a = null;
// })();



// var rbrace = /^(?:\{.*\}|\[.*\])$/;

// jQuery.extend({
// 	cache: {},

// 	// Please use with caution
// 	uuid: 0,

// 	// Unique for each copy of jQuery on the page
// 	// Non-digits removed to match rinlinejQuery
// 	expando: "jQuery" + ( jQuery.fn.jquery + Math.random() ).replace( /\D/g, "" ),

// 	// The following elements throw uncatchable exceptions if you
// 	// attempt to add expando properties to them.
// 	noData: {
// 		"embed": true,
// 		// Ban all objects except for Flash (which handle expandos)
// 		"object": "clsid:D27CDB6E-AE6D-11cf-96B8-444553540000",
// 		"applet": true
// 	},

// 	hasData: function( elem ) {
// 		elem = elem.nodeType ? jQuery.cache[ elem[jQuery.expando] ] : elem[ jQuery.expando ];

// 		return !!elem && !jQuery.isEmptyObject(elem);
// 	},

// 	data: function( elem, name, data, pvt /* Internal Use Only */ ) {
// 		if ( !jQuery.acceptData( elem ) ) {
// 			return;
// 		}

// 		var internalKey = jQuery.expando, getByName = typeof name === "string", thisCache,

// 			// We have to handle DOM nodes and JS objects differently because IE6-7
// 			// can't GC object references properly across the DOM-JS boundary
// 			isNode = elem.nodeType,

// 			// Only DOM nodes need the global jQuery cache; JS object data is
// 			// attached directly to the object so GC can occur automatically
// 			cache = isNode ? jQuery.cache : elem,

// 			// Only defining an ID for JS objects if its cache already exists allows
// 			// the code to shortcut on the same path as a DOM node with no cache
// 			id = isNode ? elem[ jQuery.expando ] : elem[ jQuery.expando ] && jQuery.expando;

// 		// Avoid doing any more work than we need to when trying to get data on an
// 		// object that has no data at all
// 		if ( (!id || (pvt && id && !cache[ id ][ internalKey ])) && getByName && data === undefined ) {
// 			return;
// 		}

// 		if ( !id ) {
// 			// Only DOM nodes need a new unique ID for each element since their data
// 			// ends up in the global cache
// 			if ( isNode ) {
// 				elem[ jQuery.expando ] = id = ++jQuery.uuid;
// 			} else {
// 				id = jQuery.expando;
// 			}
// 		}

// 		if ( !cache[ id ] ) {
// 			cache[ id ] = {};
// 		}

// 		// An object can be passed to jQuery.data instead of a key/value pair; this gets
// 		// shallow copied over onto the existing cache
// 		if ( typeof name === "object" ) {
// 			if ( pvt ) {
// 				cache[ id ][ internalKey ] = jQuery.extend(cache[ id ][ internalKey ], name);
// 			} else {
// 				cache[ id ] = jQuery.extend(cache[ id ], name);
// 			}
// 		}

// 		thisCache = cache[ id ];

// 		// Internal jQuery data is stored in a separate object inside the object's data
// 		// cache in order to avoid key collisions between internal data and user-defined
// 		// data
// 		if ( pvt ) {
// 			if ( !thisCache[ internalKey ] ) {
// 				thisCache[ internalKey ] = {};
// 			}

// 			thisCache = thisCache[ internalKey ];
// 		}

// 		if ( data !== undefined ) {
// 			thisCache[ name ] = data;
// 		}

// 		// TODO: This is a hack for 1.5 ONLY. It will be removed in 1.6. Users should
// 		// not attempt to inspect the internal events object using jQuery.data, as this
// 		// internal data object is undocumented and subject to change.
// 		if ( name === "events" && !thisCache[name] ) {
// 			return thisCache[ internalKey ] && thisCache[ internalKey ].events;
// 		}

// 		return getByName ? thisCache[ name ] : thisCache;
// 	},

// 	removeData: function( elem, name, pvt /* Internal Use Only */ ) {
// 		if ( !jQuery.acceptData( elem ) ) {
// 			return;
// 		}

// 		var internalKey = jQuery.expando, isNode = elem.nodeType,

// 			// See jQuery.data for more information
// 			cache = isNode ? jQuery.cache : elem,

// 			// See jQuery.data for more information
// 			id = isNode ? elem[ jQuery.expando ] : jQuery.expando;

// 		// If there is already no cache entry for this object, there is no
// 		// purpose in continuing
// 		if ( !cache[ id ] ) {
// 			return;
// 		}

// 		if ( name ) {
// 			var thisCache = pvt ? cache[ id ][ internalKey ] : cache[ id ];

// 			if ( thisCache ) {
// 				delete thisCache[ name ];

// 				// If there is no data left in the cache, we want to continue
// 				// and let the cache object itself get destroyed
// 				if ( !jQuery.isEmptyObject(thisCache) ) {
// 					return;
// 				}
// 			}
// 		}

// 		// See jQuery.data for more information
// 		if ( pvt ) {
// 			delete cache[ id ][ internalKey ];

// 			// Don't destroy the parent cache unless the internal data object
// 			// had been the only thing left in it
// 			if ( !jQuery.isEmptyObject(cache[ id ]) ) {
// 				return;
// 			}
// 		}

// 		var internalCache = cache[ id ][ internalKey ];

// 		// Browsers that fail expando deletion also refuse to delete expandos on
// 		// the window, but it will allow it on all other JS objects; other browsers
// 		// don't care
// 		if ( jQuery.support.deleteExpando || cache != window ) {
// 			delete cache[ id ];
// 		} else {
// 			cache[ id ] = null;
// 		}

// 		// We destroyed the entire user cache at once because it's faster than
// 		// iterating through each key, but we need to continue to persist internal
// 		// data if it existed
// 		if ( internalCache ) {
// 			cache[ id ] = {};
// 			cache[ id ][ internalKey ] = internalCache;

// 		// Otherwise, we need to eliminate the expando on the node to avoid
// 		// false lookups in the cache for entries that no longer exist
// 		} else if ( isNode ) {
// 			// IE does not allow us to delete expando properties from nodes,
// 			// nor does it have a removeAttribute function on Document nodes;
// 			// we must handle all of these cases
// 			if ( jQuery.support.deleteExpando ) {
// 				delete elem[ jQuery.expando ];
// 			} else if ( elem.removeAttribute ) {
// 				elem.removeAttribute( jQuery.expando );
// 			} else {
// 				elem[ jQuery.expando ] = null;
// 			}
// 		}
// 	},

// 	// For internal use only.
// 	_data: function( elem, name, data ) {
// 		return jQuery.data( elem, name, data, true );
// 	},

// 	// A method for determining if a DOM node can handle the data expando
// 	acceptData: function( elem ) {
// 		if ( elem.nodeName ) {
// 			var match = jQuery.noData[ elem.nodeName.toLowerCase() ];

// 			if ( match ) {
// 				return !(match === true || elem.getAttribute("classid") !== match);
// 			}
// 		}

// 		return true;
// 	}
// });

// jQuery.fn.extend({
// 	data: function( key, value ) {
// 		var data = null;

// 		if ( typeof key === "undefined" ) {
// 			if ( this.length ) {
// 				data = jQuery.data( this[0] );

// 				if ( this[0].nodeType === 1 ) {
// 					var attr = this[0].attributes, name;
// 					for ( var i = 0, l = attr.length; i < l; i++ ) {
// 						name = attr[i].name;

// 						if ( name.indexOf( "data-" ) === 0 ) {
// 							name = name.substr( 5 );
// 							dataAttr( this[0], name, data[ name ] );
// 						}
// 					}
// 				}
// 			}

// 			return data;

// 		} else if ( typeof key === "object" ) {
// 			return this.each(function() {
// 				jQuery.data( this, key );
// 			});
// 		}

// 		var parts = key.split(".");
// 		parts[1] = parts[1] ? "." + parts[1] : "";

// 		if ( value === undefined ) {
// 			data = this.triggerHandler("getData" + parts[1] + "!", [parts[0]]);

// 			// Try to fetch any internally stored data first
// 			if ( data === undefined && this.length ) {
// 				data = jQuery.data( this[0], key );
// 				data = dataAttr( this[0], key, data );
// 			}

// 			return data === undefined && parts[1] ?
// 				this.data( parts[0] ) :
// 				data;

// 		} else {
// 			return this.each(function() {
// 				var $this = jQuery( this ),
// 					args = [ parts[0], value ];

// 				$this.triggerHandler( "setData" + parts[1] + "!", args );
// 				jQuery.data( this, key, value );
// 				$this.triggerHandler( "changeData" + parts[1] + "!", args );
// 			});
// 		}
// 	},

// 	removeData: function( key ) {
// 		return this.each(function() {
// 			jQuery.removeData( this, key );
// 		});
// 	}
// });

// function dataAttr( elem, key, data ) {
// 	// If nothing was found internally, try to fetch any
// 	// data from the HTML5 data-* attribute
// 	if ( data === undefined && elem.nodeType === 1 ) {
// 		data = elem.getAttribute( "data-" + key );

// 		if ( typeof data === "string" ) {
// 			try {
// 				data = data === "true" ? true :
// 				data === "false" ? false :
// 				data === "null" ? null :
// 				!jQuery.isNaN( data ) ? parseFloat( data ) :
// 					rbrace.test( data ) ? jQuery.parseJSON( data ) :
// 					data;
// 			} catch( e ) {}

// 			// Make sure we set the data so it isn't changed later
// 			jQuery.data( elem, key, data );

// 		} else {
// 			data = undefined;
// 		}
// 	}

// 	return data;
// }




// jQuery.extend({
// 	queue: function( elem, type, data ) {
// 		if ( !elem ) {
// 			return;
// 		}

// 		type = (type || "fx") + "queue";
// 		var q = jQuery._data( elem, type );

// 		// Speed up dequeue by getting out quickly if this is just a lookup
// 		if ( !data ) {
// 			return q || [];
// 		}

// 		if ( !q || jQuery.isArray(data) ) {
// 			q = jQuery._data( elem, type, jQuery.makeArray(data) );

// 		} else {
// 			q.push( data );
// 		}

// 		return q;
// 	},

// 	dequeue: function( elem, type ) {
// 		type = type || "fx";

// 		var queue = jQuery.queue( elem, type ),
// 			fn = queue.shift();

// 		// If the fx queue is dequeued, always remove the progress sentinel
// 		if ( fn === "inprogress" ) {
// 			fn = queue.shift();
// 		}

// 		if ( fn ) {
// 			// Add a progress sentinel to prevent the fx queue from being
// 			// automatically dequeued
// 			if ( type === "fx" ) {
// 				queue.unshift("inprogress");
// 			}

// 			fn.call(elem, function() {
// 				jQuery.dequeue(elem, type);
// 			});
// 		}

// 		if ( !queue.length ) {
// 			jQuery.removeData( elem, type + "queue", true );
// 		}
// 	}
// });

// jQuery.fn.extend({
// 	queue: function( type, data ) {
// 		if ( typeof type !== "string" ) {
// 			data = type;
// 			type = "fx";
// 		}

// 		if ( data === undefined ) {
// 			return jQuery.queue( this[0], type );
// 		}
// 		return this.each(function( i ) {
// 			var queue = jQuery.queue( this, type, data );

// 			if ( type === "fx" && queue[0] !== "inprogress" ) {
// 				jQuery.dequeue( this, type );
// 			}
// 		});
// 	},
// 	dequeue: function( type ) {
// 		return this.each(function() {
// 			jQuery.dequeue( this, type );
// 		});
// 	},

// 	// Based off of the plugin by Clint Helfers, with permission.
// 	// http://blindsignals.com/index.php/2009/07/jquery-delay/
// 	delay: function( time, type ) {
// 		time = jQuery.fx ? jQuery.fx.speeds[time] || time : time;
// 		type = type || "fx";

// 		return this.queue( type, function() {
// 			var elem = this;
// 			setTimeout(function() {
// 				jQuery.dequeue( elem, type );
// 			}, time );
// 		});
// 	},

// 	clearQueue: function( type ) {
// 		return this.queue( type || "fx", [] );
// 	}
// });




// var rclass = /[\n\t\r]/g,
// 	rspaces = /\s+/,
// 	rreturn = /\r/g,
// 	rspecialurl = /^(?:href|src|style)$/,
// 	rtype = /^(?:button|input)$/i,
// 	rfocusable = /^(?:button|input|object|select|textarea)$/i,
// 	rclickable = /^a(?:rea)?$/i,
// 	rradiocheck = /^(?:radio|checkbox)$/i;

// jQuery.props = {
// 	"for": "htmlFor",
// 	"class": "className",
// 	readonly: "readOnly",
// 	maxlength: "maxLength",
// 	cellspacing: "cellSpacing",
// 	rowspan: "rowSpan",
// 	colspan: "colSpan",
// 	tabindex: "tabIndex",
// 	usemap: "useMap",
// 	frameborder: "frameBorder"
// };

// jQuery.fn.extend({
// 	attr: function( name, value ) {
// 		return jQuery.access( this, name, value, true, jQuery.attr );
// 	},

// 	removeAttr: function( name, fn ) {
// 		return this.each(function(){
// 			jQuery.attr( this, name, "" );
// 			if ( this.nodeType === 1 ) {
// 				this.removeAttribute( name );
// 			}
// 		});
// 	},

// 	addClass: function( value ) {
// 		if ( jQuery.isFunction(value) ) {
// 			return this.each(function(i) {
// 				var self = jQuery(this);
// 				self.addClass( value.call(this, i, self.attr("class")) );
// 			});
// 		}

// 		if ( value && typeof value === "string" ) {
// 			var classNames = (value || "").split( rspaces );

// 			for ( var i = 0, l = this.length; i < l; i++ ) {
// 				var elem = this[i];

// 				if ( elem.nodeType === 1 ) {
// 					if ( !elem.className ) {
// 						elem.className = value;

// 					} else {
// 						var className = " " + elem.className + " ",
// 							setClass = elem.className;

// 						for ( var c = 0, cl = classNames.length; c < cl; c++ ) {
// 							if ( className.indexOf( " " + classNames[c] + " " ) < 0 ) {
// 								setClass += " " + classNames[c];
// 							}
// 						}
// 						elem.className = jQuery.trim( setClass );
// 					}
// 				}
// 			}
// 		}

// 		return this;
// 	},

// 	removeClass: function( value ) {
// 		if ( jQuery.isFunction(value) ) {
// 			return this.each(function(i) {
// 				var self = jQuery(this);
// 				self.removeClass( value.call(this, i, self.attr("class")) );
// 			});
// 		}

// 		if ( (value && typeof value === "string") || value === undefined ) {
// 			var classNames = (value || "").split( rspaces );

// 			for ( var i = 0, l = this.length; i < l; i++ ) {
// 				var elem = this[i];

// 				if ( elem.nodeType === 1 && elem.className ) {
// 					if ( value ) {
// 						var className = (" " + elem.className + " ").replace(rclass, " ");
// 						for ( var c = 0, cl = classNames.length; c < cl; c++ ) {
// 							className = className.replace(" " + classNames[c] + " ", " ");
// 						}
// 						elem.className = jQuery.trim( className );

// 					} else {
// 						elem.className = "";
// 					}
// 				}
// 			}
// 		}

// 		return this;
// 	},

// 	toggleClass: function( value, stateVal ) {
// 		var type = typeof value,
// 			isBool = typeof stateVal === "boolean";

// 		if ( jQuery.isFunction( value ) ) {
// 			return this.each(function(i) {
// 				var self = jQuery(this);
// 				self.toggleClass( value.call(this, i, self.attr("class"), stateVal), stateVal );
// 			});
// 		}

// 		return this.each(function() {
// 			if ( type === "string" ) {
// 				// toggle individual class names
// 				var className,
// 					i = 0,
// 					self = jQuery( this ),
// 					state = stateVal,
// 					classNames = value.split( rspaces );

// 				while ( (className = classNames[ i++ ]) ) {
// 					// check each className given, space separated list
// 					state = isBool ? state : !self.hasClass( className );
// 					self[ state ? "addClass" : "removeClass" ]( className );
// 				}

// 			} else if ( type === "undefined" || type === "boolean" ) {
// 				if ( this.className ) {
// 					// store className if set
// 					jQuery._data( this, "__className__", this.className );
// 				}

// 				// toggle whole className
// 				this.className = this.className || value === false ? "" : jQuery._data( this, "__className__" ) || "";
// 			}
// 		});
// 	},

// 	hasClass: function( selector ) {
// 		var className = " " + selector + " ";
// 		for ( var i = 0, l = this.length; i < l; i++ ) {
// 			if ( (" " + this[i].className + " ").replace(rclass, " ").indexOf( className ) > -1 ) {
// 				return true;
// 			}
// 		}

// 		return false;
// 	},

// 	val: function( value ) {
// 		if ( !arguments.length ) {
// 			var elem = this[0];

// 			if ( elem ) {
// 				if ( jQuery.nodeName( elem, "option" ) ) {
// 					// attributes.value is undefined in Blackberry 4.7 but
// 					// uses .value. See #6932
// 					var val = elem.attributes.value;
// 					return !val || val.specified ? elem.value : elem.text;
// 				}

// 				// We need to handle select boxes special
// 				if ( jQuery.nodeName( elem, "select" ) ) {
// 					var index = elem.selectedIndex,
// 						values = [],
// 						options = elem.options,
// 						one = elem.type === "select-one";

// 					// Nothing was selected
// 					if ( index < 0 ) {
// 						return null;
// 					}

// 					// Loop through all the selected options
// 					for ( var i = one ? index : 0, max = one ? index + 1 : options.length; i < max; i++ ) {
// 						var option = options[ i ];

// 						// Don't return options that are disabled or in a disabled optgroup
// 						if ( option.selected && (jQuery.support.optDisabled ? !option.disabled : option.getAttribute("disabled") === null) &&
// 								(!option.parentNode.disabled || !jQuery.nodeName( option.parentNode, "optgroup" )) ) {

// 							// Get the specific value for the option
// 							value = jQuery(option).val();

// 							// We don't need an array for one selects
// 							if ( one ) {
// 								return value;
// 							}

// 							// Multi-Selects return an array
// 							values.push( value );
// 						}
// 					}

// 					return values;
// 				}

// 				// Handle the case where in Webkit "" is returned instead of "on" if a value isn't specified
// 				if ( rradiocheck.test( elem.type ) && !jQuery.support.checkOn ) {
// 					return elem.getAttribute("value") === null ? "on" : elem.value;
// 				}

// 				// Everything else, we just grab the value
// 				return (elem.value || "").replace(rreturn, "");

// 			}

// 			return undefined;
// 		}

// 		var isFunction = jQuery.isFunction(value);

// 		return this.each(function(i) {
// 			var self = jQuery(this), val = value;

// 			if ( this.nodeType !== 1 ) {
// 				return;
// 			}

// 			if ( isFunction ) {
// 				val = value.call(this, i, self.val());
// 			}

// 			// Treat null/undefined as ""; convert numbers to string
// 			if ( val == null ) {
// 				val = "";
// 			} else if ( typeof val === "number" ) {
// 				val += "";
// 			} else if ( jQuery.isArray(val) ) {
// 				val = jQuery.map(val, function (value) {
// 					return value == null ? "" : value + "";
// 				});
// 			}

// 			if ( jQuery.isArray(val) && rradiocheck.test( this.type ) ) {
// 				this.checked = jQuery.inArray( self.val(), val ) >= 0;

// 			} else if ( jQuery.nodeName( this, "select" ) ) {
// 				var values = jQuery.makeArray(val);

// 				jQuery( "option", this ).each(function() {
// 					this.selected = jQuery.inArray( jQuery(this).val(), values ) >= 0;
// 				});

// 				if ( !values.length ) {
// 					this.selectedIndex = -1;
// 				}

// 			} else {
// 				this.value = val;
// 			}
// 		});
// 	}
// });

// jQuery.extend({
// 	attrFn: {
// 		val: true,
// 		css: true,
// 		html: true,
// 		text: true,
// 		data: true,
// 		width: true,
// 		height: true,
// 		offset: true
// 	},

// 	attr: function( elem, name, value, pass ) {
// 		// don't get/set attributes on text, comment and attribute nodes
// 		if ( !elem || elem.nodeType === 3 || elem.nodeType === 8 || elem.nodeType === 2 ) {
// 			return undefined;
// 		}

// 		if ( pass && name in jQuery.attrFn ) {
// 			return jQuery(elem)[name](value);
// 		}

// 		var notxml = elem.nodeType !== 1 || !jQuery.isXMLDoc( elem ),
// 			// Whether we are setting (or getting)
// 			set = value !== undefined;

// 		// Try to normalize/fix the name
// 		name = notxml && jQuery.props[ name ] || name;

// 		// Only do all the following if this is a node (faster for style)
// 		if ( elem.nodeType === 1 ) {
// 			// These attributes require special treatment
// 			var special = rspecialurl.test( name );

// 			// Safari mis-reports the default selected property of an option
// 			// Accessing the parent's selectedIndex property fixes it
// 			if ( name === "selected" && !jQuery.support.optSelected ) {
// 				var parent = elem.parentNode;
// 				if ( parent ) {
// 					parent.selectedIndex;

// 					// Make sure that it also works with optgroups, see #5701
// 					if ( parent.parentNode ) {
// 						parent.parentNode.selectedIndex;
// 					}
// 				}
// 			}

// 			// If applicable, access the attribute via the DOM 0 way
// 			// 'in' checks fail in Blackberry 4.7 #6931
// 			if ( (name in elem || elem[ name ] !== undefined) && notxml && !special ) {
// 				if ( set ) {
// 					// We can't allow the type property to be changed (since it causes problems in IE)
// 					if ( name === "type" && rtype.test( elem.nodeName ) && elem.parentNode ) {
// 						jQuery.error( "type property can't be changed" );
// 					}

// 					if ( value === null ) {
// 						if ( elem.nodeType === 1 ) {
// 							elem.removeAttribute( name );
// 						}

// 					} else {
// 						elem[ name ] = value;
// 					}
// 				}

// 				// browsers index elements by id/name on forms, give priority to attributes.
// 				if ( jQuery.nodeName( elem, "form" ) && elem.getAttributeNode(name) ) {
// 					return elem.getAttributeNode( name ).nodeValue;
// 				}

// 				// elem.tabIndex doesn't always return the correct value when it hasn't been explicitly set
// 				// http://fluidproject.org/blog/2008/01/09/getting-setting-and-removing-tabindex-values-with-javascript/
// 				if ( name === "tabIndex" ) {
// 					var attributeNode = elem.getAttributeNode( "tabIndex" );

// 					return attributeNode && attributeNode.specified ?
// 						attributeNode.value :
// 						rfocusable.test( elem.nodeName ) || rclickable.test( elem.nodeName ) && elem.href ?
// 							0 :
// 							undefined;
// 				}

// 				return elem[ name ];
// 			}

// 			if ( !jQuery.support.style && notxml && name === "style" ) {
// 				if ( set ) {
// 					elem.style.cssText = "" + value;
// 				}

// 				return elem.style.cssText;
// 			}

// 			if ( set ) {
// 				// convert the value to a string (all browsers do this but IE) see #1070
// 				elem.setAttribute( name, "" + value );
// 			}

// 			// Ensure that missing attributes return undefined
// 			// Blackberry 4.7 returns "" from getAttribute #6938
// 			if ( !elem.attributes[ name ] && (elem.hasAttribute && !elem.hasAttribute( name )) ) {
// 				return undefined;
// 			}

// 			var attr = !jQuery.support.hrefNormalized && notxml && special ?
// 					// Some attributes require a special call on IE
// 					elem.getAttribute( name, 2 ) :
// 					elem.getAttribute( name );

// 			// Non-existent attributes return null, we normalize to undefined
// 			return attr === null ? undefined : attr;
// 		}
// 		// Handle everything which isn't a DOM element node
// 		if ( set ) {
// 			elem[ name ] = value;
// 		}
// 		return elem[ name ];
// 	}
// });




// var rnamespaces = /\.(.*)$/,
// 	rformElems = /^(?:textarea|input|select)$/i,
// 	rperiod = /\./g,
// 	rspace = / /g,
// 	rescape = /[^\w\s.|`]/g,
// 	fcleanup = function( nm ) {
// 		return nm.replace(rescape, "\\$&");
// 	},
// 	eventKey = "events";

// /*
//  * A number of helper functions used for managing events.
//  * Many of the ideas behind this code originated from
//  * Dean Edwards' addEvent library.
//  */
// jQuery.event = {

// 	// Bind an event to an element
// 	// Original by Dean Edwards
// 	add: function( elem, types, handler, data ) {
// 		if ( elem.nodeType === 3 || elem.nodeType === 8 ) {
// 			return;
// 		}

// 		// For whatever reason, IE has trouble passing the window object
// 		// around, causing it to be cloned in the process
// 		if ( jQuery.isWindow( elem ) && ( elem !== window && !elem.frameElement ) ) {
// 			elem = window;
// 		}

// 		if ( handler === false ) {
// 			handler = returnFalse;
// 		} else if ( !handler ) {
// 			// Fixes bug #7229. Fix recommended by jdalton
// 		  return;
// 		}

// 		var handleObjIn, handleObj;

// 		if ( handler.handler ) {
// 			handleObjIn = handler;
// 			handler = handleObjIn.handler;
// 		}

// 		// Make sure that the function being executed has a unique ID
// 		if ( !handler.guid ) {
// 			handler.guid = jQuery.guid++;
// 		}

// 		// Init the element's event structure
// 		var elemData = jQuery._data( elem );

// 		// If no elemData is found then we must be trying to bind to one of the
// 		// banned noData elements
// 		if ( !elemData ) {
// 			return;
// 		}

// 		var events = elemData[ eventKey ],
// 			eventHandle = elemData.handle;

// 		if ( typeof events === "function" ) {
// 			// On plain objects events is a fn that holds the the data
// 			// which prevents this data from being JSON serialized
// 			// the function does not need to be called, it just contains the data
// 			eventHandle = events.handle;
// 			events = events.events;

// 		} else if ( !events ) {
// 			if ( !elem.nodeType ) {
// 				// On plain objects, create a fn that acts as the holder
// 				// of the values to avoid JSON serialization of event data
// 				elemData[ eventKey ] = elemData = function(){};
// 			}

// 			elemData.events = events = {};
// 		}

// 		if ( !eventHandle ) {
// 			elemData.handle = eventHandle = function() {
// 				// Handle the second event of a trigger and when
// 				// an event is called after a page has unloaded
// 				return typeof jQuery !== "undefined" && !jQuery.event.triggered ?
// 					jQuery.event.handle.apply( eventHandle.elem, arguments ) :
// 					undefined;
// 			};
// 		}

// 		// Add elem as a property of the handle function
// 		// This is to prevent a memory leak with non-native events in IE.
// 		eventHandle.elem = elem;

// 		// Handle multiple events separated by a space
// 		// jQuery(...).bind("mouseover mouseout", fn);
// 		types = types.split(" ");

// 		var type, i = 0, namespaces;

// 		while ( (type = types[ i++ ]) ) {
// 			handleObj = handleObjIn ?
// 				jQuery.extend({}, handleObjIn) :
// 				{ handler: handler, data: data };

// 			// Namespaced event handlers
// 			if ( type.indexOf(".") > -1 ) {
// 				namespaces = type.split(".");
// 				type = namespaces.shift();
// 				handleObj.namespace = namespaces.slice(0).sort().join(".");

// 			} else {
// 				namespaces = [];
// 				handleObj.namespace = "";
// 			}

// 			handleObj.type = type;
// 			if ( !handleObj.guid ) {
// 				handleObj.guid = handler.guid;
// 			}

// 			// Get the current list of functions bound to this event
// 			var handlers = events[ type ],
// 				special = jQuery.event.special[ type ] || {};

// 			// Init the event handler queue
// 			if ( !handlers ) {
// 				handlers = events[ type ] = [];

// 				// Check for a special event handler
// 				// Only use addEventListener/attachEvent if the special
// 				// events handler returns false
// 				if ( !special.setup || special.setup.call( elem, data, namespaces, eventHandle ) === false ) {
// 					// Bind the global event handler to the element
// 					if ( elem.addEventListener ) {
// 						elem.addEventListener( type, eventHandle, false );

// 					} else if ( elem.attachEvent ) {
// 						elem.attachEvent( "on" + type, eventHandle );
// 					}
// 				}
// 			}

// 			if ( special.add ) {
// 				special.add.call( elem, handleObj );

// 				if ( !handleObj.handler.guid ) {
// 					handleObj.handler.guid = handler.guid;
// 				}
// 			}

// 			// Add the function to the element's handler list
// 			handlers.push( handleObj );

// 			// Keep track of which events have been used, for global triggering
// 			jQuery.event.global[ type ] = true;
// 		}

// 		// Nullify elem to prevent memory leaks in IE
// 		elem = null;
// 	},

// 	global: {},

// 	// Detach an event or set of events from an element
// 	remove: function( elem, types, handler, pos ) {
// 		// don't do events on text and comment nodes
// 		if ( elem.nodeType === 3 || elem.nodeType === 8 ) {
// 			return;
// 		}

// 		if ( handler === false ) {
// 			handler = returnFalse;
// 		}

// 		var ret, type, fn, j, i = 0, all, namespaces, namespace, special, eventType, handleObj, origType,
// 			elemData = jQuery.hasData( elem ) && jQuery._data( elem ),
// 			events = elemData && elemData[ eventKey ];

// 		if ( !elemData || !events ) {
// 			return;
// 		}

// 		if ( typeof events === "function" ) {
// 			elemData = events;
// 			events = events.events;
// 		}

// 		// types is actually an event object here
// 		if ( types && types.type ) {
// 			handler = types.handler;
// 			types = types.type;
// 		}

// 		// Unbind all events for the element
// 		if ( !types || typeof types === "string" && types.charAt(0) === "." ) {
// 			types = types || "";

// 			for ( type in events ) {
// 				jQuery.event.remove( elem, type + types );
// 			}

// 			return;
// 		}

// 		// Handle multiple events separated by a space
// 		// jQuery(...).unbind("mouseover mouseout", fn);
// 		types = types.split(" ");

// 		while ( (type = types[ i++ ]) ) {
// 			origType = type;
// 			handleObj = null;
// 			all = type.indexOf(".") < 0;
// 			namespaces = [];

// 			if ( !all ) {
// 				// Namespaced event handlers
// 				namespaces = type.split(".");
// 				type = namespaces.shift();

// 				namespace = new RegExp("(^|\\.)" +
// 					jQuery.map( namespaces.slice(0).sort(), fcleanup ).join("\\.(?:.*\\.)?") + "(\\.|$)");
// 			}

// 			eventType = events[ type ];

// 			if ( !eventType ) {
// 				continue;
// 			}

// 			if ( !handler ) {
// 				for ( j = 0; j < eventType.length; j++ ) {
// 					handleObj = eventType[ j ];

// 					if ( all || namespace.test( handleObj.namespace ) ) {
// 						jQuery.event.remove( elem, origType, handleObj.handler, j );
// 						eventType.splice( j--, 1 );
// 					}
// 				}

// 				continue;
// 			}

// 			special = jQuery.event.special[ type ] || {};

// 			for ( j = pos || 0; j < eventType.length; j++ ) {
// 				handleObj = eventType[ j ];

// 				if ( handler.guid === handleObj.guid ) {
// 					// remove the given handler for the given type
// 					if ( all || namespace.test( handleObj.namespace ) ) {
// 						if ( pos == null ) {
// 							eventType.splice( j--, 1 );
// 						}

// 						if ( special.remove ) {
// 							special.remove.call( elem, handleObj );
// 						}
// 					}

// 					if ( pos != null ) {
// 						break;
// 					}
// 				}
// 			}

// 			// remove generic event handler if no more handlers exist
// 			if ( eventType.length === 0 || pos != null && eventType.length === 1 ) {
// 				if ( !special.teardown || special.teardown.call( elem, namespaces ) === false ) {
// 					jQuery.removeEvent( elem, type, elemData.handle );
// 				}

// 				ret = null;
// 				delete events[ type ];
// 			}
// 		}

// 		// Remove the expando if it's no longer used
// 		if ( jQuery.isEmptyObject( events ) ) {
// 			var handle = elemData.handle;
// 			if ( handle ) {
// 				handle.elem = null;
// 			}

// 			delete elemData.events;
// 			delete elemData.handle;

// 			if ( typeof elemData === "function" ) {
// 				jQuery.removeData( elem, eventKey, true );

// 			} else if ( jQuery.isEmptyObject( elemData ) ) {
// 				jQuery.removeData( elem, undefined, true );
// 			}
// 		}
// 	},

// 	// bubbling is internal
// 	trigger: function( event, data, elem /*, bubbling */ ) {
// 		// Event object or event type
// 		var type = event.type || event,
// 			bubbling = arguments[3];

// 		if ( !bubbling ) {
// 			event = typeof event === "object" ?
// 				// jQuery.Event object
// 				event[ jQuery.expando ] ? event :
// 				// Object literal
// 				jQuery.extend( jQuery.Event(type), event ) :
// 				// Just the event type (string)
// 				jQuery.Event(type);

// 			if ( type.indexOf("!") >= 0 ) {
// 				event.type = type = type.slice(0, -1);
// 				event.exclusive = true;
// 			}

// 			// Handle a global trigger
// 			if ( !elem ) {
// 				// Don't bubble custom events when global (to avoid too much overhead)
// 				event.stopPropagation();

// 				// Only trigger if we've ever bound an event for it
// 				if ( jQuery.event.global[ type ] ) {
// 					// XXX This code smells terrible. event.js should not be directly
// 					// inspecting the data cache
// 					jQuery.each( jQuery.cache, function() {
// 						// internalKey variable is just used to make it easier to find
// 						// and potentially change this stuff later; currently it just
// 						// points to jQuery.expando
// 						var internalKey = jQuery.expando,
// 							internalCache = this[ internalKey ];
// 						if ( internalCache && internalCache.events && internalCache.events[type] ) {
// 							jQuery.event.trigger( event, data, internalCache.handle.elem );
// 						}
// 					});
// 				}
// 			}

// 			// Handle triggering a single element

// 			// don't do events on text and comment nodes
// 			if ( !elem || elem.nodeType === 3 || elem.nodeType === 8 ) {
// 				return undefined;
// 			}

// 			// Clean up in case it is reused
// 			event.result = undefined;
// 			event.target = elem;

// 			// Clone the incoming data, if any
// 			data = jQuery.makeArray( data );
// 			data.unshift( event );
// 		}

// 		event.currentTarget = elem;

// 		// Trigger the event, it is assumed that "handle" is a function
// 		var handle = elem.nodeType ?
// 			jQuery._data( elem, "handle" ) :
// 			(jQuery._data( elem, eventKey ) || {}).handle;

// 		if ( handle ) {
// 			handle.apply( elem, data );
// 		}

// 		var parent = elem.parentNode || elem.ownerDocument;

// 		// Trigger an inline bound script
// 		try {
// 			if ( !(elem && elem.nodeName && jQuery.noData[elem.nodeName.toLowerCase()]) ) {
// 				if ( elem[ "on" + type ] && elem[ "on" + type ].apply( elem, data ) === false ) {
// 					event.result = false;
// 					event.preventDefault();
// 				}
// 			}

// 		// prevent IE from throwing an error for some elements with some event types, see #3533
// 		} catch (inlineError) {}

// 		if ( !event.isPropagationStopped() && parent ) {
// 			jQuery.event.trigger( event, data, parent, true );

// 		} else if ( !event.isDefaultPrevented() ) {
// 			var old,
// 				target = event.target,
// 				targetType = type.replace( rnamespaces, "" ),
// 				isClick = jQuery.nodeName( target, "a" ) && targetType === "click",
// 				special = jQuery.event.special[ targetType ] || {};

// 			if ( (!special._default || special._default.call( elem, event ) === false) &&
// 				!isClick && !(target && target.nodeName && jQuery.noData[target.nodeName.toLowerCase()]) ) {

// 				try {
// 					if ( target[ targetType ] ) {
// 						// Make sure that we don't accidentally re-trigger the onFOO events
// 						old = target[ "on" + targetType ];

// 						if ( old ) {
// 							target[ "on" + targetType ] = null;
// 						}

// 						jQuery.event.triggered = true;
// 						target[ targetType ]();
// 					}

// 				// prevent IE from throwing an error for some elements with some event types, see #3533
// 				} catch (triggerError) {}

// 				if ( old ) {
// 					target[ "on" + targetType ] = old;
// 				}

// 				jQuery.event.triggered = false;
// 			}
// 		}
// 	},

// 	handle: function( event ) {
// 		var all, handlers, namespaces, namespace_re, events,
// 			namespace_sort = [],
// 			args = jQuery.makeArray( arguments );

// 		event = args[0] = jQuery.event.fix( event || window.event );
// 		event.currentTarget = this;

// 		// Namespaced event handlers
// 		all = event.type.indexOf(".") < 0 && !event.exclusive;

// 		if ( !all ) {
// 			namespaces = event.type.split(".");
// 			event.type = namespaces.shift();
// 			namespace_sort = namespaces.slice(0).sort();
// 			namespace_re = new RegExp("(^|\\.)" + namespace_sort.join("\\.(?:.*\\.)?") + "(\\.|$)");
// 		}

// 		event.namespace = event.namespace || namespace_sort.join(".");

// 		events = jQuery._data(this, eventKey);

// 		if ( typeof events === "function" ) {
// 			events = events.events;
// 		}

// 		handlers = (events || {})[ event.type ];

// 		if ( events && handlers ) {
// 			// Clone the handlers to prevent manipulation
// 			handlers = handlers.slice(0);

// 			for ( var j = 0, l = handlers.length; j < l; j++ ) {
// 				var handleObj = handlers[ j ];

// 				// Filter the functions by class
// 				if ( all || namespace_re.test( handleObj.namespace ) ) {
// 					// Pass in a reference to the handler function itself
// 					// So that we can later remove it
// 					event.handler = handleObj.handler;
// 					event.data = handleObj.data;
// 					event.handleObj = handleObj;

// 					var ret = handleObj.handler.apply( this, args );

// 					if ( ret !== undefined ) {
// 						event.result = ret;
// 						if ( ret === false ) {
// 							event.preventDefault();
// 							event.stopPropagation();
// 						}
// 					}

// 					if ( event.isImmediatePropagationStopped() ) {
// 						break;
// 					}
// 				}
// 			}
// 		}

// 		return event.result;
// 	},

// 	props: "altKey attrChange attrName bubbles button cancelable charCode clientX clientY ctrlKey currentTarget data detail eventPhase fromElement handler keyCode layerX layerY metaKey newValue offsetX offsetY pageX pageY prevValue relatedNode relatedTarget screenX screenY shiftKey srcElement target toElement view wheelDelta which".split(" "),

// 	fix: function( event ) {
// 		if ( event[ jQuery.expando ] ) {
// 			return event;
// 		}

// 		// store a copy of the original event object
// 		// and "clone" to set read-only properties
// 		var originalEvent = event;
// 		event = jQuery.Event( originalEvent );

// 		for ( var i = this.props.length, prop; i; ) {
// 			prop = this.props[ --i ];
// 			event[ prop ] = originalEvent[ prop ];
// 		}

// 		// Fix target property, if necessary
// 		if ( !event.target ) {
// 			// Fixes #1925 where srcElement might not be defined either
// 			event.target = event.srcElement || document;
// 		}

// 		// check if target is a textnode (safari)
// 		if ( event.target.nodeType === 3 ) {
// 			event.target = event.target.parentNode;
// 		}

// 		// Add relatedTarget, if necessary
// 		if ( !event.relatedTarget && event.fromElement ) {
// 			event.relatedTarget = event.fromElement === event.target ? event.toElement : event.fromElement;
// 		}

// 		// Calculate pageX/Y if missing and clientX/Y available
// 		if ( event.pageX == null && event.clientX != null ) {
// 			var doc = document.documentElement,
// 				body = document.body;

// 			event.pageX = event.clientX + (doc && doc.scrollLeft || body && body.scrollLeft || 0) - (doc && doc.clientLeft || body && body.clientLeft || 0);
// 			event.pageY = event.clientY + (doc && doc.scrollTop  || body && body.scrollTop  || 0) - (doc && doc.clientTop  || body && body.clientTop  || 0);
// 		}

// 		// Add which for key events
// 		if ( event.which == null && (event.charCode != null || event.keyCode != null) ) {
// 			event.which = event.charCode != null ? event.charCode : event.keyCode;
// 		}

// 		// Add metaKey to non-Mac browsers (use ctrl for PC's and Meta for Macs)
// 		if ( !event.metaKey && event.ctrlKey ) {
// 			event.metaKey = event.ctrlKey;
// 		}

// 		// Add which for click: 1 === left; 2 === middle; 3 === right
// 		// Note: button is not normalized, so don't use it
// 		if ( !event.which && event.button !== undefined ) {
// 			event.which = (event.button & 1 ? 1 : ( event.button & 2 ? 3 : ( event.button & 4 ? 2 : 0 ) ));
// 		}

// 		return event;
// 	},

// 	// Deprecated, use jQuery.guid instead
// 	guid: 1E8,

// 	// Deprecated, use jQuery.proxy instead
// 	proxy: jQuery.proxy,

// 	special: {
// 		ready: {
// 			// Make sure the ready event is setup
// 			setup: jQuery.bindReady,
// 			teardown: jQuery.noop
// 		},

// 		live: {
// 			add: function( handleObj ) {
// 				jQuery.event.add( this,
// 					liveConvert( handleObj.origType, handleObj.selector ),
// 					jQuery.extend({}, handleObj, {handler: liveHandler, guid: handleObj.handler.guid}) );
// 			},

// 			remove: function( handleObj ) {
// 				jQuery.event.remove( this, liveConvert( handleObj.origType, handleObj.selector ), handleObj );
// 			}
// 		},

// 		beforeunload: {
// 			setup: function( data, namespaces, eventHandle ) {
// 				// We only want to do this special case on windows
// 				if ( jQuery.isWindow( this ) ) {
// 					this.onbeforeunload = eventHandle;
// 				}
// 			},

// 			teardown: function( namespaces, eventHandle ) {
// 				if ( this.onbeforeunload === eventHandle ) {
// 					this.onbeforeunload = null;
// 				}
// 			}
// 		}
// 	}
// };

// jQuery.removeEvent = document.removeEventListener ?
// 	function( elem, type, handle ) {
// 		if ( elem.removeEventListener ) {
// 			elem.removeEventListener( type, handle, false );
// 		}
// 	} :
// 	function( elem, type, handle ) {
// 		if ( elem.detachEvent ) {
// 			elem.detachEvent( "on" + type, handle );
// 		}
// 	};

// jQuery.Event = function( src ) {
// 	// Allow instantiation without the 'new' keyword
// 	if ( !this.preventDefault ) {
// 		return new jQuery.Event( src );
// 	}

// 	// Event object
// 	if ( src && src.type ) {
// 		this.originalEvent = src;
// 		this.type = src.type;

// 		// Events bubbling up the document may have been marked as prevented
// 		// by a handler lower down the tree; reflect the correct value.
// 		this.isDefaultPrevented = (src.defaultPrevented || src.returnValue === false || 
// 			src.getPreventDefault && src.getPreventDefault()) ? returnTrue : returnFalse;

// 	// Event type
// 	} else {
// 		this.type = src;
// 	}

// 	// timeStamp is buggy for some events on Firefox(#3843)
// 	// So we won't rely on the native value
// 	this.timeStamp = jQuery.now();

// 	// Mark it as fixed
// 	this[ jQuery.expando ] = true;
// };

// function returnFalse() {
// 	return false;
// }
// function returnTrue() {
// 	return true;
// }

// // jQuery.Event is based on DOM3 Events as specified by the ECMAScript Language Binding
// // http://www.w3.org/TR/2003/WD-DOM-Level-3-Events-20030331/ecma-script-binding.html
// jQuery.Event.prototype = {
// 	preventDefault: function() {
// 		this.isDefaultPrevented = returnTrue;

// 		var e = this.originalEvent;
// 		if ( !e ) {
// 			return;
// 		}

// 		// if preventDefault exists run it on the original event
// 		if ( e.preventDefault ) {
// 			e.preventDefault();

// 		// otherwise set the returnValue property of the original event to false (IE)
// 		} else {
// 			e.returnValue = false;
// 		}
// 	},
// 	stopPropagation: function() {
// 		this.isPropagationStopped = returnTrue;

// 		var e = this.originalEvent;
// 		if ( !e ) {
// 			return;
// 		}
// 		// if stopPropagation exists run it on the original event
// 		if ( e.stopPropagation ) {
// 			e.stopPropagation();
// 		}
// 		// otherwise set the cancelBubble property of the original event to true (IE)
// 		e.cancelBubble = true;
// 	},
// 	stopImmediatePropagation: function() {
// 		this.isImmediatePropagationStopped = returnTrue;
// 		this.stopPropagation();
// 	},
// 	isDefaultPrevented: returnFalse,
// 	isPropagationStopped: returnFalse,
// 	isImmediatePropagationStopped: returnFalse
// };

// // Checks if an event happened on an element within another element
// // Used in jQuery.event.special.mouseenter and mouseleave handlers
// var withinElement = function( event ) {
// 	// Check if mouse(over|out) are still within the same parent element
// 	var parent = event.relatedTarget;

// 	// Firefox sometimes assigns relatedTarget a XUL element
// 	// which we cannot access the parentNode property of
// 	try {
// 		// Traverse up the tree
// 		while ( parent && parent !== this ) {
// 			parent = parent.parentNode;
// 		}

// 		if ( parent !== this ) {
// 			// set the correct event type
// 			event.type = event.data;

// 			// handle event if we actually just moused on to a non sub-element
// 			jQuery.event.handle.apply( this, arguments );
// 		}

// 	// assuming we've left the element since we most likely mousedover a xul element
// 	} catch(e) { }
// },

// // In case of event delegation, we only need to rename the event.type,
// // liveHandler will take care of the rest.
// delegate = function( event ) {
// 	event.type = event.data;
// 	jQuery.event.handle.apply( this, arguments );
// };

// // Create mouseenter and mouseleave events
// jQuery.each({
// 	mouseenter: "mouseover",
// 	mouseleave: "mouseout"
// }, function( orig, fix ) {
// 	jQuery.event.special[ orig ] = {
// 		setup: function( data ) {
// 			jQuery.event.add( this, fix, data && data.selector ? delegate : withinElement, orig );
// 		},
// 		teardown: function( data ) {
// 			jQuery.event.remove( this, fix, data && data.selector ? delegate : withinElement );
// 		}
// 	};
// });

// // submit delegation
// if ( !jQuery.support.submitBubbles ) {

// 	jQuery.event.special.submit = {
// 		setup: function( data, namespaces ) {
// 			if ( this.nodeName && this.nodeName.toLowerCase() !== "form" ) {
// 				jQuery.event.add(this, "click.specialSubmit", function( e ) {
// 					var elem = e.target,
// 						type = elem.type;

// 					if ( (type === "submit" || type === "image") && jQuery( elem ).closest("form").length ) {
// 						e.liveFired = undefined;
// 						return trigger( "submit", this, arguments );
// 					}
// 				});

// 				jQuery.event.add(this, "keypress.specialSubmit", function( e ) {
// 					var elem = e.target,
// 						type = elem.type;

// 					if ( (type === "text" || type === "password") && jQuery( elem ).closest("form").length && e.keyCode === 13 ) {
// 						e.liveFired = undefined;
// 						return trigger( "submit", this, arguments );
// 					}
// 				});

// 			} else {
// 				return false;
// 			}
// 		},

// 		teardown: function( namespaces ) {
// 			jQuery.event.remove( this, ".specialSubmit" );
// 		}
// 	};

// }

// // change delegation, happens here so we have bind.
// if ( !jQuery.support.changeBubbles ) {

// 	var changeFilters,

// 	getVal = function( elem ) {
// 		var type = elem.type, val = elem.value;

// 		if ( type === "radio" || type === "checkbox" ) {
// 			val = elem.checked;

// 		} else if ( type === "select-multiple" ) {
// 			val = elem.selectedIndex > -1 ?
// 				jQuery.map( elem.options, function( elem ) {
// 					return elem.selected;
// 				}).join("-") :
// 				"";

// 		} else if ( elem.nodeName.toLowerCase() === "select" ) {
// 			val = elem.selectedIndex;
// 		}

// 		return val;
// 	},

// 	testChange = function testChange( e ) {
// 		var elem = e.target, data, val;

// 		if ( !rformElems.test( elem.nodeName ) || elem.readOnly ) {
// 			return;
// 		}

// 		data = jQuery._data( elem, "_change_data" );
// 		val = getVal(elem);

// 		// the current data will be also retrieved by beforeactivate
// 		if ( e.type !== "focusout" || elem.type !== "radio" ) {
// 			jQuery._data( elem, "_change_data", val );
// 		}

// 		if ( data === undefined || val === data ) {
// 			return;
// 		}

// 		if ( data != null || val ) {
// 			e.type = "change";
// 			e.liveFired = undefined;
// 			return jQuery.event.trigger( e, arguments[1], elem );
// 		}
// 	};

// 	jQuery.event.special.change = {
// 		filters: {
// 			focusout: testChange,

// 			beforedeactivate: testChange,

// 			click: function( e ) {
// 				var elem = e.target, type = elem.type;

// 				if ( type === "radio" || type === "checkbox" || elem.nodeName.toLowerCase() === "select" ) {
// 					return testChange.call( this, e );
// 				}
// 			},

// 			// Change has to be called before submit
// 			// Keydown will be called before keypress, which is used in submit-event delegation
// 			keydown: function( e ) {
// 				var elem = e.target, type = elem.type;

// 				if ( (e.keyCode === 13 && elem.nodeName.toLowerCase() !== "textarea") ||
// 					(e.keyCode === 32 && (type === "checkbox" || type === "radio")) ||
// 					type === "select-multiple" ) {
// 					return testChange.call( this, e );
// 				}
// 			},

// 			// Beforeactivate happens also before the previous element is blurred
// 			// with this event you can't trigger a change event, but you can store
// 			// information
// 			beforeactivate: function( e ) {
// 				var elem = e.target;
// 				jQuery._data( elem, "_change_data", getVal(elem) );
// 			}
// 		},

// 		setup: function( data, namespaces ) {
// 			if ( this.type === "file" ) {
// 				return false;
// 			}

// 			for ( var type in changeFilters ) {
// 				jQuery.event.add( this, type + ".specialChange", changeFilters[type] );
// 			}

// 			return rformElems.test( this.nodeName );
// 		},

// 		teardown: function( namespaces ) {
// 			jQuery.event.remove( this, ".specialChange" );

// 			return rformElems.test( this.nodeName );
// 		}
// 	};

// 	changeFilters = jQuery.event.special.change.filters;

// 	// Handle when the input is .focus()'d
// 	changeFilters.focus = changeFilters.beforeactivate;
// }

// function trigger( type, elem, args ) {
// 	args[0].type = type;
// 	return jQuery.event.handle.apply( elem, args );
// }

// // Create "bubbling" focus and blur events
// if ( document.addEventListener ) {
// 	jQuery.each({ focus: "focusin", blur: "focusout" }, function( orig, fix ) {
// 		jQuery.event.special[ fix ] = {
// 			setup: function() {
// 				this.addEventListener( orig, handler, true );
// 			}, 
// 			teardown: function() { 
// 				this.removeEventListener( orig, handler, true );
// 			}
// 		};

// 		function handler( e ) {
// 			e = jQuery.event.fix( e );
// 			e.type = fix;
// 			return jQuery.event.handle.call( this, e );
// 		}
// 	});
// }

// jQuery.each(["bind", "one"], function( i, name ) {
// 	jQuery.fn[ name ] = function( type, data, fn ) {
// 		// Handle object literals
// 		if ( typeof type === "object" ) {
// 			for ( var key in type ) {
// 				this[ name ](key, data, type[key], fn);
// 			}
// 			return this;
// 		}

// 		if ( jQuery.isFunction( data ) || data === false ) {
// 			fn = data;
// 			data = undefined;
// 		}

// 		var handler = name === "one" ? jQuery.proxy( fn, function( event ) {
// 			jQuery( this ).unbind( event, handler );
// 			return fn.apply( this, arguments );
// 		}) : fn;

// 		if ( type === "unload" && name !== "one" ) {
// 			this.one( type, data, fn );

// 		} else {
// 			for ( var i = 0, l = this.length; i < l; i++ ) {
// 				jQuery.event.add( this[i], type, handler, data );
// 			}
// 		}

// 		return this;
// 	};
// });

// jQuery.fn.extend({
// 	unbind: function( type, fn ) {
// 		// Handle object literals
// 		if ( typeof type === "object" && !type.preventDefault ) {
// 			for ( var key in type ) {
// 				this.unbind(key, type[key]);
// 			}

// 		} else {
// 			for ( var i = 0, l = this.length; i < l; i++ ) {
// 				jQuery.event.remove( this[i], type, fn );
// 			}
// 		}

// 		return this;
// 	},

// 	delegate: function( selector, types, data, fn ) {
// 		return this.live( types, data, fn, selector );
// 	},

// 	undelegate: function( selector, types, fn ) {
// 		if ( arguments.length === 0 ) {
// 				return this.unbind( "live" );

// 		} else {
// 			return this.die( types, null, fn, selector );
// 		}
// 	},

// 	trigger: function( type, data ) {
// 		return this.each(function() {
// 			jQuery.event.trigger( type, data, this );
// 		});
// 	},

// 	triggerHandler: function( type, data ) {
// 		if ( this[0] ) {
// 			var event = jQuery.Event( type );
// 			event.preventDefault();
// 			event.stopPropagation();
// 			jQuery.event.trigger( event, data, this[0] );
// 			return event.result;
// 		}
// 	},

// 	toggle: function( fn ) {
// 		// Save reference to arguments for access in closure
// 		var args = arguments,
// 			i = 1;

// 		// link all the functions, so any of them can unbind this click handler
// 		while ( i < args.length ) {
// 			jQuery.proxy( fn, args[ i++ ] );
// 		}

// 		return this.click( jQuery.proxy( fn, function( event ) {
// 			// Figure out which function to execute
// 			var lastToggle = ( jQuery._data( this, "lastToggle" + fn.guid ) || 0 ) % i;
// 			jQuery._data( this, "lastToggle" + fn.guid, lastToggle + 1 );

// 			// Make sure that clicks stop
// 			event.preventDefault();

// 			// and execute the function
// 			return args[ lastToggle ].apply( this, arguments ) || false;
// 		}));
// 	},

// 	hover: function( fnOver, fnOut ) {
// 		return this.mouseenter( fnOver ).mouseleave( fnOut || fnOver );
// 	}
// });

// var liveMap = {
// 	focus: "focusin",
// 	blur: "focusout",
// 	mouseenter: "mouseover",
// 	mouseleave: "mouseout"
// };

// jQuery.each(["live", "die"], function( i, name ) {
// 	jQuery.fn[ name ] = function( types, data, fn, origSelector /* Internal Use Only */ ) {
// 		var type, i = 0, match, namespaces, preType,
// 			selector = origSelector || this.selector,
// 			context = origSelector ? this : jQuery( this.context );

// 		if ( typeof types === "object" && !types.preventDefault ) {
// 			for ( var key in types ) {
// 				context[ name ]( key, data, types[key], selector );
// 			}

// 			return this;
// 		}

// 		if ( jQuery.isFunction( data ) ) {
// 			fn = data;
// 			data = undefined;
// 		}

// 		types = (types || "").split(" ");

// 		while ( (type = types[ i++ ]) != null ) {
// 			match = rnamespaces.exec( type );
// 			namespaces = "";

// 			if ( match )  {
// 				namespaces = match[0];
// 				type = type.replace( rnamespaces, "" );
// 			}

// 			if ( type === "hover" ) {
// 				types.push( "mouseenter" + namespaces, "mouseleave" + namespaces );
// 				continue;
// 			}

// 			preType = type;

// 			if ( type === "focus" || type === "blur" ) {
// 				types.push( liveMap[ type ] + namespaces );
// 				type = type + namespaces;

// 			} else {
// 				type = (liveMap[ type ] || type) + namespaces;
// 			}

// 			if ( name === "live" ) {
// 				// bind live handler
// 				for ( var j = 0, l = context.length; j < l; j++ ) {
// 					jQuery.event.add( context[j], "live." + liveConvert( type, selector ),
// 						{ data: data, selector: selector, handler: fn, origType: type, origHandler: fn, preType: preType } );
// 				}

// 			} else {
// 				// unbind live handler
// 				context.unbind( "live." + liveConvert( type, selector ), fn );
// 			}
// 		}

// 		return this;
// 	};
// });

// function liveHandler( event ) {
// 	var stop, maxLevel, related, match, handleObj, elem, j, i, l, data, close, namespace, ret,
// 		elems = [],
// 		selectors = [],
// 		events = jQuery._data( this, eventKey );

// 	if ( typeof events === "function" ) {
// 		events = events.events;
// 	}

// 	// Make sure we avoid non-left-click bubbling in Firefox (#3861) and disabled elements in IE (#6911)
// 	if ( event.liveFired === this || !events || !events.live || event.target.disabled || event.button && event.type === "click" ) {
// 		return;
// 	}

// 	if ( event.namespace ) {
// 		namespace = new RegExp("(^|\\.)" + event.namespace.split(".").join("\\.(?:.*\\.)?") + "(\\.|$)");
// 	}

// 	event.liveFired = this;

// 	var live = events.live.slice(0);

// 	for ( j = 0; j < live.length; j++ ) {
// 		handleObj = live[j];

// 		if ( handleObj.origType.replace( rnamespaces, "" ) === event.type ) {
// 			selectors.push( handleObj.selector );

// 		} else {
// 			live.splice( j--, 1 );
// 		}
// 	}

// 	match = jQuery( event.target ).closest( selectors, event.currentTarget );

// 	for ( i = 0, l = match.length; i < l; i++ ) {
// 		close = match[i];

// 		for ( j = 0; j < live.length; j++ ) {
// 			handleObj = live[j];

// 			if ( close.selector === handleObj.selector && (!namespace || namespace.test( handleObj.namespace )) ) {
// 				elem = close.elem;
// 				related = null;

// 				// Those two events require additional checking
// 				if ( handleObj.preType === "mouseenter" || handleObj.preType === "mouseleave" ) {
// 					event.type = handleObj.preType;
// 					related = jQuery( event.relatedTarget ).closest( handleObj.selector )[0];
// 				}

// 				if ( !related || related !== elem ) {
// 					elems.push({ elem: elem, handleObj: handleObj, level: close.level });
// 				}
// 			}
// 		}
// 	}

// 	for ( i = 0, l = elems.length; i < l; i++ ) {
// 		match = elems[i];

// 		if ( maxLevel && match.level > maxLevel ) {
// 			break;
// 		}

// 		event.currentTarget = match.elem;
// 		event.data = match.handleObj.data;
// 		event.handleObj = match.handleObj;

// 		ret = match.handleObj.origHandler.apply( match.elem, arguments );

// 		if ( ret === false || event.isPropagationStopped() ) {
// 			maxLevel = match.level;

// 			if ( ret === false ) {
// 				stop = false;
// 			}
// 			if ( event.isImmediatePropagationStopped() ) {
// 				break;
// 			}
// 		}
// 	}

// 	return stop;
// }

// function liveConvert( type, selector ) {
// 	return (type && type !== "*" ? type + "." : "") + selector.replace(rperiod, "`").replace(rspace, "&");
// }

// jQuery.each( ("blur focus focusin focusout load resize scroll unload click dblclick " +
// 	"mousedown mouseup mousemove mouseover mouseout mouseenter mouseleave " +
// 	"change select submit keydown keypress keyup error").split(" "), function( i, name ) {

// 	// Handle event binding
// 	jQuery.fn[ name ] = function( data, fn ) {
// 		if ( fn == null ) {
// 			fn = data;
// 			data = null;
// 		}

// 		return arguments.length > 0 ?
// 			this.bind( name, data, fn ) :
// 			this.trigger( name );
// 	};

// 	if ( jQuery.attrFn ) {
// 		jQuery.attrFn[ name ] = true;
// 	}
// });


// /*!
//  * Sizzle CSS Selector Engine
//  *  Copyright 2011, The Dojo Foundation
//  *  Released under the MIT, BSD, and GPL Licenses.
//  *  More information: http://sizzlejs.com/
//  */
// (function(){

// var chunker = /((?:\((?:\([^()]+\)|[^()]+)+\)|\[(?:\[[^\[\]]*\]|['"][^'"]*['"]|[^\[\]'"]+)+\]|\\.|[^ >+~,(\[\\]+)+|[>+~])(\s*,\s*)?((?:.|\r|\n)*)/g,
// 	done = 0,
// 	toString = Object.prototype.toString,
// 	hasDuplicate = false,
// 	baseHasDuplicate = true;

// // Here we check if the JavaScript engine is using some sort of
// // optimization where it does not always call our comparision
// // function. If that is the case, discard the hasDuplicate value.
// //   Thus far that includes Google Chrome.
// [0, 0].sort(function() {
// 	baseHasDuplicate = false;
// 	return 0;
// });

// var Sizzle = function( selector, context, results, seed ) {
// 	results = results || [];
// 	context = context || document;

// 	var origContext = context;

// 	if ( context.nodeType !== 1 && context.nodeType !== 9 ) {
// 		return [];
// 	}
	
// 	if ( !selector || typeof selector !== "string" ) {
// 		return results;
// 	}

// 	var m, set, checkSet, extra, ret, cur, pop, i,
// 		prune = true,
// 		contextXML = Sizzle.isXML( context ),
// 		parts = [],
// 		soFar = selector;
	
// 	// Reset the position of the chunker regexp (start from head)
// 	do {
// 		chunker.exec( "" );
// 		m = chunker.exec( soFar );

// 		if ( m ) {
// 			soFar = m[3];
		
// 			parts.push( m[1] );
		
// 			if ( m[2] ) {
// 				extra = m[3];
// 				break;
// 			}
// 		}
// 	} while ( m );

// 	if ( parts.length > 1 && origPOS.exec( selector ) ) {

// 		if ( parts.length === 2 && Expr.relative[ parts[0] ] ) {
// 			set = posProcess( parts[0] + parts[1], context );

// 		} else {
// 			set = Expr.relative[ parts[0] ] ?
// 				[ context ] :
// 				Sizzle( parts.shift(), context );

// 			while ( parts.length ) {
// 				selector = parts.shift();

// 				if ( Expr.relative[ selector ] ) {
// 					selector += parts.shift();
// 				}
				
// 				set = posProcess( selector, set );
// 			}
// 		}

// 	} else {
// 		// Take a shortcut and set the context if the root selector is an ID
// 		// (but not if it'll be faster if the inner selector is an ID)
// 		if ( !seed && parts.length > 1 && context.nodeType === 9 && !contextXML &&
// 				Expr.match.ID.test(parts[0]) && !Expr.match.ID.test(parts[parts.length - 1]) ) {

// 			ret = Sizzle.find( parts.shift(), context, contextXML );
// 			context = ret.expr ?
// 				Sizzle.filter( ret.expr, ret.set )[0] :
// 				ret.set[0];
// 		}

// 		if ( context ) {
// 			ret = seed ?
// 				{ expr: parts.pop(), set: makeArray(seed) } :
// 				Sizzle.find( parts.pop(), parts.length === 1 && (parts[0] === "~" || parts[0] === "+") && context.parentNode ? context.parentNode : context, contextXML );

// 			set = ret.expr ?
// 				Sizzle.filter( ret.expr, ret.set ) :
// 				ret.set;

// 			if ( parts.length > 0 ) {
// 				checkSet = makeArray( set );

// 			} else {
// 				prune = false;
// 			}

// 			while ( parts.length ) {
// 				cur = parts.pop();
// 				pop = cur;

// 				if ( !Expr.relative[ cur ] ) {
// 					cur = "";
// 				} else {
// 					pop = parts.pop();
// 				}

// 				if ( pop == null ) {
// 					pop = context;
// 				}

// 				Expr.relative[ cur ]( checkSet, pop, contextXML );
// 			}

// 		} else {
// 			checkSet = parts = [];
// 		}
// 	}

// 	if ( !checkSet ) {
// 		checkSet = set;
// 	}

// 	if ( !checkSet ) {
// 		Sizzle.error( cur || selector );
// 	}

// 	if ( toString.call(checkSet) === "[object Array]" ) {
// 		if ( !prune ) {
// 			results.push.apply( results, checkSet );

// 		} else if ( context && context.nodeType === 1 ) {
// 			for ( i = 0; checkSet[i] != null; i++ ) {
// 				if ( checkSet[i] && (checkSet[i] === true || checkSet[i].nodeType === 1 && Sizzle.contains(context, checkSet[i])) ) {
// 					results.push( set[i] );
// 				}
// 			}

// 		} else {
// 			for ( i = 0; checkSet[i] != null; i++ ) {
// 				if ( checkSet[i] && checkSet[i].nodeType === 1 ) {
// 					results.push( set[i] );
// 				}
// 			}
// 		}

// 	} else {
// 		makeArray( checkSet, results );
// 	}

// 	if ( extra ) {
// 		Sizzle( extra, origContext, results, seed );
// 		Sizzle.uniqueSort( results );
// 	}

// 	return results;
// };

// Sizzle.uniqueSort = function( results ) {
// 	if ( sortOrder ) {
// 		hasDuplicate = baseHasDuplicate;
// 		results.sort( sortOrder );

// 		if ( hasDuplicate ) {
// 			for ( var i = 1; i < results.length; i++ ) {
// 				if ( results[i] === results[ i - 1 ] ) {
// 					results.splice( i--, 1 );
// 				}
// 			}
// 		}
// 	}

// 	return results;
// };

// Sizzle.matches = function( expr, set ) {
// 	return Sizzle( expr, null, null, set );
// };

// Sizzle.matchesSelector = function( node, expr ) {
// 	return Sizzle( expr, null, null, [node] ).length > 0;
// };

// Sizzle.find = function( expr, context, isXML ) {
// 	var set;

// 	if ( !expr ) {
// 		return [];
// 	}

// 	for ( var i = 0, l = Expr.order.length; i < l; i++ ) {
// 		var match,
// 			type = Expr.order[i];
		
// 		if ( (match = Expr.leftMatch[ type ].exec( expr )) ) {
// 			var left = match[1];
// 			match.splice( 1, 1 );

// 			if ( left.substr( left.length - 1 ) !== "\\" ) {
// 				match[1] = (match[1] || "").replace(/\\/g, "");
// 				set = Expr.find[ type ]( match, context, isXML );

// 				if ( set != null ) {
// 					expr = expr.replace( Expr.match[ type ], "" );
// 					break;
// 				}
// 			}
// 		}
// 	}

// 	if ( !set ) {
// 		set = typeof context.getElementsByTagName !== "undefined" ?
// 			context.getElementsByTagName( "*" ) :
// 			[];
// 	}

// 	return { set: set, expr: expr };
// };

// Sizzle.filter = function( expr, set, inplace, not ) {
// 	var match, anyFound,
// 		old = expr,
// 		result = [],
// 		curLoop = set,
// 		isXMLFilter = set && set[0] && Sizzle.isXML( set[0] );

// 	while ( expr && set.length ) {
// 		for ( var type in Expr.filter ) {
// 			if ( (match = Expr.leftMatch[ type ].exec( expr )) != null && match[2] ) {
// 				var found, item,
// 					filter = Expr.filter[ type ],
// 					left = match[1];

// 				anyFound = false;

// 				match.splice(1,1);

// 				if ( left.substr( left.length - 1 ) === "\\" ) {
// 					continue;
// 				}

// 				if ( curLoop === result ) {
// 					result = [];
// 				}

// 				if ( Expr.preFilter[ type ] ) {
// 					match = Expr.preFilter[ type ]( match, curLoop, inplace, result, not, isXMLFilter );

// 					if ( !match ) {
// 						anyFound = found = true;

// 					} else if ( match === true ) {
// 						continue;
// 					}
// 				}

// 				if ( match ) {
// 					for ( var i = 0; (item = curLoop[i]) != null; i++ ) {
// 						if ( item ) {
// 							found = filter( item, match, i, curLoop );
// 							var pass = not ^ !!found;

// 							if ( inplace && found != null ) {
// 								if ( pass ) {
// 									anyFound = true;

// 								} else {
// 									curLoop[i] = false;
// 								}

// 							} else if ( pass ) {
// 								result.push( item );
// 								anyFound = true;
// 							}
// 						}
// 					}
// 				}

// 				if ( found !== undefined ) {
// 					if ( !inplace ) {
// 						curLoop = result;
// 					}

// 					expr = expr.replace( Expr.match[ type ], "" );

// 					if ( !anyFound ) {
// 						return [];
// 					}

// 					break;
// 				}
// 			}
// 		}

// 		// Improper expression
// 		if ( expr === old ) {
// 			if ( anyFound == null ) {
// 				Sizzle.error( expr );

// 			} else {
// 				break;
// 			}
// 		}

// 		old = expr;
// 	}

// 	return curLoop;
// };

// Sizzle.error = function( msg ) {
// 	throw "Syntax error, unrecognized expression: " + msg;
// };

// var Expr = Sizzle.selectors = {
// 	order: [ "ID", "NAME", "TAG" ],

// 	match: {
// 		ID: /#((?:[\w\u00c0-\uFFFF\-]|\\.)+)/,
// 		CLASS: /\.((?:[\w\u00c0-\uFFFF\-]|\\.)+)/,
// 		NAME: /\[name=['"]*((?:[\w\u00c0-\uFFFF\-]|\\.)+)['"]*\]/,
// 		ATTR: /\[\s*((?:[\w\u00c0-\uFFFF\-]|\\.)+)\s*(?:(\S?=)\s*(?:(['"])(.*?)\3|(#?(?:[\w\u00c0-\uFFFF\-]|\\.)*)|)|)\s*\]/,
// 		TAG: /^((?:[\w\u00c0-\uFFFF\*\-]|\\.)+)/,
// 		CHILD: /:(only|nth|last|first)-child(?:\(\s*(even|odd|(?:[+\-]?\d+|(?:[+\-]?\d*)?n\s*(?:[+\-]\s*\d+)?))\s*\))?/,
// 		POS: /:(nth|eq|gt|lt|first|last|even|odd)(?:\((\d*)\))?(?=[^\-]|$)/,
// 		PSEUDO: /:((?:[\w\u00c0-\uFFFF\-]|\\.)+)(?:\((['"]?)((?:\([^\)]+\)|[^\(\)]*)+)\2\))?/
// 	},

// 	leftMatch: {},

// 	attrMap: {
// 		"class": "className",
// 		"for": "htmlFor"
// 	},

// 	attrHandle: {
// 		href: function( elem ) {
// 			return elem.getAttribute( "href" );
// 		}
// 	},

// 	relative: {
// 		"+": function(checkSet, part){
// 			var isPartStr = typeof part === "string",
// 				isTag = isPartStr && !/\W/.test( part ),
// 				isPartStrNotTag = isPartStr && !isTag;

// 			if ( isTag ) {
// 				part = part.toLowerCase();
// 			}

// 			for ( var i = 0, l = checkSet.length, elem; i < l; i++ ) {
// 				if ( (elem = checkSet[i]) ) {
// 					while ( (elem = elem.previousSibling) && elem.nodeType !== 1 ) {}

// 					checkSet[i] = isPartStrNotTag || elem && elem.nodeName.toLowerCase() === part ?
// 						elem || false :
// 						elem === part;
// 				}
// 			}

// 			if ( isPartStrNotTag ) {
// 				Sizzle.filter( part, checkSet, true );
// 			}
// 		},

// 		">": function( checkSet, part ) {
// 			var elem,
// 				isPartStr = typeof part === "string",
// 				i = 0,
// 				l = checkSet.length;

// 			if ( isPartStr && !/\W/.test( part ) ) {
// 				part = part.toLowerCase();

// 				for ( ; i < l; i++ ) {
// 					elem = checkSet[i];

// 					if ( elem ) {
// 						var parent = elem.parentNode;
// 						checkSet[i] = parent.nodeName.toLowerCase() === part ? parent : false;
// 					}
// 				}

// 			} else {
// 				for ( ; i < l; i++ ) {
// 					elem = checkSet[i];

// 					if ( elem ) {
// 						checkSet[i] = isPartStr ?
// 							elem.parentNode :
// 							elem.parentNode === part;
// 					}
// 				}

// 				if ( isPartStr ) {
// 					Sizzle.filter( part, checkSet, true );
// 				}
// 			}
// 		},

// 		"": function(checkSet, part, isXML){
// 			var nodeCheck,
// 				doneName = done++,
// 				checkFn = dirCheck;

// 			if ( typeof part === "string" && !/\W/.test(part) ) {
// 				part = part.toLowerCase();
// 				nodeCheck = part;
// 				checkFn = dirNodeCheck;
// 			}

// 			checkFn( "parentNode", part, doneName, checkSet, nodeCheck, isXML );
// 		},

// 		"~": function( checkSet, part, isXML ) {
// 			var nodeCheck,
// 				doneName = done++,
// 				checkFn = dirCheck;

// 			if ( typeof part === "string" && !/\W/.test( part ) ) {
// 				part = part.toLowerCase();
// 				nodeCheck = part;
// 				checkFn = dirNodeCheck;
// 			}

// 			checkFn( "previousSibling", part, doneName, checkSet, nodeCheck, isXML );
// 		}
// 	},

// 	find: {
// 		ID: function( match, context, isXML ) {
// 			if ( typeof context.getElementById !== "undefined" && !isXML ) {
// 				var m = context.getElementById(match[1]);
// 				// Check parentNode to catch when Blackberry 4.6 returns
// 				// nodes that are no longer in the document #6963
// 				return m && m.parentNode ? [m] : [];
// 			}
// 		},

// 		NAME: function( match, context ) {
// 			if ( typeof context.getElementsByName !== "undefined" ) {
// 				var ret = [],
// 					results = context.getElementsByName( match[1] );

// 				for ( var i = 0, l = results.length; i < l; i++ ) {
// 					if ( results[i].getAttribute("name") === match[1] ) {
// 						ret.push( results[i] );
// 					}
// 				}

// 				return ret.length === 0 ? null : ret;
// 			}
// 		},

// 		TAG: function( match, context ) {
// 			if ( typeof context.getElementsByTagName !== "undefined" ) {
// 				return context.getElementsByTagName( match[1] );
// 			}
// 		}
// 	},
// 	preFilter: {
// 		CLASS: function( match, curLoop, inplace, result, not, isXML ) {
// 			match = " " + match[1].replace(/\\/g, "") + " ";

// 			if ( isXML ) {
// 				return match;
// 			}

// 			for ( var i = 0, elem; (elem = curLoop[i]) != null; i++ ) {
// 				if ( elem ) {
// 					if ( not ^ (elem.className && (" " + elem.className + " ").replace(/[\t\n\r]/g, " ").indexOf(match) >= 0) ) {
// 						if ( !inplace ) {
// 							result.push( elem );
// 						}

// 					} else if ( inplace ) {
// 						curLoop[i] = false;
// 					}
// 				}
// 			}

// 			return false;
// 		},

// 		ID: function( match ) {
// 			return match[1].replace(/\\/g, "");
// 		},

// 		TAG: function( match, curLoop ) {
// 			return match[1].toLowerCase();
// 		},

// 		CHILD: function( match ) {
// 			if ( match[1] === "nth" ) {
// 				if ( !match[2] ) {
// 					Sizzle.error( match[0] );
// 				}

// 				match[2] = match[2].replace(/^\+|\s*/g, '');

// 				// parse equations like 'even', 'odd', '5', '2n', '3n+2', '4n-1', '-n+6'
// 				var test = /(-?)(\d*)(?:n([+\-]?\d*))?/.exec(
// 					match[2] === "even" && "2n" || match[2] === "odd" && "2n+1" ||
// 					!/\D/.test( match[2] ) && "0n+" + match[2] || match[2]);

// 				// calculate the numbers (first)n+(last) including if they are negative
// 				match[2] = (test[1] + (test[2] || 1)) - 0;
// 				match[3] = test[3] - 0;
// 			}
// 			else if ( match[2] ) {
// 				Sizzle.error( match[0] );
// 			}

// 			// TODO: Move to normal caching system
// 			match[0] = done++;

// 			return match;
// 		},

// 		ATTR: function( match, curLoop, inplace, result, not, isXML ) {
// 			var name = match[1] = match[1].replace(/\\/g, "");
			
// 			if ( !isXML && Expr.attrMap[name] ) {
// 				match[1] = Expr.attrMap[name];
// 			}

// 			// Handle if an un-quoted value was used
// 			match[4] = ( match[4] || match[5] || "" ).replace(/\\/g, "");

// 			if ( match[2] === "~=" ) {
// 				match[4] = " " + match[4] + " ";
// 			}

// 			return match;
// 		},

// 		PSEUDO: function( match, curLoop, inplace, result, not ) {
// 			if ( match[1] === "not" ) {
// 				// If we're dealing with a complex expression, or a simple one
// 				if ( ( chunker.exec(match[3]) || "" ).length > 1 || /^\w/.test(match[3]) ) {
// 					match[3] = Sizzle(match[3], null, null, curLoop);

// 				} else {
// 					var ret = Sizzle.filter(match[3], curLoop, inplace, true ^ not);

// 					if ( !inplace ) {
// 						result.push.apply( result, ret );
// 					}

// 					return false;
// 				}

// 			} else if ( Expr.match.POS.test( match[0] ) || Expr.match.CHILD.test( match[0] ) ) {
// 				return true;
// 			}
			
// 			return match;
// 		},

// 		POS: function( match ) {
// 			match.unshift( true );

// 			return match;
// 		}
// 	},
	
// 	filters: {
// 		enabled: function( elem ) {
// 			return elem.disabled === false && elem.type !== "hidden";
// 		},

// 		disabled: function( elem ) {
// 			return elem.disabled === true;
// 		},

// 		checked: function( elem ) {
// 			return elem.checked === true;
// 		},
		
// 		selected: function( elem ) {
// 			// Accessing this property makes selected-by-default
// 			// options in Safari work properly
// 			elem.parentNode.selectedIndex;
			
// 			return elem.selected === true;
// 		},

// 		parent: function( elem ) {
// 			return !!elem.firstChild;
// 		},

// 		empty: function( elem ) {
// 			return !elem.firstChild;
// 		},

// 		has: function( elem, i, match ) {
// 			return !!Sizzle( match[3], elem ).length;
// 		},

// 		header: function( elem ) {
// 			return (/h\d/i).test( elem.nodeName );
// 		},

// 		text: function( elem ) {
// 			return "text" === elem.type;
// 		},
// 		radio: function( elem ) {
// 			return "radio" === elem.type;
// 		},

// 		checkbox: function( elem ) {
// 			return "checkbox" === elem.type;
// 		},

// 		file: function( elem ) {
// 			return "file" === elem.type;
// 		},
// 		password: function( elem ) {
// 			return "password" === elem.type;
// 		},

// 		submit: function( elem ) {
// 			return "submit" === elem.type;
// 		},

// 		image: function( elem ) {
// 			return "image" === elem.type;
// 		},

// 		reset: function( elem ) {
// 			return "reset" === elem.type;
// 		},

// 		button: function( elem ) {
// 			return "button" === elem.type || elem.nodeName.toLowerCase() === "button";
// 		},

// 		input: function( elem ) {
// 			return (/input|select|textarea|button/i).test( elem.nodeName );
// 		}
// 	},
// 	setFilters: {
// 		first: function( elem, i ) {
// 			return i === 0;
// 		},

// 		last: function( elem, i, match, array ) {
// 			return i === array.length - 1;
// 		},

// 		even: function( elem, i ) {
// 			return i % 2 === 0;
// 		},

// 		odd: function( elem, i ) {
// 			return i % 2 === 1;
// 		},

// 		lt: function( elem, i, match ) {
// 			return i < match[3] - 0;
// 		},

// 		gt: function( elem, i, match ) {
// 			return i > match[3] - 0;
// 		},

// 		nth: function( elem, i, match ) {
// 			return match[3] - 0 === i;
// 		},

// 		eq: function( elem, i, match ) {
// 			return match[3] - 0 === i;
// 		}
// 	},
// 	filter: {
// 		PSEUDO: function( elem, match, i, array ) {
// 			var name = match[1],
// 				filter = Expr.filters[ name ];

// 			if ( filter ) {
// 				return filter( elem, i, match, array );

// 			} else if ( name === "contains" ) {
// 				return (elem.textContent || elem.innerText || Sizzle.getText([ elem ]) || "").indexOf(match[3]) >= 0;

// 			} else if ( name === "not" ) {
// 				var not = match[3];

// 				for ( var j = 0, l = not.length; j < l; j++ ) {
// 					if ( not[j] === elem ) {
// 						return false;
// 					}
// 				}

// 				return true;

// 			} else {
// 				Sizzle.error( name );
// 			}
// 		},

// 		CHILD: function( elem, match ) {
// 			var type = match[1],
// 				node = elem;

// 			switch ( type ) {
// 				case "only":
// 				case "first":
// 					while ( (node = node.previousSibling) )	 {
// 						if ( node.nodeType === 1 ) { 
// 							return false; 
// 						}
// 					}

// 					if ( type === "first" ) { 
// 						return true; 
// 					}

// 					node = elem;

// 				case "last":
// 					while ( (node = node.nextSibling) )	 {
// 						if ( node.nodeType === 1 ) { 
// 							return false; 
// 						}
// 					}

// 					return true;

// 				case "nth":
// 					var first = match[2],
// 						last = match[3];

// 					if ( first === 1 && last === 0 ) {
// 						return true;
// 					}
					
// 					var doneName = match[0],
// 						parent = elem.parentNode;
	
// 					if ( parent && (parent.sizcache !== doneName || !elem.nodeIndex) ) {
// 						var count = 0;
						
// 						for ( node = parent.firstChild; node; node = node.nextSibling ) {
// 							if ( node.nodeType === 1 ) {
// 								node.nodeIndex = ++count;
// 							}
// 						} 

// 						parent.sizcache = doneName;
// 					}
					
// 					var diff = elem.nodeIndex - last;

// 					if ( first === 0 ) {
// 						return diff === 0;

// 					} else {
// 						return ( diff % first === 0 && diff / first >= 0 );
// 					}
// 			}
// 		},

// 		ID: function( elem, match ) {
// 			return elem.nodeType === 1 && elem.getAttribute("id") === match;
// 		},

// 		TAG: function( elem, match ) {
// 			return (match === "*" && elem.nodeType === 1) || elem.nodeName.toLowerCase() === match;
// 		},
		
// 		CLASS: function( elem, match ) {
// 			return (" " + (elem.className || elem.getAttribute("class")) + " ")
// 				.indexOf( match ) > -1;
// 		},

// 		ATTR: function( elem, match ) {
// 			var name = match[1],
// 				result = Expr.attrHandle[ name ] ?
// 					Expr.attrHandle[ name ]( elem ) :
// 					elem[ name ] != null ?
// 						elem[ name ] :
// 						elem.getAttribute( name ),
// 				value = result + "",
// 				type = match[2],
// 				check = match[4];

// 			return result == null ?
// 				type === "!=" :
// 				type === "=" ?
// 				value === check :
// 				type === "*=" ?
// 				value.indexOf(check) >= 0 :
// 				type === "~=" ?
// 				(" " + value + " ").indexOf(check) >= 0 :
// 				!check ?
// 				value && result !== false :
// 				type === "!=" ?
// 				value !== check :
// 				type === "^=" ?
// 				value.indexOf(check) === 0 :
// 				type === "$=" ?
// 				value.substr(value.length - check.length) === check :
// 				type === "|=" ?
// 				value === check || value.substr(0, check.length + 1) === check + "-" :
// 				false;
// 		},

// 		POS: function( elem, match, i, array ) {
// 			var name = match[2],
// 				filter = Expr.setFilters[ name ];

// 			if ( filter ) {
// 				return filter( elem, i, match, array );
// 			}
// 		}
// 	}
// };

// var origPOS = Expr.match.POS,
// 	fescape = function(all, num){
// 		return "\\" + (num - 0 + 1);
// 	};

// for ( var type in Expr.match ) {
// 	Expr.match[ type ] = new RegExp( Expr.match[ type ].source + (/(?![^\[]*\])(?![^\(]*\))/.source) );
// 	Expr.leftMatch[ type ] = new RegExp( /(^(?:.|\r|\n)*?)/.source + Expr.match[ type ].source.replace(/\\(\d+)/g, fescape) );
// }

// var makeArray = function( array, results ) {
// 	array = Array.prototype.slice.call( array, 0 );

// 	if ( results ) {
// 		results.push.apply( results, array );
// 		return results;
// 	}
	
// 	return array;
// };

// // Perform a simple check to determine if the browser is capable of
// // converting a NodeList to an array using builtin methods.
// // Also verifies that the returned array holds DOM nodes
// // (which is not the case in the Blackberry browser)
// try {
// 	Array.prototype.slice.call( document.documentElement.childNodes, 0 )[0].nodeType;

// // Provide a fallback method if it does not work
// } catch( e ) {
// 	makeArray = function( array, results ) {
// 		var i = 0,
// 			ret = results || [];

// 		if ( toString.call(array) === "[object Array]" ) {
// 			Array.prototype.push.apply( ret, array );

// 		} else {
// 			if ( typeof array.length === "number" ) {
// 				for ( var l = array.length; i < l; i++ ) {
// 					ret.push( array[i] );
// 				}

// 			} else {
// 				for ( ; array[i]; i++ ) {
// 					ret.push( array[i] );
// 				}
// 			}
// 		}

// 		return ret;
// 	};
// }

// var sortOrder, siblingCheck;

// if ( document.documentElement.compareDocumentPosition ) {
// 	sortOrder = function( a, b ) {
// 		if ( a === b ) {
// 			hasDuplicate = true;
// 			return 0;
// 		}

// 		if ( !a.compareDocumentPosition || !b.compareDocumentPosition ) {
// 			return a.compareDocumentPosition ? -1 : 1;
// 		}

// 		return a.compareDocumentPosition(b) & 4 ? -1 : 1;
// 	};

// } else {
// 	sortOrder = function( a, b ) {
// 		var al, bl,
// 			ap = [],
// 			bp = [],
// 			aup = a.parentNode,
// 			bup = b.parentNode,
// 			cur = aup;

// 		// The nodes are identical, we can exit early
// 		if ( a === b ) {
// 			hasDuplicate = true;
// 			return 0;

// 		// If the nodes are siblings (or identical) we can do a quick check
// 		} else if ( aup === bup ) {
// 			return siblingCheck( a, b );

// 		// If no parents were found then the nodes are disconnected
// 		} else if ( !aup ) {
// 			return -1;

// 		} else if ( !bup ) {
// 			return 1;
// 		}

// 		// Otherwise they're somewhere else in the tree so we need
// 		// to build up a full list of the parentNodes for comparison
// 		while ( cur ) {
// 			ap.unshift( cur );
// 			cur = cur.parentNode;
// 		}

// 		cur = bup;

// 		while ( cur ) {
// 			bp.unshift( cur );
// 			cur = cur.parentNode;
// 		}

// 		al = ap.length;
// 		bl = bp.length;

// 		// Start walking down the tree looking for a discrepancy
// 		for ( var i = 0; i < al && i < bl; i++ ) {
// 			if ( ap[i] !== bp[i] ) {
// 				return siblingCheck( ap[i], bp[i] );
// 			}
// 		}

// 		// We ended someplace up the tree so do a sibling check
// 		return i === al ?
// 			siblingCheck( a, bp[i], -1 ) :
// 			siblingCheck( ap[i], b, 1 );
// 	};

// 	siblingCheck = function( a, b, ret ) {
// 		if ( a === b ) {
// 			return ret;
// 		}

// 		var cur = a.nextSibling;

// 		while ( cur ) {
// 			if ( cur === b ) {
// 				return -1;
// 			}

// 			cur = cur.nextSibling;
// 		}

// 		return 1;
// 	};
// }

// // Utility function for retreiving the text value of an array of DOM nodes
// Sizzle.getText = function( elems ) {
// 	var ret = "", elem;

// 	for ( var i = 0; elems[i]; i++ ) {
// 		elem = elems[i];

// 		// Get the text from text nodes and CDATA nodes
// 		if ( elem.nodeType === 3 || elem.nodeType === 4 ) {
// 			ret += elem.nodeValue;

// 		// Traverse everything else, except comment nodes
// 		} else if ( elem.nodeType !== 8 ) {
// 			ret += Sizzle.getText( elem.childNodes );
// 		}
// 	}

// 	return ret;
// };

// // Check to see if the browser returns elements by name when
// // querying by getElementById (and provide a workaround)
// (function(){
// 	// We're going to inject a fake input element with a specified name
// 	var form = document.createElement("div"),
// 		id = "script" + (new Date()).getTime(),
// 		root = document.documentElement;

// 	form.innerHTML = "<a name='" + id + "'/>";

// 	// Inject it into the root element, check its status, and remove it quickly
// 	root.insertBefore( form, root.firstChild );

// 	// The workaround has to do additional checks after a getElementById
// 	// Which slows things down for other browsers (hence the branching)
// 	if ( document.getElementById( id ) ) {
// 		Expr.find.ID = function( match, context, isXML ) {
// 			if ( typeof context.getElementById !== "undefined" && !isXML ) {
// 				var m = context.getElementById(match[1]);

// 				return m ?
// 					m.id === match[1] || typeof m.getAttributeNode !== "undefined" && m.getAttributeNode("id").nodeValue === match[1] ?
// 						[m] :
// 						undefined :
// 					[];
// 			}
// 		};

// 		Expr.filter.ID = function( elem, match ) {
// 			var node = typeof elem.getAttributeNode !== "undefined" && elem.getAttributeNode("id");

// 			return elem.nodeType === 1 && node && node.nodeValue === match;
// 		};
// 	}

// 	root.removeChild( form );

// 	// release memory in IE
// 	root = form = null;
// })();

// (function(){
// 	// Check to see if the browser returns only elements
// 	// when doing getElementsByTagName("*")

// 	// Create a fake element
// 	var div = document.createElement("div");
// 	div.appendChild( document.createComment("") );

// 	// Make sure no comments are found
// 	if ( div.getElementsByTagName("*").length > 0 ) {
// 		Expr.find.TAG = function( match, context ) {
// 			var results = context.getElementsByTagName( match[1] );

// 			// Filter out possible comments
// 			if ( match[1] === "*" ) {
// 				var tmp = [];

// 				for ( var i = 0; results[i]; i++ ) {
// 					if ( results[i].nodeType === 1 ) {
// 						tmp.push( results[i] );
// 					}
// 				}

// 				results = tmp;
// 			}

// 			return results;
// 		};
// 	}

// 	// Check to see if an attribute returns normalized href attributes
// 	div.innerHTML = "<a href='#'></a>";

// 	if ( div.firstChild && typeof div.firstChild.getAttribute !== "undefined" &&
// 			div.firstChild.getAttribute("href") !== "#" ) {

// 		Expr.attrHandle.href = function( elem ) {
// 			return elem.getAttribute( "href", 2 );
// 		};
// 	}

// 	// release memory in IE
// 	div = null;
// })();

// if ( document.querySelectorAll ) {
// 	(function(){
// 		var oldSizzle = Sizzle,
// 			div = document.createElement("div"),
// 			id = "__sizzle__";

// 		div.innerHTML = "<p class='TEST'></p>";

// 		// Safari can't handle uppercase or unicode characters when
// 		// in quirks mode.
// 		if ( div.querySelectorAll && div.querySelectorAll(".TEST").length === 0 ) {
// 			return;
// 		}
	
// 		Sizzle = function( query, context, extra, seed ) {
// 			context = context || document;

// 			// Only use querySelectorAll on non-XML documents
// 			// (ID selectors don't work in non-HTML documents)
// 			if ( !seed && !Sizzle.isXML(context) ) {
// 				// See if we find a selector to speed up
// 				var match = /^(\w+$)|^\.([\w\-]+$)|^#([\w\-]+$)/.exec( query );
				
// 				if ( match && (context.nodeType === 1 || context.nodeType === 9) ) {
// 					// Speed-up: Sizzle("TAG")
// 					if ( match[1] ) {
// 						return makeArray( context.getElementsByTagName( query ), extra );
					
// 					// Speed-up: Sizzle(".CLASS")
// 					} else if ( match[2] && Expr.find.CLASS && context.getElementsByClassName ) {
// 						return makeArray( context.getElementsByClassName( match[2] ), extra );
// 					}
// 				}
				
// 				if ( context.nodeType === 9 ) {
// 					// Speed-up: Sizzle("body")
// 					// The body element only exists once, optimize finding it
// 					if ( query === "body" && context.body ) {
// 						return makeArray( [ context.body ], extra );
						
// 					// Speed-up: Sizzle("#ID")
// 					} else if ( match && match[3] ) {
// 						var elem = context.getElementById( match[3] );

// 						// Check parentNode to catch when Blackberry 4.6 returns
// 						// nodes that are no longer in the document #6963
// 						if ( elem && elem.parentNode ) {
// 							// Handle the case where IE and Opera return items
// 							// by name instead of ID
// 							if ( elem.id === match[3] ) {
// 								return makeArray( [ elem ], extra );
// 							}
							
// 						} else {
// 							return makeArray( [], extra );
// 						}
// 					}
					
// 					try {
// 						return makeArray( context.querySelectorAll(query), extra );
// 					} catch(qsaError) {}

// 				// qSA works strangely on Element-rooted queries
// 				// We can work around this by specifying an extra ID on the root
// 				// and working up from there (Thanks to Andrew Dupont for the technique)
// 				// IE 8 doesn't work on object elements
// 				} else if ( context.nodeType === 1 && context.nodeName.toLowerCase() !== "object" ) {
// 					var old = context.getAttribute( "id" ),
// 						nid = old || id,
// 						hasParent = context.parentNode,
// 						relativeHierarchySelector = /^\s*[+~]/.test( query );

// 					if ( !old ) {
// 						context.setAttribute( "id", nid );
// 					} else {
// 						nid = nid.replace( /'/g, "\\$&" );
// 					}
// 					if ( relativeHierarchySelector && hasParent ) {
// 						context = context.parentNode;
// 					}

// 					try {
// 						if ( !relativeHierarchySelector || hasParent ) {
// 							return makeArray( context.querySelectorAll( "[id='" + nid + "'] " + query ), extra );
// 						}

// 					} catch(pseudoError) {
// 					} finally {
// 						if ( !old ) {
// 							context.removeAttribute( "id" );
// 						}
// 					}
// 				}
// 			}
		
// 			return oldSizzle(query, context, extra, seed);
// 		};

// 		for ( var prop in oldSizzle ) {
// 			Sizzle[ prop ] = oldSizzle[ prop ];
// 		}

// 		// release memory in IE
// 		div = null;
// 	})();
// }

// (function(){
// 	var html = document.documentElement,
// 		matches = html.matchesSelector || html.mozMatchesSelector || html.webkitMatchesSelector || html.msMatchesSelector,
// 		pseudoWorks = false;

// 	try {
// 		// This should fail with an exception
// 		// Gecko does not error, returns false instead
// 		matches.call( document.documentElement, "[test!='']:sizzle" );
	
// 	} catch( pseudoError ) {
// 		pseudoWorks = true;
// 	}

// 	if ( matches ) {
// 		Sizzle.matchesSelector = function( node, expr ) {
// 			// Make sure that attribute selectors are quoted
// 			expr = expr.replace(/\=\s*([^'"\]]*)\s*\]/g, "='$1']");

// 			if ( !Sizzle.isXML( node ) ) {
// 				try { 
// 					if ( pseudoWorks || !Expr.match.PSEUDO.test( expr ) && !/!=/.test( expr ) ) {
// 						return matches.call( node, expr );
// 					}
// 				} catch(e) {}
// 			}

// 			return Sizzle(expr, null, null, [node]).length > 0;
// 		};
// 	}
// })();

// (function(){
// 	var div = document.createElement("div");

// 	div.innerHTML = "<div class='test e'></div><div class='test'></div>";

// 	// Opera can't find a second classname (in 9.6)
// 	// Also, make sure that getElementsByClassName actually exists
// 	if ( !div.getElementsByClassName || div.getElementsByClassName("e").length === 0 ) {
// 		return;
// 	}

// 	// Safari caches class attributes, doesn't catch changes (in 3.2)
// 	div.lastChild.className = "e";

// 	if ( div.getElementsByClassName("e").length === 1 ) {
// 		return;
// 	}
	
// 	Expr.order.splice(1, 0, "CLASS");
// 	Expr.find.CLASS = function( match, context, isXML ) {
// 		if ( typeof context.getElementsByClassName !== "undefined" && !isXML ) {
// 			return context.getElementsByClassName(match[1]);
// 		}
// 	};

// 	// release memory in IE
// 	div = null;
// })();

// function dirNodeCheck( dir, cur, doneName, checkSet, nodeCheck, isXML ) {
// 	for ( var i = 0, l = checkSet.length; i < l; i++ ) {
// 		var elem = checkSet[i];

// 		if ( elem ) {
// 			var match = false;

// 			elem = elem[dir];

// 			while ( elem ) {
// 				if ( elem.sizcache === doneName ) {
// 					match = checkSet[elem.sizset];
// 					break;
// 				}

// 				if ( elem.nodeType === 1 && !isXML ){
// 					elem.sizcache = doneName;
// 					elem.sizset = i;
// 				}

// 				if ( elem.nodeName.toLowerCase() === cur ) {
// 					match = elem;
// 					break;
// 				}

// 				elem = elem[dir];
// 			}

// 			checkSet[i] = match;
// 		}
// 	}
// }

// function dirCheck( dir, cur, doneName, checkSet, nodeCheck, isXML ) {
// 	for ( var i = 0, l = checkSet.length; i < l; i++ ) {
// 		var elem = checkSet[i];

// 		if ( elem ) {
// 			var match = false;
			
// 			elem = elem[dir];

// 			while ( elem ) {
// 				if ( elem.sizcache === doneName ) {
// 					match = checkSet[elem.sizset];
// 					break;
// 				}

// 				if ( elem.nodeType === 1 ) {
// 					if ( !isXML ) {
// 						elem.sizcache = doneName;
// 						elem.sizset = i;
// 					}

// 					if ( typeof cur !== "string" ) {
// 						if ( elem === cur ) {
// 							match = true;
// 							break;
// 						}

// 					} else if ( Sizzle.filter( cur, [elem] ).length > 0 ) {
// 						match = elem;
// 						break;
// 					}
// 				}

// 				elem = elem[dir];
// 			}

// 			checkSet[i] = match;
// 		}
// 	}
// }

// if ( document.documentElement.contains ) {
// 	Sizzle.contains = function( a, b ) {
// 		return a !== b && (a.contains ? a.contains(b) : true);
// 	};

// } else if ( document.documentElement.compareDocumentPosition ) {
// 	Sizzle.contains = function( a, b ) {
// 		return !!(a.compareDocumentPosition(b) & 16);
// 	};

// } else {
// 	Sizzle.contains = function() {
// 		return false;
// 	};
// }

// Sizzle.isXML = function( elem ) {
// 	// documentElement is verified for cases where it doesn't yet exist
// 	// (such as loading iframes in IE - #4833) 
// 	var documentElement = (elem ? elem.ownerDocument || elem : 0).documentElement;

// 	return documentElement ? documentElement.nodeName !== "HTML" : false;
// };

// var posProcess = function( selector, context ) {
// 	var match,
// 		tmpSet = [],
// 		later = "",
// 		root = context.nodeType ? [context] : context;

// 	// Position selectors must be done after the filter
// 	// And so must :not(positional) so we move all PSEUDOs to the end
// 	while ( (match = Expr.match.PSEUDO.exec( selector )) ) {
// 		later += match[0];
// 		selector = selector.replace( Expr.match.PSEUDO, "" );
// 	}

// 	selector = Expr.relative[selector] ? selector + "*" : selector;

// 	for ( var i = 0, l = root.length; i < l; i++ ) {
// 		Sizzle( selector, root[i], tmpSet );
// 	}

// 	return Sizzle.filter( later, tmpSet );
// };

// // EXPOSE
// jQuery.find = Sizzle;
// jQuery.expr = Sizzle.selectors;
// jQuery.expr[":"] = jQuery.expr.filters;
// jQuery.unique = Sizzle.uniqueSort;
// jQuery.text = Sizzle.getText;
// jQuery.isXMLDoc = Sizzle.isXML;
// jQuery.contains = Sizzle.contains;


// })();


// var runtil = /Until$/,
// 	rparentsprev = /^(?:parents|prevUntil|prevAll)/,
// 	// Note: This RegExp should be improved, or likely pulled from Sizzle
// 	rmultiselector = /,/,
// 	isSimple = /^.[^:#\[\.,]*$/,
// 	slice = Array.prototype.slice,
// 	POS = jQuery.expr.match.POS,
// 	// methods guaranteed to produce a unique set when starting from a unique set
// 	guaranteedUnique = {
// 		children: true,
// 		contents: true,
// 		next: true,
// 		prev: true
// 	};

// jQuery.fn.extend({
// 	find: function( selector ) {
// 		var ret = this.pushStack( "", "find", selector ),
// 			length = 0;

// 		for ( var i = 0, l = this.length; i < l; i++ ) {
// 			length = ret.length;
// 			jQuery.find( selector, this[i], ret );

// 			if ( i > 0 ) {
// 				// Make sure that the results are unique
// 				for ( var n = length; n < ret.length; n++ ) {
// 					for ( var r = 0; r < length; r++ ) {
// 						if ( ret[r] === ret[n] ) {
// 							ret.splice(n--, 1);
// 							break;
// 						}
// 					}
// 				}
// 			}
// 		}

// 		return ret;
// 	},

// 	has: function( target ) {
// 		var targets = jQuery( target );
// 		return this.filter(function() {
// 			for ( var i = 0, l = targets.length; i < l; i++ ) {
// 				if ( jQuery.contains( this, targets[i] ) ) {
// 					return true;
// 				}
// 			}
// 		});
// 	},

// 	not: function( selector ) {
// 		return this.pushStack( winnow(this, selector, false), "not", selector);
// 	},

// 	filter: function( selector ) {
// 		return this.pushStack( winnow(this, selector, true), "filter", selector );
// 	},

// 	is: function( selector ) {
// 		return !!selector && jQuery.filter( selector, this ).length > 0;
// 	},

// 	closest: function( selectors, context ) {
// 		var ret = [], i, l, cur = this[0];

// 		if ( jQuery.isArray( selectors ) ) {
// 			var match, selector,
// 				matches = {},
// 				level = 1;

// 			if ( cur && selectors.length ) {
// 				for ( i = 0, l = selectors.length; i < l; i++ ) {
// 					selector = selectors[i];

// 					if ( !matches[selector] ) {
// 						matches[selector] = jQuery.expr.match.POS.test( selector ) ?
// 							jQuery( selector, context || this.context ) :
// 							selector;
// 					}
// 				}

// 				while ( cur && cur.ownerDocument && cur !== context ) {
// 					for ( selector in matches ) {
// 						match = matches[selector];

// 						if ( match.jquery ? match.index(cur) > -1 : jQuery(cur).is(match) ) {
// 							ret.push({ selector: selector, elem: cur, level: level });
// 						}
// 					}

// 					cur = cur.parentNode;
// 					level++;
// 				}
// 			}

// 			return ret;
// 		}

// 		var pos = POS.test( selectors ) ?
// 			jQuery( selectors, context || this.context ) : null;

// 		for ( i = 0, l = this.length; i < l; i++ ) {
// 			cur = this[i];

// 			while ( cur ) {
// 				if ( pos ? pos.index(cur) > -1 : jQuery.find.matchesSelector(cur, selectors) ) {
// 					ret.push( cur );
// 					break;

// 				} else {
// 					cur = cur.parentNode;
// 					if ( !cur || !cur.ownerDocument || cur === context ) {
// 						break;
// 					}
// 				}
// 			}
// 		}

// 		ret = ret.length > 1 ? jQuery.unique(ret) : ret;

// 		return this.pushStack( ret, "closest", selectors );
// 	},

// 	// Determine the position of an element within
// 	// the matched set of elements
// 	index: function( elem ) {
// 		if ( !elem || typeof elem === "string" ) {
// 			return jQuery.inArray( this[0],
// 				// If it receives a string, the selector is used
// 				// If it receives nothing, the siblings are used
// 				elem ? jQuery( elem ) : this.parent().children() );
// 		}
// 		// Locate the position of the desired element
// 		return jQuery.inArray(
// 			// If it receives a jQuery object, the first element is used
// 			elem.jquery ? elem[0] : elem, this );
// 	},

// 	add: function( selector, context ) {
// 		var set = typeof selector === "string" ?
// 				jQuery( selector, context ) :
// 				jQuery.makeArray( selector ),
// 			all = jQuery.merge( this.get(), set );

// 		return this.pushStack( isDisconnected( set[0] ) || isDisconnected( all[0] ) ?
// 			all :
// 			jQuery.unique( all ) );
// 	},

// 	andSelf: function() {
// 		return this.add( this.prevObject );
// 	}
// });

// // A painfully simple check to see if an element is disconnected
// // from a document (should be improved, where feasible).
// function isDisconnected( node ) {
// 	return !node || !node.parentNode || node.parentNode.nodeType === 11;
// }

// jQuery.each({
// 	parent: function( elem ) {
// 		var parent = elem.parentNode;
// 		return parent && parent.nodeType !== 11 ? parent : null;
// 	},
// 	parents: function( elem ) {
// 		return jQuery.dir( elem, "parentNode" );
// 	},
// 	parentsUntil: function( elem, i, until ) {
// 		return jQuery.dir( elem, "parentNode", until );
// 	},
// 	next: function( elem ) {
// 		return jQuery.nth( elem, 2, "nextSibling" );
// 	},
// 	prev: function( elem ) {
// 		return jQuery.nth( elem, 2, "previousSibling" );
// 	},
// 	nextAll: function( elem ) {
// 		return jQuery.dir( elem, "nextSibling" );
// 	},
// 	prevAll: function( elem ) {
// 		return jQuery.dir( elem, "previousSibling" );
// 	},
// 	nextUntil: function( elem, i, until ) {
// 		return jQuery.dir( elem, "nextSibling", until );
// 	},
// 	prevUntil: function( elem, i, until ) {
// 		return jQuery.dir( elem, "previousSibling", until );
// 	},
// 	siblings: function( elem ) {
// 		return jQuery.sibling( elem.parentNode.firstChild, elem );
// 	},
// 	children: function( elem ) {
// 		return jQuery.sibling( elem.firstChild );
// 	},
// 	contents: function( elem ) {
// 		return jQuery.nodeName( elem, "iframe" ) ?
// 			elem.contentDocument || elem.contentWindow.document :
// 			jQuery.makeArray( elem.childNodes );
// 	}
// }, function( name, fn ) {
// 	jQuery.fn[ name ] = function( until, selector ) {
// 		var ret = jQuery.map( this, fn, until ),
//                 // The variable 'args' was introduced in
//                 // https://github.com/jquery/jquery/commit/52a0238
//                 // to work around a bug in Chrome 10 (Dev) and should be removed when the bug is fixed.
//                 // http://code.google.com/p/v8/issues/detail?id=1050
//                     args = slice.call(arguments);

// 		if ( !runtil.test( name ) ) {
// 			selector = until;
// 		}

// 		if ( selector && typeof selector === "string" ) {
// 			ret = jQuery.filter( selector, ret );
// 		}

// 		ret = this.length > 1 && !guaranteedUnique[ name ] ? jQuery.unique( ret ) : ret;

// 		if ( (this.length > 1 || rmultiselector.test( selector )) && rparentsprev.test( name ) ) {
// 			ret = ret.reverse();
// 		}

// 		return this.pushStack( ret, name, args.join(",") );
// 	};
// });

// jQuery.extend({
// 	filter: function( expr, elems, not ) {
// 		if ( not ) {
// 			expr = ":not(" + expr + ")";
// 		}

// 		return elems.length === 1 ?
// 			jQuery.find.matchesSelector(elems[0], expr) ? [ elems[0] ] : [] :
// 			jQuery.find.matches(expr, elems);
// 	},

// 	dir: function( elem, dir, until ) {
// 		var matched = [],
// 			cur = elem[ dir ];

// 		while ( cur && cur.nodeType !== 9 && (until === undefined || cur.nodeType !== 1 || !jQuery( cur ).is( until )) ) {
// 			if ( cur.nodeType === 1 ) {
// 				matched.push( cur );
// 			}
// 			cur = cur[dir];
// 		}
// 		return matched;
// 	},

// 	nth: function( cur, result, dir, elem ) {
// 		result = result || 1;
// 		var num = 0;

// 		for ( ; cur; cur = cur[dir] ) {
// 			if ( cur.nodeType === 1 && ++num === result ) {
// 				break;
// 			}
// 		}

// 		return cur;
// 	},

// 	sibling: function( n, elem ) {
// 		var r = [];

// 		for ( ; n; n = n.nextSibling ) {
// 			if ( n.nodeType === 1 && n !== elem ) {
// 				r.push( n );
// 			}
// 		}

// 		return r;
// 	}
// });

// // Implement the identical functionality for filter and not
// function winnow( elements, qualifier, keep ) {
// 	if ( jQuery.isFunction( qualifier ) ) {
// 		return jQuery.grep(elements, function( elem, i ) {
// 			var retVal = !!qualifier.call( elem, i, elem );
// 			return retVal === keep;
// 		});

// 	} else if ( qualifier.nodeType ) {
// 		return jQuery.grep(elements, function( elem, i ) {
// 			return (elem === qualifier) === keep;
// 		});

// 	} else if ( typeof qualifier === "string" ) {
// 		var filtered = jQuery.grep(elements, function( elem ) {
// 			return elem.nodeType === 1;
// 		});

// 		if ( isSimple.test( qualifier ) ) {
// 			return jQuery.filter(qualifier, filtered, !keep);
// 		} else {
// 			qualifier = jQuery.filter( qualifier, filtered );
// 		}
// 	}

// 	return jQuery.grep(elements, function( elem, i ) {
// 		return (jQuery.inArray( elem, qualifier ) >= 0) === keep;
// 	});
// }




// var rinlinejQuery = / jQuery\d+="(?:\d+|null)"/g,
// 	rleadingWhitespace = /^\s+/,
// 	rxhtmlTag = /<(?!area|br|col|embed|hr|img|input|link|meta|param)(([\w:]+)[^>]*)\/>/ig,
// 	rtagName = /<([\w:]+)/,
// 	rtbody = /<tbody/i,
// 	rhtml = /<|&#?\w+;/,
// 	rnocache = /<(?:script|object|embed|option|style)/i,
// 	// checked="checked" or checked (html5)
// 	rchecked = /checked\s*(?:[^=]|=\s*.checked.)/i,
// 	wrapMap = {
// 		option: [ 1, "<select multiple='multiple'>", "</select>" ],
// 		legend: [ 1, "<fieldset>", "</fieldset>" ],
// 		thead: [ 1, "<table>", "</table>" ],
// 		tr: [ 2, "<table><tbody>", "</tbody></table>" ],
// 		td: [ 3, "<table><tbody><tr>", "</tr></tbody></table>" ],
// 		col: [ 2, "<table><tbody></tbody><colgroup>", "</colgroup></table>" ],
// 		area: [ 1, "<map>", "</map>" ],
// 		_default: [ 0, "", "" ]
// 	};

// wrapMap.optgroup = wrapMap.option;
// wrapMap.tbody = wrapMap.tfoot = wrapMap.colgroup = wrapMap.caption = wrapMap.thead;
// wrapMap.th = wrapMap.td;

// // IE can't serialize <link> and <script> tags normally
// if ( !jQuery.support.htmlSerialize ) {
// 	wrapMap._default = [ 1, "div<div>", "</div>" ];
// }

// jQuery.fn.extend({
// 	text: function( text ) {
// 		if ( jQuery.isFunction(text) ) {
// 			return this.each(function(i) {
// 				var self = jQuery( this );

// 				self.text( text.call(this, i, self.text()) );
// 			});
// 		}

// 		if ( typeof text !== "object" && text !== undefined ) {
// 			return this.empty().append( (this[0] && this[0].ownerDocument || document).createTextNode( text ) );
// 		}

// 		return jQuery.text( this );
// 	},

// 	wrapAll: function( html ) {
// 		if ( jQuery.isFunction( html ) ) {
// 			return this.each(function(i) {
// 				jQuery(this).wrapAll( html.call(this, i) );
// 			});
// 		}

// 		if ( this[0] ) {
// 			// The elements to wrap the target around
// 			var wrap = jQuery( html, this[0].ownerDocument ).eq(0).clone(true);

// 			if ( this[0].parentNode ) {
// 				wrap.insertBefore( this[0] );
// 			}

// 			wrap.map(function() {
// 				var elem = this;

// 				while ( elem.firstChild && elem.firstChild.nodeType === 1 ) {
// 					elem = elem.firstChild;
// 				}

// 				return elem;
// 			}).append(this);
// 		}

// 		return this;
// 	},

// 	wrapInner: function( html ) {
// 		if ( jQuery.isFunction( html ) ) {
// 			return this.each(function(i) {
// 				jQuery(this).wrapInner( html.call(this, i) );
// 			});
// 		}

// 		return this.each(function() {
// 			var self = jQuery( this ),
// 				contents = self.contents();

// 			if ( contents.length ) {
// 				contents.wrapAll( html );

// 			} else {
// 				self.append( html );
// 			}
// 		});
// 	},

// 	wrap: function( html ) {
// 		return this.each(function() {
// 			jQuery( this ).wrapAll( html );
// 		});
// 	},

// 	unwrap: function() {
// 		return this.parent().each(function() {
// 			if ( !jQuery.nodeName( this, "body" ) ) {
// 				jQuery( this ).replaceWith( this.childNodes );
// 			}
// 		}).end();
// 	},

// 	append: function() {
// 		return this.domManip(arguments, true, function( elem ) {
// 			if ( this.nodeType === 1 ) {
// 				this.appendChild( elem );
// 			}
// 		});
// 	},

// 	prepend: function() {
// 		return this.domManip(arguments, true, function( elem ) {
// 			if ( this.nodeType === 1 ) {
// 				this.insertBefore( elem, this.firstChild );
// 			}
// 		});
// 	},

// 	before: function() {
// 		if ( this[0] && this[0].parentNode ) {
// 			return this.domManip(arguments, false, function( elem ) {
// 				this.parentNode.insertBefore( elem, this );
// 			});
// 		} else if ( arguments.length ) {
// 			var set = jQuery(arguments[0]);
// 			set.push.apply( set, this.toArray() );
// 			return this.pushStack( set, "before", arguments );
// 		}
// 	},

// 	after: function() {
// 		if ( this[0] && this[0].parentNode ) {
// 			return this.domManip(arguments, false, function( elem ) {
// 				this.parentNode.insertBefore( elem, this.nextSibling );
// 			});
// 		} else if ( arguments.length ) {
// 			var set = this.pushStack( this, "after", arguments );
// 			set.push.apply( set, jQuery(arguments[0]).toArray() );
// 			return set;
// 		}
// 	},

// 	// keepData is for internal use only--do not document
// 	remove: function( selector, keepData ) {
// 		for ( var i = 0, elem; (elem = this[i]) != null; i++ ) {
// 			if ( !selector || jQuery.filter( selector, [ elem ] ).length ) {
// 				if ( !keepData && elem.nodeType === 1 ) {
// 					jQuery.cleanData( elem.getElementsByTagName("*") );
// 					jQuery.cleanData( [ elem ] );
// 				}

// 				if ( elem.parentNode ) {
// 					 elem.parentNode.removeChild( elem );
// 				}
// 			}
// 		}

// 		return this;
// 	},

// 	empty: function() {
// 		for ( var i = 0, elem; (elem = this[i]) != null; i++ ) {
// 			// Remove element nodes and prevent memory leaks
// 			if ( elem.nodeType === 1 ) {
// 				jQuery.cleanData( elem.getElementsByTagName("*") );
// 			}

// 			// Remove any remaining nodes
// 			while ( elem.firstChild ) {
// 				elem.removeChild( elem.firstChild );
// 			}
// 		}

// 		return this;
// 	},

// 	clone: function( dataAndEvents, deepDataAndEvents ) {
// 		dataAndEvents = dataAndEvents == null ? true : dataAndEvents;
// 		deepDataAndEvents = deepDataAndEvents == null ? dataAndEvents : deepDataAndEvents;

// 		return this.map( function () {
// 			return jQuery.clone( this, dataAndEvents, deepDataAndEvents );
// 		});
// 	},

// 	html: function( value ) {
// 		if ( value === undefined ) {
// 			return this[0] && this[0].nodeType === 1 ?
// 				this[0].innerHTML.replace(rinlinejQuery, "") :
// 				null;

// 		// See if we can take a shortcut and just use innerHTML
// 		} else if ( typeof value === "string" && !rnocache.test( value ) &&
// 			(jQuery.support.leadingWhitespace || !rleadingWhitespace.test( value )) &&
// 			!wrapMap[ (rtagName.exec( value ) || ["", ""])[1].toLowerCase() ] ) {

// 			value = value.replace(rxhtmlTag, "<$1></$2>");

// 			try {
// 				for ( var i = 0, l = this.length; i < l; i++ ) {
// 					// Remove element nodes and prevent memory leaks
// 					if ( this[i].nodeType === 1 ) {
// 						jQuery.cleanData( this[i].getElementsByTagName("*") );
// 						this[i].innerHTML = value;
// 					}
// 				}

// 			// If using innerHTML throws an exception, use the fallback method
// 			} catch(e) {
// 				this.empty().append( value );
// 			}

// 		} else if ( jQuery.isFunction( value ) ) {
// 			this.each(function(i){
// 				var self = jQuery( this );

// 				self.html( value.call(this, i, self.html()) );
// 			});

// 		} else {
// 			this.empty().append( value );
// 		}

// 		return this;
// 	},

// 	replaceWith: function( value ) {
// 		if ( this[0] && this[0].parentNode ) {
// 			// Make sure that the elements are removed from the DOM before they are inserted
// 			// this can help fix replacing a parent with child elements
// 			if ( jQuery.isFunction( value ) ) {
// 				return this.each(function(i) {
// 					var self = jQuery(this), old = self.html();
// 					self.replaceWith( value.call( this, i, old ) );
// 				});
// 			}

// 			if ( typeof value !== "string" ) {
// 				value = jQuery( value ).detach();
// 			}

// 			return this.each(function() {
// 				var next = this.nextSibling,
// 					parent = this.parentNode;

// 				jQuery( this ).remove();

// 				if ( next ) {
// 					jQuery(next).before( value );
// 				} else {
// 					jQuery(parent).append( value );
// 				}
// 			});
// 		} else {
// 			return this.pushStack( jQuery(jQuery.isFunction(value) ? value() : value), "replaceWith", value );
// 		}
// 	},

// 	detach: function( selector ) {
// 		return this.remove( selector, true );
// 	},

// 	domManip: function( args, table, callback ) {
// 		var results, first, fragment, parent,
// 			value = args[0],
// 			scripts = [];

// 		// We can't cloneNode fragments that contain checked, in WebKit
// 		if ( !jQuery.support.checkClone && arguments.length === 3 && typeof value === "string" && rchecked.test( value ) ) {
// 			return this.each(function() {
// 				jQuery(this).domManip( args, table, callback, true );
// 			});
// 		}

// 		if ( jQuery.isFunction(value) ) {
// 			return this.each(function(i) {
// 				var self = jQuery(this);
// 				args[0] = value.call(this, i, table ? self.html() : undefined);
// 				self.domManip( args, table, callback );
// 			});
// 		}

// 		if ( this[0] ) {
// 			parent = value && value.parentNode;

// 			// If we're in a fragment, just use that instead of building a new one
// 			if ( jQuery.support.parentNode && parent && parent.nodeType === 11 && parent.childNodes.length === this.length ) {
// 				results = { fragment: parent };

// 			} else {
// 				results = jQuery.buildFragment( args, this, scripts );
// 			}

// 			fragment = results.fragment;

// 			if ( fragment.childNodes.length === 1 ) {
// 				first = fragment = fragment.firstChild;
// 			} else {
// 				first = fragment.firstChild;
// 			}

// 			if ( first ) {
// 				table = table && jQuery.nodeName( first, "tr" );

// 				for ( var i = 0, l = this.length, lastIndex = l - 1; i < l; i++ ) {
// 					callback.call(
// 						table ?
// 							root(this[i], first) :
// 							this[i],
// 						// Make sure that we do not leak memory by inadvertently discarding
// 						// the original fragment (which might have attached data) instead of
// 						// using it; in addition, use the original fragment object for the last
// 						// item instead of first because it can end up being emptied incorrectly
// 						// in certain situations (Bug #8070).
// 						// Fragments from the fragment cache must always be cloned and never used
// 						// in place.
// 						results.cacheable || (l > 1 && i < lastIndex) ?
// 							jQuery.clone( fragment, true, true ) :
// 							fragment
// 					);
// 				}
// 			}

// 			if ( scripts.length ) {
// 				jQuery.each( scripts, evalScript );
// 			}
// 		}

// 		return this;
// 	}
// });

// function root( elem, cur ) {
// 	return jQuery.nodeName(elem, "table") ?
// 		(elem.getElementsByTagName("tbody")[0] ||
// 		elem.appendChild(elem.ownerDocument.createElement("tbody"))) :
// 		elem;
// }

// function cloneCopyEvent( src, dest ) {

// 	if ( dest.nodeType !== 1 || !jQuery.hasData( src ) ) {
// 		return;
// 	}

// 	var internalKey = jQuery.expando,
// 			oldData = jQuery.data( src ),
// 			curData = jQuery.data( dest, oldData );

// 	// Switch to use the internal data object, if it exists, for the next
// 	// stage of data copying
// 	if ( (oldData = oldData[ internalKey ]) ) {
// 		var events = oldData.events;
// 				curData = curData[ internalKey ] = jQuery.extend({}, oldData);

// 		if ( events ) {
// 			delete curData.handle;
// 			curData.events = {};

// 			for ( var type in events ) {
// 				for ( var i = 0, l = events[ type ].length; i < l; i++ ) {
// 					jQuery.event.add( dest, type, events[ type ][ i ], events[ type ][ i ].data );
// 				}
// 			}
// 		}
// 	}
// }

// function cloneFixAttributes(src, dest) {
// 	// We do not need to do anything for non-Elements
// 	if ( dest.nodeType !== 1 ) {
// 		return;
// 	}

// 	var nodeName = dest.nodeName.toLowerCase();

// 	// clearAttributes removes the attributes, which we don't want,
// 	// but also removes the attachEvent events, which we *do* want
// 	dest.clearAttributes();

// 	// mergeAttributes, in contrast, only merges back on the
// 	// original attributes, not the events
// 	dest.mergeAttributes(src);

// 	// IE6-8 fail to clone children inside object elements that use
// 	// the proprietary classid attribute value (rather than the type
// 	// attribute) to identify the type of content to display
// 	if ( nodeName === "object" ) {
// 		dest.outerHTML = src.outerHTML;

// 	} else if ( nodeName === "input" && (src.type === "checkbox" || src.type === "radio") ) {
// 		// IE6-8 fails to persist the checked state of a cloned checkbox
// 		// or radio button. Worse, IE6-7 fail to give the cloned element
// 		// a checked appearance if the defaultChecked value isn't also set
// 		if ( src.checked ) {
// 			dest.defaultChecked = dest.checked = src.checked;
// 		}

// 		// IE6-7 get confused and end up setting the value of a cloned
// 		// checkbox/radio button to an empty string instead of "on"
// 		if ( dest.value !== src.value ) {
// 			dest.value = src.value;
// 		}

// 	// IE6-8 fails to return the selected option to the default selected
// 	// state when cloning options
// 	} else if ( nodeName === "option" ) {
// 		dest.selected = src.defaultSelected;

// 	// IE6-8 fails to set the defaultValue to the correct value when
// 	// cloning other types of input fields
// 	} else if ( nodeName === "input" || nodeName === "textarea" ) {
// 		dest.defaultValue = src.defaultValue;
// 	}

// 	// Event data gets referenced instead of copied if the expando
// 	// gets copied too
// 	dest.removeAttribute( jQuery.expando );
// }

// jQuery.buildFragment = function( args, nodes, scripts ) {
// 	var fragment, cacheable, cacheresults,
// 		doc = (nodes && nodes[0] ? nodes[0].ownerDocument || nodes[0] : document);

// 	// Only cache "small" (1/2 KB) HTML strings that are associated with the main document
// 	// Cloning options loses the selected state, so don't cache them
// 	// IE 6 doesn't like it when you put <object> or <embed> elements in a fragment
// 	// Also, WebKit does not clone 'checked' attributes on cloneNode, so don't cache
// 	if ( args.length === 1 && typeof args[0] === "string" && args[0].length < 512 && doc === document &&
// 		args[0].charAt(0) === "<" && !rnocache.test( args[0] ) && (jQuery.support.checkClone || !rchecked.test( args[0] )) ) {

// 		cacheable = true;
// 		cacheresults = jQuery.fragments[ args[0] ];
// 		if ( cacheresults ) {
// 			if ( cacheresults !== 1 ) {
// 				fragment = cacheresults;
// 			}
// 		}
// 	}

// 	if ( !fragment ) {
// 		fragment = doc.createDocumentFragment();
// 		jQuery.clean( args, doc, fragment, scripts );
// 	}

// 	if ( cacheable ) {
// 		jQuery.fragments[ args[0] ] = cacheresults ? fragment : 1;
// 	}

// 	return { fragment: fragment, cacheable: cacheable };
// };

// jQuery.fragments = {};

// jQuery.each({
// 	appendTo: "append",
// 	prependTo: "prepend",
// 	insertBefore: "before",
// 	insertAfter: "after",
// 	replaceAll: "replaceWith"
// }, function( name, original ) {
// 	jQuery.fn[ name ] = function( selector ) {
// 		var ret = [],
// 			insert = jQuery( selector ),
// 			parent = this.length === 1 && this[0].parentNode;

// 		if ( parent && parent.nodeType === 11 && parent.childNodes.length === 1 && insert.length === 1 ) {
// 			insert[ original ]( this[0] );
// 			return this;

// 		} else {
// 			for ( var i = 0, l = insert.length; i < l; i++ ) {
// 				var elems = (i > 0 ? this.clone(true) : this).get();
// 				jQuery( insert[i] )[ original ]( elems );
// 				ret = ret.concat( elems );
// 			}

// 			return this.pushStack( ret, name, insert.selector );
// 		}
// 	};
// });

// jQuery.extend({
// 	clone: function( elem, dataAndEvents, deepDataAndEvents ) {
// 		var clone = elem.cloneNode(true),
// 				srcElements,
// 				destElements,
// 				i;

// 		if ( !jQuery.support.noCloneEvent && (elem.nodeType === 1 || elem.nodeType === 11) && !jQuery.isXMLDoc(elem) ) {
// 			// IE copies events bound via attachEvent when using cloneNode.
// 			// Calling detachEvent on the clone will also remove the events
// 			// from the original. In order to get around this, we use some
// 			// proprietary methods to clear the events. Thanks to MooTools
// 			// guys for this hotness.

// 			// Using Sizzle here is crazy slow, so we use getElementsByTagName
// 			// instead
// 			srcElements = elem.getElementsByTagName("*");
// 			destElements = clone.getElementsByTagName("*");

// 			// Weird iteration because IE will replace the length property
// 			// with an element if you are cloning the body and one of the
// 			// elements on the page has a name or id of "length"
// 			for ( i = 0; srcElements[i]; ++i ) {
// 				cloneFixAttributes( srcElements[i], destElements[i] );
// 			}

// 			cloneFixAttributes( elem, clone );
// 		}

// 		// Copy the events from the original to the clone
// 		if ( dataAndEvents ) {

// 			cloneCopyEvent( elem, clone );

// 			if ( deepDataAndEvents && "getElementsByTagName" in elem ) {

// 				srcElements = elem.getElementsByTagName("*");
// 				destElements = clone.getElementsByTagName("*");

// 				if ( srcElements.length ) {
// 					for ( i = 0; srcElements[i]; ++i ) {
// 						cloneCopyEvent( srcElements[i], destElements[i] );
// 					}
// 				}
// 			}
// 		}
// 		// Return the cloned set
// 		return clone;
//   },
// 	clean: function( elems, context, fragment, scripts ) {
// 		context = context || document;

// 		// !context.createElement fails in IE with an error but returns typeof 'object'
// 		if ( typeof context.createElement === "undefined" ) {
// 			context = context.ownerDocument || context[0] && context[0].ownerDocument || document;
// 		}

// 		var ret = [];

// 		for ( var i = 0, elem; (elem = elems[i]) != null; i++ ) {
// 			if ( typeof elem === "number" ) {
// 				elem += "";
// 			}

// 			if ( !elem ) {
// 				continue;
// 			}

// 			// Convert html string into DOM nodes
// 			if ( typeof elem === "string" && !rhtml.test( elem ) ) {
// 				elem = context.createTextNode( elem );

// 			} else if ( typeof elem === "string" ) {
// 				// Fix "XHTML"-style tags in all browsers
// 				elem = elem.replace(rxhtmlTag, "<$1></$2>");

// 				// Trim whitespace, otherwise indexOf won't work as expected
// 				var tag = (rtagName.exec( elem ) || ["", ""])[1].toLowerCase(),
// 					wrap = wrapMap[ tag ] || wrapMap._default,
// 					depth = wrap[0],
// 					div = context.createElement("div");

// 				// Go to html and back, then peel off extra wrappers
// 				div.innerHTML = wrap[1] + elem + wrap[2];

// 				// Move to the right depth
// 				while ( depth-- ) {
// 					div = div.lastChild;
// 				}

// 				// Remove IE's autoinserted <tbody> from table fragments
// 				if ( !jQuery.support.tbody ) {

// 					// String was a <table>, *may* have spurious <tbody>
// 					var hasBody = rtbody.test(elem),
// 						tbody = tag === "table" && !hasBody ?
// 							div.firstChild && div.firstChild.childNodes :

// 							// String was a bare <thead> or <tfoot>
// 							wrap[1] === "<table>" && !hasBody ?
// 								div.childNodes :
// 								[];

// 					for ( var j = tbody.length - 1; j >= 0 ; --j ) {
// 						if ( jQuery.nodeName( tbody[ j ], "tbody" ) && !tbody[ j ].childNodes.length ) {
// 							tbody[ j ].parentNode.removeChild( tbody[ j ] );
// 						}
// 					}

// 				}

// 				// IE completely kills leading whitespace when innerHTML is used
// 				if ( !jQuery.support.leadingWhitespace && rleadingWhitespace.test( elem ) ) {
// 					div.insertBefore( context.createTextNode( rleadingWhitespace.exec(elem)[0] ), div.firstChild );
// 				}

// 				elem = div.childNodes;
// 			}

// 			if ( elem.nodeType ) {
// 				ret.push( elem );
// 			} else {
// 				ret = jQuery.merge( ret, elem );
// 			}
// 		}

// 		if ( fragment ) {
// 			for ( i = 0; ret[i]; i++ ) {
// 				if ( scripts && jQuery.nodeName( ret[i], "script" ) && (!ret[i].type || ret[i].type.toLowerCase() === "text/javascript") ) {
// 					scripts.push( ret[i].parentNode ? ret[i].parentNode.removeChild( ret[i] ) : ret[i] );

// 				} else {
// 					if ( ret[i].nodeType === 1 ) {
// 						ret.splice.apply( ret, [i + 1, 0].concat(jQuery.makeArray(ret[i].getElementsByTagName("script"))) );
// 					}
// 					fragment.appendChild( ret[i] );
// 				}
// 			}
// 		}

// 		return ret;
// 	},

// 	cleanData: function( elems ) {
// 		var data, id, cache = jQuery.cache, internalKey = jQuery.expando, special = jQuery.event.special,
// 			deleteExpando = jQuery.support.deleteExpando;

// 		for ( var i = 0, elem; (elem = elems[i]) != null; i++ ) {
// 			if ( elem.nodeName && jQuery.noData[elem.nodeName.toLowerCase()] ) {
// 				continue;
// 			}

// 			id = elem[ jQuery.expando ];

// 			if ( id ) {
// 				data = cache[ id ] && cache[ id ][ internalKey ];

// 				if ( data && data.events ) {
// 					for ( var type in data.events ) {
// 						if ( special[ type ] ) {
// 							jQuery.event.remove( elem, type );

// 						// This is a shortcut to avoid jQuery.event.remove's overhead
// 						} else {
// 							jQuery.removeEvent( elem, type, data.handle );
// 						}
// 					}

// 					// Null the DOM reference to avoid IE6/7/8 leak (#7054)
// 					if ( data.handle ) {
// 						data.handle.elem = null;
// 					}
// 				}

// 				if ( deleteExpando ) {
// 					delete elem[ jQuery.expando ];

// 				} else if ( elem.removeAttribute ) {
// 					elem.removeAttribute( jQuery.expando );
// 				}

// 				delete cache[ id ];
// 			}
// 		}
// 	}
// });

// function evalScript( i, elem ) {
// 	if ( elem.src ) {
// 		jQuery.ajax({
// 			url: elem.src,
// 			async: false,
// 			dataType: "script"
// 		});
// 	} else {
// 		jQuery.globalEval( elem.text || elem.textContent || elem.innerHTML || "" );
// 	}

// 	if ( elem.parentNode ) {
// 		elem.parentNode.removeChild( elem );
// 	}
// }




// var ralpha = /alpha\([^)]*\)/i,
// 	ropacity = /opacity=([^)]*)/,
// 	rdashAlpha = /-([a-z])/ig,
// 	rupper = /([A-Z])/g,
// 	rnumpx = /^-?\d+(?:px)?$/i,
// 	rnum = /^-?\d/,

// 	cssShow = { position: "absolute", visibility: "hidden", display: "block" },
// 	cssWidth = [ "Left", "Right" ],
// 	cssHeight = [ "Top", "Bottom" ],
// 	curCSS,

// 	getComputedStyle,
// 	currentStyle,

// 	fcamelCase = function( all, letter ) {
// 		return letter.toUpperCase();
// 	};

// jQuery.fn.css = function( name, value ) {
// 	// Setting 'undefined' is a no-op
// 	if ( arguments.length === 2 && value === undefined ) {
// 		return this;
// 	}

// 	return jQuery.access( this, name, value, true, function( elem, name, value ) {
// 		return value !== undefined ?
// 			jQuery.style( elem, name, value ) :
// 			jQuery.css( elem, name );
// 	});
// };

// jQuery.extend({
// 	// Add in style property hooks for overriding the default
// 	// behavior of getting and setting a style property
// 	cssHooks: {
// 		opacity: {
// 			get: function( elem, computed ) {
// 				if ( computed ) {
// 					// We should always get a number back from opacity
// 					var ret = curCSS( elem, "opacity", "opacity" );
// 					return ret === "" ? "1" : ret;

// 				} else {
// 					return elem.style.opacity;
// 				}
// 			}
// 		}
// 	},

// 	// Exclude the following css properties to add px
// 	cssNumber: {
// 		"zIndex": true,
// 		"fontWeight": true,
// 		"opacity": true,
// 		"zoom": true,
// 		"lineHeight": true
// 	},

// 	// Add in properties whose names you wish to fix before
// 	// setting or getting the value
// 	cssProps: {
// 		// normalize float css property
// 		"float": jQuery.support.cssFloat ? "cssFloat" : "styleFloat"
// 	},

// 	// Get and set the style property on a DOM Node
// 	style: function( elem, name, value, extra ) {
// 		// Don't set styles on text and comment nodes
// 		if ( !elem || elem.nodeType === 3 || elem.nodeType === 8 || !elem.style ) {
// 			return;
// 		}

// 		// Make sure that we're working with the right name
// 		var ret, origName = jQuery.camelCase( name ),
// 			style = elem.style, hooks = jQuery.cssHooks[ origName ];

// 		name = jQuery.cssProps[ origName ] || origName;

// 		// Check if we're setting a value
// 		if ( value !== undefined ) {
// 			// Make sure that NaN and null values aren't set. See: #7116
// 			if ( typeof value === "number" && isNaN( value ) || value == null ) {
// 				return;
// 			}

// 			// If a number was passed in, add 'px' to the (except for certain CSS properties)
// 			if ( typeof value === "number" && !jQuery.cssNumber[ origName ] ) {
// 				value += "px";
// 			}

// 			// If a hook was provided, use that value, otherwise just set the specified value
// 			if ( !hooks || !("set" in hooks) || (value = hooks.set( elem, value )) !== undefined ) {
// 				// Wrapped to prevent IE from throwing errors when 'invalid' values are provided
// 				// Fixes bug #5509
// 				try {
// 					style[ name ] = value;
// 				} catch(e) {}
// 			}

// 		} else {
// 			// If a hook was provided get the non-computed value from there
// 			if ( hooks && "get" in hooks && (ret = hooks.get( elem, false, extra )) !== undefined ) {
// 				return ret;
// 			}

// 			// Otherwise just get the value from the style object
// 			return style[ name ];
// 		}
// 	},

// 	css: function( elem, name, extra ) {
// 		// Make sure that we're working with the right name
// 		var ret, origName = jQuery.camelCase( name ),
// 			hooks = jQuery.cssHooks[ origName ];

// 		name = jQuery.cssProps[ origName ] || origName;

// 		// If a hook was provided get the computed value from there
// 		if ( hooks && "get" in hooks && (ret = hooks.get( elem, true, extra )) !== undefined ) {
// 			return ret;

// 		// Otherwise, if a way to get the computed value exists, use that
// 		} else if ( curCSS ) {
// 			return curCSS( elem, name, origName );
// 		}
// 	},

// 	// A method for quickly swapping in/out CSS properties to get correct calculations
// 	swap: function( elem, options, callback ) {
// 		var old = {};

// 		// Remember the old values, and insert the new ones
// 		for ( var name in options ) {
// 			old[ name ] = elem.style[ name ];
// 			elem.style[ name ] = options[ name ];
// 		}

// 		callback.call( elem );

// 		// Revert the old values
// 		for ( name in options ) {
// 			elem.style[ name ] = old[ name ];
// 		}
// 	},

// 	camelCase: function( string ) {
// 		return string.replace( rdashAlpha, fcamelCase );
// 	}
// });

// // DEPRECATED, Use jQuery.css() instead
// jQuery.curCSS = jQuery.css;

// jQuery.each(["height", "width"], function( i, name ) {
// 	jQuery.cssHooks[ name ] = {
// 		get: function( elem, computed, extra ) {
// 			var val;

// 			if ( computed ) {
// 				if ( elem.offsetWidth !== 0 ) {
// 					val = getWH( elem, name, extra );

// 				} else {
// 					jQuery.swap( elem, cssShow, function() {
// 						val = getWH( elem, name, extra );
// 					});
// 				}

// 				if ( val <= 0 ) {
// 					val = curCSS( elem, name, name );

// 					if ( val === "0px" && currentStyle ) {
// 						val = currentStyle( elem, name, name );
// 					}

// 					if ( val != null ) {
// 						// Should return "auto" instead of 0, use 0 for
// 						// temporary backwards-compat
// 						return val === "" || val === "auto" ? "0px" : val;
// 					}
// 				}

// 				if ( val < 0 || val == null ) {
// 					val = elem.style[ name ];

// 					// Should return "auto" instead of 0, use 0 for
// 					// temporary backwards-compat
// 					return val === "" || val === "auto" ? "0px" : val;
// 				}

// 				return typeof val === "string" ? val : val + "px";
// 			}
// 		},

// 		set: function( elem, value ) {
// 			if ( rnumpx.test( value ) ) {
// 				// ignore negative width and height values #1599
// 				value = parseFloat(value);

// 				if ( value >= 0 ) {
// 					return value + "px";
// 				}

// 			} else {
// 				return value;
// 			}
// 		}
// 	};
// });

// if ( !jQuery.support.opacity ) {
// 	jQuery.cssHooks.opacity = {
// 		get: function( elem, computed ) {
// 			// IE uses filters for opacity
// 			return ropacity.test((computed && elem.currentStyle ? elem.currentStyle.filter : elem.style.filter) || "") ?
// 				(parseFloat(RegExp.$1) / 100) + "" :
// 				computed ? "1" : "";
// 		},

// 		set: function( elem, value ) {
// 			var style = elem.style;

// 			// IE has trouble with opacity if it does not have layout
// 			// Force it by setting the zoom level
// 			style.zoom = 1;

// 			// Set the alpha filter to set the opacity
// 			var opacity = jQuery.isNaN(value) ?
// 				"" :
// 				"alpha(opacity=" + value * 100 + ")",
// 				filter = style.filter || "";

// 			style.filter = ralpha.test(filter) ?
// 				filter.replace(ralpha, opacity) :
// 				style.filter + ' ' + opacity;
// 		}
// 	};
// }

// if ( document.defaultView && document.defaultView.getComputedStyle ) {
// 	getComputedStyle = function( elem, newName, name ) {
// 		var ret, defaultView, computedStyle;

// 		name = name.replace( rupper, "-$1" ).toLowerCase();

// 		if ( !(defaultView = elem.ownerDocument.defaultView) ) {
// 			return undefined;
// 		}

// 		if ( (computedStyle = defaultView.getComputedStyle( elem, null )) ) {
// 			ret = computedStyle.getPropertyValue( name );
// 			if ( ret === "" && !jQuery.contains( elem.ownerDocument.documentElement, elem ) ) {
// 				ret = jQuery.style( elem, name );
// 			}
// 		}

// 		return ret;
// 	};
// }

// if ( document.documentElement.currentStyle ) {
// 	currentStyle = function( elem, name ) {
// 		var left, 
// 			ret = elem.currentStyle && elem.currentStyle[ name ],
// 			rsLeft = elem.runtimeStyle && elem.runtimeStyle[ name ],
// 			style = elem.style;

// 		// From the awesome hack by Dean Edwards
// 		// http://erik.eae.net/archives/2007/07/27/18.54.15/#comment-102291

// 		// If we're not dealing with a regular pixel number
// 		// but a number that has a weird ending, we need to convert it to pixels
// 		if ( !rnumpx.test( ret ) && rnum.test( ret ) ) {
// 			// Remember the original values
// 			left = style.left;

// 			// Put in the new values to get a computed value out
// 			if ( rsLeft ) {
// 				elem.runtimeStyle.left = elem.currentStyle.left;
// 			}
// 			style.left = name === "fontSize" ? "1em" : (ret || 0);
// 			ret = style.pixelLeft + "px";

// 			// Revert the changed values
// 			style.left = left;
// 			if ( rsLeft ) {
// 				elem.runtimeStyle.left = rsLeft;
// 			}
// 		}

// 		return ret === "" ? "auto" : ret;
// 	};
// }

// curCSS = getComputedStyle || currentStyle;

// function getWH( elem, name, extra ) {
// 	var which = name === "width" ? cssWidth : cssHeight,
// 		val = name === "width" ? elem.offsetWidth : elem.offsetHeight;

// 	if ( extra === "border" ) {
// 		return val;
// 	}

// 	jQuery.each( which, function() {
// 		if ( !extra ) {
// 			val -= parseFloat(jQuery.css( elem, "padding" + this )) || 0;
// 		}

// 		if ( extra === "margin" ) {
// 			val += parseFloat(jQuery.css( elem, "margin" + this )) || 0;

// 		} else {
// 			val -= parseFloat(jQuery.css( elem, "border" + this + "Width" )) || 0;
// 		}
// 	});

// 	return val;
// }

// if ( jQuery.expr && jQuery.expr.filters ) {
// 	jQuery.expr.filters.hidden = function( elem ) {
// 		var width = elem.offsetWidth,
// 			height = elem.offsetHeight;

// 		return (width === 0 && height === 0) || (!jQuery.support.reliableHiddenOffsets && (elem.style.display || jQuery.css( elem, "display" )) === "none");
// 	};

// 	jQuery.expr.filters.visible = function( elem ) {
// 		return !jQuery.expr.filters.hidden( elem );
// 	};
// }




// var r20 = /%20/g,
// 	rbracket = /\[\]$/,
// 	rCRLF = /\r?\n/g,
// 	rhash = /#.*$/,
// 	rheaders = /^(.*?):\s*(.*?)\r?$/mg, // IE leaves an \r character at EOL
// 	rinput = /^(?:color|date|datetime|email|hidden|month|number|password|range|search|tel|text|time|url|week)$/i,
// 	rnoContent = /^(?:GET|HEAD)$/,
// 	rprotocol = /^\/\//,
// 	rquery = /\?/,
// 	rscript = /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
// 	rselectTextarea = /^(?:select|textarea)/i,
// 	rspacesAjax = /\s+/,
// 	rts = /([?&])_=[^&]*/,
// 	rurl = /^(\w+:)\/\/([^\/?#:]+)(?::(\d+))?/,

// 	// Keep a copy of the old load method
// 	_load = jQuery.fn.load,

// 	/* Prefilters
// 	 * 1) They are useful to introduce custom dataTypes (see ajax/jsonp.js for an example)
// 	 * 2) These are called:
// 	 *    - BEFORE asking for a transport
// 	 *    - AFTER param serialization (s.data is a string if s.processData is true)
// 	 * 3) key is the dataType
// 	 * 4) the catchall symbol "*" can be used
// 	 * 5) execution will start with transport dataType and THEN continue down to "*" if needed
// 	 */
// 	prefilters = {},

// 	/* Transports bindings
// 	 * 1) key is the dataType
// 	 * 2) the catchall symbol "*" can be used
// 	 * 3) selection will start with transport dataType and THEN go to "*" if needed
// 	 */
// 	transports = {};

// // Base "constructor" for jQuery.ajaxPrefilter and jQuery.ajaxTransport
// function addToPrefiltersOrTransports( structure ) {

// 	// dataTypeExpression is optional and defaults to "*"
// 	return function( dataTypeExpression, func ) {

// 		if ( typeof dataTypeExpression !== "string" ) {
// 			func = dataTypeExpression;
// 			dataTypeExpression = "*";
// 		}

// 		if ( jQuery.isFunction( func ) ) {
// 			var dataTypes = dataTypeExpression.toLowerCase().split( rspacesAjax ),
// 				i = 0,
// 				length = dataTypes.length,
// 				dataType,
// 				list,
// 				placeBefore;

// 			// For each dataType in the dataTypeExpression
// 			for(; i < length; i++ ) {
// 				dataType = dataTypes[ i ];
// 				// We control if we're asked to add before
// 				// any existing element
// 				placeBefore = /^\+/.test( dataType );
// 				if ( placeBefore ) {
// 					dataType = dataType.substr( 1 ) || "*";
// 				}
// 				list = structure[ dataType ] = structure[ dataType ] || [];
// 				// then we add to the structure accordingly
// 				list[ placeBefore ? "unshift" : "push" ]( func );
// 			}
// 		}
// 	};
// }

// //Base inspection function for prefilters and transports
// function inspectPrefiltersOrTransports( structure, options, originalOptions, jXHR,
// 		dataType /* internal */, inspected /* internal */ ) {

// 	dataType = dataType || options.dataTypes[ 0 ];
// 	inspected = inspected || {};

// 	inspected[ dataType ] = true;

// 	var list = structure[ dataType ],
// 		i = 0,
// 		length = list ? list.length : 0,
// 		executeOnly = ( structure === prefilters ),
// 		selection;

// 	for(; i < length && ( executeOnly || !selection ); i++ ) {
// 		selection = list[ i ]( options, originalOptions, jXHR );
// 		// If we got redirected to another dataType
// 		// we try there if not done already
// 		if ( typeof selection === "string" ) {
// 			if ( inspected[ selection ] ) {
// 				selection = undefined;
// 			} else {
// 				options.dataTypes.unshift( selection );
// 				selection = inspectPrefiltersOrTransports(
// 						structure, options, originalOptions, jXHR, selection, inspected );
// 			}
// 		}
// 	}
// 	// If we're only executing or nothing was selected
// 	// we try the catchall dataType if not done already
// 	if ( ( executeOnly || !selection ) && !inspected[ "*" ] ) {
// 		selection = inspectPrefiltersOrTransports(
// 				structure, options, originalOptions, jXHR, "*", inspected );
// 	}
// 	// unnecessary when only executing (prefilters)
// 	// but it'll be ignored by the caller in that case
// 	return selection;
// }

// jQuery.fn.extend({
// 	load: function( url, params, callback ) {
// 		if ( typeof url !== "string" && _load ) {
// 			return _load.apply( this, arguments );

// 		// Don't do a request if no elements are being requested
// 		} else if ( !this.length ) {
// 			return this;
// 		}

// 		var off = url.indexOf( " " );
// 		if ( off >= 0 ) {
// 			var selector = url.slice( off, url.length );
// 			url = url.slice( 0, off );
// 		}

// 		// Default to a GET request
// 		var type = "GET";

// 		// If the second parameter was provided
// 		if ( params ) {
// 			// If it's a function
// 			if ( jQuery.isFunction( params ) ) {
// 				// We assume that it's the callback
// 				callback = params;
// 				params = null;

// 			// Otherwise, build a param string
// 			} else if ( typeof params === "object" ) {
// 				params = jQuery.param( params, jQuery.ajaxSettings.traditional );
// 				type = "POST";
// 			}
// 		}

// 		var self = this;

// 		// Request the remote document
// 		jQuery.ajax({
// 			url: url,
// 			type: type,
// 			dataType: "html",
// 			data: params,
// 			// Complete callback (responseText is used internally)
// 			complete: function( jXHR, status, responseText ) {
// 				// Store the response as specified by the jXHR object
// 				responseText = jXHR.responseText;
// 				// If successful, inject the HTML into all the matched elements
// 				if ( jXHR.isResolved() ) {
// 					// #4825: Get the actual response in case
// 					// a dataFilter is present in ajaxSettings
// 					jXHR.done(function( r ) {
// 						responseText = r;
// 					});
// 					// See if a selector was specified
// 					self.html( selector ?
// 						// Create a dummy div to hold the results
// 						jQuery("<div>")
// 							// inject the contents of the document in, removing the scripts
// 							// to avoid any 'Permission Denied' errors in IE
// 							.append(responseText.replace(rscript, ""))

// 							// Locate the specified elements
// 							.find(selector) :

// 						// If not, just inject the full result
// 						responseText );
// 				}

// 				if ( callback ) {
// 					self.each( callback, [ responseText, status, jXHR ] );
// 				}
// 			}
// 		});

// 		return this;
// 	},

// 	serialize: function() {
// 		return jQuery.param( this.serializeArray() );
// 	},

// 	serializeArray: function() {
// 		return this.map(function(){
// 			return this.elements ? jQuery.makeArray( this.elements ) : this;
// 		})
// 		.filter(function(){
// 			return this.name && !this.disabled &&
// 				( this.checked || rselectTextarea.test( this.nodeName ) ||
// 					rinput.test( this.type ) );
// 		})
// 		.map(function( i, elem ){
// 			var val = jQuery( this ).val();

// 			return val == null ?
// 				null :
// 				jQuery.isArray( val ) ?
// 					jQuery.map( val, function( val, i ){
// 						return { name: elem.name, value: val.replace( rCRLF, "\r\n" ) };
// 					}) :
// 					{ name: elem.name, value: val.replace( rCRLF, "\r\n" ) };
// 		}).get();
// 	}
// });

// // Attach a bunch of functions for handling common AJAX events
// jQuery.each( "ajaxStart ajaxStop ajaxComplete ajaxError ajaxSuccess ajaxSend".split( " " ), function( i, o ){
// 	jQuery.fn[ o ] = function( f ){
// 		return this.bind( o, f );
// 	};
// } );

// jQuery.each( [ "get", "post" ], function( i, method ) {
// 	jQuery[ method ] = function( url, data, callback, type ) {
// 		// shift arguments if data argument was omitted
// 		if ( jQuery.isFunction( data ) ) {
// 			type = type || callback;
// 			callback = data;
// 			data = null;
// 		}

// 		return jQuery.ajax({
// 			type: method,
// 			url: url,
// 			data: data,
// 			success: callback,
// 			dataType: type
// 		});
// 	};
// } );

// jQuery.extend({

// 	getScript: function( url, callback ) {
// 		return jQuery.get( url, null, callback, "script" );
// 	},

// 	getJSON: function( url, data, callback ) {
// 		return jQuery.get( url, data, callback, "json" );
// 	},

// 	ajaxSetup: function( settings ) {
// 		jQuery.extend( true, jQuery.ajaxSettings, settings );
// 		if ( settings.context ) {
// 			jQuery.ajaxSettings.context = settings.context;
// 		}
// 	},

// 	ajaxSettings: {
// 		url: location.href,
// 		global: true,
// 		type: "GET",
// 		contentType: "application/x-www-form-urlencoded",
// 		processData: true,
// 		async: true,
// 		/*
// 		timeout: 0,
// 		data: null,
// 		dataType: null,
// 		username: null,
// 		password: null,
// 		cache: null,
// 		traditional: false,
// 		headers: {},
// 		crossDomain: null,
// 		*/

// 		accepts: {
// 			xml: "application/xml, text/xml",
// 			html: "text/html",
// 			text: "text/plain",
// 			json: "application/json, text/javascript",
// 			"*": "*/*"
// 		},

// 		contents: {
// 			xml: /xml/,
// 			html: /html/,
// 			json: /json/
// 		},

// 		responseFields: {
// 			xml: "responseXML",
// 			text: "responseText"
// 		},

// 		// List of data converters
// 		// 1) key format is "source_type destination_type" (a single space in-between)
// 		// 2) the catchall symbol "*" can be used for source_type
// 		converters: {

// 			// Convert anything to text
// 			"* text": window.String,

// 			// Text to html (true = no transformation)
// 			"text html": true,

// 			// Evaluate text as a json expression
// 			"text json": jQuery.parseJSON,

// 			// Parse text as xml
// 			"text xml": jQuery.parseXML
// 		}
// 	},

// 	ajaxPrefilter: addToPrefiltersOrTransports( prefilters ),
// 	ajaxTransport: addToPrefiltersOrTransports( transports ),

// 	// Main method
// 	ajax: function( url, options ) {

// 		// If options is not an object,
// 		// we simulate pre-1.5 signature
// 		if ( typeof options !== "object" ) {
// 			options = url;
// 			url = undefined;
// 		}

// 		// Force options to be an object
// 		options = options || {};

// 		var // Create the final options object
// 			s = jQuery.extend( true, {}, jQuery.ajaxSettings, options ),
// 			// Callbacks contexts
// 			// We force the original context if it exists
// 			// or take it from jQuery.ajaxSettings otherwise
// 			// (plain objects used as context get extended)
// 			callbackContext =
// 				( s.context = ( "context" in options ? options : jQuery.ajaxSettings ).context ) || s,
// 			globalEventContext = callbackContext === s ? jQuery.event : jQuery( callbackContext ),
// 			// Deferreds
// 			deferred = jQuery.Deferred(),
// 			completeDeferred = jQuery._Deferred(),
// 			// Status-dependent callbacks
// 			statusCode = s.statusCode || {},
// 			// Headers (they are sent all at once)
// 			requestHeaders = {},
// 			// Response headers
// 			responseHeadersString,
// 			responseHeaders,
// 			// transport
// 			transport,
// 			// timeout handle
// 			timeoutTimer,
// 			// Cross-domain detection vars
// 			loc = document.location,
// 			protocol = loc.protocol || "http:",
// 			parts,
// 			// The jXHR state
// 			state = 0,
// 			// Loop variable
// 			i,
// 			// Fake xhr
// 			jXHR = {

// 				readyState: 0,

// 				// Caches the header
// 				setRequestHeader: function( name, value ) {
// 					if ( state === 0 ) {
// 						requestHeaders[ name.toLowerCase() ] = value;
// 					}
// 					return this;
// 				},

// 				// Raw string
// 				getAllResponseHeaders: function() {
// 					return state === 2 ? responseHeadersString : null;
// 				},

// 				// Builds headers hashtable if needed
// 				getResponseHeader: function( key ) {
// 					var match;
// 					if ( state === 2 ) {
// 						if ( !responseHeaders ) {
// 							responseHeaders = {};
// 							while( ( match = rheaders.exec( responseHeadersString ) ) ) {
// 								responseHeaders[ match[1].toLowerCase() ] = match[ 2 ];
// 							}
// 						}
// 						match = responseHeaders[ key.toLowerCase() ];
// 					}
// 					return match || null;
// 				},

// 				// Cancel the request
// 				abort: function( statusText ) {
// 					statusText = statusText || "abort";
// 					if ( transport ) {
// 						transport.abort( statusText );
// 					}
// 					done( 0, statusText );
// 					return this;
// 				}
// 			};

// 		// Callback for when everything is done
// 		// It is defined here because jslint complains if it is declared
// 		// at the end of the function (which would be more logical and readable)
// 		function done( status, statusText, responses, headers) {

// 			// Called once
// 			if ( state === 2 ) {
// 				return;
// 			}

// 			// State is "done" now
// 			state = 2;

// 			// Clear timeout if it exists
// 			if ( timeoutTimer ) {
// 				clearTimeout( timeoutTimer );
// 			}

// 			// Dereference transport for early garbage collection
// 			// (no matter how long the jXHR object will be used)
// 			transport = undefined;

// 			// Cache response headers
// 			responseHeadersString = headers || "";

// 			// Set readyState
// 			jXHR.readyState = status ? 4 : 0;

// 			var isSuccess,
// 				success,
// 				error,
// 				response = responses ? ajaxHandleResponses( s, jXHR, responses ) : undefined,
// 				lastModified,
// 				etag;

// 			// If successful, handle type chaining
// 			if ( status >= 200 && status < 300 || status === 304 ) {

// 				// Set the If-Modified-Since and/or If-None-Match header, if in ifModified mode.
// 				if ( s.ifModified ) {

// 					if ( ( lastModified = jXHR.getResponseHeader( "Last-Modified" ) ) ) {
// 						jQuery.lastModified[ s.url ] = lastModified;
// 					}
// 					if ( ( etag = jXHR.getResponseHeader( "Etag" ) ) ) {
// 						jQuery.etag[ s.url ] = etag;
// 					}
// 				}

// 				// If not modified
// 				if ( status === 304 ) {

// 					statusText = "notmodified";
// 					isSuccess = true;

// 				// If we have data
// 				} else {

// 					try {
// 						success = ajaxConvert( s, response );
// 						statusText = "success";
// 						isSuccess = true;
// 					} catch(e) {
// 						// We have a parsererror
// 						statusText = "parsererror";
// 						error = e;
// 					}
// 				}
// 			} else {
// 				// We extract error from statusText
// 				// then normalize statusText and status for non-aborts
// 				error = statusText;
// 				if( status ) {
// 					statusText = "error";
// 					if ( status < 0 ) {
// 						status = 0;
// 					}
// 				}
// 			}

// 			// Set data for the fake xhr object
// 			jXHR.status = status;
// 			jXHR.statusText = statusText;

// 			// Success/Error
// 			if ( isSuccess ) {
// 				deferred.resolveWith( callbackContext, [ success, statusText, jXHR ] );
// 			} else {
// 				deferred.rejectWith( callbackContext, [ jXHR, statusText, error ] );
// 			}

// 			// Status-dependent callbacks
// 			jXHR.statusCode( statusCode );
// 			statusCode = undefined;

// 			if ( s.global ) {
// 				globalEventContext.trigger( "ajax" + ( isSuccess ? "Success" : "Error" ),
// 						[ jXHR, s, isSuccess ? success : error ] );
// 			}

// 			// Complete
// 			completeDeferred.resolveWith( callbackContext, [ jXHR, statusText ] );

// 			if ( s.global ) {
// 				globalEventContext.trigger( "ajaxComplete", [ jXHR, s] );
// 				// Handle the global AJAX counter
// 				if ( !( --jQuery.active ) ) {
// 					jQuery.event.trigger( "ajaxStop" );
// 				}
// 			}
// 		}

// 		// Attach deferreds
// 		deferred.promise( jXHR );
// 		jXHR.success = jXHR.done;
// 		jXHR.error = jXHR.fail;
// 		jXHR.complete = completeDeferred.done;

// 		// Status-dependent callbacks
// 		jXHR.statusCode = function( map ) {
// 			if ( map ) {
// 				var tmp;
// 				if ( state < 2 ) {
// 					for( tmp in map ) {
// 						statusCode[ tmp ] = [ statusCode[tmp], map[tmp] ];
// 					}
// 				} else {
// 					tmp = map[ jXHR.status ];
// 					jXHR.then( tmp, tmp );
// 				}
// 			}
// 			return this;
// 		};

// 		// Remove hash character (#7531: and string promotion)
// 		// Add protocol if not provided (#5866: IE7 issue with protocol-less urls)
// 		// We also use the url parameter if available
// 		s.url = ( "" + ( url || s.url ) ).replace( rhash, "" ).replace( rprotocol, protocol + "//" );

// 		// Extract dataTypes list
// 		s.dataTypes = jQuery.trim( s.dataType || "*" ).toLowerCase().split( rspacesAjax );

// 		// Determine if a cross-domain request is in order
// 		if ( !s.crossDomain ) {
// 			parts = rurl.exec( s.url.toLowerCase() );
// 			s.crossDomain = !!( parts &&
// 				( parts[ 1 ] != protocol || parts[ 2 ] != loc.hostname ||
// 					( parts[ 3 ] || ( parts[ 1 ] === "http:" ? 80 : 443 ) ) !=
// 						( loc.port || ( protocol === "http:" ? 80 : 443 ) ) )
// 			);
// 		}

// 		// Convert data if not already a string
// 		if ( s.data && s.processData && typeof s.data !== "string" ) {
// 			s.data = jQuery.param( s.data, s.traditional );
// 		}

// 		// Apply prefilters
// 		inspectPrefiltersOrTransports( prefilters, s, options, jXHR );

// 		// Uppercase the type
// 		s.type = s.type.toUpperCase();

// 		// Determine if request has content
// 		s.hasContent = !rnoContent.test( s.type );

// 		// Watch for a new set of requests
// 		if ( s.global && jQuery.active++ === 0 ) {
// 			jQuery.event.trigger( "ajaxStart" );
// 		}

// 		// More options handling for requests with no content
// 		if ( !s.hasContent ) {

// 			// If data is available, append data to url
// 			if ( s.data ) {
// 				s.url += ( rquery.test( s.url ) ? "&" : "?" ) + s.data;
// 			}

// 			// Add anti-cache in url if needed
// 			if ( s.cache === false ) {

// 				var ts = jQuery.now(),
// 					// try replacing _= if it is there
// 					ret = s.url.replace( rts, "$1_=" + ts );

// 				// if nothing was replaced, add timestamp to the end
// 				s.url = ret + ( (ret === s.url ) ? ( rquery.test( s.url ) ? "&" : "?" ) + "_=" + ts : "" );
// 			}
// 		}

// 		// Set the correct header, if data is being sent
// 		if ( s.data && s.hasContent && s.contentType !== false || options.contentType ) {
// 			requestHeaders[ "content-type" ] = s.contentType;
// 		}

// 		// Set the If-Modified-Since and/or If-None-Match header, if in ifModified mode.
// 		if ( s.ifModified ) {
// 			if ( jQuery.lastModified[ s.url ] ) {
// 				requestHeaders[ "if-modified-since" ] = jQuery.lastModified[ s.url ];
// 			}
// 			if ( jQuery.etag[ s.url ] ) {
// 				requestHeaders[ "if-none-match" ] = jQuery.etag[ s.url ];
// 			}
// 		}

// 		// Set the Accepts header for the server, depending on the dataType
// 		requestHeaders.accept = s.dataTypes[ 0 ] && s.accepts[ s.dataTypes[0] ] ?
// 			s.accepts[ s.dataTypes[0] ] + ( s.dataTypes[ 0 ] !== "*" ? ", */*; q=0.01" : "" ) :
// 			s.accepts[ "*" ];

// 		// Check for headers option
// 		for ( i in s.headers ) {
// 			requestHeaders[ i.toLowerCase() ] = s.headers[ i ];
// 		}

// 		// Allow custom headers/mimetypes and early abort
// 		if ( s.beforeSend && ( s.beforeSend.call( callbackContext, jXHR, s ) === false || state === 2 ) ) {
// 				// Abort if not done already
// 				done( 0, "abort" );
// 				// Return false
// 				jXHR = false;

// 		} else {

// 			// Install callbacks on deferreds
// 			for ( i in { success: 1, error: 1, complete: 1 } ) {
// 				jXHR[ i ]( s[ i ] );
// 			}

// 			// Get transport
// 			transport = inspectPrefiltersOrTransports( transports, s, options, jXHR );

// 			// If no transport, we auto-abort
// 			if ( !transport ) {
// 				done( -1, "No Transport" );
// 			} else {
// 				// Set state as sending
// 				state = jXHR.readyState = 1;
// 				// Send global event
// 				if ( s.global ) {
// 					globalEventContext.trigger( "ajaxSend", [ jXHR, s ] );
// 				}
// 				// Timeout
// 				if ( s.async && s.timeout > 0 ) {
// 					timeoutTimer = setTimeout( function(){
// 						jXHR.abort( "timeout" );
// 					}, s.timeout );
// 				}

// 				try {
// 					transport.send( requestHeaders, done );
// 				} catch (e) {
// 					// Propagate exception as error if not done
// 					if ( status < 2 ) {
// 						done( -1, e );
// 					// Simply rethrow otherwise
// 					} else {
// 						jQuery.error( e );
// 					}
// 				}
// 			}
// 		}
// 		return jXHR;
// 	},

// 	// Serialize an array of form elements or a set of
// 	// key/values into a query string
// 	param: function( a, traditional ) {
// 		var s = [],
// 			add = function( key, value ) {
// 				// If value is a function, invoke it and return its value
// 				value = jQuery.isFunction( value ) ? value() : value;
// 				s[ s.length ] = encodeURIComponent( key ) + "=" + encodeURIComponent( value );
// 			};

// 		// Set traditional to true for jQuery <= 1.3.2 behavior.
// 		if ( traditional === undefined ) {
// 			traditional = jQuery.ajaxSettings.traditional;
// 		}

// 		// If an array was passed in, assume that it is an array of form elements.
// 		if ( jQuery.isArray( a ) || a.jquery ) {
// 			// Serialize the form elements
// 			jQuery.each( a, function() {
// 				add( this.name, this.value );
// 			} );

// 		} else {
// 			// If traditional, encode the "old" way (the way 1.3.2 or older
// 			// did it), otherwise encode params recursively.
// 			for ( var prefix in a ) {
// 				buildParams( prefix, a[ prefix ], traditional, add );
// 			}
// 		}

// 		// Return the resulting serialization
// 		return s.join( "&" ).replace( r20, "+" );
// 	}
// });

// function buildParams( prefix, obj, traditional, add ) {
// 	if ( jQuery.isArray( obj ) && obj.length ) {
// 		// Serialize array item.
// 		jQuery.each( obj, function( i, v ) {
// 			if ( traditional || rbracket.test( prefix ) ) {
// 				// Treat each array item as a scalar.
// 				add( prefix, v );

// 			} else {
// 				// If array item is non-scalar (array or object), encode its
// 				// numeric index to resolve deserialization ambiguity issues.
// 				// Note that rack (as of 1.0.0) can't currently deserialize
// 				// nested arrays properly, and attempting to do so may cause
// 				// a server error. Possible fixes are to modify rack's
// 				// deserialization algorithm or to provide an option or flag
// 				// to force array serialization to be shallow.
// 				buildParams( prefix + "[" + ( typeof v === "object" || jQuery.isArray(v) ? i : "" ) + "]", v, traditional, add );
// 			}
// 		});

// 	} else if ( !traditional && obj != null && typeof obj === "object" ) {
// 		// If we see an array here, it is empty and should be treated as an empty
// 		// object
// 		if ( jQuery.isArray( obj ) || jQuery.isEmptyObject( obj ) ) {
// 			add( prefix, "" );

// 		// Serialize object item.
// 		} else {
// 			jQuery.each( obj, function( k, v ) {
// 				buildParams( prefix + "[" + k + "]", v, traditional, add );
// 			});
// 		}

// 	} else {
// 		// Serialize scalar item.
// 		add( prefix, obj );
// 	}
// }

// // This is still on the jQuery object... for now
// // Want to move this to jQuery.ajax some day
// jQuery.extend({

// 	// Counter for holding the number of active queries
// 	active: 0,

// 	// Last-Modified header cache for next request
// 	lastModified: {},
// 	etag: {}

// });

// /* Handles responses to an ajax request:
//  * - sets all responseXXX fields accordingly
//  * - finds the right dataType (mediates between content-type and expected dataType)
//  * - returns the corresponding response
//  */
// function ajaxHandleResponses( s, jXHR, responses ) {

// 	var contents = s.contents,
// 		dataTypes = s.dataTypes,
// 		responseFields = s.responseFields,
// 		ct,
// 		type,
// 		finalDataType,
// 		firstDataType;

// 	// Fill responseXXX fields
// 	for( type in responseFields ) {
// 		if ( type in responses ) {
// 			jXHR[ responseFields[type] ] = responses[ type ];
// 		}
// 	}

// 	// Remove auto dataType and get content-type in the process
// 	while( dataTypes[ 0 ] === "*" ) {
// 		dataTypes.shift();
// 		if ( ct === undefined ) {
// 			ct = jXHR.getResponseHeader( "content-type" );
// 		}
// 	}

// 	// Check if we're dealing with a known content-type
// 	if ( ct ) {
// 		for ( type in contents ) {
// 			if ( contents[ type ] && contents[ type ].test( ct ) ) {
// 				dataTypes.unshift( type );
// 				break;
// 			}
// 		}
// 	}

// 	// Check to see if we have a response for the expected dataType
// 	if ( dataTypes[ 0 ] in responses ) {
// 		finalDataType = dataTypes[ 0 ];
// 	} else {
// 		// Try convertible dataTypes
// 		for ( type in responses ) {
// 			if ( !dataTypes[ 0 ] || s.converters[ type + " " + dataTypes[0] ] ) {
// 				finalDataType = type;
// 				break;
// 			}
// 			if ( !firstDataType ) {
// 				firstDataType = type;
// 			}
// 		}
// 		// Or just use first one
// 		finalDataType = finalDataType || firstDataType;
// 	}

// 	// If we found a dataType
// 	// We add the dataType to the list if needed
// 	// and return the corresponding response
// 	if ( finalDataType ) {
// 		if ( finalDataType !== dataTypes[ 0 ] ) {
// 			dataTypes.unshift( finalDataType );
// 		}
// 		return responses[ finalDataType ];
// 	}
// }

// // Chain conversions given the request and the original response
// function ajaxConvert( s, response ) {

// 	// Apply the dataFilter if provided
// 	if ( s.dataFilter ) {
// 		response = s.dataFilter( response, s.dataType );
// 	}

// 	var dataTypes = s.dataTypes,
// 		converters = s.converters,
// 		i,
// 		length = dataTypes.length,
// 		tmp,
// 		// Current and previous dataTypes
// 		current = dataTypes[ 0 ],
// 		prev,
// 		// Conversion expression
// 		conversion,
// 		// Conversion function
// 		conv,
// 		// Conversion functions (transitive conversion)
// 		conv1,
// 		conv2;

// 	// For each dataType in the chain
// 	for( i = 1; i < length; i++ ) {

// 		// Get the dataTypes
// 		prev = current;
// 		current = dataTypes[ i ];

// 		// If current is auto dataType, update it to prev
// 		if( current === "*" ) {
// 			current = prev;
// 		// If no auto and dataTypes are actually different
// 		} else if ( prev !== "*" && prev !== current ) {

// 			// Get the converter
// 			conversion = prev + " " + current;
// 			conv = converters[ conversion ] || converters[ "* " + current ];

// 			// If there is no direct converter, search transitively
// 			if ( !conv ) {
// 				conv2 = undefined;
// 				for( conv1 in converters ) {
// 					tmp = conv1.split( " " );
// 					if ( tmp[ 0 ] === prev || tmp[ 0 ] === "*" ) {
// 						conv2 = converters[ tmp[1] + " " + current ];
// 						if ( conv2 ) {
// 							conv1 = converters[ conv1 ];
// 							if ( conv1 === true ) {
// 								conv = conv2;
// 							} else if ( conv2 === true ) {
// 								conv = conv1;
// 							}
// 							break;
// 						}
// 					}
// 				}
// 			}
// 			// If we found no converter, dispatch an error
// 			if ( !( conv || conv2 ) ) {
// 				jQuery.error( "No conversion from " + conversion.replace(" "," to ") );
// 			}
// 			// If found converter is not an equivalence
// 			if ( conv !== true ) {
// 				// Convert with 1 or 2 converters accordingly
// 				response = conv ? conv( response ) : conv2( conv1(response) );
// 			}
// 		}
// 	}
// 	return response;
// }




// var jsc = jQuery.now(),
// 	jsre = /(\=)\?(&|$)|()\?\?()/i;

// // Default jsonp settings
// jQuery.ajaxSetup({
// 	jsonp: "callback",
// 	jsonpCallback: function() {
// 		return jQuery.expando + "_" + ( jsc++ );
// 	}
// });

// // Detect, normalize options and install callbacks for jsonp requests
// jQuery.ajaxPrefilter( "json jsonp", function( s, originalSettings, dataIsString /* internal */ ) {

// 	dataIsString = ( typeof s.data === "string" );

// 	if ( s.dataTypes[ 0 ] === "jsonp" ||
// 		originalSettings.jsonpCallback ||
// 		originalSettings.jsonp != null ||
// 		s.jsonp !== false && ( jsre.test( s.url ) ||
// 				dataIsString && jsre.test( s.data ) ) ) {

// 		var responseContainer,
// 			jsonpCallback = s.jsonpCallback =
// 				jQuery.isFunction( s.jsonpCallback ) ? s.jsonpCallback() : s.jsonpCallback,
// 			previous = window[ jsonpCallback ],
// 			url = s.url,
// 			data = s.data,
// 			replace = "$1" + jsonpCallback + "$2";

// 		if ( s.jsonp !== false ) {
// 			url = url.replace( jsre, replace );
// 			if ( s.url === url ) {
// 				if ( dataIsString ) {
// 					data = data.replace( jsre, replace );
// 				}
// 				if ( s.data === data ) {
// 					// Add callback manually
// 					url += (/\?/.test( url ) ? "&" : "?") + s.jsonp + "=" + jsonpCallback;
// 				}
// 			}
// 		}

// 		s.url = url;
// 		s.data = data;

// 		window[ jsonpCallback ] = function( response ) {
// 			responseContainer = [ response ];
// 		};

// 		s.complete = [ function() {

// 			// Set callback back to previous value
// 			window[ jsonpCallback ] = previous;

// 			// Call if it was a function and we have a response
// 			if ( previous) {
// 				if ( responseContainer && jQuery.isFunction( previous ) ) {
// 					window[ jsonpCallback ] ( responseContainer[ 0 ] );
// 				}
// 			} else {
// 				// else, more memory leak avoidance
// 				try{
// 					delete window[ jsonpCallback ];
// 				} catch( e ) {}
// 			}

// 		}, s.complete ];

// 		// Use data converter to retrieve json after script execution
// 		s.converters["script json"] = function() {
// 			if ( ! responseContainer ) {
// 				jQuery.error( jsonpCallback + " was not called" );
// 			}
// 			return responseContainer[ 0 ];
// 		};

// 		// force json dataType
// 		s.dataTypes[ 0 ] = "json";

// 		// Delegate to script
// 		return "script";
// 	}
// } );




// // Install script dataType
// jQuery.ajaxSetup({
// 	accepts: {
// 		script: "text/javascript, application/javascript"
// 	},
// 	contents: {
// 		script: /javascript/
// 	},
// 	converters: {
// 		"text script": function( text ) {
// 			jQuery.globalEval( text );
// 			return text;
// 		}
// 	}
// });

// // Handle cache's special case and global
// jQuery.ajaxPrefilter( "script", function( s ) {
// 	if ( s.cache === undefined ) {
// 		s.cache = false;
// 	}
// 	if ( s.crossDomain ) {
// 		s.type = "GET";
// 		s.global = false;
// 	}
// } );

// // Bind script tag hack transport
// jQuery.ajaxTransport( "script", function(s) {

// 	// This transport only deals with cross domain requests
// 	if ( s.crossDomain ) {

// 		var script,
// 			head = document.getElementsByTagName( "head" )[ 0 ] || document.documentElement;

// 		return {

// 			send: function( _, callback ) {

// 				script = document.createElement( "script" );

// 				script.async = "async";

// 				if ( s.scriptCharset ) {
// 					script.charset = s.scriptCharset;
// 				}

// 				script.src = s.url;

// 				// Attach handlers for all browsers
// 				script.onload = script.onreadystatechange = function( _, isAbort ) {

// 					if ( !script.readyState || /loaded|complete/.test( script.readyState ) ) {

// 						// Handle memory leak in IE
// 						script.onload = script.onreadystatechange = null;

// 						// Remove the script
// 						if ( head && script.parentNode ) {
// 							head.removeChild( script );
// 						}

// 						// Dereference the script
// 						script = undefined;

// 						// Callback if not abort
// 						if ( !isAbort ) {
// 							callback( 200, "success" );
// 						}
// 					}
// 				};
// 				// Use insertBefore instead of appendChild  to circumvent an IE6 bug.
// 				// This arises when a base node is used (#2709 and #4378).
// 				head.insertBefore( script, head.firstChild );
// 			},

// 			abort: function() {
// 				if ( script ) {
// 					script.onload( 0, 1 );
// 				}
// 			}
// 		};
// 	}
// } );




// var // Next active xhr id
// 	xhrId = jQuery.now(),

// 	// active xhrs
// 	xhrs = {},

// 	// #5280: see below
// 	xhrUnloadAbortInstalled,

// 	// XHR used to determine supports properties
// 	testXHR;

// // Create the request object
// // (This is still attached to ajaxSettings for backward compatibility)
// jQuery.ajaxSettings.xhr = window.ActiveXObject ?
// 	/* Microsoft failed to properly
// 	 * implement the XMLHttpRequest in IE7 (can't request local files),
// 	 * so we use the ActiveXObject when it is available
// 	 * Additionally XMLHttpRequest can be disabled in IE7/IE8 so
// 	 * we need a fallback.
// 	 */
// 	function() {
// 		if ( window.location.protocol !== "file:" ) {
// 			try {
// 				return new window.XMLHttpRequest();
// 			} catch( xhrError ) {}
// 		}

// 		try {
// 			return new window.ActiveXObject("Microsoft.XMLHTTP");
// 		} catch( activeError ) {}
// 	} :
// 	// For all other browsers, use the standard XMLHttpRequest object
// 	function() {
// 		return new window.XMLHttpRequest();
// 	};

// // Test if we can create an xhr object
// try {
// 	testXHR = jQuery.ajaxSettings.xhr();
// } catch( xhrCreationException ) {}

// //Does this browser support XHR requests?
// jQuery.support.ajax = !!testXHR;

// // Does this browser support crossDomain XHR requests
// jQuery.support.cors = testXHR && ( "withCredentials" in testXHR );

// // No need for the temporary xhr anymore
// testXHR = undefined;

// // Create transport if the browser can provide an xhr
// if ( jQuery.support.ajax ) {

// 	jQuery.ajaxTransport(function( s ) {
// 		// Cross domain only allowed if supported through XMLHttpRequest
// 		if ( !s.crossDomain || jQuery.support.cors ) {

// 			var callback;

// 			return {
// 				send: function( headers, complete ) {

// 					// #5280: we need to abort on unload or IE will keep connections alive
// 					if ( !xhrUnloadAbortInstalled ) {

// 						xhrUnloadAbortInstalled = 1;

// 						jQuery(window).bind( "unload", function() {

// 							// Abort all pending requests
// 							jQuery.each( xhrs, function( _, xhr ) {
// 								if ( xhr.onreadystatechange ) {
// 									xhr.onreadystatechange( 1 );
// 								}
// 							} );

// 						} );
// 					}

// 					// Get a new xhr
// 					var xhr = s.xhr(),
// 						handle;

// 					// Open the socket
// 					// Passing null username, generates a login popup on Opera (#2865)
// 					if ( s.username ) {
// 						xhr.open( s.type, s.url, s.async, s.username, s.password );
// 					} else {
// 						xhr.open( s.type, s.url, s.async );
// 					}

// 					// Requested-With header
// 					// Not set for crossDomain requests with no content
// 					// (see why at http://trac.dojotoolkit.org/ticket/9486)
// 					// Won't change header if already provided
// 					if ( !( s.crossDomain && !s.hasContent ) && !headers["x-requested-with"] ) {
// 						headers[ "x-requested-with" ] = "XMLHttpRequest";
// 					}

// 					// Need an extra try/catch for cross domain requests in Firefox 3
// 					try {
// 						jQuery.each( headers, function( key, value ) {
// 							xhr.setRequestHeader( key, value );
// 						} );
// 					} catch( _ ) {}

// 					// Do send the request
// 					// This may raise an exception which is actually
// 					// handled in jQuery.ajax (so no try/catch here)
// 					xhr.send( ( s.hasContent && s.data ) || null );

// 					// Listener
// 					callback = function( _, isAbort ) {

// 						// Was never called and is aborted or complete
// 						if ( callback && ( isAbort || xhr.readyState === 4 ) ) {

// 							// Only called once
// 							callback = 0;

// 							// Do not keep as active anymore
// 							if ( handle ) {
// 								xhr.onreadystatechange = jQuery.noop;
// 								delete xhrs[ handle ];
// 							}

// 							// If it's an abort
// 							if ( isAbort ) {
// 								// Abort it manually if needed
// 								if ( xhr.readyState !== 4 ) {
// 									xhr.abort();
// 								}
// 							} else {
// 								// Get info
// 								var status = xhr.status,
// 									statusText,
// 									responseHeaders = xhr.getAllResponseHeaders(),
// 									responses = {},
// 									xml = xhr.responseXML;

// 								// Construct response list
// 								if ( xml && xml.documentElement /* #4958 */ ) {
// 									responses.xml = xml;
// 								}
// 								responses.text = xhr.responseText;

// 								// Firefox throws an exception when accessing
// 								// statusText for faulty cross-domain requests
// 								try {
// 									statusText = xhr.statusText;
// 								} catch( e ) {
// 									// We normalize with Webkit giving an empty statusText
// 									statusText = "";
// 								}

// 								// Filter status for non standard behaviours
// 								status =
// 									// Opera returns 0 when it should be 304
// 									// Webkit returns 0 for failing cross-domain no matter the real status
// 									status === 0 ?
// 										(
// 											// Webkit, Firefox: filter out faulty cross-domain requests
// 											!s.crossDomain || statusText ?
// 											(
// 												// Opera: filter out real aborts #6060
// 												responseHeaders ?
// 												304 :
// 												0
// 											) :
// 											// We assume 302 but could be anything cross-domain related
// 											302
// 										) :
// 										(
// 											// IE sometimes returns 1223 when it should be 204 (see #1450)
// 											status == 1223 ?
// 												204 :
// 												status
// 										);

// 								// Call complete
// 								complete( status, statusText, responses, responseHeaders );
// 							}
// 						}
// 					};

// 					// if we're in sync mode or it's in cache
// 					// and has been retrieved directly (IE6 & IE7)
// 					// we need to manually fire the callback
// 					if ( !s.async || xhr.readyState === 4 ) {
// 						callback();
// 					} else {
// 						// Add to list of active xhrs
// 						handle = xhrId++;
// 						xhrs[ handle ] = xhr;
// 						xhr.onreadystatechange = callback;
// 					}
// 				},

// 				abort: function() {
// 					if ( callback ) {
// 						callback(0,1);
// 					}
// 				}
// 			};
// 		}
// 	});
// }




// var elemdisplay = {},
// 	rfxtypes = /^(?:toggle|show|hide)$/,
// 	rfxnum = /^([+\-]=)?([\d+.\-]+)([a-z%]*)$/i,
// 	timerId,
// 	fxAttrs = [
// 		// height animations
// 		[ "height", "marginTop", "marginBottom", "paddingTop", "paddingBottom" ],
// 		// width animations
// 		[ "width", "marginLeft", "marginRight", "paddingLeft", "paddingRight" ],
// 		// opacity animations
// 		[ "opacity" ]
// 	];

// jQuery.fn.extend({
// 	show: function( speed, easing, callback ) {
// 		var elem, display;

// 		if ( speed || speed === 0 ) {
// 			return this.animate( genFx("show", 3), speed, easing, callback);

// 		} else {
// 			for ( var i = 0, j = this.length; i < j; i++ ) {
// 				elem = this[i];
// 				display = elem.style.display;

// 				// Reset the inline display of this element to learn if it is
// 				// being hidden by cascaded rules or not
// 				if ( !jQuery._data(elem, "olddisplay") && display === "none" ) {
// 					display = elem.style.display = "";
// 				}

// 				// Set elements which have been overridden with display: none
// 				// in a stylesheet to whatever the default browser style is
// 				// for such an element
// 				if ( display === "" && jQuery.css( elem, "display" ) === "none" ) {
// 					jQuery._data(elem, "olddisplay", defaultDisplay(elem.nodeName));
// 				}
// 			}

// 			// Set the display of most of the elements in a second loop
// 			// to avoid the constant reflow
// 			for ( i = 0; i < j; i++ ) {
// 				elem = this[i];
// 				display = elem.style.display;

// 				if ( display === "" || display === "none" ) {
// 					elem.style.display = jQuery._data(elem, "olddisplay") || "";
// 				}
// 			}

// 			return this;
// 		}
// 	},

// 	hide: function( speed, easing, callback ) {
// 		if ( speed || speed === 0 ) {
// 			return this.animate( genFx("hide", 3), speed, easing, callback);

// 		} else {
// 			for ( var i = 0, j = this.length; i < j; i++ ) {
// 				var display = jQuery.css( this[i], "display" );

// 				if ( display !== "none" && !jQuery._data( this[i], "olddisplay" ) ) {
// 					jQuery._data( this[i], "olddisplay", display );
// 				}
// 			}

// 			// Set the display of the elements in a second loop
// 			// to avoid the constant reflow
// 			for ( i = 0; i < j; i++ ) {
// 				this[i].style.display = "none";
// 			}

// 			return this;
// 		}
// 	},

// 	// Save the old toggle function
// 	_toggle: jQuery.fn.toggle,

// 	toggle: function( fn, fn2, callback ) {
// 		var bool = typeof fn === "boolean";

// 		if ( jQuery.isFunction(fn) && jQuery.isFunction(fn2) ) {
// 			this._toggle.apply( this, arguments );

// 		} else if ( fn == null || bool ) {
// 			this.each(function() {
// 				var state = bool ? fn : jQuery(this).is(":hidden");
// 				jQuery(this)[ state ? "show" : "hide" ]();
// 			});

// 		} else {
// 			this.animate(genFx("toggle", 3), fn, fn2, callback);
// 		}

// 		return this;
// 	},

// 	fadeTo: function( speed, to, easing, callback ) {
// 		return this.filter(":hidden").css("opacity", 0).show().end()
// 					.animate({opacity: to}, speed, easing, callback);
// 	},

// 	animate: function( prop, speed, easing, callback ) {
// 		var optall = jQuery.speed(speed, easing, callback);

// 		if ( jQuery.isEmptyObject( prop ) ) {
// 			return this.each( optall.complete );
// 		}

// 		return this[ optall.queue === false ? "each" : "queue" ](function() {
// 			// XXX 'this' does not always have a nodeName when running the
// 			// test suite

// 			var opt = jQuery.extend({}, optall), p,
// 				isElement = this.nodeType === 1,
// 				hidden = isElement && jQuery(this).is(":hidden"),
// 				self = this;

// 			for ( p in prop ) {
// 				var name = jQuery.camelCase( p );

// 				if ( p !== name ) {
// 					prop[ name ] = prop[ p ];
// 					delete prop[ p ];
// 					p = name;
// 				}

// 				if ( prop[p] === "hide" && hidden || prop[p] === "show" && !hidden ) {
// 					return opt.complete.call(this);
// 				}

// 				if ( isElement && ( p === "height" || p === "width" ) ) {
// 					// Make sure that nothing sneaks out
// 					// Record all 3 overflow attributes because IE does not
// 					// change the overflow attribute when overflowX and
// 					// overflowY are set to the same value
// 					opt.overflow = [ this.style.overflow, this.style.overflowX, this.style.overflowY ];

// 					// Set display property to inline-block for height/width
// 					// animations on inline elements that are having width/height
// 					// animated
// 					if ( jQuery.css( this, "display" ) === "inline" &&
// 							jQuery.css( this, "float" ) === "none" ) {
// 						if ( !jQuery.support.inlineBlockNeedsLayout ) {
// 							this.style.display = "inline-block";

// 						} else {
// 							var display = defaultDisplay(this.nodeName);

// 							// inline-level elements accept inline-block;
// 							// block-level elements need to be inline with layout
// 							if ( display === "inline" ) {
// 								this.style.display = "inline-block";

// 							} else {
// 								this.style.display = "inline";
// 								this.style.zoom = 1;
// 							}
// 						}
// 					}
// 				}

// 				if ( jQuery.isArray( prop[p] ) ) {
// 					// Create (if needed) and add to specialEasing
// 					(opt.specialEasing = opt.specialEasing || {})[p] = prop[p][1];
// 					prop[p] = prop[p][0];
// 				}
// 			}

// 			if ( opt.overflow != null ) {
// 				this.style.overflow = "hidden";
// 			}

// 			opt.curAnim = jQuery.extend({}, prop);

// 			jQuery.each( prop, function( name, val ) {
// 				var e = new jQuery.fx( self, opt, name );

// 				if ( rfxtypes.test(val) ) {
// 					e[ val === "toggle" ? hidden ? "show" : "hide" : val ]( prop );

// 				} else {
// 					var parts = rfxnum.exec(val),
// 						start = e.cur() || 0;

// 					if ( parts ) {
// 						var end = parseFloat( parts[2] ),
// 							unit = parts[3] || "px";

// 						// We need to compute starting value
// 						if ( unit !== "px" ) {
// 							jQuery.style( self, name, (end || 1) + unit);
// 							start = ((end || 1) / e.cur()) * start;
// 							jQuery.style( self, name, start + unit);
// 						}

// 						// If a +=/-= token was provided, we're doing a relative animation
// 						if ( parts[1] ) {
// 							end = ((parts[1] === "-=" ? -1 : 1) * end) + start;
// 						}

// 						e.custom( start, end, unit );

// 					} else {
// 						e.custom( start, val, "" );
// 					}
// 				}
// 			});

// 			// For JS strict compliance
// 			return true;
// 		});
// 	},

// 	stop: function( clearQueue, gotoEnd ) {
// 		var timers = jQuery.timers;

// 		if ( clearQueue ) {
// 			this.queue([]);
// 		}

// 		this.each(function() {
// 			// go in reverse order so anything added to the queue during the loop is ignored
// 			for ( var i = timers.length - 1; i >= 0; i-- ) {
// 				if ( timers[i].elem === this ) {
// 					if (gotoEnd) {
// 						// force the next step to be the last
// 						timers[i](true);
// 					}

// 					timers.splice(i, 1);
// 				}
// 			}
// 		});

// 		// start the next in the queue if the last step wasn't forced
// 		if ( !gotoEnd ) {
// 			this.dequeue();
// 		}

// 		return this;
// 	}

// });

// function genFx( type, num ) {
// 	var obj = {};

// 	jQuery.each( fxAttrs.concat.apply([], fxAttrs.slice(0,num)), function() {
// 		obj[ this ] = type;
// 	});

// 	return obj;
// }

// // Generate shortcuts for custom animations
// jQuery.each({
// 	slideDown: genFx("show", 1),
// 	slideUp: genFx("hide", 1),
// 	slideToggle: genFx("toggle", 1),
// 	fadeIn: { opacity: "show" },
// 	fadeOut: { opacity: "hide" },
// 	fadeToggle: { opacity: "toggle" }
// }, function( name, props ) {
// 	jQuery.fn[ name ] = function( speed, easing, callback ) {
// 		return this.animate( props, speed, easing, callback );
// 	};
// });

// jQuery.extend({
// 	speed: function( speed, easing, fn ) {
// 		var opt = speed && typeof speed === "object" ? jQuery.extend({}, speed) : {
// 			complete: fn || !fn && easing ||
// 				jQuery.isFunction( speed ) && speed,
// 			duration: speed,
// 			easing: fn && easing || easing && !jQuery.isFunction(easing) && easing
// 		};

// 		opt.duration = jQuery.fx.off ? 0 : typeof opt.duration === "number" ? opt.duration :
// 			opt.duration in jQuery.fx.speeds ? jQuery.fx.speeds[opt.duration] : jQuery.fx.speeds._default;

// 		// Queueing
// 		opt.old = opt.complete;
// 		opt.complete = function() {
// 			if ( opt.queue !== false ) {
// 				jQuery(this).dequeue();
// 			}
// 			if ( jQuery.isFunction( opt.old ) ) {
// 				opt.old.call( this );
// 			}
// 		};

// 		return opt;
// 	},

// 	easing: {
// 		linear: function( p, n, firstNum, diff ) {
// 			return firstNum + diff * p;
// 		},
// 		swing: function( p, n, firstNum, diff ) {
// 			return ((-Math.cos(p*Math.PI)/2) + 0.5) * diff + firstNum;
// 		}
// 	},

// 	timers: [],

// 	fx: function( elem, options, prop ) {
// 		this.options = options;
// 		this.elem = elem;
// 		this.prop = prop;

// 		if ( !options.orig ) {
// 			options.orig = {};
// 		}
// 	}

// });

// jQuery.fx.prototype = {
// 	// Simple function for setting a style value
// 	update: function() {
// 		if ( this.options.step ) {
// 			this.options.step.call( this.elem, this.now, this );
// 		}

// 		(jQuery.fx.step[this.prop] || jQuery.fx.step._default)( this );
// 	},

// 	// Get the current size
// 	cur: function() {
// 		if ( this.elem[this.prop] != null && (!this.elem.style || this.elem.style[this.prop] == null) ) {
// 			return this.elem[ this.prop ];
// 		}

// 		var r = parseFloat( jQuery.css( this.elem, this.prop ) );
// 		return r || 0;
// 	},

// 	// Start an animation from one number to another
// 	custom: function( from, to, unit ) {
// 		var self = this,
// 			fx = jQuery.fx;

// 		this.startTime = jQuery.now();
// 		this.start = from;
// 		this.end = to;
// 		this.unit = unit || this.unit || "px";
// 		this.now = this.start;
// 		this.pos = this.state = 0;

// 		function t( gotoEnd ) {
// 			return self.step(gotoEnd);
// 		}

// 		t.elem = this.elem;

// 		if ( t() && jQuery.timers.push(t) && !timerId ) {
// 			timerId = setInterval(fx.tick, fx.interval);
// 		}
// 	},

// 	// Simple 'show' function
// 	show: function() {
// 		// Remember where we started, so that we can go back to it later
// 		this.options.orig[this.prop] = jQuery.style( this.elem, this.prop );
// 		this.options.show = true;

// 		// Begin the animation
// 		// Make sure that we start at a small width/height to avoid any
// 		// flash of content
// 		this.custom(this.prop === "width" || this.prop === "height" ? 1 : 0, this.cur());

// 		// Start by showing the element
// 		jQuery( this.elem ).show();
// 	},

// 	// Simple 'hide' function
// 	hide: function() {
// 		// Remember where we started, so that we can go back to it later
// 		this.options.orig[this.prop] = jQuery.style( this.elem, this.prop );
// 		this.options.hide = true;

// 		// Begin the animation
// 		this.custom(this.cur(), 0);
// 	},

// 	// Each step of an animation
// 	step: function( gotoEnd ) {
// 		var t = jQuery.now(), done = true;

// 		if ( gotoEnd || t >= this.options.duration + this.startTime ) {
// 			this.now = this.end;
// 			this.pos = this.state = 1;
// 			this.update();

// 			this.options.curAnim[ this.prop ] = true;

// 			for ( var i in this.options.curAnim ) {
// 				if ( this.options.curAnim[i] !== true ) {
// 					done = false;
// 				}
// 			}

// 			if ( done ) {
// 				// Reset the overflow
// 				if ( this.options.overflow != null && !jQuery.support.shrinkWrapBlocks ) {
// 					var elem = this.elem,
// 						options = this.options;

// 					jQuery.each( [ "", "X", "Y" ], function (index, value) {
// 						elem.style[ "overflow" + value ] = options.overflow[index];
// 					} );
// 				}

// 				// Hide the element if the "hide" operation was done
// 				if ( this.options.hide ) {
// 					jQuery(this.elem).hide();
// 				}

// 				// Reset the properties, if the item has been hidden or shown
// 				if ( this.options.hide || this.options.show ) {
// 					for ( var p in this.options.curAnim ) {
// 						jQuery.style( this.elem, p, this.options.orig[p] );
// 					}
// 				}

// 				// Execute the complete function
// 				this.options.complete.call( this.elem );
// 			}

// 			return false;

// 		} else {
// 			var n = t - this.startTime;
// 			this.state = n / this.options.duration;

// 			// Perform the easing function, defaults to swing
// 			var specialEasing = this.options.specialEasing && this.options.specialEasing[this.prop];
// 			var defaultEasing = this.options.easing || (jQuery.easing.swing ? "swing" : "linear");
// 			this.pos = jQuery.easing[specialEasing || defaultEasing](this.state, n, 0, 1, this.options.duration);
// 			this.now = this.start + ((this.end - this.start) * this.pos);

// 			// Perform the next step of the animation
// 			this.update();
// 		}

// 		return true;
// 	}
// };

// jQuery.extend( jQuery.fx, {
// 	tick: function() {
// 		var timers = jQuery.timers;

// 		for ( var i = 0; i < timers.length; i++ ) {
// 			if ( !timers[i]() ) {
// 				timers.splice(i--, 1);
// 			}
// 		}

// 		if ( !timers.length ) {
// 			jQuery.fx.stop();
// 		}
// 	},

// 	interval: 13,

// 	stop: function() {
// 		clearInterval( timerId );
// 		timerId = null;
// 	},

// 	speeds: {
// 		slow: 600,
// 		fast: 200,
// 		// Default speed
// 		_default: 400
// 	},

// 	step: {
// 		opacity: function( fx ) {
// 			jQuery.style( fx.elem, "opacity", fx.now );
// 		},

// 		_default: function( fx ) {
// 			if ( fx.elem.style && fx.elem.style[ fx.prop ] != null ) {
// 				fx.elem.style[ fx.prop ] = (fx.prop === "width" || fx.prop === "height" ? Math.max(0, fx.now) : fx.now) + fx.unit;
// 			} else {
// 				fx.elem[ fx.prop ] = fx.now;
// 			}
// 		}
// 	}
// });

// if ( jQuery.expr && jQuery.expr.filters ) {
// 	jQuery.expr.filters.animated = function( elem ) {
// 		return jQuery.grep(jQuery.timers, function( fn ) {
// 			return elem === fn.elem;
// 		}).length;
// 	};
// }

// function defaultDisplay( nodeName ) {
// 	if ( !elemdisplay[ nodeName ] ) {
// 		var elem = jQuery("<" + nodeName + ">").appendTo("body"),
// 			display = elem.css("display");

// 		elem.remove();

// 		if ( display === "none" || display === "" ) {
// 			display = "block";
// 		}

// 		elemdisplay[ nodeName ] = display;
// 	}

// 	return elemdisplay[ nodeName ];
// }




// var rtable = /^t(?:able|d|h)$/i,
// 	rroot = /^(?:body|html)$/i;

// if ( "getBoundingClientRect" in document.documentElement ) {
// 	jQuery.fn.offset = function( options ) {
// 		var elem = this[0], box;

// 		if ( options ) {
// 			return this.each(function( i ) {
// 				jQuery.offset.setOffset( this, options, i );
// 			});
// 		}

// 		if ( !elem || !elem.ownerDocument ) {
// 			return null;
// 		}

// 		if ( elem === elem.ownerDocument.body ) {
// 			return jQuery.offset.bodyOffset( elem );
// 		}

// 		try {
// 			box = elem.getBoundingClientRect();
// 		} catch(e) {}

// 		var doc = elem.ownerDocument,
// 			docElem = doc.documentElement;

// 		// Make sure we're not dealing with a disconnected DOM node
// 		if ( !box || !jQuery.contains( docElem, elem ) ) {
// 			return box ? { top: box.top, left: box.left } : { top: 0, left: 0 };
// 		}

// 		var body = doc.body,
// 			win = getWindow(doc),
// 			clientTop  = docElem.clientTop  || body.clientTop  || 0,
// 			clientLeft = docElem.clientLeft || body.clientLeft || 0,
// 			scrollTop  = (win.pageYOffset || jQuery.support.boxModel && docElem.scrollTop  || body.scrollTop ),
// 			scrollLeft = (win.pageXOffset || jQuery.support.boxModel && docElem.scrollLeft || body.scrollLeft),
// 			top  = box.top  + scrollTop  - clientTop,
// 			left = box.left + scrollLeft - clientLeft;

// 		return { top: top, left: left };
// 	};

// } else {
// 	jQuery.fn.offset = function( options ) {
// 		var elem = this[0];

// 		if ( options ) {
// 			return this.each(function( i ) {
// 				jQuery.offset.setOffset( this, options, i );
// 			});
// 		}

// 		if ( !elem || !elem.ownerDocument ) {
// 			return null;
// 		}

// 		if ( elem === elem.ownerDocument.body ) {
// 			return jQuery.offset.bodyOffset( elem );
// 		}

// 		jQuery.offset.initialize();

// 		var computedStyle,
// 			offsetParent = elem.offsetParent,
// 			prevOffsetParent = elem,
// 			doc = elem.ownerDocument,
// 			docElem = doc.documentElement,
// 			body = doc.body,
// 			defaultView = doc.defaultView,
// 			prevComputedStyle = defaultView ? defaultView.getComputedStyle( elem, null ) : elem.currentStyle,
// 			top = elem.offsetTop,
// 			left = elem.offsetLeft;

// 		while ( (elem = elem.parentNode) && elem !== body && elem !== docElem ) {
// 			if ( jQuery.offset.supportsFixedPosition && prevComputedStyle.position === "fixed" ) {
// 				break;
// 			}

// 			computedStyle = defaultView ? defaultView.getComputedStyle(elem, null) : elem.currentStyle;
// 			top  -= elem.scrollTop;
// 			left -= elem.scrollLeft;

// 			if ( elem === offsetParent ) {
// 				top  += elem.offsetTop;
// 				left += elem.offsetLeft;

// 				if ( jQuery.offset.doesNotAddBorder && !(jQuery.offset.doesAddBorderForTableAndCells && rtable.test(elem.nodeName)) ) {
// 					top  += parseFloat( computedStyle.borderTopWidth  ) || 0;
// 					left += parseFloat( computedStyle.borderLeftWidth ) || 0;
// 				}

// 				prevOffsetParent = offsetParent;
// 				offsetParent = elem.offsetParent;
// 			}

// 			if ( jQuery.offset.subtractsBorderForOverflowNotVisible && computedStyle.overflow !== "visible" ) {
// 				top  += parseFloat( computedStyle.borderTopWidth  ) || 0;
// 				left += parseFloat( computedStyle.borderLeftWidth ) || 0;
// 			}

// 			prevComputedStyle = computedStyle;
// 		}

// 		if ( prevComputedStyle.position === "relative" || prevComputedStyle.position === "static" ) {
// 			top  += body.offsetTop;
// 			left += body.offsetLeft;
// 		}

// 		if ( jQuery.offset.supportsFixedPosition && prevComputedStyle.position === "fixed" ) {
// 			top  += Math.max( docElem.scrollTop, body.scrollTop );
// 			left += Math.max( docElem.scrollLeft, body.scrollLeft );
// 		}

// 		return { top: top, left: left };
// 	};
// }

// jQuery.offset = {
// 	initialize: function() {
// 		var body = document.body, container = document.createElement("div"), innerDiv, checkDiv, table, td, bodyMarginTop = parseFloat( jQuery.css(body, "marginTop") ) || 0,
// 			html = "<div style='position:absolute;top:0;left:0;margin:0;border:5px solid #000;padding:0;width:1px;height:1px;'><div></div></div><table style='position:absolute;top:0;left:0;margin:0;border:5px solid #000;padding:0;width:1px;height:1px;' cellpadding='0' cellspacing='0'><tr><td></td></tr></table>";

// 		jQuery.extend( container.style, { position: "absolute", top: 0, left: 0, margin: 0, border: 0, width: "1px", height: "1px", visibility: "hidden" } );

// 		container.innerHTML = html;
// 		body.insertBefore( container, body.firstChild );
// 		innerDiv = container.firstChild;
// 		checkDiv = innerDiv.firstChild;
// 		td = innerDiv.nextSibling.firstChild.firstChild;

// 		this.doesNotAddBorder = (checkDiv.offsetTop !== 5);
// 		this.doesAddBorderForTableAndCells = (td.offsetTop === 5);

// 		checkDiv.style.position = "fixed";
// 		checkDiv.style.top = "20px";

// 		// safari subtracts parent border width here which is 5px
// 		this.supportsFixedPosition = (checkDiv.offsetTop === 20 || checkDiv.offsetTop === 15);
// 		checkDiv.style.position = checkDiv.style.top = "";

// 		innerDiv.style.overflow = "hidden";
// 		innerDiv.style.position = "relative";

// 		this.subtractsBorderForOverflowNotVisible = (checkDiv.offsetTop === -5);

// 		this.doesNotIncludeMarginInBodyOffset = (body.offsetTop !== bodyMarginTop);

// 		body.removeChild( container );
// 		body = container = innerDiv = checkDiv = table = td = null;
// 		jQuery.offset.initialize = jQuery.noop;
// 	},

// 	bodyOffset: function( body ) {
// 		var top = body.offsetTop,
// 			left = body.offsetLeft;

// 		jQuery.offset.initialize();

// 		if ( jQuery.offset.doesNotIncludeMarginInBodyOffset ) {
// 			top  += parseFloat( jQuery.css(body, "marginTop") ) || 0;
// 			left += parseFloat( jQuery.css(body, "marginLeft") ) || 0;
// 		}

// 		return { top: top, left: left };
// 	},

// 	setOffset: function( elem, options, i ) {
// 		var position = jQuery.css( elem, "position" );

// 		// set position first, in-case top/left are set even on static elem
// 		if ( position === "static" ) {
// 			elem.style.position = "relative";
// 		}

// 		var curElem = jQuery( elem ),
// 			curOffset = curElem.offset(),
// 			curCSSTop = jQuery.css( elem, "top" ),
// 			curCSSLeft = jQuery.css( elem, "left" ),
// 			calculatePosition = (position === "absolute" && jQuery.inArray('auto', [curCSSTop, curCSSLeft]) > -1),
// 			props = {}, curPosition = {}, curTop, curLeft;

// 		// need to be able to calculate position if either top or left is auto and position is absolute
// 		if ( calculatePosition ) {
// 			curPosition = curElem.position();
// 		}

// 		curTop  = calculatePosition ? curPosition.top  : parseInt( curCSSTop,  10 ) || 0;
// 		curLeft = calculatePosition ? curPosition.left : parseInt( curCSSLeft, 10 ) || 0;

// 		if ( jQuery.isFunction( options ) ) {
// 			options = options.call( elem, i, curOffset );
// 		}

// 		if (options.top != null) {
// 			props.top = (options.top - curOffset.top) + curTop;
// 		}
// 		if (options.left != null) {
// 			props.left = (options.left - curOffset.left) + curLeft;
// 		}

// 		if ( "using" in options ) {
// 			options.using.call( elem, props );
// 		} else {
// 			curElem.css( props );
// 		}
// 	}
// };


// jQuery.fn.extend({
// 	position: function() {
// 		if ( !this[0] ) {
// 			return null;
// 		}

// 		var elem = this[0],

// 		// Get *real* offsetParent
// 		offsetParent = this.offsetParent(),

// 		// Get correct offsets
// 		offset       = this.offset(),
// 		parentOffset = rroot.test(offsetParent[0].nodeName) ? { top: 0, left: 0 } : offsetParent.offset();

// 		// Subtract element margins
// 		// note: when an element has margin: auto the offsetLeft and marginLeft
// 		// are the same in Safari causing offset.left to incorrectly be 0
// 		offset.top  -= parseFloat( jQuery.css(elem, "marginTop") ) || 0;
// 		offset.left -= parseFloat( jQuery.css(elem, "marginLeft") ) || 0;

// 		// Add offsetParent borders
// 		parentOffset.top  += parseFloat( jQuery.css(offsetParent[0], "borderTopWidth") ) || 0;
// 		parentOffset.left += parseFloat( jQuery.css(offsetParent[0], "borderLeftWidth") ) || 0;

// 		// Subtract the two offsets
// 		return {
// 			top:  offset.top  - parentOffset.top,
// 			left: offset.left - parentOffset.left
// 		};
// 	},

// 	offsetParent: function() {
// 		return this.map(function() {
// 			var offsetParent = this.offsetParent || document.body;
// 			while ( offsetParent && (!rroot.test(offsetParent.nodeName) && jQuery.css(offsetParent, "position") === "static") ) {
// 				offsetParent = offsetParent.offsetParent;
// 			}
// 			return offsetParent;
// 		});
// 	}
// });


// // Create scrollLeft and scrollTop methods
// jQuery.each( ["Left", "Top"], function( i, name ) {
// 	var method = "scroll" + name;

// 	jQuery.fn[ method ] = function(val) {
// 		var elem = this[0], win;

// 		if ( !elem ) {
// 			return null;
// 		}

// 		if ( val !== undefined ) {
// 			// Set the scroll offset
// 			return this.each(function() {
// 				win = getWindow( this );

// 				if ( win ) {
// 					win.scrollTo(
// 						!i ? val : jQuery(win).scrollLeft(),
// 						 i ? val : jQuery(win).scrollTop()
// 					);

// 				} else {
// 					this[ method ] = val;
// 				}
// 			});
// 		} else {
// 			win = getWindow( elem );

// 			// Return the scroll offset
// 			return win ? ("pageXOffset" in win) ? win[ i ? "pageYOffset" : "pageXOffset" ] :
// 				jQuery.support.boxModel && win.document.documentElement[ method ] ||
// 					win.document.body[ method ] :
// 				elem[ method ];
// 		}
// 	};
// });

// function getWindow( elem ) {
// 	return jQuery.isWindow( elem ) ?
// 		elem :
// 		elem.nodeType === 9 ?
// 			elem.defaultView || elem.parentWindow :
// 			false;
// }




// // Create innerHeight, innerWidth, outerHeight and outerWidth methods
// jQuery.each([ "Height", "Width" ], function( i, name ) {

// 	var type = name.toLowerCase();

// 	// innerHeight and innerWidth
// 	jQuery.fn["inner" + name] = function() {
// 		return this[0] ?
// 			parseFloat( jQuery.css( this[0], type, "padding" ) ) :
// 			null;
// 	};

// 	// outerHeight and outerWidth
// 	jQuery.fn["outer" + name] = function( margin ) {
// 		return this[0] ?
// 			parseFloat( jQuery.css( this[0], type, margin ? "margin" : "border" ) ) :
// 			null;
// 	};

// 	jQuery.fn[ type ] = function( size ) {
// 		// Get window width or height
// 		var elem = this[0];
// 		if ( !elem ) {
// 			return size == null ? null : this;
// 		}

// 		if ( jQuery.isFunction( size ) ) {
// 			return this.each(function( i ) {
// 				var self = jQuery( this );
// 				self[ type ]( size.call( this, i, self[ type ]() ) );
// 			});
// 		}

// 		if ( jQuery.isWindow( elem ) ) {
// 			// Everyone else use document.documentElement or document.body depending on Quirks vs Standards mode
// 			// 3rd condition allows Nokia support, as it supports the docElem prop but not CSS1Compat
// 			var docElemProp = elem.document.documentElement[ "client" + name ];
// 			return elem.document.compatMode === "CSS1Compat" && docElemProp ||
// 				elem.document.body[ "client" + name ] || docElemProp;

// 		// Get document width or height
// 		} else if ( elem.nodeType === 9 ) {
// 			// Either scroll[Width/Height] or offset[Width/Height], whichever is greater
// 			return Math.max(
// 				elem.documentElement["client" + name],
// 				elem.body["scroll" + name], elem.documentElement["scroll" + name],
// 				elem.body["offset" + name], elem.documentElement["offset" + name]
// 			);

// 		// Get or set width or height on the element
// 		} else if ( size === undefined ) {
// 			var orig = jQuery.css( elem, type ),
// 				ret = parseFloat( orig );

// 			return jQuery.isNaN( ret ) ? orig : ret;

// 		// Set the width or height on the element (default to pixels if value is unitless)
// 		} else {
// 			return this.css( type, typeof size === "string" ? size : size + "px" );
// 		}
// 	};

// });


// })(window);
