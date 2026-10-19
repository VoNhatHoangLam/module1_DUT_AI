/**
 * Base API Client xử lý các request HTTP tới Backend FastAPI.
 */

export class ApiError extends Error {
  status: number;
  data: any;

  constructor(message: string, status: number, data?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

const BASE_URL = '/api';

export async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${BASE_URL}${endpoint}`;
  const headers = new Headers(options.headers || {});

  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = `Lỗi hệ thống (${response.status})`;
    let errorData = null;
    try {
      errorData = await response.json();
      if (errorData && errorData.detail) {
        errorDetail = typeof errorData.detail === 'string'
          ? errorData.detail
          : JSON.stringify(errorData.detail);
      }
    } catch {
      // Bỏ qua lỗi parse JSON nếu body không phải JSON
    }
    throw new ApiError(errorDetail, response.status, errorData);
  }

  // Nếu response không có content (204)
  if (response.status === 204) {
    return {} as T;
  }

  return response.json() as Promise<T>;
}
