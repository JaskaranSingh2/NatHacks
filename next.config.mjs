const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  images: {
    unoptimized: true
  },
  experimental: {
    appDir: true,
    typedRoutes: true
  },
  webpack(config) {
    config.experiments = {
      ...(config.experiments ?? {}),
      asyncWebAssembly: true,
      layers: true
    };
    config.module.rules.push({
      test: /\.wasm$/,
      type: "asset/resource"
    });
    return config;
  }
};

export default nextConfig;
