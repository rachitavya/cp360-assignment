// Requires CryptoJS (https://cdnjs.cloudflare.com/ajax/libs/crypto-js/4.1.1/crypto-js.min.js)
// You can include it via CDN in your HTML if needed.

const AES_KEY = 'supersecretkey123456789012345678'; // Must match backend (32 chars)

function encryptAES(data) {
    const iv = CryptoJS.lib.WordArray.random(16);
    const key = CryptoJS.enc.Utf8.parse(AES_KEY);
    const message = typeof data === 'string' ? data : JSON.stringify(data);
    const encrypted = CryptoJS.AES.encrypt(message, key, {
        iv: iv,
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.Pkcs7
    });
    // Prepend IV to ciphertext, base64 encode
    const result = iv.concat(encrypted.ciphertext);
    return CryptoJS.enc.Base64.stringify(result);
}

function decryptAES(base64) {
    const raw = CryptoJS.enc.Base64.parse(base64);
    const iv = CryptoJS.lib.WordArray.create(raw.words.slice(0, 4));
    const ciphertext = CryptoJS.lib.WordArray.create(raw.words.slice(4));
    const key = CryptoJS.enc.Utf8.parse(AES_KEY);
    const decrypted = CryptoJS.AES.decrypt({ ciphertext: ciphertext }, key, {
        iv: iv,
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.Pkcs7
    });
    const result = decrypted.toString(CryptoJS.enc.Utf8);
    try {
        return JSON.parse(result);
    } catch {
        return result;
    }
} 