import { create } from "zustand";
import type { Source } from "@/lib/api";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
};

type ChatState = {
  messages: Message[];
  previousResponseId: string | null;
  addMessage: (message: Message) => void;
  setPreviousResponseId: (id: string | null) => void;
  resetChat: () => void;
};

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  previousResponseId: null,
  addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
  setPreviousResponseId: (id) => set({ previousResponseId: id }),
  resetChat: () => set({ messages: [], previousResponseId: null }),
}));
