import AskForm from "@/components/AskForm";
import BackendStatus from "@/components/BackendStatus";

export default function Home() {
  return (
    <main className="min-h-screen flex items-center justify-center">
      <div className="w-full max-w-2xl p-8">
        <h1 className="text-3xl font-bold mb-2">
          AI Infrastructure Research Assistant
        </h1>

        <p className="text-gray-500 mb-8">
          Ask questions about AI infrastructure companies and documents.
        </p>
        {/* <BackendStatus /> */}
        <AskForm />

      </div>
    </main>
  );
}