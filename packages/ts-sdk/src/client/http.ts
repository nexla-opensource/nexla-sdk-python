export interface RetryOptions {
  maxRetries?: number;
  backoffMs?: number;
  maxBackoffMs?: number;
  retryOn?: number[];
}

const DEFAULT_RETRY_ON = [429, 502, 503, 504];

export const createFetchWithRetry = (baseFetch: typeof fetch, options: RetryOptions = {}): ((input: Request) => Promise<Response>) => {
  const maxRetries = options.maxRetries ?? 3;
  const backoffMs = options.backoffMs ?? 300;
  const maxBackoffMs = options.maxBackoffMs ?? 3000;
  const retryOn = options.retryOn ?? DEFAULT_RETRY_ON;

  return async (input: Request): Promise<Response> => {
    const original = input;

    let attempt = 0;
    while (true) {
      const request = original.clone();
      try {
        const response = await baseFetch(request);
        if (shouldRetryResponse(response.status, retryOn) && attempt < maxRetries) {
          const delay = computeRetryDelay(backoffMs, maxBackoffMs, attempt, response);
          await sleep(delay);
          attempt += 1;
          continue;
        }
        return response;
      } catch (error) {
        if (attempt >= maxRetries) throw error;
        const delay = computeRetryDelay(backoffMs, maxBackoffMs, attempt);
        await sleep(delay);
        attempt += 1;
      }
    }
  };
};

const shouldRetryResponse = (status: number, retryOn: number[]): boolean => {
  return retryOn.includes(status);
};

const computeRetryDelay = (base: number, max: number, attempt: number, response?: Response): number => {
  const retryAfter = response?.headers.get("retry-after");
  if (retryAfter) {
    const parsed = Number(retryAfter);
    if (!Number.isNaN(parsed)) {
      return Math.min(parsed * 1000, max);
    }
  }

  const jitter = Math.random() * 100;
  const delay = Math.min(base * 2 ** attempt + jitter, max);
  return delay;
};

const sleep = (ms: number): Promise<void> => new Promise((resolve) => setTimeout(resolve, ms));
