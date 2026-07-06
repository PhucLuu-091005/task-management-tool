/** @type {import('next').NextConfig} */
// Server-side proxy target. NEXT_PUBLIC_API_URL is the legacy name (kept as a
// fallback so existing tooling/E2E that sets it still points the proxy correctly).
const BACKEND =
  process.env.BACKEND_INTERNAL_URL ??
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000";

const nextConfig = {
  // Django's API routes all end in "/". Next strips the trailing slash when matching
  // rewrites, so re-add it on the way to the backend; otherwise Django's APPEND_SLASH
  // 500s the slash-less POST. skipTrailingSlashRedirect keeps page routes untouched.
  skipTrailingSlashRedirect: true,
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${BACKEND}/api/:path*/` }];
  },
};

export default nextConfig;
