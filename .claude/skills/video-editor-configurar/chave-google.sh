#!/bin/zsh
# Conecta o rclone ao Google Drive com a chave própria da pessoa (guia: chave-google.md).
# Sempre refaz a conexão "gdrive" do zero (autoriza de novo no navegador) e confere a renovação do acesso.
R=$(command -v rclone || echo ~/.local/bin/rclone)
echo ""
echo "Cole o ID DO CLIENTE (termina com .apps.googleusercontent.com) e aperte Enter:"
read -r ID
echo ""
echo "Cole a CHAVE SECRETA (começa com GOCSPX-) UMA VEZ e aperte Enter."
echo "(por segurança ela não aparece na tela enquanto você cola)"
read -rs SEGREDO
echo ""
ID="${ID//[[:space:]]/}"
SEGREDO="${SEGREDO//[[:space:]]/}"
if [[ "$ID" != *.apps.googleusercontent.com ]]; then
  echo "O ID não parece certo (precisa terminar com .apps.googleusercontent.com). Nada foi alterado."
  exit 1
fi
if [[ ! "$SEGREDO" =~ '^GOCSPX-[A-Za-z0-9_-]{20,40}$' ]]; then
  echo "A chave secreta não parece certa (tem ${#SEGREDO} caracteres; o normal é ~35, começando com GOCSPX-)."
  echo "Talvez tenha sido colada duas vezes. Nada foi alterado. Rode de novo."
  exit 1
fi
echo "Vai abrir o Google no navegador: escolha a conta do seu Drive e clique em Permitir."
echo ""
"$R" config delete gdrive >/dev/null 2>&1
"$R" config create gdrive drive scope=drive client_id="$ID" client_secret="$SEGREDO" >/dev/null   # a config impressa (com a chave) vai pro lixo; o link de autorização (stderr) continua visível
echo ""
# Confere de verdade: pede ao Google um acesso novo com a chave gravada (é o que acontece a cada hora)
if "$R" config dump 2>/dev/null | python3 -c '
import json, sys, urllib.request, urllib.parse
c = json.load(sys.stdin)["gdrive"]; t = json.loads(c["token"])
d = urllib.parse.urlencode(dict(client_id=c["client_id"], client_secret=c["client_secret"],
                                refresh_token=t["refresh_token"], grant_type="refresh_token")).encode()
urllib.request.urlopen("https://oauth2.googleapis.com/token", d, timeout=30)' 2>/dev/null && "$R" lsd gdrive: >/dev/null 2>&1; then
  echo "PRONTO: conexão com o Drive funcionando com a sua chave (renovação do acesso conferida)."
else
  echo "A conexão falhou. Se acabou de criar a chave, o Google pode levar alguns minutos: espere e rode de novo."
  exit 1
fi
