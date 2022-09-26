import axios, { AxiosInstance } from 'axios'
import qs from 'qs'

import { useUserSession } from '/@src/stores/userSession'

let api: AxiosInstance

export function createApi() {
  // Here we set the base URL for all requests made to the api
  api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
  })

  api.defaults.paramsSerializer = (params) => {
    return qs.stringify(params, { indices: false });
  }

  // We set an interceptor for each request to
  // include Bearer token to the request if user is logged in
  api.interceptors.request.use((config) => {
    const userSession = useUserSession()

    if (userSession.isLoggedIn) {
      config.headers = {
        ...config.headers,
        Authorization: `Bearer ${userSession.token}`,
      }
    }

    return config
  })

  api.interceptors.response.use((response) => {
    // Any status code that lie within the range of 2xx cause this function to trigger
    // Do something with response data
    return response;
  }, async (error) => {
    // Any status codes that falls outside the range of 2xx cause this function to trigger
    // Do something with response error
    const { response = {}, message } = error;
    let { data = {}, status } = response;
    let fields = null;

    // errors when request blob
    if (data instanceof Blob && data.type === "application/json") {
      data = JSON.parse(await data.text())
    }

    if (status === 422 && Array.isArray(data?.detail)) {
      fields = data.detail.reduce(
        (
          acc: object,
          { loc = {} as (string | number)[], msg = "error" as string }
        ) => {
          const [body, ...field] = loc;

          // TODO: add translation for generic error messages
          return { ...acc, [field.join(".")]: msg };
        },
        {}
      );
    }
    return Promise.reject(status ? {error: {status, message, fields, ...data}} : (message || error));
  })

  return api
}

export function useApi() {
  if (!api) {
    createApi()
  }
  return api
}
