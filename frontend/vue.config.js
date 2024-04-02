module.exports = {
  chainWebpack: config => {
    config.plugin("html").tap(args => {
      args[0].title = "LenoreFin";
      return args;
    });
  },
  devServer: {
    proxy: {
      "/api": {
        target: "https://back-dev.danielleandjohn.love/api", // Change this to your backend API server
        changeOrigin: true,
        pathRewrite: { "^/api": "" },
      },
    },
    allowedHosts: ["front-dev.danielleandjohn.love"],
    https: true,
  },
};
