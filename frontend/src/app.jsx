import { useState } from "react";
import { askRAG } from "./api";

function App() {
  const [doc, setDoc] = useState("");
  const [q, setQ] = useState("");
  const [ans, setAns] = useState(null);
  const [loading, setLoading] = useState(false);

  const run = async () => {
    if (!doc.trim() || !q.trim()) {
      alert("Please enter both document text and a question");
      return;
    }
    setLoading(true);
    try {
      const data = await askRAG(doc, q);
      setAns(data);
    } catch (error) {
      console.error("Error:", error);
      setAns({ answer: "An error occurred. Please try again.", sources: [] });
    }
    setLoading(false);
  };

  return (
    <div className="app">
      <header className="header">
        <h1>✨ Mini RAG</h1>
        <p>Ask questions about your documents using AI</p>
      </header>

      <main className="main">
        <div className="input-section">
          <div className="card">
            <label>📄 Document Text</label>
            <textarea
              placeholder="Paste your document text here..."
              value={doc}
              onChange={(e) => setDoc(e.target.value)}
              rows={8}
            />
          </div>

          <div className="card">
            <label>❓ Question</label>
            <input
              type="text"
              placeholder="Ask a question about your document..."
              value={q}
              onChange={(e) => setQ(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && run()}
            />
          </div>

          <button className="ask-btn" onClick={run} disabled={loading}>
            {loading ? (
              <span className="loading">Thinking...</span>
            ) : (
              <span>🚀 Ask</span>
            )}
          </button>
        </div>

        {ans && (
          <div className="output-section">
            <div className="answer-card">
              <h2>💡 Answer</h2>
              <div className="answer-text">{ans.answer}</div>
              <div className="meta">⏱ {ans.time}s</div>
            </div>

            {ans.sources.length > 0 && (
              <div className="sources-card">
                <h3>📚 Sources</h3>
                {ans.sources.map((s, i) => (
                  <div key={i} className="source-item">
                    <span className="source-num">[{i + 1}]</span>
                    <span className="source-text">
                      {s.length > 300 ? s.slice(0, 300) + "..." : s}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>

      <footer className="footer">
        <p>Built with React + FastAPI + OpenAI + Cohere + Supabase</p>
      </footer>
    </div>
  );
}

export default App;

