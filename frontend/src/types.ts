/**
 * Type definitions matching the FastAPI backend.
 * 
 * These types ensure compile-time safety when calling the backend
 * and displaying results. They mirror the Pydantic models exactly.
 */

/**
 * User preferences for model selection.
 * Backend uses these to optimize routing decisions.
 */
export type UserPreference = "cost" | "quality" | "latency";

/**
 * Request payload sent to POST /chat
 */
export interface ChatRequest {
  prompt: string;
  preference: UserPreference;
}

/**
 * Response from POST /chat
 * 
 * Contains everything needed to display:
 * - The AI's response
 * - Which model was used
 * - Why that model was chosen
 */
export interface ChatResponse {
  response: string;
  model_used: string;
  routing_reason: string;
}

/**
 * Error response from backend
 */
export interface ErrorResponse {
  detail: string;
}

/**
 * UI state for the application
 */
export interface AppState {
  prompt: string;
  preference: UserPreference;
  isLoading: boolean;
  result: ChatResponse | null;
  error: string | null;
}
