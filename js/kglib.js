//------------------------------------------------------------------------------
//
//    This file is a part of alib.
//
//    Copyright 2011-2013 Andrew Lamoureux
//
//    alib is free software: you can redistribute it and/or modify
//    it under the terms of the GNU General Public License as published by
//    the Free Software Foundation, either version 3 of the License, or
//    (at your option) any later version.
//
//    This program is distributed in the hope that it will be useful,
//    but WITHOUT ANY WARRANTY; without even the implied warranty of
//    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//    GNU General Public License for more details.
//
//    You should have received a copy of the GNU General Public License
//    along with this program.  If not, see <http://www.gnu.org/licenses/>.
//
//------------------------------------------------------------------------------

// some of this stuff was found online - I tried to attribute everything
// contact me if improper credit was given

/******************************************************************************
 * globals
 *****************************************************************************/
// [0,3] from least to greatest
var g_DEBUG_LEVEL = 1;

function debug3(msg) {
    if(g_DEBUG_LEVEL >= 3) {
        console.log(msg);
    }
}

function debug2(msg) {
    if(g_DEBUG_LEVEL >= 2) {
        console.log(msg);
    }
}

function debug1(msg) {
    if(g_DEBUG_LEVEL >= 1) {
        console.log(msg);
    }
}

function debug0(msg) {
    console.log(msg);
}

function debug(msg) {
    console.log(msg);
}

/******************************************************************************
 * bit action
 *****************************************************************************/

// add within a register
function bitadd32(a, b) {
    return (a+b) & 0xFFFFFFFF;
}

// shifts
function bitshl32(a, n) {
    // js standard will shift by n&0x1F or (n%32) producing non-ordinary
    // results like (1<<32) == 1
    if(n >= 32) {
        return 0;
    }

    return (a<<n) & 0xFFFFFFFF;
}

function bitshr32(a, n) {
    return (a>>>n) & 0xFFFFFFFF;
}

// rotate left
function bitrol32(r, n) {
    n = n % regsize
    return (bitshl32(r,n) | (r>>(regsize-n))) & 0xFFFFFFFF;
}

// rotate right
function bitror32(r, n) {
    n = n % 32
    return ((r>>n) | (r<<(32-n))) & 0xFFFFFFFF;
}

/******************************************************************************
 * hex/binary conversions
 *****************************************************************************/
//
// hexadecimal representation of a number 
//   (note toString(16) is implementation-dependant, and  
//   in IE returns signed numbers when used on full words)
//
function toHexStr(n) {
    var s="", v;
    for (var i=7; i>=0; i--) { 
        v = (n>>>(i*4)) & 0xf; 
        s += v.toString(16); 
    }

    return s;
}

function toBinStr(n) {
    var s="";
    while (n) {
        s = (n & 1).toString() + s;
        n = n >>> 1;
    }

    return s;
}

/******************************************************************************
 * misc utilities
 *****************************************************************************/
function compareArrays(a,b) {
    if(a==b) {
        return true;
    }

    if(a.length != b.length) {
        return false;
    }

    for(var i=0; i<a.length; ++i) {
        if(a[i] != b[i]) {
            return false;
        }
    }

    return true;
}

/******************************************************************************
 * XTEA cipher
 *****************************************************************************/

