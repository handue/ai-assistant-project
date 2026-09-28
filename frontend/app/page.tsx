import AskForm from "@/components/AskForm";
import DocumentUpload from "@/components/DocumentUpload";
import ChatMessages from "@/components/ChatMessages";

export default function Home() {
  return (
    <main className="min-h-screen flex items-center justify-center">
      <div className="w-full max-w-2xl p-8">
        <h1 className="text-3xl font-bold mb-2">
          AI Infrastructure Research Assistant
        </h1>

        <p className="text-gray-500 mb-8">
          Upload PDFs and ask questions with document sources.
        </p>
        <DocumentUpload />
        <AskForm />
        <ChatMessages />

      </div>
    </main>
  );
}
