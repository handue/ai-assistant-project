import { create } from "zustand";

type Message = {
    id: string;
    role: "user" | "assistant";
    content: string;
};

type ChatState = {
    messages: Message[];
    previousResponseId: string | null;
    addMessage: (message: Message) => void;
    setPrviousResponseId: (id: string) => void;
};

export const useChatStore = create<ChatState>((set) => ({
    messages: [],
    previousResponseId: null,

    addMessage: (message) =>
        set((state) => ({
            messages: [...state.messages, message],

        })),
    setPrviousResponseId: (id) =>
        set((state) => ({
            previousResponseId: id,
        })),
}));