// adapted from the code in the Wikipedia article (http://en.wikipedia.org/wiki/XTEA)
// example invocation: XTEA.encrypt_block([0x41424344, 0x45464748], [0x00010203, 0x04050607, 0x08090a0b, 0x0c0d0e0f])
var XTEA = {
    //
    // input:
    //     v: 2-array of [v0,v1] (each a 32-bit part of the 64-bit plaintext block)
    //   key: 4-array of subkeys (each a 32-bit part of the 128-bit key)
    //
    // output:
    //   ciphertext: a 2-array (each a 32-bit part of the 64-bit ciphertext block)
    //
    encrypt_block : function(v, key, num_rounds) {
        debug3("encrypt_block()");

        var num_rounds = (typeof num_rounds == 'undefined') ? 32 : num_rounds;
        var sum = 0;
        var delta = 0x9E3779B9;
    
        for(var i=0; i<num_rounds; ++i) {
            debug3("entering encrypt round=" + i
                    + " v=(" + toHexStr(v[0]) + ", " + toHexStr(v[1]) + ")"
                    + " sum=" + toHexStr(sum))
                    
            v[0] += (((v[1] << 4) ^ (v[1] >>> 5)) + v[1]) ^ (sum + key[sum & 3]);
            sum += delta;
            v[1] += (((v[0] << 4) ^ (v[0] >>> 5)) + v[0]) ^ (sum + key[(sum>>>11) & 3]);
        }
    
        // return unsigned 32-bit versions
        return [v[0]>>>0, v[1]>>>0];
    },
    
    //
    // input:
    //     v: 2-array of [v0,v1] (each a 32-bit part of the 64-bit plaintext block)
    //   key: 4-array of subkeys (each a 32-bit part of the 128-bit key)
    //
    // output:
    //   plaintext: a 2-array (each a 32-bit pa32rt of the 64-bit pl32aintext block)
    //
    decrypt_block : function(v, key, num_rounds) {
        debug3("decrypt_block()");

        var num_rounds = (typeof num_rounds == 'undefined') ? 32 : num_rounds;
        var delta = 0x9E3779B9;
        var sum = (delta*num_rounds) & 0xFFFFFFFF;
        
        for(var i=0; i<num_rounds; ++i) {
            debug3("entering decrypt round=" + i
                    + " v=(" + toHexStr(v[0]) + ", " + toHexStr(v[1]) + ")"
                    + " sum=" + toHexStr(sum))

            v[1] -= (((v[0] << 4) ^ (v[0] >>> 5)) + v[0]) ^ (sum + key[(sum>>>11) & 3]);
            sum -= delta;
            v[0] -= (((v[1] << 4) ^ (v[1] >>> 5)) + v[1]) ^ (sum + key[sum & 3]);
        }
    
        // return unsigned 32-bit versions
        return [v[0]>>>0, v[1]>>>0];
    },

    // output feedback mode
    // input:
    //  plaintext: an array of bytes
    // 
    // output:
    //  ciphertext: an array of bytes (integers in range [0,255])
    encrypt_ofb : function(plaintext, key, iv, num_rounds) {
        debug3("encrypt_ofb()");

        var iv = (typeof iv == 'undefined') ? [0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48] : iv;
        var num_rounds = (typeof num_rounds == 'undefined') ? 32 : num_rounds;
        var length = plaintext.length;
    
        // build stream at least as long as the plaintext
        var ct = iv;
        var stream = [];
        for(var i=0; i<((length + 7) / 8); i++) {
            ct = XTEA.encrypt_block(ct, key, num_rounds);
            stream = stream.concat(XTEA.splitDword(ct[0]));
            stream = stream.concat(XTEA.splitDword(ct[1]));
        }
      
        // print stream
        debug3("XTEA OFB stream: " + stream);    
 
        // xor each byte against the stream
        var ciphertext = [];
        for(var i=0; i<length; ++i) {
            ciphertext.push(plaintext[i] ^ stream[i]);
        }
    
        return ciphertext;
    },

    splitDword : function(x) {
        return([x>>>24, (x>>>16) & 0xFF, (x>>>8) & 0xFF, x & 0xFF]);
    },

    compareBlock : function(a, b) {
        debug3("compareBlock()");
        debug3("comparing a=[" + a[0] + ", " + a[1] + "]");
        debug3("comparing b=[" + b[0] + ", " + b[1] + "]");
        return a[0]==b[0] && a[1]==b[1];
    },

    test : function() {
        // these test vectors come from http://www.freemedialibrary.com/index.php/XTEA_test_vectors

        keys = [
            [0x00010203, 0x04050607, 0x08090a0b, 0x0c0d0e0f],
            [0x00010203, 0x04050607, 0x08090a0b, 0x0c0d0e0f],
            [0x00010203, 0x04050607, 0x08090a0b, 0x0c0d0e0f],
            [0x00000000, 0x00000000, 0x00000000, 0x00000000],
            [0x00000000, 0x00000000, 0x00000000, 0x00000000],
            [0x00000000, 0x00000000, 0x00000000, 0x00000000]
        ]

        plaintexts = [
            [0x41424344, 0x45464748],
            [0x41414141, 0x41414141],
            [0x5a5b6e27, 0x8948d77f],
            [0x41424344, 0x45464748],
            [0x41414141, 0x41414141],
            [0x70e1225d, 0x6e4e7655]
        ]

        ciphertexts = [
            [0x497df3d0, 0x72612cb5],
            [0xe78f2d13, 0x744341d8],
            [0x41414141, 0x41414141],
            [0xa0390589, 0xf8b8efa5],
            [0xed23375a, 0x821a8c2d],
            [0x41414141, 0x41414141]
        ]

        for(var i=0; i<keys.length; ++i) {
            key = keys[i]
            // IMPORTANT! make a copy of this array (else cipher will change it
            // in place via the reference)
            plain = plaintexts[i].slice(0)

            debug0("----test round=" + (i+1) + "/" + keys.length);
            debug0("plain: " + toHexStr(plain[0]) + " " + toHexStr(plain[1]));
            debug0("  key: " + toHexStr(key[0]) + " " + toHexStr(key[1]) + " " + toHexStr(key[2]) + " " + toHexStr(key[3]));

            debug0("encryption test!");
            cipher = XTEA.encrypt_block(plain, key);
            debug0("ciphertext: " + toHexStr(cipher[0]) + " " + toHexStr(cipher[1]));
            if(XTEA.compareBlock(cipher, ciphertexts[i])) {
                debug0("PASS");
            } else {
                throw("FAIL");
            }

            debug0("decryption test!");
            plain = XTEA.decrypt_block(cipher, key);
            debug0("plaintext: " + toHexStr(plain[0]) + " " + toHexStr(plain[1]));
            if(XTEA.compareBlock(plain, plaintexts[i])) {
                debug0("PASS");
            } else {
                throw("FAIL");
            }
        }

        debug0("ofb test!");
        var input = stringToBytes("The quick brown fox jumps over the lazy dog");
        debug0("plaintext: " + input);
        var ct = XTEA.encrypt_ofb(input.slice(0), keys[0]) 
        if(compareArrays(ct, input)) {
            throw("FAIL - did encryption do anything?");
        }
        debug0("ciphertext: " + ct);
        if(compareArrays(input, XTEA.encrypt_ofb(ct, keys[0]))) {
            debug0("PASS");
        }
        else {
            debug0("FAIL");
        }
    }
}

