import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'
import type { PanelData, Video } from '../types'

const PANE = 'video-editor'
const panelData = atom(
  { plugin: 'video-editor-painel', key: 'data' } as const,
  { marca: null, setup: false, padroes: [], videos: [], lastRefresh: null, refreshMsg: null } as PanelData,
)

const ETAPA_ICON: Record<string, string> = {
  novo: '●',
  plano: '◐',
  storyboard: '◐',
  montagem: '◐',
  preview: '◎',
  entregue: '✓',
}

const ETAPA_LABEL: Record<string, string> = {
  novo: 'Novo',
  plano: 'Planejando cortes e estrutura',
  storyboard: 'Visualizando como vai ficar',
  montagem: 'Montando o video',
  preview: 'Pronto pra voce assistir',
  entregue: 'Entregue',
}

async function findProjectRoot($: any): Promise<string> {
  const cwd = await $.session.cwd()
  try {
    await $.fs.read(`${cwd}/registro.json`)
    return cwd
  } catch {}
  const knownNames = ['video-editor.nosync', 'video-editor']
  for (const name of knownNames) {
    try {
      await $.fs.read(`${cwd}/${name}/registro.json`)
      return `${cwd}/${name}`
    } catch {}
  }
  try {
    const entries = await $.fs.list(cwd)
    for (const entry of entries) {
      if (entry.type === 'directory' && entry.name.includes('video-editor')) {
        try {
          await $.fs.read(`${cwd}/${entry.name}/registro.json`)
          return `${cwd}/${entry.name}`
        } catch {}
      }
    }
  } catch {}
  return cwd
}

async function loadData($: any): Promise<PanelData> {
  const root = await findProjectRoot($)
  let marca: string | null = null
  let setup = false
  const padroes: string[] = []
  const videos: Video[] = []

  try {
    const marcasDir = await $.fs.list(`${root}/marcas`)
    for (const entry of marcasDir) {
      if (entry.type === 'directory') {
        try {
          await $.fs.read(`${root}/marcas/${entry.name}/marca.json`)
          if (!marca) marca = entry.name
        } catch {}
      }
    }
  } catch {}

  try {
    const padDir = await $.fs.list(`${root}/padroes`)
    for (const entry of padDir) {
      if (entry.type === 'directory') padroes.push(entry.name)
    }
  } catch {}

  try {
    await $.fs.read(`${root}/config/ambiente.json`)
    setup = true
  } catch {
    setup = padroes.length > 0
  }

  let lastRefresh: string | null = null
  let refreshMsg: string | null = null
  try {
    const reg = await $.fs.read(`${root}/registro.json`)
    const parsed = JSON.parse(reg)
    for (const v of parsed.videos || []) {
      videos.push({
        bruto: v.bruto,
        etapa: v.etapa || 'novo',
        tamanho_mb: Math.round((v.tamanho || 0) / 1e6 * 10) / 10,
        padrao: v.padrao || null,
      })
    }
    if (parsed._driveCheck) {
      lastRefresh = parsed._driveCheck.checked || null
      refreshMsg = parsed._driveCheck.message || null
    }
  } catch {}

  return { marca, setup, padroes, videos, lastRefresh, refreshMsg }
}

function send($: any, text: string) {
  void $.prompt.submit({ text, asUser: true })
}

function formatSize(mb: number): string {
  return mb >= 1000 ? `${(mb / 1000).toFixed(1)} GB` : `${Math.round(mb)} MB`
}

