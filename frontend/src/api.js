const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function askRAG(document, question) {
  const res = await fetch(`${API_URL}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ document, question })
  });
  return res.json();
}