var Sha1 = {
    /* - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  */
    /*  SHA-1 implementation in JavaScript | (c) Chris Veness 2002-2010 | www.movable-type.co.uk      */
    /*   - see http://csrc.nist.gov/groups/ST/toolkit/secure_hashing.html                             */
    /*         http://csrc.nist.gov/groups/ST/toolkit/examples.html                                   */
    /* - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  */

    // MOD: input an array of bytes ([0,255] integers)
    // MOD: output an array of bytes
    hash : function(msg) {
      debug3("Sha1.hash(" + msg + ")");

      // constants [§4.2.1]
      var K = [0x5a827999, 0x6ed9eba1, 0x8f1bbcdc, 0xca62c1d6];
      
      // PREPROCESSING 
      
      msg.push(0x80);  // add trailing '1' bit (+ 0's padding) to string [§5.1.1]
      
      // convert string msg into 512-bit/16-integer blocks arrays of ints [§5.2.1]
      var l = msg.length/4 + 2;  // length (in 32-bit integers) of msg + ‘1’ + appended length
      var N = Math.ceil(l/16);   // number of 16-integer-blocks required to hold 'l' ints
      var M = new Array(N);
      
      for (var i=0; i<N; i++) {
        M[i] = new Array(16);
        for (var j=0; j<16; j++) {  // encode 4 chars per integer, big-endian encoding
          M[i][j] = (msg[i*64+j*4]<<24) | (msg[i*64+j*4+1]<<16) | 
            (msg[i*64+j*4+2]<<8) | (msg[i*64+j*4+3]);
        } // note running off the end of msg is ok 'cos bitwise ops on NaN return 0
      }
      // add length (in bits) into final pair of 32-bit integers (big-endian) [§5.1.1]
      // note: most significant word would be (len-1)*8 >>> 32, but since JS converts
      // bitwise-op args to 32 bits, we need to simulate this by arithmetic operators
      M[N-1][14] = ((msg.length-1)*8) / Math.pow(2, 32); M[N-1][14] = Math.floor(M[N-1][14])
      M[N-1][15] = ((msg.length-1)*8) & 0xffffffff;
      
      // set initial hash value [§5.3.1]
      var H0 = 0x67452301;
      var H1 = 0xefcdab89;
      var H2 = 0x98badcfe;
      var H3 = 0x10325476;
      var H4 = 0xc3d2e1f0;
      
      // HASH COMPUTATION [§6.1.2]
      
      var W = new Array(80); var a, b, c, d, e;
      for (var i=0; i<N; i++) {
      
        // 1 - prepare message schedule 'W'
        for (var t=0;  t<16; t++) W[t] = M[i][t];
        for (var t=16; t<80; t++) W[t] = Sha1.ROTL(W[t-3] ^ W[t-8] ^ W[t-14] ^ W[t-16], 1);
        
        // 2 - initialise five working variables a, b, c, d, e with previous hash value
        a = H0; b = H1; c = H2; d = H3; e = H4;
        
        // 3 - main loop
        for (var t=0; t<80; t++) {
          var s = Math.floor(t/20); // seq for blocks of 'f' functions and 'K' constants
          var T = (Sha1.ROTL(a,5) + Sha1.f(s,b,c,d) + e + K[s] + W[t]) & 0xffffffff;
          e = d;
          d = c;
          c = Sha1.ROTL(b, 30);
          b = a;
          a = T;
        }
        
        // 4 - compute the new intermediate hash value
        H0 = (H0+a) & 0xffffffff;  // note 'addition modulo 2^32'
        H1 = (H1+b) & 0xffffffff; 
        H2 = (H2+c) & 0xffffffff; 
        H3 = (H3+d) & 0xffffffff; 
        H4 = (H4+e) & 0xffffffff;
      }
   
      return [
        H0>>>24, (H0>>>16) & 0xFF, (H0>>>8) & 0xFF, H0 & 0xFF,
        H1>>>24, (H1>>>16) & 0xFF, (H1>>>8) & 0xFF, H1 & 0xFF,
        H2>>>24, (H2>>>16) & 0xFF, (H2>>>8) & 0xFF, H2 & 0xFF,
        H3>>>24, (H3>>>16) & 0xFF, (H3>>>8) & 0xFF, H3 & 0xFF,
        H4>>>24, (H4>>>16) & 0xFF, (H4>>>8) & 0xFF, H4 & 0xFF
      ];

    },
 
    //
    // function 'f' [§4.1.1]
    //
    f : function(s, x, y, z)  {
      switch (s) {
        case 0: return (x & y) ^ (~x & z);           // Ch()
        case 1: return x ^ y ^ z;                    // Parity()
        case 2: return (x & y) ^ (x & z) ^ (y & z);  // Maj()
        case 3: return x ^ y ^ z;                    // Parity()
      }
    },
    
    //
    // rotate left (circular left shift) value x by n positions [§3.2.5]
    //
    ROTL : function(x, n) {
      return (x<<n) | (x>>>(32-n));
    },

    hashToString : function(h) {
        var lookup = "0123456789ABCDEF";
        var r = "";
        for(var i=0; i<20; ++i) {
            r += lookup[h[i] >> 4];
            r += lookup[h[i] & 0xF];
        }
    
        return r;
    },

    // MOD: add test
    test : function() {
        // got these test vectors from Wikipedia of course http://en.wikipedia.org/wiki/SHA-1
        var inputs = ["The quick brown fox jumps over the lazy dog",
                 "The quick brown fox jumps over the lazy cog",
                 ""];

        var checks = ["2FD4E1C67A2D28FCED849EE1BB76E7391B93EB12",
                    "DE9F2C7FD25E1B3AFAD3E85A0BD17D9B100DB4B3",
                    "DA39A3EE5E6B4B0D3255BFEF95601890AFD80709"];

        for(var i=0; i<inputs.length; ++i) {
            console.log("Sha1 test " + (i+1) + "/" + inputs.length);
            hash = Sha1.hash(stringToBytes(inputs[i]));

            if(Sha1.hashToString(hash) == checks[i]) {
                console.log("PASS");
            } else {
                throw("FAIL");
            }
        }
    } 
}

