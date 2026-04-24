/// <reference types="vite/client" />

interface ProviewDesktopActionResult {
  ok: boolean
  error?: string
  path?: string
}

interface ProviewDesktopBridge {
  isDesktop: boolean
  locateFile?: (filePath: string) => Promise<ProviewDesktopActionResult>
  openFile?: (filePath: string) => Promise<ProviewDesktopActionResult>
  getZoomFactor?: () => number
  setZoomFactor?: (factor: number) => number
}

interface Window {
  proviewDesktop?: ProviewDesktopBridge
}

declare module '*.vue' {
  import type { DefineComponent } from 'vue'

  const component: DefineComponent<Record<string, never>, Record<string, never>, any>
  export default component
}
