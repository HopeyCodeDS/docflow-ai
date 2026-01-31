import { useState, useEffect } from 'react';

/**
 * Returns a value that updates only after the input has been stable for `delayMs`.
 * Useful for search inputs to avoid excessive API calls.
 */
export function useDebouncedValue<T>(value: T, delayMs: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setDebouncedValue(value);
    }, delayMs);
    return () => window.clearTimeout(timer);
  }, [value, delayMs]);

  return debouncedValue;
}