/******************************************************************************
 * UTF8 decoding/encoding
 *****************************************************************************/
// got it somewhere, quick google result shows code here also: 
// http://www.webtoolkit.info/javascript-utf8.html

// keycode c
// [0, 128)     - to one byte (remains the same)
// [128, 2048)  - to two bytes
// [2049, ...)  - to three bytes

function encodeUtf8(string) {
    string = string.replace(/\r\n/g,"\n");
    var utftext = "";

    for (var n = 0; n < string.length; n++) {

        var c = string.charCodeAt(n);

        if (c < 128) {
            utftext += String.fromCharCode(c);
        }
        else if((c > 127) && (c < 2048)) {
            utftext += String.fromCharCode((c >> 6) | 192);
            utftext += String.fromCharCode((c & 63) | 128);
        }
        else {
            utftext += String.fromCharCode((c >> 12) | 224);
            utftext += String.fromCharCode(((c >> 6) & 63) | 128);
            utftext += String.fromCharCode((c & 63) | 128);
        }

    }

    return utftext;
}
 
function decodeUtf8(utftext) { 
    var string = "";
    var i = 0;
    var c = 0, c1 = 0, c2 = 0;

    while ( i < utftext.length ) {

        c = utftext.charCodeAt(i);

        if (c < 128) {
            string += String.fromCharCode(c);
            i++;
        }
        else if((c > 191) && (c < 224)) {
            c1 = utftext.charCodeAt(i+1);
            string += String.fromCharCode(((c & 31) << 6) | (c1 & 63));
            i += 2;
        }
        else {
            c1 = utftext.charCodeAt(i+1);
            c2 = utftext.charCodeAt(i+2);
            string += String.fromCharCode(((c & 15) << 12) | ((c1 & 63) << 6) | (c2 & 63));
            i += 3;
        }

    }

    return string;
}

