// API client for interacting with the Django backend

interface User {
  id: number
  username: string
  email: string
}

interface Message {
  id: number
  conversation: number
  sender: number
  sender_username: string
  encrypted_content: string
  encryption_mode: string
  iv: string
  hmac: string
  created_at: string
}

interface Conversation {
  id: number
  participants: User[]
  last_message: Message | null
  created_at: string
  updated_at: string
}

interface KeyExchange {
  id: number
  user: number
  username: string
  conversation: number
  public_key: string
  created_at: string
  is_active: boolean
}

// Base API URL - in a real app, this would be in an environment variable
const API_BASE_URL = "http://localhost:8000/api"

// Helper function for making authenticated API requests
async function apiRequest(endpoint: string, method = "GET", data: any = null, token: string | null = null) {
  const url = `${API_BASE_URL}${endpoint}`
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  }

  if (token) {
    headers["Authorization"] = `Bearer ${token}`
  }

  const options: RequestInit = {
    method,
    headers,
    credentials: "include", // Include cookies for session authentication
  }

  if (data && (method === "POST" || method === "PUT" || method === "PATCH")) {
    options.body = JSON.stringify(data)
  }

  const response = await fetch(url, options)

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || `API request failed with status ${response.status}`)
  }

  // For DELETE requests, we might not have a response body
  if (method === "DELETE") {
    return null
  }

  return await response.json()
}

// Authentication
export async function login(username: string, password: string) {
  return apiRequest("/auth/login/", "POST", { username, password })
}

export async function logout() {
  return apiRequest("/auth/logout/", "POST")
}

export async function register(username: string, email: string, password: string) {
  return apiRequest("/auth/register/", "POST", { username, email, password })
}

// Users
export async function getUsers() {
  return apiRequest("/users/")
}

// Conversations
export async function getConversations() {
  return apiRequest("/conversations/")
}

export async function getConversation(id: number) {
  return apiRequest(`/conversations/${id}/`)
}

export async function createConversation(participant_ids: number[]) {
  return apiRequest("/conversations/", "POST", { participant_ids })
}

export async function getConversationMessages(id: number) {
  return apiRequest(`/conversations/${id}/messages/`)
}

// Messages
export async function sendMessage(
  conversation_id: number,
  encrypted_content: string,
  encryption_mode: string,
  iv: string,
  hmac: string,
) {
  return apiRequest("/messages/", "POST", {
    conversation: conversation_id,
    encrypted_content,
    encryption_mode,
    iv,
    hmac,
  })
}

// Key Exchange
export async function getKeyExchanges(conversation_id: number) {
  return apiRequest(`/key-exchanges/?conversation=${conversation_id}`)
}

export async function createKeyExchange(conversation_id: number, public_key: string) {
  return apiRequest("/key-exchanges/", "POST", {
    conversation: conversation_id,
    public_key,
  })
}

