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

## Passos — instalação pelo zip (pasta sem `.git`, caso de todos os clientes)

1. Se a pessoa pediu por conta própria (sem o aviso do hook), conferir:
   ```bash
   python3 motor/atualizar.py checar
   ```
   - `"disponivel": false` → "Seu editor já está na versão mais recente." e parar.
   - Erro de conexão → "Não consegui falar com o GitHub agora. Confira a internet e tente de novo mais tarde." e parar.
   - Disponível → perguntar em uma frase se pode atualizar (se o hook já perguntou e ela disse sim, não perguntar de novo).

2. Aplicar:
   ```bash
   python3 motor/atualizar.py aplicar
   ```

3. Responder em linguagem simples, sem termos técnicos:
   > Pronto, o editor está atualizado. Seus vídeos, sua marca e a conexão com o Drive continuam iguais.

   Se a saída tiver `mudancas` (do `checar`) com algo relevante (padrão novo, melhoria visível), citar em uma frase.
   Os comandos novos ou alterados passam a valer na próxima vez que o Claude Code for aberto: avisar
   "Feche e abra o Claude Code de novo pra garantir que tudo novo apareça."

4. Se der `ERRO`: mostrar a frase do erro em linguagem simples, dizer que nada foi perdido (o script desfaz
   sozinho) e sugerir avisar a autora do editor. Nunca tentar consertar apagando ou movendo pastas na mão.

## Pasta com `.git` (instalação da autora)

O `motor/atualizar.py aplicar` se recusa a rodar onde existe `.git`. Nesse caso:

```bash
/opt/homebrew/bin/git -C "$CLAUDE_PROJECT_DIR" status --short
/opt/homebrew/bin/git -C "$CLAUDE_PROJECT_DIR" pull --ff-only origin main
```

Se houver alterações locais ou conflito, mostrar quais arquivos e perguntar como seguir; nunca descartar
alterações sem OK.