/******************************************************************************
 * Base64 decoding/encoding
 *****************************************************************************/

// input:
//   array of bytes ([0,255] integers)
// output:
//   js string encoding the bytes
//
function encodeBase64(input) {
    var keyStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
    var output = "";
    var chr1, chr2, chr3, enc1, enc2, enc3, enc4;
    var i = 0;

    while (i < input.length) {
        chr1 = input[i++];
        chr2 = input[i++];
        chr3 = input[i++];

        enc1 = chr1 >> 2;
        enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);
        enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);
        enc4 = chr3 & 63;

        if (isNaN(chr2)) {
            enc3 = enc4 = 64;
        } else if (isNaN(chr3)) {
            enc4 = 64;
        }

        output = output +
            keyStr.charAt(enc1) + keyStr.charAt(enc2) +
            keyStr.charAt(enc3) + keyStr.charAt(enc4);
    }

    return output;
}

// input:
//   js string encoding the bytes
// output:
//   array of bytes ([0,255] integers)
//
function decodeBase64(input) {
    var keyStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
    var output = [];
    var chr1, chr2, chr3;
    var enc1, enc2, enc3, enc4;
    var i = 0;

    // filter out anything that's not in the output
    input = input.replace(/[^A-Za-z0-9\+\/\=]/g, "");

    while (i < input.length) {
        enc1 = keyStr.indexOf(input.charAt(i++));
        enc2 = keyStr.indexOf(input.charAt(i++));
        enc3 = keyStr.indexOf(input.charAt(i++));
        enc4 = keyStr.indexOf(input.charAt(i++));

        chr1 = (enc1 << 2) | (enc2 >> 4);
        chr2 = ((enc2 & 15) << 4) | (enc3 >> 2);
        chr3 = ((enc3 & 3) << 6) | enc4;

        output.push(chr1);

        if (enc3 != 64) {
            output.push(chr2);
        }
        if (enc4 != 64) {
            output.push(chr3);
        }

    }

    return output;
}

/******************************************************************************
 * string <-> bytes conversion
 *****************************************************************************/
// primitive string can hold two integers to represent a larger code point
//
// primitive string can hold single integer of code point > 255
// 
// so the conversion chosen is to encode incoming string in UTF-8 (which may
// produce >1 byte for large points)
//
// eg: the Cyrillic asterisk is String.fromCharCode(1244)
//     via UTF-8 this becomes String.fromCharCode(211, 156)
//     so we get two 1-byte values
//
// blah blah so conversion is simple:
// - utf8 incoming string
// - each code point is a byte to an array

// input:
//   string
// output:
//   array of bytes ([0,255] integers)
function stringToBytes(str) {
    var t = encodeUtf8(str);
    var r = new Array(t.length);
    for(var i=0; i<t.length; ++i) {
        r[i] = t.charCodeAt(i);
    }
    return r;
}
  
// input:
//   array of bytes ([0,255] integers)
// output:
//   string 
function bytesToString(bytes) {
    var r = ""
    for(var i=0; i<bytes.length; ++i) {
        r = r + String.fromCharCode(bytes[i]);
    }
    r = decodeUtf8(r);
    return r;
}


