/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    env: {
        NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || '',
    },
    async rewrites() {
        // Determine API URL based on environment
        // Production: NEXT_PUBLIC_API_URL should be set to your production API URL
        // Local: Use localhost:8000 (default backend port)
        let apiUrl = process.env.NEXT_PUBLIC_API_URL;

        if (!apiUrl) {
            // Local development: default to port 8000
            // Override via NEXT_PUBLIC_BACKEND_PORT environment variable if needed
            const backendPort = process.env.NEXT_PUBLIC_BACKEND_PORT || '8000';
            apiUrl = `http://localhost:${backendPort}`;
        }

        return [
            {
                source: '/api/:path*',
                destination: `${apiUrl}/api/:path*`,
            },
            {
                source: '/output/:path*',
                destination: `${apiUrl}/output/:path*`,
            },
        ];
    },
}

module.exports = nextConfig