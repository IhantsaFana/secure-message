"use client"

import { useEffect, useRef } from "react"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Lock } from "lucide-react"

interface Message {
  id: string
  sender: string
  content: string
  encrypted: string
  timestamp: Date
  isSelf: boolean
}

interface MessageListProps {
  messages: Message[]
  currentUser: string
}

export function MessageList({ messages, currentUser }: MessageListProps) {
  const scrollAreaRef = useRef<HTMLDivElement>(null)

  // Scroll to bottom when messages change
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector("[data-radix-scroll-area-viewport]")
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight
      }
    }
  }, [messages])

  return (
    <ScrollArea className="h-[400px] pr-4" ref={scrollAreaRef}>
      {messages.length === 0 ? (
        <div className="h-full flex flex-col items-center justify-center text-center p-4">
          <Lock className="h-12 w-12 text-muted-foreground mb-4 opacity-50" />
          <h3 className="text-lg font-medium">End-to-End Encrypted Chat</h3>
          <p className="text-sm text-muted-foreground mt-2 max-w-md">
            Messages are encrypted with AES before being sent. Only you and the recipient can read them.
          </p>
        </div>
      ) : (
        messages.map((message) => (
          <div key={message.id} className={`mb-4 ${message.isSelf ? "ml-auto max-w-[80%]" : "mr-auto max-w-[80%]"}`}>
            <div className={`flex flex-col ${message.isSelf ? "items-end" : "items-start"}`}>
              <div className="flex items-center gap-2 mb-1">
                {!message.isSelf && (
                  <Avatar className="h-6 w-6">
                    <AvatarFallback className="text-xs">{message.sender[0]}</AvatarFallback>
                  </Avatar>
                )}
                <span className="text-xs font-medium">{message.sender}</span>
                <span className="text-xs text-muted-foreground">{message.timestamp.toLocaleTimeString()}</span>
              </div>

              <div className={`rounded-lg p-3 ${message.isSelf ? "bg-primary text-primary-foreground" : "bg-muted"}`}>
                <p>{message.content}</p>
                <details className="mt-2">
                  <summary className="text-xs cursor-pointer">Show encrypted data</summary>
                  <p className="text-xs mt-1 font-mono break-all">{message.encrypted}</p>
                </details>
              </div>
            </div>
          </div>
        ))
      )}
    </ScrollArea>
  )
}

