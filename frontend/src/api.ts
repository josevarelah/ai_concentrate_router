/**
 * API client for the AI Router backend.
 * 
 *Communicate with the FastAPI backend.
 */

import type { ChatRequest, ChatResponse, ErrorResponse } from "./types";

/**
 * Configuration for the API client.
 */
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Custom error class for API failures.
 */
export class ApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/**
 * Send a chat request to the backend.
 * 
 * @param request - User's prompt and preference
 * @returns Promise with AI response and routing details
 * @throws ApiError if request fails
 */
export async function sendChatRequest(
  request: ChatRequest
): Promise<ChatResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    });

    // Handle non-2xx responses
    if (!response.ok) {
      const errorData: ErrorResponse = await response.json();
      throw new ApiError(
        response.status,
        errorData.detail || `HTTP ${response.status}: ${response.statusText}`
      );
    }

    // Parse successful response
    const data: ChatResponse = await response.json();
    return data;
  } catch (error) {
    // Re-throw ApiError as-is
    if (error instanceof ApiError) {
      throw error;
    }

    // Network errors (CORS, connection refused, etc.)
    if (error instanceof TypeError) {
      throw new ApiError(
        0,
        `Network error: Cannot reach backend at ${API_BASE_URL}. ` +
          `Is the FastAPI server running?`
      );
    }

    // Unknown errors
    throw new ApiError(
      500,
      error instanceof Error ? error.message : "Unknown error occurred"
    );
  }
}

/**
 * Health check endpoint.
 * Useful for verifying backend connectivity.
 */
export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch {
    return false;
  }
}
