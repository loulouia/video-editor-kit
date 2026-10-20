---
name: video-editor-videos
description: Mostra os vídeos do editor de vídeo (video-editor) no Google Drive — novos, em andamento (plano, storyboard, preview) e entregues. Use quando a pessoa perguntar se tem vídeo novo, o que falta editar ou o status dos vídeos.
---

# Vídeos no Drive

1. Rodar `~/.video-skill/bin/python -I motor/registro.py` (consulta `brutos/` no Drive e o `registro.json`).
2. Mostrar uma tabela curta: 🆕 novos · ⏳ em andamento (com a etapa) · ✅ entregues (com o nome do arquivo em `editados/`).
3. Avisos:
   - nome que parece b-roll em `brutos/` → perguntar se é bruto ou inserção de outro vídeo (nunca decidir sozinho);
   - vídeo registrado que sumiu de `brutos/` → avisar (sem o bruto não dá pra reeditar).
4. Oferecer o próximo passo: "quer começar algum? `/video-editor-editar <nome>`".

Se o setup estiver incompleto, indicar `/video-editor-configurar` em vez de consultar.
