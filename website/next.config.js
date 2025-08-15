/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
  assetPrefix: process.env.NODE_ENV === 'production' ? '/quantum-grand-challenges' : '',
  basePath: process.env.NODE_ENV === 'production' ? '/quantum-grand-challenges' : '',
}

module.exports = nextConfig
