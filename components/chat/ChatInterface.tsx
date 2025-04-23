"use client";

import React from "react";
import { useState, useRef, useEffect } from "react";
import { Send, Loader2 } from "lucide-react";
import { Button } from "../ui/button";
import { Textarea } from "../ui/textarea";
import { ChatMessage } from "./ChatMessage";
import { useLoading } from "../../lib/hooks/useLoading";

interface Message {
  id: string;
  content: string;
  role: "user" | "assistant";
  timestamp: Date;
}

interface ChatInterfaceProps {
  onSendMessage: (message: string) => Promise<void>;
  initialMessages?: Message[];
}

export function ChatInterface({
  onSendMessage,
  initialMessages = [],
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [inputValue, setInputValue] = useState("");
  const { isLoading, withLoading } = useLoading();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    if (typeof window !== 'undefined' && messagesEndRef.current?.scrollIntoView) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async () => {
    if (!inputValue.trim()) return;

    await withLoading(onSendMessage(inputValue));
    setInputValue("");
  };

  return (
    <div className="flex h-[600px] flex-col rounded-lg border">
      <div className="flex-1 overflow-y-auto p-4">
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}
        <div ref={messagesEndRef} />
      </div>
      <div className="border-t p-4">
        <div className="flex gap-2">
          <Textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type your message..."
            className="min-h-[60px] resize-none"
          />
          <Button
            onClick={handleSubmit}
            disabled={!inputValue.trim() || isLoading}
            className="h-[60px] w-[60px]"
            aria-label="Send message"
          >
            {isLoading ? (
              <Loader2 className="animate-spin" data-testid="loading-spinner" />
            ) : (
              <Send className="h-5 w-5" />
            )}
          </Button>
        </div>
      </div>
    </div>
  );
} 