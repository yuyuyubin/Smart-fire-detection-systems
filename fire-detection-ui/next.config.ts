const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api-proxy/:path*',
        destination: `${process.env.INTERNAL_API_BASE_URL}/:path*`,
      },
    ]
  },
  images: {
    domains: [process.env.IMAGE_DOMAIN],
  },
}

module.exports = nextConfig;
