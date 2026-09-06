/** @type {import('next').NextConfig} */

const isGithubPages = process.env.NEXT_PUBLIC_GITHUB_PAGES === 'true';
const repoName = 'hotel-price-comparator';

const nextConfig = {
  ...(isGithubPages
    ? {
        output: 'export',
        basePath: `/${repoName}`,
        assetPrefix: `/${repoName}/`,
      }
    : {
        async rewrites() {
          return [
            {
              source: '/api/:path*',
              destination: 'http://127.0.0.1:8000/api/:path*',
            },
          ];
        },
      }),
};

export default nextConfig;
