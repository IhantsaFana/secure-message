// Cryptographic utilities for client-side encryption/decryption

// Convert string to ArrayBuffer
function str2ab(str: string): ArrayBuffer {
  const buf = new ArrayBuffer(str.length)
  const bufView = new Uint8Array(buf)
  for (let i = 0, strLen = str.length; i < strLen; i++) {
    bufView[i] = str.charCodeAt(i)
  }
  return buf
}

// Convert ArrayBuffer to string
function ab2str(buf: ArrayBuffer): string {
  return String.fromCharCode.apply(null, Array.from(new Uint8Array(buf)))
}

// Convert hex string to ArrayBuffer
function hexToArrayBuffer(hex: string): ArrayBuffer {
  const bytes = new Uint8Array(hex.length / 2)
  for (let i = 0; i < hex.length; i += 2) {
    bytes[i / 2] = Number.parseInt(hex.substring(i, i + 2), 16)
  }
  return bytes.buffer
}

// Convert ArrayBuffer to hex string
function arrayBufferToHex(buffer: ArrayBuffer): string {
  return Array.from(new Uint8Array(buffer))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("")
}

// Generate a random initialization vector
export function generateIV(): Uint8Array {
  return window.crypto.getRandomValues(new Uint8Array(16))
}

// Generate a random AES key
export async function generateAESKey(): Promise<CryptoKey> {
  return window.crypto.subtle.generateKey(
    {
      name: "AES-CBC",
      length: 256,
    },
    true,
    ["encrypt", "decrypt"],
  )
}

// Export a CryptoKey to raw format
export async function exportKey(key: CryptoKey): Promise<string> {
  const exported = await window.crypto.subtle.exportKey("raw", key)
  return arrayBufferToHex(exported)
}

// Import a raw key
export async function importKey(keyData: string, algorithm = "AES-CBC"): Promise<CryptoKey> {
  const keyBuffer = hexToArrayBuffer(keyData)
  return window.crypto.subtle.importKey("raw", keyBuffer, { name: algorithm }, false, ["encrypt", "decrypt"])
}

// Encrypt a message using AES
export async function encryptAES(
  message: string,
  key: CryptoKey | string,
  mode = "CBC",
  iv?: Uint8Array,
): Promise<{ ciphertext: string; iv: string }> {
  // If key is a string, import it
  let cryptoKey = key as CryptoKey
  if (typeof key === "string") {
    cryptoKey = await importKey(key, `AES-${mode}`)
  }

  // Generate IV if not provided
  if (!iv) {
    iv = generateIV()
  }

  // Prepare the algorithm parameters based on the mode
  let algorithm: any
  switch (mode) {
    case "CBC":
      algorithm = { name: "AES-CBC", iv }
      break
    case "CTR":
      algorithm = { name: "AES-CTR", counter: iv, length: 128 }
      break
    case "GCM":
      algorithm = { name: "AES-GCM", iv }
      break
    default:
      throw new Error(`Unsupported encryption mode: ${mode}`)
  }

  // Encrypt the message
  const encodedMessage = new TextEncoder().encode(message)
  const encryptedBuffer = await window.crypto.subtle.encrypt(algorithm, cryptoKey, encodedMessage)

  // Convert the encrypted data to a hex string
  const ciphertext = arrayBufferToHex(encryptedBuffer)
  const ivHex = arrayBufferToHex(iv.buffer)

  return { ciphertext, iv: ivHex }
}

// Decrypt a message using AES
export async function decryptAES(
  ciphertext: string,
  key: CryptoKey | string,
  mode = "CBC",
  ivHex: string,
): Promise<string> {
  // If key is a string, import it
  let cryptoKey = key as CryptoKey
  if (typeof key === "string") {
    cryptoKey = await importKey(key, `AES-${mode}`)
  }

  // Convert hex IV to Uint8Array
  const iv = new Uint8Array(hexToArrayBuffer(ivHex))

  // Prepare the algorithm parameters based on the mode
  let algorithm: any
  switch (mode) {
    case "CBC":
      algorithm = { name: "AES-CBC", iv }
      break
    case "CTR":
      algorithm = { name: "AES-CTR", counter: iv, length: 128 }
      break
    case "GCM":
      algorithm = { name: "AES-GCM", iv }
      break
    default:
      throw new Error(`Unsupported decryption mode: ${mode}`)
  }

  // Convert the ciphertext from hex to ArrayBuffer
  const encryptedBuffer = hexToArrayBuffer(ciphertext)

  // Decrypt the message
  const decryptedBuffer = await window.crypto.subtle.decrypt(algorithm, cryptoKey, encryptedBuffer)

  // Convert the decrypted data to a string
  return new TextDecoder().decode(decryptedBuffer)
}

// Generate an HMAC for message authentication
export async function generateHMAC(message: string, key: string): Promise<string> {
  // Import the key for HMAC
  const cryptoKey = await window.crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(key),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  )

  // Sign the message
  const signature = await window.crypto.subtle.sign("HMAC", cryptoKey, new TextEncoder().encode(message))

  // Convert the signature to a hex string
  return arrayBufferToHex(signature)
}

// Verify an HMAC
export async function verifyHMAC(message: string, key: string, hmac: string): Promise<boolean> {
  // Generate the HMAC for the message
  const calculatedHMAC = await generateHMAC(message, key)

  // Compare the calculated HMAC with the provided HMAC
  return calculatedHMAC === hmac
}

// Generate a key pair for Diffie-Hellman key exchange
export async function generateDHKeyPair(): Promise<CryptoKeyPair> {
  return window.crypto.subtle.generateKey(
    {
      name: "ECDH",
      namedCurve: "P-256",
    },
    true,
    ["deriveKey", "deriveBits"],
  )
}

// Export a public key for sharing
export async function exportPublicKey(keyPair: CryptoKeyPair): Promise<string> {
  const exported = await window.crypto.subtle.exportKey("spki", keyPair.publicKey)
  return arrayBufferToHex(exported)
}

// Import a public key
export async function importPublicKey(publicKeyData: string): Promise<CryptoKey> {
  const keyBuffer = hexToArrayBuffer(publicKeyData)
  return window.crypto.subtle.importKey(
    "spki",
    keyBuffer,
    {
      name: "ECDH",
      namedCurve: "P-256",
    },
    true,
    [],
  )
}

// Derive a shared secret using Diffie-Hellman
export async function deriveSharedSecret(privateKey: CryptoKey, publicKey: CryptoKey): Promise<CryptoKey> {
  // Derive bits from the key pair
  const derivedBits = await window.crypto.subtle.deriveBits(
    {
      name: "ECDH",
      public: publicKey,
    },
    privateKey,
    256,
  )

  // Use the derived bits to create an AES key
  return window.crypto.subtle.importKey("raw", derivedBits, { name: "AES-CBC" }, false, ["encrypt", "decrypt"])
}

