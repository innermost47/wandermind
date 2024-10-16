const path = require("path");

module.exports = {
  entry: "./src/index.js",
  output: {
    filename: "bundle.js",
    path: path.resolve(__dirname, "static/js"),
  },
  mode: "development",
  watch: true,
};
