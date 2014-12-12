(function() {
  
  var WUN = 653826927654; // weird unique number

  var $_ = new Object();
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = $_;
  }
  this.$_ = $_;

  // convert list to object, assumes that all element of list has property name

  $_.utils = (function() {
    function isArray(o) {
      return Object.prototype.toString.call(o) === '[object Array]';
    }

    function isString(a) {
      return typeof a === "string" || a instanceof String;
    }

    function isNumber(a) {
      return typeof a === "number" || a instanceof Number;
    }

    function isBoolean(a) {
      return typeof a === "boolean" || a instanceof Boolean;
    }

    function isFunction(a) {
      return typeof a === "function" || a instanceof Function;
    }

    function isDate(a) {
      return a instanceof Date;
    }

    function isNull(a) {
      return a === null || a === undefined;
    }

    function isPrimitive(a) {
      return isString(a) || isNumber(a) || isBoolean(a) || isFunction(a)
          || isDate(a);
    }

    function isObject(a) {
      return !isPrimitive(a) && !isArray(a);
    }

    function isArrayEmpty(array){
      return isNull(array) || array.length == 0;
    }
    
    function extractArray(args) {
      var array = null;
      if (args.length === 0) {
        array = [];
      } else if (args.length > 1) {
        array = args;
      } else if (args.length === 1) {
        var arg = args[0];
        if (isArray(arg)) {
          array = arg;
        } else if (isPrimitive(arg)) {
          array = [ arg ];
        }
      }
      return array;
    }

    
    function brodcastCall(brodcastTo, funcName, args){
      if(! isArrayEmpty(brodcastTo) ){
        brodcastTo.forEach(
            function(castTo){
              var f = castTo[funcName];
              if( isFunction(f) ) f.apply(castTo,args);
            }
        );
      }
    }


    function extractFunctionName(f) { // because IE does not support Function.prototype.name property
      var m = f.toString().match(/^\s*function\s*([^\s(]+)/);
      return m ? m[1] : "";
    }
    
    function getPropertyExtractor(property) { 
      return function(o) { 
        return o[property];
      };
    }
    
    function combineKeyExtractors() {
      var extractors = arguments;
      return function(o) {
        for ( var i = 0; i < extractors.length; i++) {
          var key = extractors[i](o);
          if(key !== undefined){
            return key;
          }
        }
        return undefined;
      };
    }

    function convertListToObject(list,extractor) {
      var obj = new Object();
      for ( var i = 0; i < list.length; i++) {
        var v = list[i];
        var k = extractor(v);
        if( k !== undefined ){
          obj[k] = v;
        }
      }
      return obj;
    }

    function splitUrlPath (urlpath) {
      var path = urlpath.split("/");
      var last = path[path.length-1].split('?');
      var result = { 
          path: path , 
          variables: {},
          toString: function(){ 
            var vars = '' ;
            var sep = '?' ;
            for ( var k in this.variables) {
              if (this.variables.hasOwnProperty(k)) {
                vars += sep + k + '=' + encodeURI(this.variables[k]);
                sep = '&';
              }
            }
            return this.path.join('/') + vars;
          }
      };
      if( last.length == 2 ){
        path[path.length-1] = last[0];
        last[1].split("&").forEach(function(part) {
          var item = part.split("=");
          if( item[0].length > 0 ){
            result.variables[item[0]] = decodeURIComponent(item[1]);
          }
        });
      }else if(last.length > 2){
        throw 'Unexpected number of "?" in url :' + urlpath ;
      }
      return result;
    }

    
    function convertFunctionsToObject(funcList) {
      return convertListToObject(funcList, combineKeyExtractors(getPropertyExtractor("name"), extractFunctionName));
    }
    
    function applyOnAll(obj, action) {
      for ( var k in obj) {
        if (obj.hasOwnProperty(k)) {
          action(obj[k], k, obj);
        }
      }
    }

    function append(object, params) {
      for ( var propertyName in params) {
        if (params.hasOwnProperty(propertyName)) {
          object[propertyName] = params[propertyName];
        }
      }
      return object;
    }

    function size(obj) {
      var size = 0;
      for ( var key in obj) {
        if (obj.hasOwnProperty(key))
          size++;
      }
      return size;
    }

    function join(array, delimiter, toString) {
      var keys = isObject(array) ? Object.keys(array) : array;
      if (!toString) {
        toString = function(s) {
          return s;
        };
      }
      if (delimiter == null) {
        delimiter = ',';
      }
      var doDelimit = (typeof delimiter === 'function') ? delimiter : function(
          array, positionFromBegining, positionFromEnd) {
        return (positionFromBegining < 0 || positionFromEnd <= 0) ? ''
            : delimiter;
      };
      var result = '';
      var positionFromBegining = -1;
      var positionFromEnd = keys.length;
      while (positionFromBegining < keys.length) {
        if (positionFromBegining >= 0) {
          result += toString(keys[positionFromBegining], array);
        }
        result += doDelimit(keys, positionFromBegining, positionFromEnd, array);
        positionFromBegining++;
        positionFromEnd--;
      }
      return result;
    }
    
    function detectRepeatingChar(l,c){
      var at = 0 ;  
      while( at < l.length && l.charAt(at) === c ) at++;
      return at;
    }

    function detectPrefix(l,prefix){
      var at = 0 ;  
      while( at < prefix.length && at < l.length && l.charAt(at) === prefix.charAt(at) ) at++;
      return prefix.length === at;
    }


    function stringify(x) {
      return x === undefined ? "undefined" : x === null ? "null"
          : isString(x) ? "'" + x + "'" : isArray(x) ? "["
              + join(x, ",", stringify) + "]" : x.toString();
    }

    function ensureDate(a) {
      return a instanceof Date ? a : new Date(a);
    }

    function ensureString(a) {
      return isString(a) ? a : String(a);
    }

    function error(params, input) {
      var e;
      if (input instanceof Error) {
        e = input;
      } else {
        e = new Error();
        if (input) {
          e.params = {
            cause : input
          };
        }
      }
      if (!e._message) {
        if (e.message) {
          e._message = e.message;
        } else if (params || params.message) {
          e._message = params.message;
          delete params['message'];
        }
      }
      var msg = e._message;
      if (!e.params) {
        e.params = {};
      }
      if (params) {
        append(e.params, params);
      }
      if (size(e.params)) {
        msg += "  ";
        for ( var k in e.params) {
          if (e.params.hasOwnProperty(k)) {
            msg += k + ":" + stringify(e.params[k]) + ", ";
          }
        }
        msg = msg.substring(0, msg.length - 2);
      }
      e.message = msg;
      return e;
    }

    function assert(provided, expected, message) {
      function checkAnyAgainstExpected() {
        for ( var i = 0; i < expected.length; i++) {
          if (provided === expected[i]) {
            return false;
          }
        }
        return true;
      }
      if (!isArray(expected) ? provided !== expected
          : checkAnyAgainstExpected()) {
        throw error({
          message : message || ("Unexpected entry: " + provided),
          expected : expected,
          provided : provided,
        });
      }
    }

    function padWith(what, pad) {
      var r = String(what);
      if (r.length !== pad.length) {
        r = (pad + r).substr(r.length, pad.length);
      }
      return r;
    }

    function dateToIsoString(date) {
      return date.getUTCFullYear() + '-'
          + padWith(date.getUTCMonth() + 1, '00') + '-'
          + padWith(date.getUTCDate(), '00') + 'T'
          + padWith(date.getUTCHours(), '00') + ':'
          + padWith(date.getUTCMinutes(), '00') + ':'
          + padWith(date.getUTCSeconds(), '00') + '.'
          + padWith(date.getUTCMilliseconds(), '0000') + 'Z';
    }
    
    //
    
    function parseDateUTC(s){
      return new Date(Date.parse(s+' UTC'));
    }
    
    function relativeDateString(date,rel) {
      if(!isDate(date)){
        if(!isNull(date)){
          date = parseDateUTC(date);
        }else{
          return "";
        }
      }
      if(!isDate(rel)){
        rel = new Date();
      }
      if( Math.abs(date.getTime() - rel.getTime()) < 86400000 ){
        var a = Math.floor( (date.getTime() - rel.getTime())  / 1000);
        var s = Math.abs(a) + 30;
        var m = Math.floor( s / 60 );
        var h = Math.floor( m / 60 );
        s = s % 60;
        m = m % 60;
        return (a < 0 ? '-' : '+') + padWith(h, '00') + ':' + padWith(m, '00')  ;
      } 
      return date.getUTCFullYear() + '-'
      + padWith(date.getUTCMonth() + 1, '00') + '-'
      + padWith(date.getUTCDate(), '00') + ' '
      + padWith(date.getUTCHours(), '00') + ':'
      + padWith(date.getUTCMinutes(), '00') ;
      
    }
    
    if (!Date.prototype.toISOString) {
      Date.prototype.toISOString = function() {
        return dateToIsoString(this);
      };
    }

    function binarySearch(searchFor, array, comparator, mapper) {
      var mapToValue = mapper || function(x) {
        return x;
      };
      var min = 0;
      var max = array.length - 1;
      var mid, r;
      while (min <= max) {
        mid = ((min + max) / 2) | 0;
        r = comparator(searchFor, mapToValue(array[mid]));
        if (r > 0) {
          min = mid + 1;
        } else if (r < 0) {
          max = mid - 1;
        } else {
          return mid;
        }
      }
      return -1 - min;
    }

    function repeat(count, value) {
      var result = [];
      for ( var i = 0; i < count; i++) {
        result.push(isFunction(value) ? value(i) : value);
      }
      return result;
    }

    function sequence(count, offset) {
      return repeat(count, function(i) {
        return isNumber(offset) || isString(offset) ? offset + i
            : isFunction(offset) ? offset(i) : i;
      });
    }

    function BiMap(map) {
      var forward = map;
      var _inverse = null;
      function inverse(){
        if( _inverse === null ){
          _inverse = {};
          for ( var key in forward) {
            if (forward.hasOwnProperty(key)) {
              _inverse[forward[key]]=key;
            }
          }
        }
        return _inverse;
      }
      return {
        get: function(key) { return forward[key]; },
        key: function(val) { return inverse()[val]; },
        put: function(key,val) { forward[key] = val; _inverse = null; },
        del: function(key) { delete forward[key];_inverse = null; },
        keys: function() { return Object.keys(forward); },
        values: function() { return Object.keys(inverse()); }
      };
    }

    function Tokenizer(s, delimiters) {
      var i = 0;

      function isValueChar() {
        return delimiters.indexOf(s.charAt(i)) < 0;
      }

      function next(condition) {
        var start = i;
        while (i < s.length && condition())
          i++;
        var next = s.substring(start, i);
        return next;
      }

      return {
        getText : function() {
          return s;
        },
        nextValue : function() {
          return next(isValueChar);
        },
        nextDelimiter : function() {
          return next(function() {
            return !isValueChar();
          });
        },
        toString : function() {
          return s.substring(0, i) + " <-i-> " + s.substring(i);
        },
        getPosition : function() {
          return i;
        },
        setPosition : function(_i) {
          i = _i;
        }
      };
    }

    var mappingEntities = {
      "<" : "&lt;",
      ">" : "&gt;",
      "&" : "&amp;",
      '"' : "&quot;",
      "'" : "&#39;",
    };

    function escapeEntities(s, delims) {
      var t = new Tokenizer(s, delims);
      var r = "";
      for (;;) {
        var v = t.nextValue();
        var d = t.nextDelimiter();
        if (v) {
          r += v;
        }
        if (d) {
          for ( var i = 0; i < d.length; i++) {
            r += mappingEntities[d.charAt(i)];
          }
        }
        if (!v && !d) {
          return r;
        }
      }
    }

    function escapeXmlAttribute(s) {
      return escapeEntities(s, "<>&'\"");
    }

    function escapeXmlBody(s) {
      return escapeEntities(s, "<>&");
    }

    return convertFunctionsToObject([ convertFunctionsToObject, convertListToObject,
        combineKeyExtractors, extractFunctionName, isArray, append, size,
        join, error, applyOnAll, assert, BiMap, Tokenizer, stringify, padWith,
        relativeDateString, parseDateUTC, dateToIsoString, ensureDate, 
        ensureString, isObject, isString, isNumber, isBoolean, isFunction, 
        isDate, isPrimitive, isNull, extractArray, binarySearch, repeat, 
        sequence, escapeXmlAttribute, escapeXmlBody, brodcastCall, 
        isArrayEmpty, detectRepeatingChar, detectPrefix, splitUrlPath ]);
  })();

  $_.percent_encoding = (function() {
    var escape_chars = "%+/?&=:";

    function toEscape(d) {
      var hex = Number(d).toString(16).toUpperCase();
      return '%' + (hex.length < 2 ? "0" + hex : hex);
    }

    function toDecimal(hex) {
      return parseInt(hex, 16);
    }

    function encode(text) {
      var data = "";
      for ( var n = 0; n < text.length; n++) {
        var c = text.charCodeAt(n);
        var ch = text.charAt(n);
        if (c < 32 || escape_chars.indexOf(ch) >= 0) {
          data += toEscape(c);
        } else if (c == 32) {
          data += "+";
        } else if (c < 128) {
          data += String.fromCharCode(c);
        } else if ((c > 127) && (c < 2048)) {
          data += toEscape((c >> 6) | 192);
          data += toEscape((c & 63) | 128);
        } else {
          data += toEscape((c >> 12) | 224);
          data += toEscape(((c >> 6) & 63) | 128);
          data += toEscape((c & 63) | 128);
        }
      }
      return data;
    }

    function decode(data) {
      var text = "";
      var i = 0;
      var b0, b1, b2;
      var c;

      function next(count) {
        if (!count)
          count = 1;
        var s = data.substr(i, count);
        i += count;
        return s;
      }

      function expectEscapeSequence() {
        c = next();
        if (c === '%') {
          return toDecimal(next(2));
        } else {
          throw {
            msg : "expected escape sequence"
          };
        }
      }

      while (i < data.length) {
        b0 = b1 = b2 = 0;
        c = next(1);
        if (c === '+') {
          text += ' ';
        } else if (c === '%') {
          b0 = toDecimal(next(2));
          if (b0 < 128) {
            text += String.fromCharCode(b0);
          } else if ((b0 > 191) && (b0 < 224)) {
            b1 = expectEscapeSequence();
            text += String.fromCharCode(((b0 & 31) << 6) | (b1 & 63));
          } else {
            next();
            b1 = expectEscapeSequence();
            b2 = expectEscapeSequence();
            text += String.fromCharCode(((b0 & 15) << 12) | ((b1 & 63) << 6)
                | (b2 & 63));
          }
        } else {
          text += c;
        }
      }
      return text;
    }

    return $_.utils.convertFunctionsToObject([ encode, decode ]);
  })();

  /**
   * Slinck amalgamation of words: slick link
   * 
   * Can represens section: slinck://host/branch/sec/ti/on
   * 
   * Can represent file: slinck://host/branch/sec/ti/on//fi/le/pa/th
   * 
   * Can represent fragment of ordered table
   * slinck://host/branch/sec/ti/on/db//a/b/c
   * 
   * or you can write same query as 'eq' condition to:
   * slinck://host/branch/sec/ti/ondb//?eq=a/b/c
   * 
   * Can represent fragment as range between two keys:
   * slinck://host/branch/sec/ti/ondb//?gte=a1/b1/c1&lt=a2/b2/c3
   * 
   * uses $_.percent_encoding to escape symbols
   * http://en.wikipedia.org/wiki/Percent-encoding
   */
  $_.utils.append($_, (function() {

    function extractPathElements(t, elems) {
      for (;;) {
        var v = t.nextValue();
        if (!v)
          return null;
        elems.push($_.percent_encoding.decode(v));
        var d = t.nextDelimiter();
        if (!d)
          return null;
        if (d && d !== "/") {
          return d;
        }
      }
    }

    function Path(path) {
      if (path === WUN)
        return this;
      var iuc = this instanceof Path ? this : new Path(WUN);
      iuc.elements = $_.utils.isArray(path) ? path : (function(s) {
        var t = $_.utils.Tokenizer(s, "/");
        var d = t.nextDelimiter();
        $_.utils.assert("", d);
        var elems = [];
        var endDelimiter = extractPathElements(t, elems);
        $_.utils.assert(endDelimiter, null);
        return elems;
      })(path);
      return iuc;
    }

    Path.prototype.toString = function() {
      return $_.utils.join(this.elements, "/", $_.percent_encoding.encode);
    };

    function Bound(condition, path) {
      if (condition === WUN)
        return this;
      var iuc = this instanceof Bound ? this : new Bound(WUN);
      iuc.condition = condition;
      iuc.path = (path instanceof Path) ? path : new Path(path);
      return iuc;
    }
    ;

    Bound.prototype.toString = function() {
      return this.condition + '=' + this.path.toString();
    };

    Path.Bound = Bound;
    Path.extractPathElements = extractPathElements;

    function Slinck(s) {
      if (s === WUN)
        return this;
      var iuc = this instanceof Slinck ? this : new Slinck(WUN);
      var t = $_.utils.Tokenizer(s, ":/?&=");
      var d = t.nextDelimiter();
      try {
        $_.utils.assert(d, [ "", "/" ]);
        var p = t.getPosition();
        var v = t.nextValue();
        d = t.nextDelimiter();
        iuc.host = iuc.path = null;
        iuc.bounds = {};
        if (v === "slinck" && d === "://") {
          iuc.host = t.nextValue();
          $_.utils.assert(t.nextDelimiter(), "/");
        } else {
          t.setPosition(p);
        }
        var sectionElements = [];
        d = extractPathElements(t, sectionElements);
        $_.utils.assert(d, [ "", "//", "?", null ]);
        iuc.section = new Path(sectionElements);
        iuc.bounds = {};
        iuc.hasBounds = false;
        if (d === "//") {
          var pathElements = [];
          d = extractPathElements(t, pathElements);
          if (pathElements.length > 0) {
            iuc.pathBound = new Bound("eq", pathElements);
          }
          iuc.path = new Path(pathElements);
        } else if (d === "?") {
          do {
            v = t.nextValue();
            if (v === null || v === "") {
              d = t.nextDelimiter();
              break;
            }
            $_.utils.assert(typeof Slinck.CONDITION[v], 'function',
                "Unknown condition:" + v);
            $_.utils.assert(t.nextDelimiter(), "=");
            var conditionPath = [];
            d = extractPathElements(t, conditionPath);
            iuc.bounds[v] = new Bound(v, conditionPath);
            iuc.hasBounds = true;
            $_.utils.assert(d, [ "", "&", null ]);
          } while (d === "&");
        }
        $_.utils.assert(d, [ "", null ]);
      } catch (e) {
        throw $_.utils.error({
          tokenator : t.toString()
        }, e);
      }
      return iuc;
    }

    Slinck.prototype.boundKeys = function() {
      var keys = [];
      if (this.pathBound) {
        keys.push("eq");
      } else {
        for ( var key in this.bounds) {
          if (this.bounds.hasOwnProperty(key)) {
            keys.push(key);
          }
        }
      }
      return keys;
    };


    Slinck.CONDITION = {
      eq :  function(r) {
        return r === 0;
      },
      ne : function(r) {
        return r !== 0;
      },
      lte : function(r) {
        return r <= 0;
      },
      gte : function(r) {
        return r >= 0;
      },
      lt : function(r) {
        return r < 0;
      },
      gt : function(r) {
        return r > 0;
      },
    };
    

    Slinck.prototype.bound = function(k) {
      if (this.pathBound && k === "eq") {
        return this.pathBound;
      }
      return this.bounds[k];
    };

    var DIRECTION = {
      up : function(vertex) {
        return vertex.upstreams;
      },
      down : function(vertex) {
        return vertex.downstreams;
      },
    };

    function visit(vertices, direction, before, after) {
      var i = 0;
      var size = $_.utils.size(vertices);
      for ( var k in vertices) {
        (function() {
          var vertex = vertices[k];
          var context = {
            k : k,
            i : i,
            size : size,
            edges : vertex.edges(direction),
            parentheses : false,
            firstOne : i === 0,
            lastOne : i === (size - 1),
          };
          if (before(vertex, direction, context)) {
            visit(context.edges, direction, before, after);
            if (after) {
              after(vertex, direction, context);
            }
          }
          i++;
        })();

      }
    }

    function Vertex(k, parent) {
      $_.utils.assert(this instanceof Vertex, true);
      this.k = k;
      this.upstreams = {};
      this.downstreams = {};
      this.graph = parent;
    }

    $_.utils.append(Vertex.prototype, {
      edges : function(direction) {
        return DIRECTION[direction](this);
      },
      isEnd : function(direction) {
        return $_.utils.size(this.edges(direction)) === 0;
      },
      remove : function() {
        var keyToDelete = this.k;
        $_.utils.applyOnAll(this.upstreams, function(vertex) {
          delete vertex.downstreams[keyToDelete];
        });
        $_.utils.applyOnAll(this.downstreams, function(vertex) {
          delete vertex.upstreams[keyToDelete];
        });
        delete this.parent.vertices[keyToDelete];
      },
      ends : function(direction) {
        var ends = {};
        for ( var k in this.vertices) {
          if (this.vertices[k].isEnd(direction)) {
            ends[k] = this.vertices[k];
          }
        }
        return ends;
      },
      setOfOne : function() {
        var r = {};
        r[this.k] = this;
        return r;
      },
      search : function(key, direction) {
        var found = false;
        visit(this.setOfOne(), direction, function(vertex) {
          if (vertex.k == key) {
            found = true;
          }
          return !found;
        });
        return found;
      },
    });

    /** Type */

    function Type(name, sortFunction) {
      this.name = name;
      this.compare = Type.nullsCompare(sortFunction);
      Type[name] = this;
      $_.utils.assert(Type[name], this,
          "Type is frozen for changes. Cannot add:" + name);
    }

    Type.nullsCompare = function(f) {
      function isUndef(x) {
        return x === undefined;
      }
      function isNull(x) {
        return x === null;
      }
      function exculdeIs(is, doIt) {
        return function(a, b) {
          return is(a) ? (is(b) ? 0 : 1) : (is(b) ? -1 : doIt(a, b));
        };
      }
      return exculdeIs(isUndef, exculdeIs(isNull, f));
    };

    Type.inverse = function(f) {
      return function(a, b) {
        return f(b, a);
      };
    };

    new Type("string", function(a, b) {
      var aStr = $_.utils.ensureString(a);
      var bStr = $_.utils.ensureString(b);
      return aStr === bStr ? 0 : aStr < bStr ? -1 : 1;
    });

    new Type("number", function(a, b) {
      return a - b;
    });

    new Type("boolean", function(a, b) {
      return a ? (b ? 0 : 1) : (b ? -1 : 0);
    });

    new Type("date", function(a, b) {
      var aDateValueOf = $_.utils.ensureDate(a).valueOf();
      var bDateValueOf = $_.utils.ensureDate(b).valueOf();
      return aDateValueOf === bDateValueOf ? 0
          : aDateValueOf < bDateValueOf ? -1 : 1;
    });

    new Type("blob", Type.string.compare);
    Object.freeze(Type);

    function ColumnRole(name) {
      this.name = name;
      ColumnRole[name] = this;
    }

    new ColumnRole("grouping_key");
    new ColumnRole("primary_key");
    new ColumnRole("data");
    new ColumnRole("attachment");
    
    

    Object.freeze(ColumnRole);

    /** /Type */

    /**
     * Graph - directed acyclic graph,
     * 
     * upstream and downstream indicates direction from upstream to downstream
     * (think flow)
     * 
     * 
     */
    function Graph() {
      $_.utils.assert(this instanceof Graph, true,
          "please use this function with new");
      this.vertices = {};
    }

    $_.utils.append(Graph.prototype, {
      get : function(k) {
        return this.vertices[k];
      },
      ensure : function(k) {
        var n = this.vertices[k];
        if (!n) {
          this.vertices[k] = n = new Vertex(k, this);
        }
        return n;
      },
      addEdge : function(downstream, upstream) {
        var un = upstream instanceof Vertex ? upstream : this.ensure(upstream);
        var dn = downstream instanceof Vertex ? downstream : this
            .ensure(downstream);
        if (un.search(downstream, "up") || dn.search(upstream, "down")) {
          throw $_.utils.error({
            message : "circular reference",
            downstream : downstream,
            upstream : upstream,
          });
        }
        un.downstreams[downstream] = dn;
        dn.upstreams[upstream] = un;
        return this;
      },
      ends : function(direction) {
        var r = {};
        for ( var k in this.vertices) {
          if (this.vertices[k].isEnd(direction)) {
            r[k] = this.vertices[k];
          }
        }
        return r;
      },
      visitBreadthFirst : function(vertexKeys, direction, onVisit, compare) {
        if (!compare)
          compare = Type.string.compare;
        var queue = $_.utils.isArray(vertexKeys) ? vertexKeys.slice(0) : Object.keys(vertexKeys);
        queue.sort(compare);
        while (queue.length > 0) {
          var k = queue.shift();
          var vertex = this.vertices[k];
          var context = {
            k : k,
            edges : vertex.edges(direction),
          };
          if (onVisit(vertex, direction, context)) {
            var childrenKeys = Object.keys(context.edges);
            if (childrenKeys.length > 0) {
              queue = queue.concat(childrenKeys.sort(compare));
            }
          }
        }
      },
      sort : function() {
        var visited = {};
        var sorted = [];
        this.visitBreadthFirst(this.ends("up"), "down", function(vertex) {
          var alreadySeen = visited[vertex.k];
          var store = !alreadySeen;
          if (store) {
            for ( var dkey in vertex.upstreams) {
              if (!visited[dkey]) {
                store = false;
              }
            }
            if (store) {
              sorted.push(vertex.k);
              visited[vertex.k] = 1;
            }
          }
          return !alreadySeen;
        });
        return sorted;
      },
      visitDepthFirst : function(vertixKeys, direction, before, after) {
        var verticesToSearch = {};
        if ($_.utils.isArray(vertixKeys)) {
          for ( var i = 0; i < vertixKeys.length; i++) {
            verticesToSearch[vertixKeys[i]] = this.vertices[vertixKeys[i]];
          }
        } else {
          verticesToSearch = vertixKeys;
        }
        visit(verticesToSearch, direction, before, after);
      },
      toString : function() {
        var s = '';
        var visited = {};
        var ends = this.ends("down");
        visit(ends, "up", function(vertex, direction, context) {
          s += vertex.k;
          var notVisited = !visited[vertex.k];
          if (notVisited) {
            visited[vertex.k] = true;
            if ($_.utils.size(context.edges) > 0) {
              context.parentheses = true;
              s += "=(";
            }
          }
          return notVisited;
        }, function(vertex, edges, context) {
          if (context.parentheses) {
            s += ")";
          }
          if (!context.lastOne) {
            s += ',';
          }
        });
        return s;
      }
    });

    Graph.parse = function(s) {
      var t = new $_.utils.Tokenizer(s, "=(),");
      var g = new Graph();
      var k, path = [];
      try {
        while (k = t.nextValue()) {
          if (path.length > 0) {
            g.addEdge(path[path.length - 1], k);
          } else {
            g.ensure(k);
          }
          var d = t.nextDelimiter();
          if (d === "=(") {
            path.push(k);
          } else if (d === "" || d === ",") {
            // do nothing
          } else {
            for ( var i = 0; i < d.length; i++) {
              var c = d.charAt(i);
              if (c === ')') {
                if (path.length === 0) {
                  throw $_.utils.error({
                    message : "unbalanced parenthesis"
                  });
                }
                path.pop();
              } else if (c === ',' && d.length === (i + 1)) {
                // do nothing
              } else {
                throw $_.utils.error({
                  message : "Unexpected delimiter",
                  c : c,
                  i : i
                });
              }
            }
          }
        }
        if (path.length !== 0) {
          throw $_.utils.error({
            path : path,
            message : "unbalanced parenthesis"
          });
        }
        if (t.getPosition() !== s.length) {
          throw $_.utils.error({
            k : k,
            message : "have to parse all charectes"
          });
        }
        return g;
      } catch (e) {
        throw $_.utils.error({
          t : t.toString()
        }, e);
      }
    };

    /** /Graph */

    /** Table */

    function Column(name, title, type) {
      $_.utils.assert(this instanceof Column, true,
          "please use 'new', when calling this function");
      this.name = name;
      this.title = title;
      this.type = type;
    }

    function Table(columns, data) {
      $_.utils.assert(this instanceof Table, true,
          "please use 'new', when calling this function");
      this.columns = [];
      this.columns.hash = {};
      this.columns.push = function() {
        for ( var i = 0; i < arguments.length; i++) {
          if (this.hash[arguments[i].name]) {
            throw $_.utils.error({
              message : "duplicate column",
              name : arguments[i].name,
              at : this.length
            });
          }
          this.hash[arguments[i].name] = arguments[i];
        }
        Array.prototype.push.apply(this, arguments);
      };
      if (columns && columns.length > 0) {
        this.columns.push.apply(this.columns, columns);
      }
      this.data = data ? data : [];
    }

    $_.utils.append(Table.prototype, {
      rowCount: function() {
        return this.data.length;
      },
      header: function(){
        return this.columns;
      },rows : function() {
        var rowIds = $_.utils.extractArray(arguments);
        if (!rowIds || rowIds.length === 0) {
          return null;
        }
        var rows = [];
        for ( var i = 0; i < rowIds.length; i++) {
          var rowId = rowIds[i];
          rows.push(this.row(rowId));
        }
        return rows;
      },
      row : function(rowId) {
        if (rowId < 0 && rowId >= this.data.length)
          throw $_.utils.error({
            message : "rowId outside of data range",
            rowId : rowId,
            dataLength : this.data.length
          });
        return this.data[rowId];
      },
      add : function(rowData) {
        var rowId = this.data.length;
        if( rowData.hasOwnProperty("_rowId") ){
          //need to clone
          rowData = $_.utils.append({},rowData);
        }
        this.data.push(rowData);
        rowData._rowId = rowId;
        return rowId;
      },
      set : function(rowId, rowData) {
        var row = this.row(rowId);
        if (row !== rowData) {
          this.checkColumns(Object.keys(rowData));
          $_.utils.append(row, rowData);
        }
      },
      filter: function(shouldRowBeIncluded){
        var filtered = new Table(this.columns);
        for ( var rowId = 0; rowId < this.data.length; rowId++) {
          if(shouldRowBeIncluded(this.data[rowId])){
            filtered.add(this.data[rowId]);
          }
        }
        return filtered;
      },
      addColumn : function(name, title, type) {
        $_.utils.assert(0, this.data.length, "Data has to be empty");
        this.columns.push(new Column(name, title, type));
      },
      checkColumns : function(keys) {
        for ( var keyIdx = 0; keyIdx < keys.length; keyIdx++) {
          this.checkColumn(keys[keyIdx]);
        }
      },
      checkColumn : function(k) {
        if ("_rowId" !== k && !this.columns.hash[k]) {
          throw $_.utils.error({
            message : "column does not exist",
            key : k
          });
        }
      },
      getRowCount : function() {
        return this.data.length;
      },
      makeCompare : function() {
        var keys = $_.utils.extractArray(arguments);
        var compares = [];
        for ( var keyIdx = 0; keyIdx < keys.length; keyIdx++) {
          var k = keys[keyIdx];
          var descending = (k.charAt(0) === "^");
          if (descending) {
            k = k.substring(1);
            keys[keyIdx] = k;
          }
          this.checkColumn(k);
          var compare = "_rowId" === k ? Type.number.compare
              : this.columns.hash[k].type.compare;
          if (descending) {
            compare = Type.inverse(compare);
          }
          compares[keyIdx] = compare;
        }
        function compareValues(rowA, rowB) {
          for ( var keyIdx = 0; keyIdx < keys.length; keyIdx++) {
            var k = keys[keyIdx];
            var compare = compares[keyIdx];
            var r = compare(rowA[k], rowB[k]);
            if (r !== 0) {
              return r;
            }
          }
          return 0;
        }
        var self = this;
        function compareRowId(rowIdA, rowIdB) {
          var rowA = self.row(rowIdA);
          var rowB = self.row(rowIdB);
          return compareValues(rowA, rowB);
        }
        ;
        compareRowId.compareValues = compareValues;
        return compareRowId;
      }
    });

    Column.Type = Type;
    Column.Role = ColumnRole;
    Table.Column = Column;

    /** /Table */

    /** Index */
    function Index(table, keys) {
      $_.utils.assert(this instanceof Index, true,
          "please use 'new', when calling this function");
      this.table = table;
      this.keys = keys;
      this.compare = table.makeCompare(keys);
      this.index = [];
      var sorted = true;
      for ( var i = 0; i < table.data.length; i++) {
        this.index[i] = i;
        if (i > 0) {
          if (sorted && this.compare(i - 1, i) > 0) {
            sorted = false;
          }
        }
      }
      if (!sorted) {
        this.index.sort(this.compare);
      }
      this.sorted = sorted;
    }

    $_.utils.append(Index.prototype, {
      getRowCount: function() {
        return this.table.getRowCount();
      },
      header: function(){
        return this.table.columns;
      },
      indexOf : function(searchFor) {
        var self = this;
        function mapper(mappee) {
          return self.table.row(mappee);
        }
        return $_.utils.binarySearch(searchFor, this.index,
            this.compare.compareValues, mapper);
      },
      row : function(rowNum) {
        return this.table.row(this.index[rowNum]);
      },
      merge : function(rowData) {
        var rowNum = this.indexOf(rowData);
        if (rowNum < 0) {
          rowNum = -1 - rowNum;
          var rowId = this.table.add(rowData);
          this.index.splice(rowNum, 0, rowId);
        } else {
          var mergeRow = this.table.row(this.index[rowNum]);
          $_.utils.append(mergeRow, rowData);
        }
        return rowNum;
      },
      add : function(rowData) {
        var rowNum = this.indexOf(rowData);
        if (rowNum < 0) {
          rowNum = -1 - rowNum;
        }
        var rowId = this.table.add(rowData);
        this.index.splice(rowNum, 0, rowId);
        return rowNum;
      }
    });

    /** /Index */

    /** XmlNode */
    function XmlNode(name, text) {
      $_.utils.assert(this instanceof XmlNode, true,
          "please use 'new', when calling this function");
      this.name = name;
      this.text = text;
      this.children = [];
      this.attributes = {};
    }
    $_.utils.append(XmlNode.prototype, {
      attr : function(k, v) {
        if (this.text) {
          throw $_.utils.error({
            message : "Cannot add attributes to text nodes",
            text : this.name
          });
        }
        if ($_.utils.isString(k) && k) {
          this.attributes[k] = v;
          return this;
        } else if ($_.utils.isObject(k)) {
          $_.utils.append(this.attributes, k);
          return this;
        }
        throw $_.utils.error({
          message : "Cannot recognize attribute",
          k : k
        });
      },
      addText : function(t) {
        this.child(t, true);
        return this;
      },
      addChildNode: function(child){
        if (this.text) {
          throw $_.utils.error({
            message : "Cannot add child to text nodes",
            text : this.name
          });
        }
        this.children.push(child);
        return ;
      },
      child : function(childName, text) {
        if ($_.utils.isArray(childName)) {
          var results = [];
          for ( var i = 0; i < childName.length; i++) {
            results.push(this.child(childName[i]));
          }
          return results;
        }else if ($_.utils.isString(childName)) {
            var child = new XmlNode(childName, text);
            this.addChildNode(child);
            return child;
        }  
        throw $_.utils.error({
          message : "Cannot detect " + text ? "text" : "childName/childNames",
          childName : childName
        });
      },
      toString : function() {
        if (this.text) {
          return $_.utils.escapeXmlBody(this.name);
        }
        var s = "<" + this.name;
        if (this.attributes) {
          s += $_.utils.join(this.attributes, "",
              function(k, map) {
                return " " + k + "=\"" + $_.utils.escapeXmlAttribute(map[k])
                    + "\"";
              });
        }
        if (this.children && this.children.length) {
          s += ">";
          for ( var i = 0; i < this.children.length; i++) {
            s += this.children[i].toString();
          }
          s += "</" + this.name + ">";
        } else {
          s += " />";
        }
        return s;
      }
    });
    /** /XmlNode */
    function TableView(data, format, columnNames,customizeTable) {
      $_.utils.assert(this instanceof TableView, true,
          "please use 'new', when calling this function");
      this.toHtml = function() {
        var table = new XmlNode("table");
        var thead = table.child("thead");
        if(!columnNames) columnNames=data.header().map(function(col){return col.name;});
        thead.child("tr").child($_.utils.repeat(columnNames.length, "th"))
            .forEach(function(th, i) {
              th.addText(columnNames[i]);
            });
        var columns = data.header();
        var tbody = table.child("tbody");
        for ( var rowIdx = 0; rowIdx < data.rowCount(); rowIdx++) {
          var tr = tbody.child("tr");
          var rowData = data.row(rowIdx);
          for ( var colIdx = 0; colIdx < columnNames.length; colIdx++) {
            var td = tr.child("td");
            var colName = columnNames[colIdx];
            var fv = !$_.utils.isFunction(format) ? rowData[colName] : format(rowData[colName],columns.hash[colName],colIdx,rowData);
            if(fv instanceof XmlNode ){
              td.addChildNode(fv);
            }else if( $_.utils.isString(fv)){
              td.addText(fv);
            }else{
              td.addText($_.utils.ensureString(fv));
            }
          }
        }
        if( customizeTable ) customizeTable(table);
        return table.toString();
      };
      return this;
    }
    
    function Buffer(s,listenres) {
      this.s = s ? s : "";
      this.broadCastTo = listenres ? listenres : [] ;
      this.append = function(toAdd){
        this.s += toAdd;
        $_.utils.brodcastCall(this.broadCastTo, 'append', arguments ); 
      };
      this.done =  function(){
        $_.utils.brodcastCall(this.broadCastTo, 'done', arguments ); 
      };
    } 
    
    
    //Renderer: #render(params)
    function Wiki(s){
      var buildReplaceFunction = function(minLength,render){
        return function (m,g1,t,g2){
          var i;
          var len = Math.min(minLength,Math.min(g1.length,g2.length));
          if( len  < g1.length ){
            i = g1.length-len;
            t = g1.substring(0,i) + t;
            g1 = g1.substring(i);
          }
          if( len  < g2.length ){
            i = g2.length-len;
            t = t + g2.substring(0,i);
            g2 = g2.substring(i);
          }
          return render(len, g1, t, g2);
        };
      };
      this.text = s;
      this.render = function(){
        var initialCleanup=this.text
        .replace(/[\r\t ]+\n/g , "\n" )
//        <strike> strike text </strike>                       
//        empty line - paragraph                               
//        <math>\sum.{n=0}\infty\frac{x^n}{n!}</math>          
        .replace(/<strike>(.+?)<\/strike>/g, "<del>$1</del>")
        .replace(/<math>(.+?)<\/math>/g, "$$$$$$ $1 $$$$$$")
        .replace(/(\n)(\n)/g, "$1</p><p>$2")
//        Horizontal rule: 
//          ----                                               
        .replace(/(\n)----(\s*\n)/g, "$1<hr>$2")
// Take care of cases:
//        ��italic��
//        ���bold���
//        ����italic bold����
        .replace(/(''+)([^'\n]+)(''+)/g, buildReplaceFunction(4,  function (len,g1,t,g2){
          var r = new XmlNode(len === 2 ? "i" : "b");
          if (len === 4){
            r.child("i").addText(t) ;
          } else {
            r.addText(t);
          }
          return r.toString();
        }))
//        Headings:
//== Level 2 ==
//=== Level 3 ===
//==== Level 4 ====
//===== Level 5 =====
//====== Level 6 ======
        .replace(/(==+) ([^\n\r]+) (==+)/g, buildReplaceFunction(6, function (len,g1,t,g2){
          return new XmlNode("h"+len).addText(t).toString();
        } ));
        // per line procesing
        var lines = initialCleanup.split(/\n/);
//      Lists:
//      * itemized list
//      ** second level
//      *** third level
//      # numbered list
//      ## second level
//      ### third level
//      ; DNA: Deoxyribonucleic acid 
//      ;; rDNA: Ribosomal DNA
//      : colon indents line 
//      :: more indented line
        var c =  {
            BULLETED:   { 
              ch: "*", 
              buildList: function(){
                return new XmlNode("ul");
              },
              addItem: function(node,text){
                node.addChildNode(new XmlNode("li").addText(text)) ;
              }
            },
            NUMBERED:   { 
              ch: "#",
              buildList: function(){
                return new XmlNode("ol");
              },
              addItem: function(node,text){
                node.addChildNode(new XmlNode("li").addText(text)) ;
              }
            },
            DEFINITION: { 
              ch: ";",
              buildList: function(){
                return new XmlNode("dl");
              },
              addItem: function(node,text){
                var re = /^([^:]+):(.*)/;
                var m=re.exec(text);
                node.addChildNode(new XmlNode("dt").addText(m[1])) ;
                node.addChildNode(new XmlNode("dd").addText(m[2])) ;
              }
            },
           INDENT:     { 
              ch: ":",
              buildList: function(){
                return new XmlNode("ul").attr("style","list-style-type: none;");
              },
              addItem: function(node,text){
                node.addChildNode(new XmlNode("li").addText(text)) ;
              }
            }, 
        };
        var result = "";
        var current = null;
        
        //detect list in current line
        function detect(line,type){
          var level = $_.utils.detectRepeatingChar(line,type.ch);
          if(level>0){
            if(current === null){
              current = { type: type, levels: [] };
            }
            var text = line.substring(level);
            if( current.levels.length > level ){  // decending like:
                                                  // ** previous line
                                                  // * this line
              current.levels = current.levels.splice(0, level);
            }else{
              // ascending like:
              // * previous line
              // ** this line
              
              while(current.levels.length < level ){
                var newLevel = type.buildList();
                // taking car of case when it is assending and  jump level:
                // * a
                // *** k
                if( current.levels.length + 1 < level){
                  type.addItem( newLevel ," ");
                }
                if(current.levels.length>0){
                  var last = current.levels[current.levels.length - 1];
                  last.children[last.children.length-1].addChildNode(newLevel);
                }
                current.levels.push(newLevel);
              }
            }
            type.addItem( current.levels[current.levels.length - 1],text);
            return true;
          }
          return false;
        }
        for ( var i = 0; i < lines.length; i++) {
          var l = lines[i];
          var detectList = detect(l,c.BULLETED) || detect(l, c.NUMBERED) || detect(l, c.DEFINITION) || detect(l, c.INDENT);
          if( detectList ){
            continue;
          }else{
            if(current != null ){
              result += "\n" + current.levels[0].toString();
              current = null;
            }
          }
          if(i !== 0 ) result += "\n";
          result += l;
        }
        if(current!==null){
          result += "\n" + current.levels[0].toString();
        }
        return result;
      };
    }
    
    function Sliki(text){
      $_.utils.assert(this instanceof Sliki, true,
      "please use 'new', when calling this function");
//      var t = $_.utils.Tokenizer('{}');
//      var parsed = [];
//      var v = t.nextValue();
      this.requiredParams = function(){return [];}
      this.render = function(params){return "<p>" + (new Wiki(text).render(params)) ;}
    }

    // d3 related stuff
    function TCell(d, varName, colspan, format){
      return {
        colspan: colspan || 1,
        content: function(){
          return !varName ? '' : format ? format(d[varName],d) : d[varName]; 
        }
      };
    }

    
    return $_.utils.convertFunctionsToObject([ Slinck, Path, Graph, Table, Column,
        Type, ColumnRole, Index, XmlNode, TableView, Sliki, TCell ]);
  })());

})();