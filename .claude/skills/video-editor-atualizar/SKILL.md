# /video-editor-atualizar — Atualizar o editor de vídeo

Atualiza o motor, padrões e configurações do projeto a partir do repositório remoto.

## Quando usar

- O hook `SessionStart` (`motor/inicio.py`) detectou commits novos em `origin/main` e avisou.
- A pessoa pediu pra atualizar ("atualizar editor", "tem versão nova?", "update").

## Passos

### 1. Verificar estado atual

```bash
git -C "$CLAUDE_PROJECT_DIR" status --short
git -C "$CLAUDE_PROJECT_DIR" log --oneline -1
git -C "$CLAUDE_PROJECT_DIR" fetch --quiet
git -C "$CLAUDE_PROJECT_DIR" log --oneline HEAD..origin/main
```

Se não houver commits novos: "Já está na versão mais recente." e parar.

### 2. Mostrar o que vem na atualização

Listar os commits pendentes numa frase curta, ex.: "Tem 3 atualizações: melhorias no padrão amanda, novo efeito no motor, correção de bug."

Se houver mudanças locais não commitadas nos arquivos que serão atualizados (motor/, padroes/, .claude/), avisar:

> Você tem alterações locais que podem conflitar. Quer que eu guarde elas (stash) antes de atualizar?

Se sim: `git stash -u`. Se não: parar e explicar que precisa resolver antes.

### 3. Aplicar a atualização

```bash
git -C "$CLAUDE_PROJECT_DIR" pull --ff-only origin main
```

Se `--ff-only` falhar (divergência de histórico):

```bash
git -C "$CLAUDE_PROJECT_DIR" pull --rebase origin main
```

Se ainda falhar (conflito): avisar a pessoa, explicar quais arquivos conflitam, e oferecer ajuda pra resolver.

### 4. Restaurar alterações locais (se fez stash)

```bash
git -C "$CLAUDE_PROJECT_DIR" stash pop
```

Se conflitar no pop: avisar e ajudar a resolver.

### 5. Confirmar

Informar em uma frase:
- Quantos commits foram aplicados
- Resumo das mudanças (padrões novos, melhorias no motor, etc.)
- Se houver mudança em `padroes/*/padrao.json` ou `padroes/*/PLAYBOOK.md`: "Os padrões foram atualizados — as mudanças valem pros próximos vídeos."
