# /video-editor-atualizar — Atualizar o editor de vídeo

Atualiza o motor, os padrões e os comandos do editor com a versão mais recente publicada pela autora no GitHub.

## Quando usar

- O hook `SessionStart` (`motor/inicio.py`) avisou "ATUALIZAÇÃO DISPONÍVEL" e a pessoa disse sim.
- A pessoa pediu pra atualizar ("atualizar editor", "tem versão nova?", "update").

## Como funciona (pra explicar se a pessoa perguntar)

O editor baixa a versão nova pela internet, direto do site do GitHub (não precisa do programa git). Troca só o
que é da autora: `motor/`, `padroes/`, `.claude/` (comandos), `CLAUDE.md`, `LEIA-ME.md`. **Nunca** mexe em
`marcas/`, `config/` (conexão com o Drive), `projetos/` e `registro.json`. Antes de trocar, guarda uma cópia
do que existia em `config/backups-atualizacao/`. Se algo falhar no meio, desfaz tudo sozinho.

Mudanças que a pessoa tenha feito no motor ou nos padrões são substituídas pela versão da autora (decisão da
autora: ajustes no motor são feitos por ela e chegam pra todos pela atualização).

## Passos — clientes (todos, mesmo quem instalou com git)

1. Se a pessoa pediu por conta própria (sem o aviso do hook), conferir:
   ```bash
   python3 motor/atualizar.py checar
   ```
   - `"disponivel": false` → "Seu editor já está na versão mais recente." e parar.
   - Erro de conexão → "Não consegui falar com o GitHub agora. Confira a internet e tente de novo mais tarde." e parar.
   - Disponível → perguntar em uma frase se pode atualizar (se o hook já perguntou e ela disse sim, não perguntar de novo).

   - **Vídeo em andamento** (em `registro.json`, etapa diferente de `novo` e `entregue`): antes de aplicar, avisar em uma frase que o vídeo em edição pode mudar de aparência quando for montado de novo (o padrão pode ter mudado) e perguntar se prefere terminar e entregar antes. Só seguir com o OK.

2. Aplicar:
   ```bash
   python3 motor/atualizar.py aplicar
   ```

3. Responder em linguagem simples, sem termos técnicos:
   > Pronto, o editor está atualizado. Seus vídeos, sua marca e a conexão com o Drive continuam iguais.

   Se a saída tiver `mudancas` (do `checar`) com algo relevante (padrão novo, melhoria visível), citar em uma frase.
   Os comandos novos ou alterados passam a valer na próxima vez que o Claude Code for aberto: avisar
   "Feche e abra o Claude Code de novo pra garantir que tudo novo apareça."

4. Se der erro, seguir a tabela abaixo. Sempre em linguagem simples, dizendo que os vídeos, a marca e o Drive
   estão a salvo. **Nunca** consertar apagando, movendo ou renomeando pastas na mão, e nunca baixar o zip do
   editor pelo navegador pra copiar por cima.

## Se der erro

| O que aparece | O que fazer |
|---|---|
| `python3: command not found`, janela pedindo pra instalar "ferramentas de linha de comando", ou o `python3` não responde | Rodar o mesmo comando com `~/.video-skill/bin/python` no lugar de `python3`. Se também não existir: o setup do editor está incompleto → `/video-editor-configurar`. |
| `ERRO: não consegui baixar do GitHub` | Internet ou GitHub fora do ar. Nada foi trocado. Dizer: "Não consegui baixar agora. Vamos tentar de novo daqui a alguns minutos." Tentar de novo uma vez; se repetir, deixar pra depois (o aviso volta na próxima vez que abrir). |
| `ERRO: o download veio incompleto` | Tentar de novo uma vez. |
| `ERRO: ... não parece a pasta do editor` | O Claude Code está aberto em outra pasta. Procurar a pasta do editor (a que tem `motor/` e `padroes/`, normalmente `~/Desktop/ClaudeCode/video-editor.nosync`) e rodar o comando de dentro dela. |
| `ERRO: uma atualização anterior foi interrompida` | Rodar `python3 motor/atualizar.py desfazer` e depois `python3 motor/atualizar.py aplicar` de novo. |
| A pasta `motor/` ou o arquivo `motor/atualizar.py` sumiu (atualização interrompida no pior momento) | Baixar o atualizador de novo: `curl -fsSL https://raw.githubusercontent.com/loulouia/video-editor-kit/main/motor/atualizar.py -o motor/atualizar.py` (criar a pasta `motor` antes, se não existir) e rodar `python3 motor/atualizar.py desfazer`. A cópia de segurança fica em `config/`, que a atualização nunca toca. |
| `ERRO: esta é a pasta de trabalho da autora` | Só acontece no Mac da autora: usar a seção "Pasta da autora" abaixo. |
| `ERRO inesperado` | Nada foi perdido (o script desfaz o que tinha trocado). Pedir pra pessoa mandar a mensagem de erro pra autora do editor. Não tentar outra coisa. |
| A atualização terminou, mas depois o editor passou a dar erro ao editar | Rodar `python3 motor/atualizar.py desfazer` (volta pra versão anterior) e pedir pra pessoa avisar a autora do editor, com a mensagem do erro. |

## Pasta da autora (repositório git + `marcas/amanda/`)

Só na pasta de trabalho da autora o `motor/atualizar.py aplicar` se recusa. Nela:

```bash
/opt/homebrew/bin/git -C "$CLAUDE_PROJECT_DIR" status --short
/opt/homebrew/bin/git -C "$CLAUDE_PROJECT_DIR" pull --ff-only origin main
```

Se houver alterações locais ou conflito, mostrar quais arquivos e perguntar como seguir; nunca descartar
alterações sem OK.
