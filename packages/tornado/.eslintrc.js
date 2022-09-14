const baseConfig = require("../../.eslintrc.js");
module.exports = {
  extends: "../../.eslintrc.js",
  parserOptions: {
    // eslint-disable-next-line node/no-unsupported-features/es-syntax
    ...baseConfig.parserOptions,
    // eslint-disable-next-line node/no-path-concat
    project: [__dirname + "/tsconfig.json"],
  },
  rules: {},
  overrides: baseConfig.overrides,
};
