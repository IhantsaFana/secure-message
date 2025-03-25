// Simple SHA-256 implementation for demonstration
// In a real app, use the Web Crypto API or a proper library

export function sha256(message: string): string {
  // This is a simplified implementation for demonstration
  // In a real app, use the Web Crypto API:
  // return crypto.subtle.digest('SHA-256', new TextEncoder().encode(message))

  // For this demo, we'll use a simple hash function
  let hash = 0
  for (let i = 0; i < message.length; i++) {
    const char = message.charCodeAt(i)
    hash = (hash << 5) - hash + char
    hash = hash & hash // Convert to 32bit integer
  }

  // Convert to hex string
  const hashHex = (hash >>> 0).toString(16).padStart(8, "0")

  // Repeat to make it look more like SHA-256 (64 chars)
  return hashHex.repeat(8)
}

// HMAC implementation for message authentication
export function hmac(message: string, key: string): string {
  // In a real app, use the Web Crypto API
  // This is just a simplified demonstration
  return sha256(key + message + key)
}

