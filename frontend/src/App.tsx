/**
 * Main application component.
 */

import { useState } from "react";
import { sendChatRequest } from "./api";
import type { AppState, UserPreference } from "./types";
import "./App.css";

function App() {
  // Application state - kept simple with useState
  const [state, setState] = useState<AppState>({
    prompt: "",
    preference: "quality",
    isLoading: false,
    result: null,
    error: null,
  });

  /**
   * Handle form submission.
   * Request flow:
   * 1. Validate input
   * 2. Set loading state
   * 3. Call backend
   * 4. Display result or error
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (!state.prompt.trim()) {
      setState((prev) => ({
        ...prev,
        error: "Please enter a prompt",
      }));
      return;
    }

    // Reset state and start loading
    setState((prev) => ({
      ...prev,
      isLoading: true,
      error: null,
      result: null,
    }));

    try {
      // Call backend API
      const result = await sendChatRequest({
        prompt: state.prompt,
        preference: state.preference,
      });

      // Success - display result
      setState((prev) => ({
        ...prev,
        isLoading: false,
        result,
      }));
    } catch (error) {
      // Error - display message
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : "An error occurred",
      }));
    }
  };

  /**
   * Update prompt text.
   */
  const handlePromptChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setState((prev) => ({
      ...prev,
      prompt: e.target.value,
      error: null,
    }));
  };

  /**
   * Update preference selection.
   */
  const handlePreferenceChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setState((prev) => ({
      ...prev,
      preference: e.target.value as UserPreference,
    }));
  };

  /**
   * Clear results and start over.
   */
  const handleReset = () => {
    setState({
      prompt: "",
      preference: "quality",
      isLoading: false,
      result: null,
      error: null,
    });
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <h1>AI Model Router</h1>
        <p className="subtitle">
          Intelligent routing to 50+ models via Concentrate API
        </p>
      </header>

      {/* Main content */}
      <main className="main">
        {/* Input Form */}
        <form onSubmit={handleSubmit} className="form">
          <div className="form-group">
            <label htmlFor="prompt">Your Prompt</label>
            <textarea
              id="prompt"
              value={state.prompt}
              onChange={handlePromptChange}
              placeholder="E.g., Write a Python function to sort a list..."
              rows={6}
              disabled={state.isLoading}
              className="textarea"
            />
          </div>

          <div className="form-group">
            <label htmlFor="preference">Routing Preference</label>
            <select
              id="preference"
              value={state.preference}
              onChange={handlePreferenceChange}
              disabled={state.isLoading}
              className="select"
            >
              <option value="cost">Cost - Minimize API costs</option>
              <option value="quality">Quality - Best output quality</option>
              <option value="latency">Latency - Fastest response</option>
            </select>
          </div>

          <div className="form-actions">
            <button
              type="submit"
              disabled={state.isLoading || !state.prompt.trim()}
              className="button button-primary"
            >
              {state.isLoading ? "Processing..." : "Send Request"}
            </button>

            {state.result && (
              <button
                type="button"
                onClick={handleReset}
                className="button button-secondary"
              >
                New Request
              </button>
            )}
          </div>
        </form>

        {/* Loading State */}
        {state.isLoading && (
          <div className="loading">
            <div className="spinner" />
            <p>Classifying prompt and routing to optimal model...</p>
          </div>
        )}

        {/* Error Display */}
        {state.error && (
          <div className="error-card">
            <h3>❌ Error</h3>
            <p>{state.error}</p>
            <details className="error-details">
              <summary>Troubleshooting</summary>
              <ul>
                <li>Ensure FastAPI backend is running on http://localhost:8000</li>
                <li>Check that CONCENTRATE_API_KEY is set in backend .env</li>
                <li>Verify you have credits in your Concentrate account</li>
              </ul>
            </details>
          </div>
        )}

        {/* Result Display */}
        {state.result && (
          <div className="result">
            {/* Primary Output - AI Response */}
            <section className="result-section result-response">
              <h2>Response</h2>
              <div className="response-content">{state.result.response}</div>
            </section>

            {/* Routing Metadata */}
            <section className="result-section result-metadata">
              <h3>Routing Details</h3>

              <div className="metadata-grid">
                {/* Model Used */}
                <div className="metadata-item">
                  <span className="metadata-label">Model Used</span>
                  <span className="metadata-value model-badge">
                    {state.result.model_used}
                  </span>
                </div>

                {/* Routing Explanation */}
                <div className="metadata-item metadata-full">
                  <span className="metadata-label">Why This Model?</span>
                  <p className="metadata-explanation">
                    {state.result.routing_reason}
                  </p>
                </div>
              </div>
            </section>

            {/* How It Works */}
            <details className="how-it-works">
              <summary>How did routing work?</summary>
              <ol>
                <li>
                  <strong>Classification:</strong> Backend analyzed your prompt
                  using a cheap model (gemini-2.5-flash) to determine task type
                  and complexity
                </li>
                <li>
                  <strong>Routing:</strong> Based on classification and your
                  preference ({state.preference}), backend selected{" "}
                  {state.result.model_used}
                </li>
                <li>
                  <strong>Completion:</strong> Your prompt was sent to{" "}
                  {state.result.model_used} via Concentrate's unified API
                </li>
              </ol>
            </details>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="footer">
        <p>
          Backend: FastAPI + Concentrate API |{" "}
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
          >
            API Docs
          </a>
        </p>
      </footer>
    </div>
  );
}

export default App;
