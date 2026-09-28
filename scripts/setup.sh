#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_ROOT}"

VENV_DIR=".venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"
REQ_DEV="requirements/dev.txt"
REQ_BASE="requirements/base.txt"

info() {
  echo -e "\033[1;34m[INFO]\033[0m ${*}"
}

warn() {
  echo -e "\033[1;33m[WARN]\033[0m ${*}"
}

die() {
  echo -e "\033[1;31m[ERROR]\033[0m ${*}" >&2
  exit 1
}

# shellcheck disable=SC2310
is_cmd() {
  command -v "${1}" >/dev/null 2>&1
}

ensure_cmd() {
  local cmd="${1}"
  local hint="${2:-}"

  if command -v "${cmd}" >/dev/null 2>&1; then
    return 0
  fi

  if [[ -n "${hint}" ]]; then
    die "Missing '${cmd}'. ${hint}"
  fi
  die "Missing '${cmd}'. Please install it and re-run."
}

# --- 1. System checks ---
info "Checking system requirements..."
ensure_cmd "${PYTHON_BIN}" "Install Python 3 then re-run."
ensure_cmd git "Install Git then re-run."

if ! "${PYTHON_BIN}" -m pip --version >/dev/null 2>&1; then
  die "pip module is not available for ${PYTHON_BIN}."
fi

if ! command -v shellcheck >/dev/null 2>&1; then
  warn "shellcheck is not installed on your system PATH (used by pre-commit)."
fi

# --- 2. Virtual environment setup ---
if [[ -d "${VENV_DIR}" ]]; then
  info "Virtualenv already exists: ${VENV_DIR}"
else
  info "Creating virtualenv: ${VENV_DIR}"
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

# Activate virtualenv in subshell context
# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

# Upgrade pip and packaging tools first
info "Upgrading core packaging tools (pip, setuptools, wheel)..."
python -m pip install --upgrade pip setuptools wheel

# --- 3. Dependencies installation ---
if [[ -f "${REQ_DEV}" ]]; then
  info "Installing dependencies from ${REQ_DEV}"
  python -m pip install -r "${REQ_DEV}"
elif [[ -f "${REQ_BASE}" ]]; then
  warn "Dev requirements not found. Installing base deps from ${REQ_BASE}"
  python -m pip install -r "${REQ_BASE}"
else
  die "No requirements found. Expected ${REQ_DEV} or ${REQ_BASE}"
fi

# --- 4. Environment files configuration ---
copy_sample_if_missing() {
  local target="${1}"
  local sample="${2}"

  if [[ ! -f "${target}" ]]; then
    if [[ -f "${sample}" ]]; then
      cp "${sample}" "${target}"
      info "Created ${target} from ${sample}"
    else
      warn "Sample file '${sample}' not found. Skipping ${target} generation."
    fi
  else
    info "Configuration file ${target} already exists."
  fi
}

info "Configuring environment files..."
copy_sample_if_missing ".env" ".env.sample"
copy_sample_if_missing ".env.test" ".test.env.sample"

# --- 5. Pre-commit hooks setup ---
if [[ -d ".git" ]]; then
  info "Configuring pre-commit hooks..."
  if command -v pre-commit >/dev/null 2>&1; then
    pre-commit install
  else
    "${VENV_DIR}/bin/pre-commit" install
  fi
else
  warn "Not a git repository. Skipping pre-commit install."
fi

info "Setup completed successfully! 🚀"
info "Activate virtualenv via: source ${VENV_DIR}/bin/activate"
