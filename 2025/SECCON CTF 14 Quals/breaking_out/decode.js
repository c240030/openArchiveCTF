const fs=require('fs');const zlib=require('zlib');
const specials=[0xe31329f4,0x9bcfbc46,0x03ffe057,0x9a1b1dca,0x66fa61da,0xf6f2f5c5,0x74074c6c,0xa37be577,0x58162ae2,0x02113426];
const rows=0xa,cols=0xa;
let acc1=0x13572468>>>0, acc2=0x24681357>>>0, acc3=((rows<<16)^cols)>>>0;
const rotl=(x,b)=>((x<<b)|(x>>> (32-b)))>>>0;
for(const v of specials){acc1=(acc1+v)>>>0;acc2=(acc2+rotl(v,7))>>>0;acc3=(acc3+((v^0x9e3779b9)>>>0))>>>0;}
const hex8=x=>x.toString(16).padStart(8,'0');
let key=hex8(acc1)+hex8(acc2)+hex8(acc3);
const txt=fs.readFileSync('game_deobfuscated.js','utf8');
const start=txt.indexOf('const _0x49f141 = [');
const end=txt.indexOf('];',start);
const arr=eval('['+txt.slice(start+'const _0x49f141 = ['.length,end)+']');
const alpha='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/=';
function pbk(str){let out='',bc=0,bs,buf,idx=0;while((buf=str.charAt(idx++))){buf=alpha.indexOf(buf);if(~buf){bs=bc%4?bs*64+buf:buf;if(bc++%4){out+=String.fromCharCode(0xff & bs >> (-2*bc & 6));}}}let res='';for(let i=0;i<out.length;i++)res+='%'+('00'+out.charCodeAt(i).toString(16)).slice(-2);return decodeURIComponent(res);}
function rotate(a){function a0(x){return pbk(a[x-0x1ac]);}(function(_0x49a966,_0x1b34ae){const _0x2e8b48=_0x49a966();while(true){try{const _0x536373=-parseInt(a0(0x1ea))/1*(parseInt(a0(0x286))/2)+-parseInt(a0(0x241))/3+parseInt(a0(0x1e6))/4*(-parseInt(a0(0x1d0))/5)+-parseInt(a0(0x1c7))/6+-parseInt(a0(0x257))/7+-parseInt(a0(0x27f))/8+parseInt(a0(0x1ff))/9*(parseInt(a0(0x1e7))/10);if(_0x536373===_0x1b34ae)break;else _0x2e8b48.push(_0x2e8b48.shift());}catch(_){_0x2e8b48.push(_0x2e8b48.shift());}}})(()=>a,0xf2bf5);} 
rotate(arr);
const decode=idx=>pbk(arr[idx-0x1ac]);
const nextStr=decode(0x1fc);
function rc4(k,d){let S=new Uint8Array(256);for(let i=0;i<256;i++)S[i]=i;let j=0;for(let i=0;i<256;i++){j=(j+S[i]+k.charCodeAt(i%k.length))&255;[S[i],S[j]]=[S[j],S[i]];}let i=0; j=0;let out=Buffer.alloc(d.length);for(let n=0;n<d.length;n++){i=(i+1)&255;j=(j+S[i])&255;[S[i],S[j]]=[S[j],S[i]];const rnd=S[(S[i]+S[j])&255];out[n]=d[n]^rnd;}return out;}

function calcKey(level){const specials=level.specials||[];const rows=level.rows||0,cols=level.cols||0;let a1=0x13572468>>>0,a2=0x24681357>>>0,a3=((rows<<16)^cols)>>>0;const rotl=(x,b)=>((x<<b)|(x>>> (32-b)))>>>0;for(const {value:v} of specials){a1=(a1+v)>>>0;a2=(a2+rotl(v,7))>>>0;a3=(a3+((v^0x9e3779b9)>>>0))>>>0;}return hex8(a1)+hex8(a2)+hex8(a3);} 

function decryptLevel(str, key){const data=Buffer.from(str,'base64');const rc=rc4(key,data);return zlib.gunzipSync(rc);} 

function showLevelInfo(idx, json){console.log(`Level ${idx}: rows=${json.rows} cols=${json.cols} specials=${json.specials?.length||0} nextLen=${json.next?json.next.length:0}`);}

let curStr=nextStr;let levelIdx=1;let curJson=null;
while(curStr){const buf=decryptLevel(curStr,key);curJson=JSON.parse(buf.toString());showLevelInfo(levelIdx,curJson);if(!curJson.next){break;}levelIdx++; if(levelIdx>120){console.log('Stopping at level cap');break;} // guard
const newKey=calcKey(curJson);curStr=curJson.next;key=newKey;}

console.log('Finished at level',levelIdx);
if(curJson){const out=JSON.stringify(curJson,null,2);fs.writeFileSync('level'+levelIdx+'.json',out);console.log('Saved last level to',`level${levelIdx}.json`);}