function formatMarca(slug: string): string {
  return slug.replace(/-/g, ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const data = await loadData($)
    await update($, panelData, () => data)

    await $.command.register({
      name: 'video-editor-painel',
      description: 'Abrir painel do editor de video',
    })
    void $.ui.open({ id: PANE, title: data.marca ? formatMarca(data.marca) : 'Editor de Video' })

    return next(e)
  })

  on('command.run', { command: 'video-editor-painel' }, async ($) => {
    const data = await loadData($)
    await update($, panelData, () => data)
    await $.ui.open({ id: PANE, title: data.marca ? formatMarca(data.marca) : 'Editor de Video' })
    return { text: 'Painel aberto.' }
  })

  on('tool.call', async ($, e, next) => {
    const result = await next(e)
    try {
      if ((e.tool === 'Write' || e.tool === 'Edit') && e.input) {
        const input = e.input as Record<string, unknown>
        const path = String(input.file_path || '')
        if (path.includes('registro.json') || path.includes('ambiente.json')) {
          const data = await loadData($)
          await update($, panelData, () => data)
        }
      }
    } catch {}
    return result
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text, Button, Input, Markdown } = $.ui.resolve(e)
    const data = await read($, panelData)
    const { marca, setup, videos, padroes, lastRefresh, refreshMsg } = data

    const novos = videos.filter(v => v.etapa === 'novo')
    const emAndamento = videos.filter(v => !['novo', 'entregue'].includes(v.etapa))
    const entregues = videos.filter(v => v.etapa === 'entregue')

    const marcaName = marca ? formatMarca(marca) : 'Editor de Video'
    const HR = '─'.repeat(40)

    const guideText = [
      '**Seu fluxo de trabalho:**',
      '',
      '1. Suba o video bruto na pasta **brutos/** do Drive',
      '2. Clique **Atualizar** pra ele aparecer aqui',
      '3. Escolha o estilo de edicao (padrao)',
      '4. Assista o resultado e peca ajustes',
      '5. Quando gostar, finalize e salve',
      '',
      '**Etapas da edicao (automaticas):**',
      '',
      '● **Novo**',
      'Seu video bruto chegou',
      '',
      '◐ **Planejando**',
      'Decidindo cortes, legendas, zoom',
      '',
      '◐ **Storyboard**',
      'Rascunho visual do resultado',
      '',
      '◐ **Montando**',
      'Juntando tudo no video final',
      '',
      '◎ **Pronto**',
      'Assista e peca mudancas',
      '',
      '✓ **Entregue**',
      'Salvo no Drive, pronto pra postar',
    ].join('\n')

    return (
      <Box flexDirection="column" padding={1}>

        {/* ── HEADER ── */}
        <Box flexDirection="row" justifyContent="space-between" alignItems="center">
          <Text bold>{marcaName}</Text>
          <Text color={setup ? 'success' : 'warning'}>{setup ? '● Pronto' : '○ Setup'}</Text>
        </Box>
        <Text dimColor>Transforme brutos em Reels prontos</Text>

        {/* ── METRICAS ── */}
        <Box flexDirection="row" gap={2} marginTop={2}>
          <Box flexDirection="column" alignItems="center" flexGrow={1}>
            <Text bold color={novos.length > 0 ? 'claude' : undefined}>{novos.length}</Text>
            <Text dimColor>novos</Text>
          </Box>
          <Text dimColor>{'│'}</Text>
          <Box flexDirection="column" alignItems="center" flexGrow={1}>
            <Text bold color={emAndamento.length > 0 ? 'warning' : undefined}>{emAndamento.length}</Text>
            <Text dimColor>editando</Text>
          </Box>
          <Text dimColor>{'│'}</Text>
          <Box flexDirection="column" alignItems="center" flexGrow={1}>
            <Text bold color={entregues.length > 0 ? 'success' : undefined}>{entregues.length}</Text>
            <Text dimColor>entregues</Text>
          </Box>
        </Box>

        {/* ── DIVIDER ── */}
        <Box marginTop={2}><Text dimColor>{HR}</Text></Box>

        {/* ── COMO FUNCIONA ── */}
        <Box flexDirection="column" marginTop={1}>
          <Text bold dimColor>COMO FUNCIONA</Text>
          <Box marginTop={1} paddingX={1}>
            <Markdown dimColor text={guideText} />
          </Box>
        </Box>

        {/* ── DIVIDER ── */}
        <Box marginTop={1}><Text dimColor>{HR}</Text></Box>

        {/* ── DRIVE ── */}
        <Box flexDirection="column" marginTop={1}>
          <Box flexDirection="row" justifyContent="space-between" alignItems="center">
            <Text bold dimColor>DRIVE</Text>
            <Button key="atualizar" onPress={() => send($, 'Rodar rclone lsf "gdrive:Edição de vídeos/brutos/" --format pst, comparar com registro.json, registrar brutos novos (etapa novo) e atualizar _driveCheck em registro.json com {"checked":"HH:MM","message":"...","newCount":N}')}>
              Atualizar
            </Button>
          </Box>
          {lastRefresh && (
            <Box paddingX={1}>
              <Text dimColor>Atualizado as {lastRefresh}{refreshMsg ? ` — ${refreshMsg}` : ''}</Text>
            </Box>
          )}
        </Box>

        {/* ── NOVOS ── */}
        {novos.length > 0 && (
          <Box flexDirection="column" marginTop={2}>
            <Text dimColor>{HR}</Text>
            <Box flexDirection="column" marginTop={1}>
              <Text bold color="claude">{'●'} NOVOS — ESCOLHER PADRAO</Text>
              {novos.map((v, i) => (
                <Box key={`novo-${i}`} flexDirection="column" marginTop={1} paddingX={1}>
                  <Text bold>{v.bruto}</Text>
                  <Text dimColor>{formatSize(v.tamanho_mb)}</Text>
                  <Box flexDirection="row" gap={1} marginTop={1}>
                    {padroes.length > 0 ? padroes.map((p, j) => (
                      <Button
                        key={`pad-${i}-${j}`}
                        variant="primary"
                        onPress={() => send($, `Editar o video ${v.bruto} com o padrao ${p}`)}
                      >
                        {p}
                      </Button>
                    )) : (
                      <Button
                        key={`edit-${i}`}
                        variant="primary"
                        onPress={() => send($, `Editar o video ${v.bruto}`)}
                      >
                        Editar
                      </Button>
                    )}
                  </Box>
                </Box>
              ))}
            </Box>
          </Box>
        )}

        {/* ── EM ANDAMENTO ── */}
        {emAndamento.length > 0 && (
          <Box flexDirection="column" marginTop={2}>
            <Text dimColor>{HR}</Text>
            <Box flexDirection="column" marginTop={1}>
              <Text bold color="warning">{'◐'} EM ANDAMENTO</Text>
              {emAndamento.map((v, i) => {
                const icon = ETAPA_ICON[v.etapa] || '·'
                const isPreview = v.etapa === 'preview'
                return (
                  <Box key={`prog-${i}`} flexDirection="column" marginTop={2} paddingX={1}>
                    {i > 0 && (
                      <Box marginTop={0}><Text dimColor>{'· · · · · · · · · · · · · · ·'}</Text></Box>
                    )}
                    <Text bold color={isPreview ? 'success' : 'warning'}>
                      {icon} {ETAPA_LABEL[v.etapa] || v.etapa}
                    </Text>
                    <Text bold>{v.bruto}</Text>
                    <Text dimColor>
                      {formatSize(v.tamanho_mb)}{v.padrao ? ` · padrao ${v.padrao}` : ''}
                    </Text>
                    <Box flexDirection="row" gap={1} marginTop={1}>
                      {isPreview && (
                        <Button
                          key={`prev-${i}`}
                          variant="primary"
                          onPress={() => send($, `Mostrar o preview do video ${v.bruto}`)}
                        >
                          Ver preview
                        </Button>
                      )}
                      {isPreview && (
                        <Button
                          key={`entregar-${i}`}
                          onPress={() => send($, `Finalizar edicao e salvar o video ${v.bruto}`)}
                        >
                          Finalizar e salvar
                        </Button>
                      )}
                      {!isPreview && (
                        <Button
                          key={`cont-${i}`}
                          variant="primary"
                          onPress={() => send($, `Continue editando ${v.bruto}`)}
                        >
                          Continuar
                        </Button>
                      )}
                    </Box>
                    <Box marginTop={1}>
                      <Input
                        key={`ajuste-${i}`}
                        placeholder="Pedir ajuste neste video..."
                        submitLabel="Enviar"
                        onSubmit={(text: string) => send($, `Ajustar no video ${v.bruto}: ${text}`)}
                      />
                    </Box>
                  </Box>
                )
              })}
            </Box>
          </Box>
        )}

        {/* ── ENTREGUES ── */}
        {entregues.length > 0 && (
          <Box flexDirection="column" marginTop={2}>
            <Text dimColor>{HR}</Text>
            <Box flexDirection="column" marginTop={1}>
              <Text bold color="success">{'✓'} ENTREGUES</Text>
              {entregues.map((v, i) => (
                <Box key={`done-${i}`} flexDirection="column" marginTop={1} paddingX={1}>
                  <Box flexDirection="row" gap={1}>
                    <Text color="success">{'✓'}</Text>
                    <Text bold>{v.bruto}</Text>
                  </Box>
                  <Box flexDirection="row" gap={1} paddingX={2}>
                    <Text dimColor>{formatSize(v.tamanho_mb)}{v.padrao ? ` · ${v.padrao}` : ''}</Text>
                    <Button
                      key={`show-${i}`}
                      onPress={() => send($, `Mostrar o video entregue ${v.bruto}`)}
                    >
                      Abrir
                    </Button>
                  </Box>
                </Box>
              ))}
            </Box>
          </Box>
        )}

        {/* ── SEM VIDEOS ── */}
        {videos.length === 0 && (
          <Box marginTop={2} paddingX={1}>
            <Text dimColor>Nenhum video ainda. Suba um bruto no Drive e clique Atualizar.</Text>
          </Box>
        )}

        {/* ── SETUP ── */}
        {!setup && (
          <Box marginTop={2}>
            <Button key="configurar" variant="primary" onPress={() => send($, 'Configurar o editor de video')}>
              Configurar editor
            </Button>
          </Box>
        )}

        {/* ── FOOTER ── */}
        <Box marginTop={2}><Text dimColor>{HR}</Text></Box>
        <Box flexDirection="column" marginTop={1}>
          {padroes.length > 0 && (
            <Text dimColor>Padroes: {padroes.join(' · ')}</Text>
          )}
          <Box marginTop={1}>
            <Button key="novo-padrao" onPress={() => send($, 'Criar um novo padrao de edicao')}>
              Novo padrao
            </Button>
          </Box>
        </Box>

      </Box>
    )
  })
}
