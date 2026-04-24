const { contextBridge, ipcRenderer, webFrame } = require('electron')

function clampZoomFactor(factor) {
  const value = Number(factor)
  if (!Number.isFinite(value)) {
    return 1
  }
  return Math.min(1.15, Math.max(0.8, value))
}

contextBridge.exposeInMainWorld('proviewDesktop', {
  isDesktop: true,
  locateFile(filePath) {
    return ipcRenderer.invoke('proview:locate-file', filePath)
  },
  openFile(filePath) {
    return ipcRenderer.invoke('proview:open-file', filePath)
  },
  getZoomFactor() {
    return webFrame.getZoomFactor()
  },
  setZoomFactor(factor) {
    const nextFactor = clampZoomFactor(factor)
    webFrame.setZoomFactor(nextFactor)
    return nextFactor
  },
})
