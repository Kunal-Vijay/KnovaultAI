/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string
  readonly VITE_API_PROXY_TARGET?: string
  readonly VITE_DEMO_LOGIN_ENABLED?: string
  readonly VITE_ALLOW_REGISTRATION?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
