export type Video = {
  bruto: string
  etapa: string
  tamanho_mb: number
  padrao: string | null
}

export type PanelData = {
  marca: string | null
  setup: boolean
  padroes: string[]
  videos: Video[]
  lastRefresh: string | null
  refreshMsg: string | null
}

declare module 'claude-code' {
  interface PluginState {
    'video-editor-painel': { data: PanelData }
  }
}
