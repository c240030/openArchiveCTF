const key = 'sn0wwyygl0be1337';
const keyBytes = Buffer.from(key, 'utf8');

function decrypt(b64) {
    const buf = Buffer.from(b64, 'base64');
    const out = Buffer.alloc(buf.length);
    for (let i = 0; i < buf.length; i++) {
        out[i] = buf[i] ^ keyBytes[i % keyBytes.length];
    }
    return out.toString('utf8');
}

const encodedStrings = [
    "XQ9HBA==",
    "XQVFFRI=",
    "XR1DHw==",
    "XQteAQ==",
    "XR5UEQ==",
    "XQpfFA8=",
    "OzpyDDpNFQ4PWVIQQmw=",
    "JT1zKDIBDQICQ1NVXwY=",
    "LF9DKBlJDQ9dXgU6XwBESg==",
];

const decoded = encodedStrings.map(decrypt);
console.log("Decoded strings:");
decoded.forEach((s, i) => console.log(`${i}: ${s}`));

const flag = decoded.slice(6).join('');
console.log("\nPotential Flag:");
console.log(flag);
