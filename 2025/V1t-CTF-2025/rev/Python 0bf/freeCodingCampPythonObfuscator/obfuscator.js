const a0_0x5b3347 = a0_0x245f;
function a0_0x245f(_0x2a6aae, _0x36b0a8) {
    const _0x11cb6f = a0_0x5d16();
    return a0_0x245f = function(_0x118b91, _0x1bb84d) {
        _0x118b91 = _0x118b91 - 0x1c3;
        let _0x5d16cd = _0x11cb6f[_0x118b91];
        return _0x5d16cd;
    }
    ,
    a0_0x245f(_0x2a6aae, _0x36b0a8);
}
(function(_0x45297f, _0x5e2c22) {
    const _0x19cf9a = a0_0x245f
      , _0x44fca1 = _0x45297f();
    while (!![]) {
        try {
            const _0x17ee8d = -parseInt(_0x19cf9a(0x1d5)) / 0x1 + parseInt(_0x19cf9a(0x1c6)) / 0x2 + -parseInt(_0x19cf9a(0x1d3)) / 0x3 * (-parseInt(_0x19cf9a(0x1d7)) / 0x4) + -parseInt(_0x19cf9a(0x1c8)) / 0x5 * (-parseInt(_0x19cf9a(0x1e0)) / 0x6) + -parseInt(_0x19cf9a(0x1d8)) / 0x7 + parseInt(_0x19cf9a(0x1d6)) / 0x8 * (-parseInt(_0x19cf9a(0x1c7)) / 0x9) + parseInt(_0x19cf9a(0x1c9)) / 0xa;
            if (_0x17ee8d === _0x5e2c22)
                break;
            else
                _0x44fca1['push'](_0x44fca1['shift']());
        } catch (_0x2b33e3) {
            _0x44fca1['push'](_0x44fca1['shift']());
        }
    }
}(a0_0x5d16, 0x348d8));
import {httpPost} from '../api.js';
import*as a0_0x379b1c from '../ide.js';
function a0_0x5d16() {
    const _0x5821ad = ['addEventListener', 'constructor', 'actionBtn', 'writeText', 'clipboard', 'Too\x20many\x20requests.\x20Try\x20again\x20later.', 'An\x20unknown\x20error\x20occurred\x20while\x20compiling.\x20Refresh\x20the\x20page\x20or\x20try\x20again\x20later.', 'setStartImg', 'apply', '18QnXffM', 'statusCode', '299901Smxjox', '8LewswE', '153944syTCrd', '2544969mBhTZA', 'setStopImg', 'getInputText', 'setOutputText', 'search', 'getOutputText', 'result', 'refreshThemeSelection', '61236feiaKz', '(((.+)+)+)+$', 'copyOutputBtn', 'toString', 'getElementById', '856764gpRYhz', '1512486mFdTsQ', '135dGxURE', '1119180ezsEsE'];
    a0_0x5d16 = function() {
        return _0x5821ad;
    }
    ;
    return a0_0x5d16();
}
async function obfuscateCode() {
    const _0x324cc0 = a0_0x245f
      , _0xc11abc = (function() {
        let _0x138ac9 = !![];
        return function(_0x20b188, _0x1ac308) {
            const _0x1cc5e8 = _0x138ac9 ? function() {
                const _0x1c5e72 = a0_0x245f;
                if (_0x1ac308) {
                    const _0x659a02 = _0x1ac308[_0x1c5e72(0x1d2)](_0x20b188, arguments);
                    return _0x1ac308 = null,
                    _0x659a02;
                }
            }
            : function() {}
            ;
            return _0x138ac9 = ![],
            _0x1cc5e8;
        }
        ;
    }())
      , _0x36f9c7 = _0xc11abc(this, function() {
        const _0x14261e = a0_0x245f;
        return _0x36f9c7[_0x14261e(0x1c4)]()[_0x14261e(0x1dc)](_0x14261e(0x1e1))[_0x14261e(0x1c4)]()[_0x14261e(0x1cb)](_0x36f9c7)[_0x14261e(0x1dc)](_0x14261e(0x1e1));
    });
    _0x36f9c7(),
    a0_0x379b1c[_0x324cc0(0x1d9)]();
    try {
        const _0x452c18 = a0_0x379b1c[_0x324cc0(0x1da)]();
        a0_0x379b1c[_0x324cc0(0x1db)]('');
        const _0x10bdec = await httpPost('/api/v1/obfuscate', {
            'language': a0_0x379b1c['language'],
            'code': _0x452c18
        });
        a0_0x379b1c['setOutputText'](_0x10bdec[_0x324cc0(0x1de)]);
    } catch (_0x3521ff) {
        switch (_0x3521ff[_0x324cc0(0x1d4)]) {
        case 0x19d:
            a0_0x379b1c[_0x324cc0(0x1db)]('Content\x20is\x20too\x20large.\x20Please\x20decrease\x20your\x20code\x20to\x20a\x20reasonable\x20size.');
            break;
        case 0x1ad:
            a0_0x379b1c['setOutputText'](_0x324cc0(0x1cf));
            break;
        default:
            a0_0x379b1c[_0x324cc0(0x1db)](_0x324cc0(0x1d0));
            break;
        }
        throw _0x3521ff;
    }
    a0_0x379b1c[_0x324cc0(0x1d1)]();
}
document[a0_0x5b3347(0x1c5)](a0_0x5b3347(0x1cc))['addEventListener']('click', async function() {
    await obfuscateCode();
}),
document['getElementById'](a0_0x5b3347(0x1c3))[a0_0x5b3347(0x1ca)]('click', async function() {
    const _0x17bb03 = a0_0x5b3347;
    var _0x42300f = a0_0x379b1c[_0x17bb03(0x1dd)]();
    await navigator[_0x17bb03(0x1ce)][_0x17bb03(0x1cd)](_0x42300f);
}),
a0_0x379b1c['initializeEditor'](!![]),
a0_0x379b1c[a0_0x5b3347(0x1df)](),
obfuscateCode();
