const webpack = require("webpack");
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
  configureWebpack: {
    plugins: [
      new webpack.DefinePlugin({
        __VUE_OPTIONS_API__: JSON.stringify(true),
        __VUE_PROD_DEVTOOLS__: JSON.stringify(false),
        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: JSON.stringify(false),
      }),
    ],
  },
};
