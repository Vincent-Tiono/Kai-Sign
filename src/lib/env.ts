/**
 * Safely gets an environment variable in both server and client contexts
 */
export function getEnvironmentVariable(key: string): string {
  // Server-side (Node.js)
  if (typeof window === 'undefined') {
    return process.env[key] || '';
  }
  
  // Client-side (browser)
  // Note: Next.js only exposes env vars prefixed with NEXT_PUBLIC_ to the client
  return process.env[`NEXT_PUBLIC_${key}`] || '';
} 