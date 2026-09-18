import type {
  RecommendationRequest,
  RecommendationResponse,
  ScholarshipRead,
} from '../types/api';

const RAW_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
)
  .trim()
  .replace(/\/+$/, '');

const API_BASE_URL = RAW_BASE_URL.endsWith('/api/v1')
  ? RAW_BASE_URL.slice(0, -7)
  : RAW_BASE_URL;

const REQUEST_TIMEOUT_MS = 15000;

export class ApiError extends Error {
  status: number;
  details?: unknown;

  constructor(message: string, status: number, details?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.details = details;
  }
}

/**
 * Format 422 validation errors into human-readable sentences
 * without exposing internal python / pydantic traces.
 */
function formatValidationErrors(detail: unknown): string {
  if (Array.isArray(detail)) {
    return detail
      .map((err) => {
        const rawField = Array.isArray(err.loc)
          ? err.loc.filter((part: unknown) => part !== 'body' && part !== 'student_profile').join('.')
          : 'field';
        const fieldName = rawField.replace(/_/g, ' ') || 'field';
        return `${fieldName}: ${err.msg}`;
      })
      .join('; ');
  }
  if (typeof detail === 'string') {
    return detail;
  }
  return 'The provided profile contains invalid or incompatible values.';
}

export async function fetchRecommendations(
  request: RecommendationRequest
): Promise<RecommendationResponse> {
  const url = `${API_BASE_URL}/api/v1/recommendations`;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  let response: Response;
  try {
    response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
      signal: controller.signal,
    });
  } catch (err: unknown) {
    clearTimeout(timeoutId);
    if (err instanceof Error && err.name === 'AbortError') {
      throw new ApiError(
        'The recommendation service request timed out after 15 seconds. Please try again.',
        408
      );
    }
    throw new ApiError(
      'ScholarMatch could not connect to the recommendation engine. Please verify the backend server is running.',
      0
    );
  } finally {
    clearTimeout(timeoutId);
  }

  if (!response.ok) {
    let errorData: { detail?: unknown } = {};
    try {
      errorData = await response.json();
    } catch {
      // Ignored if non-JSON response
    }

    if (response.status === 422) {
      const msg = formatValidationErrors(errorData.detail);
      throw new ApiError(`Profile Validation Error: ${msg}`, 422, errorData);
    }

    if (response.status >= 500) {
      throw new ApiError(
        'The recommendation service encountered an internal processing issue. Please try again.',
        response.status,
        errorData
      );
    }

    throw new ApiError(
      `Request failed with status ${response.status}: ${
        typeof errorData.detail === 'string'
          ? errorData.detail
          : 'Unexpected server response'
      }`,
      response.status,
      errorData
    );
  }

  return response.json();
}

export async function fetchScholarshipDetails(
  id: number
): Promise<ScholarshipRead> {
  const url = `${API_BASE_URL}/api/v1/scholarships/${id}`;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  let response: Response;
  try {
    response = await fetch(url, { signal: controller.signal });
  } catch (err: unknown) {
    clearTimeout(timeoutId);
    if (err instanceof Error && err.name === 'AbortError') {
      throw new ApiError('Request timed out when fetching scholarship details.', 408);
    }
    throw new ApiError(
      'Network error when fetching scholarship details. Please check your connection.',
      0
    );
  } finally {
    clearTimeout(timeoutId);
  }

  if (!response.ok) {
    throw new ApiError(
      `Failed to load scholarship details (HTTP ${response.status})`,
      response.status
    );
  }

  return response.json();
}
