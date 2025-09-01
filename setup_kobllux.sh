#!/usr/bin/env bash
set -euo pipefail

# =========================
# CONFIG (edite se quiser)
# =========================
REPO_OWNER="truetruextrue"
REPO_NAME="KOBLLUX_ORGANIZADO"
REPO_DIR="$HOME/$REPO_NAME"

# Se quiser copiar conteúdo do Android (ajuste o caminho se necessário)
ANDROID_SRC="/storage/emulated/0/Download/kobllux_ascii_pack/kobllux_narrativa"

# Escolha do método de push:
# - Para SSH: export GITHUB_SSH=1
# - Para HTTPS+PAT: export GITHUB_PAT="seu_token_com_escopo_repo"
GITHUB_SSH="${GITHUB_SSH:-}"
GITHUB_PAT="${GITHUB_PAT:-}"

# =========================
log(){ printf "\n\033[1;36m[LOG]\033[0m %s\n" "$*"; }
die(){ printf "\n\033[1;31m[ERRO]\033[0m %s\n" "$*" ; exit 1; }

# 0) Pacotes base + acesso ao /storage
log "Atualizando Termux e instalando pacotes..."
pkg update -y >/dev/null
pkg install -y git python unzip >/dev/null || die "Falha instalando git/python/unzip"
if [ ! -d /storage/emulated/0 ]; then
  log "Habilitando acesso ao armazenamento (termux-setup-storage)..."
  termux-setup-storage || true
fi

# 1) Preparar diretório do repositório
mkdir -p "$REPO_DIR"
cd "$REPO_DIR"

# 2) Se o diretório NÃO é repo git, inicializa e configura remoto
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  log "Inicializando repositório git local em: $REPO_DIR"
  git init
  git branch -M main

  if [ -n "$GITHUB_SSH" ]; then
    REMOTE_URL="git@github.com:${REPO_OWNER}/${REPO_NAME}.git"
  elif [ -n "$GITHUB_PAT" ]; then
    REMOTE_URL="https://${REPO_OWNER}:${GITHUB_PAT}@github.com/${REPO_OWNER}/${REPO_NAME}.git"
  else
    # Sem credenciais fornecidas: ainda assim setamos a URL SSH por padrão (você pode configurar depois)
    REMOTE_URL="git@github.com:${REPO_OWNER}/${REPO_NAME}.git"
    log "Nenhuma credencial definida (GITHUB_SSH ou GITHUB_PAT). Vou configurar remoto SSH por padrão."
    log "Se ainda não tiver chave SSH no GitHub: ssh-keygen -t ed25519 -C \"termux@phone\" && cat ~/.ssh/id_ed25519.pub"
  fi

  git remote add origin "$REMOTE_URL" || true
else
  log "Repositório git já existe aqui. Remoto atual:"
  git remote -v || true
fi

# 3) Copiar conteúdo do ANDROID_SRC (se existir e a raiz estiver vazia ou sem o pacote)
if [ -d "$ANDROID_SRC" ]; then
  # Detecta conteúdo mínimo
  NEED_COPY=0
  [ ! -d "$REPO_DIR/kobllux" ] && NEED_COPY=1
  [ ! -f "$REPO_DIR/pyproject.toml" ] && NEED_COPY=1

  if [ "$NEED_COPY" -eq 1 ]; then
    log "Copiando conteúdo de $ANDROID_SRC para $REPO_DIR ..."
    cp -r "$ANDROID_SRC"/* "$REPO_DIR"/
  else
    log "Conteúdo já presente, não vou sobrescrever a partir do ANDROID_SRC."
  fi
else
  log "ANDROID_SRC não encontrado ($ANDROID_SRC). Pulando cópia (ok)."
fi

# 4) Garantir .gitignore seguro
log "Escrevendo .gitignore seguro..."
cat > .gitignore <<'EOF'
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.venv/
.env
.vscode/
.idea/
.DS_Store
*.pub
id_ed25519*
*key*
arquetipos.json
EOF

# 5) Venv + instalação em modo dev
log "Criando venv e instalando pacote em modo desenvolvimento..."
python -m venv .venv
source .venv/bin/activate
pip install -U pip setuptools wheel >/dev/null
pip install -e . >/dev/null || die "Falha no pip install -e . (verifique pyproject.toml e pasta kobllux/)"

# 6) Smoke tests (CLI)
log "Rodando smoke tests (CLI)..."
if command -v kobllux >/dev/null 2>&1; then
  kobllux list || true
  kobllux roda || true
  kobllux prompt --name Atlas || true
  kobllux system || true
else
  log "Binário 'kobllux' não apareceu no PATH, usando python -m ..."
  python -m kobllux.cli list || true
  python -m kobllux.cli roda || true
  python -m kobllux.cli prompt --name Atlas || true
  python -m kobllux.cli system || true
fi

# 7) Commit & push
log "Preparando commit..."
git add -A
git commit -m "seed: KOBLLUX narrativa + CLI + docs ASCII" >/dev/null || log "Nada a commitar (talvez já esteja versionado)."

log "Enviando ao GitHub (git push)..."
set +e
git push -u origin main
PUSH_RC=$?
set -e

if [ "$PUSH_RC" -ne 0 ]; then
  log "git push falhou (provável falta de credenciais SSH ou PAT)."
  if [ -n "$GITHUB_SSH" ]; then
    cat <<MSG

DICA SSH:
1) Gere e registre a chave:
   ssh-keygen -t ed25519 -C "termux@phone"
   cat ~/.ssh/id_ed25519.pub  # cole em GitHub → Settings → SSH and GPG keys

2) Teste:
   eval "\$(ssh-agent -s)"
   ssh-add ~/.ssh/id_ed25519
   ssh -T git@github.com

3) Tente o push novamente:
   cd "$REPO_DIR" && git push -u origin main

MSG
  elif [ -n "$GITHUB_PAT" ]; then
    cat <<MSG

DICA HTTPS+PAT:
- PAT inválido ou sem escopo 'repo'.
- Gere um novo em https://github.com/settings/tokens (classic), marque 'repo',
  e reexporte:
    export GITHUB_PAT="SEU_NOVO_TOKEN"
  Depois:
    cd "$REPO_DIR" && git remote set-url origin "https://${REPO_OWNER}:${GITHUB_PAT}@github.com/${REPO_OWNER}/${REPO_NAME}.git"
    git push -u origin main

MSG
  else
    cat <<MSG

NENHUMA CREDENCIAL DEFINIDA:
Escolha um método e repita o push:

A) SSH:
   ssh-keygen -t ed25519 -C "termux@phone"
   cat ~/.ssh/id_ed25519.pub  # adicione no GitHub (SSH keys)
   eval "\$(ssh-agent -s)"
   ssh-add ~/.ssh/id_ed25519
   ssh -T git@github.com
   cd "$REPO_DIR" && git push -u origin main

B) HTTPS + PAT:
   Gere token em https://github.com/settings/tokens (classic), escopo 'repo'
   export GITHUB_PAT="SEU_TOKEN"
   cd "$REPO_DIR"
   git remote set-url origin "https://${REPO_OWNER}:${GITHUB_PAT}@github.com/${REPO_OWNER}/${REPO_NAME}.git"
   git push -u origin main

MSG
  fi
else
  log "Push ok ✅"
fi

log "Setup concluído. Ative a venv quando quiser usar:"
echo "  source \"$REPO_DIR/.venv/bin/activate\""
echo "  kobllux list"
