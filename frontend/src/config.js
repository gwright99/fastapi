import runtimeEnv from '@mars/heroku-js-runtime-env';

const env = runtimeEnv();
const config = {
  // apiBasePath: env.REACT_APP_API_BASE_PATH || 'https://fastapi-recipe-app.herokuapp.com',
  apiBasePath: env.REACT_APP_API_BASE_PATH || 'http://localhost:8001',
  reactAppMode: process.env.REACT_APP_MODE || 'dev',
};

export default config;
