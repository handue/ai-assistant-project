"use client";

import { useChatStore } from "@/store/chatStore";

export default function ChatMessages() {
  const messages = useChatStore((state) => state.messages);

  if (messages.length === 0) {
    return null;
  }

  return (
    <div className="mt-8 space-y-4">
      {messages.map((message) => (
        <div
          key={message.id}
          className="border rounded-lg p-4"
        >
          <p className="font-semibold">
            {message.role === "user" ? "You" : "AI"}
          </p>

          <p>{message.content}</p>
        </div>
      ))}
    </div>
  );
}