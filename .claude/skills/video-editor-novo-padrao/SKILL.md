---
name: video-editor-novo-padrao
description: Cria (ou atualiza) um padrão de edição no editor de vídeo (video-editor) a partir de vídeos de referência — analisa, monta a tabela comparativa, escreve PLAYBOOK.md e padrao.json e testa com um storyboard. Use quando a pessoa quiser um estilo novo, copiar o estilo de um criador ou mudar um padrão.
argument-hint: "[nome do padrão]"
---

# Criar um padrão novo

Padrão: $ARGUMENTS (se vazio, perguntar o nome; slug sem acentos, ex.: `topo-livre`). Método completo em `CLAUDE.md` → "Criação e atualização de um padrão".

1. **Caminho:** A (partir dos editados da marca, em `_marca/meus-editados/` no Drive) ou B (copiar referências: 2–3 vídeos do mesmo criador). Perguntar também: o padrão é pra uso próprio ou pra clientes (clientes: só fontes livres, sem logo fixo).
2. **Referências:** pedir que a pessoa suba em `_padroes/<padrão>/referencias/` no Drive e diga o que gosta em cada uma. Baixar com `motor/drive.py baixar` pra uma pasta temporária (análise na resolução original; apagar ao terminar).
3. **Analisar** (ritmo, legendas, gancho, inserções, efeitos, cor, **música, efeitos sonoros e transições** — o que usar da biblioteca `_audio/` e `_transicoes/` do Drive) e entregar a **tabela comparativa** com valores medidos × estimados. Decisões são da pessoa; confirmar antes de mudar qualquer regra.
4. Criar `padroes/<padrão>/` com `PLAYBOOK.md` (regras e porquês), `padrao.json` (valores que o motor lê — partir do mais parecido entre os existentes), `CHANGELOG.md`, `fontes/` (com a licença) e `analise/`. Recurso que o motor ainda não tem → implementar no motor de forma configurável (sem quebrar os padrões existentes: rodar a regressão do `taste-washing-5`).
5. **Testar** com um bruto: storyboard primeiro; montagem só se a pessoa pedir.
6. Registrar no `CLAUDE.md` (lista de padrões) e no `LEIA-ME.md`.
