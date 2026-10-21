# Chave própria do Google (guia passo a passo)

Por quê: o rclone vem com uma chave compartilhada do Google que está sendo desativada em 2026 (o rclone avisa com um NOTICE sobre `client_id`). Com a chave própria, a conexão com o Drive é só da pessoa e não para. Grátis, ~10 minutos.

Como guiar:
- **Um passo por mensagem.** Esperar "feito" ou um print antes do próximo. Linguagem simples; botões em **negrito**, exatamente como aparecem na tela.
- Pra ver a tela da pessoa: pedir print. Se o navegador dela estiver liberado pro controle de tela, dá pra olhar (navegadores são só leitura: quem clica é ela). Extensões de navegador podem ter `console.cloud.google.com` bloqueado.
- Sempre que possível, mandar o **endereço direto** da página (menos menus pra procurar).
- **Nunca** pedir os códigos no chat. Eles são colados no terminal (`chave-google.sh`).
- Aceitar termos do Google e clicar em Criar/Publicar é da pessoa.

## Antes: qual conta e se tem organização

Perguntar com qual conta Google ela vai usar o Drive. Contas de empresa (Google Workspace, ex.: `nome@empresa.com`) costumam ter **organização**; Gmail pessoal não tem. Isso muda os passos 1 e 3.

## Passo 1 — Criar o projeto

Endereço: `console.cloud.google.com/projectcreate` (entrar com a conta do Drive; aceitar os termos do Google Cloud se for o primeiro acesso).
- **Nome do projeto:** `Editor de video` (o "ID do projeto" é automático; anotar, ele vai nos endereços dos próximos passos).
- **Conta de faturamento** (se aparecer): pode deixar. Usar o Drive por aqui não gera cobrança.
- **Organização:** se existir, escolher a organização (ex.: `empresa.com`); o **Recurso pai** preenche sozinho e deve ficar assim. Sem organização: "Nenhuma organização".
- **Criar** → esperar ~30 s → conferir que o nome do projeto aparece no topo da página.

Problemas conhecidos:
- Erro "verifique se todos os campos estão corretos" / Recurso pai vazio → a conta tem organização: escolher a organização.
- Clicar em **Cancelar** abre outro projeto da pessoa — não é erro; voltar pelo endereço do passo 1.
- Aviso de cota de projetos: tudo bem enquanto houver ao menos 1 restante.

## Passo 2 — Ativar a Google Drive API

Endereço: `console.cloud.google.com/apis/library/drive.googleapis.com?project=<ID do projeto>`
- **Ativar**. Pronto quando aparecer "Status: Ativado" ou o botão **Desabilitar API**.

## Passo 3 — Tela de autorização

Endereço: `console.cloud.google.com/auth/overview?project=<ID do projeto>` → **Começar**.
- **Nome do app:** `Editor de video` · **E-mail de suporte:** o dela.
- **Público-alvo:**
  - **Interno** se a conta do Drive for da mesma organização do projeto (melhor: sem aviso de "app não verificado" e o acesso não expira).
  - **Externo** se não houver organização (Gmail pessoal).
- **Informações de contato:** o e-mail dela → marcar a concordância com a política de dados → **Continuar** → **Criar**. Aparece "Configuração do OAuth criada".
- **Só se for Externo:** menu **Público-alvo** → **Publicar app** → confirmar. Sem isso, o acesso expira a cada 7 dias.

## Passo 4 — Criar a chave

Na mesma página: **Criar um cliente OAuth** (ou menu **Clientes** → **Criar cliente**).
- **Tipo de aplicativo:** **App para computador**.
- **Nome:** `rclone`. **Não** marcar "Use this client for an AI-powered agent".
- **Criar** → abre uma janela com **ID do cliente** (termina em `.apps.googleusercontent.com`) e **Chave secreta** (começa com `GOCSPX-`). Deixar aberta.

## Passo 5 — Conectar (terminal)

Abrir um terminal pra pessoa rodando `zsh .claude/skills/video-editor-configurar/chave-google.sh` (no app: aba de terminal; fora dele: app Terminal, na pasta do projeto). O script pede o ID, depois a chave (que não aparece na tela), grava no rclone e abre o Google no navegador:
- escolher a conta do Drive → **Permitir**;
- só se for **Externo**: aparece "O Google não verificou este app" → **Avançado** → **Acessar Editor de video** (normal: o app é da própria pessoa).

O terminal termina com **PRONTO**. Conferir: `rclone lsd gdrive:` lista as pastas **sem** o NOTICE de `client_id`.

Se falhar logo depois de criar a chave: o Google pode levar de 5 minutos a algumas horas pra ativar. Esperar e rodar o script de novo (ele não estraga nada).
