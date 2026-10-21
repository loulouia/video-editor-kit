#!/bin/zsh
# Conecta o rclone ao Google Drive com a chave própria da pessoa (guia: chave-google.md).
# Cria a conexão "gdrive" se ainda não existir, ou troca a chave de uma conexão existente.
R=$(command -v rclone || echo ~/.local/bin/rclone)
echo ""
echo "Cole o ID DO CLIENTE (termina com .apps.googleusercontent.com) e aperte Enter:"
read -r ID
echo ""
echo "Cole a CHAVE SECRETA (começa com GOCSPX-) e aperte Enter."
echo "(por segurança ela não aparece na tela enquanto você cola)"
read -rs SEGREDO
echo ""
ID="${ID//[[:space:]]/}"
SEGREDO="${SEGREDO//[[:space:]]/}"
if [[ "$ID" != *.apps.googleusercontent.com || "$SEGREDO" != GOCSPX-* ]]; then
  echo "Algum código não parece certo. Nada foi alterado. Rode de novo."
  exit 1
fi
echo "Vai abrir o Google no navegador: escolha a conta do seu Drive e clique em Permitir."
echo ""
if "$R" listremotes 2>/dev/null | grep -qx "gdrive:"; then
  "$R" config update gdrive client_id="$ID" client_secret="$SEGREDO" >/dev/null 2>&1 || { echo "Erro ao gravar. Nada foi alterado."; exit 1; }
  "$R" config reconnect gdrive: --auto-confirm 2>&1 | grep -v NOTICE
else
  "$R" config create gdrive drive scope=drive client_id="$ID" client_secret="$SEGREDO" 2>&1 | grep -iv "token\|NOTICE"
fi
echo ""
if "$R" lsd gdrive: >/dev/null 2>&1; then
  echo "PRONTO: conexão com o Drive funcionando com a sua chave."
else
  echo "A conexão falhou. Pode ser o Google ainda ativando a chave: espere uns minutos e rode de novo."
fi
