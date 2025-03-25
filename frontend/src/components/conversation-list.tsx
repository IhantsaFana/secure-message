"use client"

import { useState, useEffect } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Plus, Users } from "lucide-react"
import { getConversations } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"

interface User {
  id: number
  username: string
  email: string
}

interface Message {
  id: number
  sender_username: string
  encrypted_content: string
  created_at: string
}

interface Conversation {
  id: number
  participants: User[]
  last_message: Message | null
  created_at: string
  updated_at: string
}

interface ConversationListProps {
  onSelectConversation: (conversation: Conversation) => void
  onNewConversation: () => void
}

export function ConversationList({ onSelectConversation, onNewConversation }: ConversationListProps) {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const { toast } = useToast()

  useEffect(() => {
    const fetchConversations = async () => {
      try {
        const data = await getConversations()
        setConversations(data)
      } catch (error) {
        toast({
          title: "Error",
          description: "Failed to load conversations",
          variant: "destructive",
        })
      } finally {
        setIsLoading(false)
      }
    }

    fetchConversations()
  }, [toast])

  // Get other participants' names (excluding current user)
  const getParticipantNames = (participants: User[]): string => {
    // In a real app, you would filter out the current user
    return participants.map((p) => p.username).join(", ")
  }

  // Format the timestamp
  const formatTime = (timestamp: string): string => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
  }

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between p-4 border-b">
        <h2 className="text-lg font-semibold">Conversations</h2>
        <Button size="sm" onClick={onNewConversation}>
          <Plus className="h-4 w-4 mr-2" />
          New
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="p-4 text-center text-muted-foreground">Loading...</div>
        ) : conversations.length === 0 ? (
          <div className="p-4 text-center text-muted-foreground">
            <Users className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p>No conversations yet</p>
            <Button variant="link" className="mt-2" onClick={onNewConversation}>
              Start a new conversation
            </Button>
          </div>
        ) : (
          conversations.map((conversation) => (
            <Card
              key={conversation.id}
              className="m-2 cursor-pointer hover:bg-muted transition-colors"
              onClick={() => onSelectConversation(conversation)}
            >
              <CardContent className="p-3">
                <div className="flex items-center gap-3">
                  <Avatar>
                    <AvatarFallback>{getParticipantNames(conversation.participants)[0]}</AvatarFallback>
                  </Avatar>

                  <div className="flex-1 min-w-0">
                    <div className="flex justify-between items-baseline">
                      <h3 className="font-medium truncate">{getParticipantNames(conversation.participants)}</h3>
                      {conversation.last_message && (
                        <span className="text-xs text-muted-foreground">
                          {formatTime(conversation.last_message.created_at)}
                        </span>
                      )}
                    </div>

                    <p className="text-sm text-muted-foreground truncate">
                      {conversation.last_message ? (
                        <span>
                          <span className="font-medium">{conversation.last_message.sender_username}:</span> [Encrypted
                          message]
                        </span>
                      ) : (
                        "No messages yet"
                      )}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}

