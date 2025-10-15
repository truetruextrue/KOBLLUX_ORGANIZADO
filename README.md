# KOBLLUX — Roda Narrativa Geométrica Fractal (Python)

Base simbólica para criar prompts, cenas e diretrizes de design a partir dos 12 arquétipos do sistema KOBLLUX.
Inclui:
- Registro de arquétipos com geometrias, cores, símbolos e Trindade (Pai/Filho/Espírito -> Mente/Corpo/Espírito).
- Ciclos 3–6–9, roda viva, e narrativas programáticas.
- Geração de *prompts* textuais para diretores de arte e designers.
- Exportação em JSON e CLI simples.

## Instalação rápida

```bash
cd kobllux_narrativa
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

## Uso rápido

```bash
kobllux prompt --name Atlas
kobllux roda
kobllux export --out ./arquetipos.json
python -m kobllux.examples.demo
./myrmide_seed.sh  # gera o fluxo MYRMIDE (semente → hub)
```

### MYRMIDE — SCI-ART 6-Polos

O comando `./myrmide_seed.sh` ativa o pipeline **MYRMIDE**, estruturado nas camadas:

- **UNO**: sementes ASCII originais e reflexos (`original/`, `mirror_h/`, `mirror_v/`, `rot180/`).
- **DUAL**: selagem em pares (`DUAL/pairs/*.pair.json`).
- **TRINITY**: fusão triple (`TRINITY/SCIART_triple.json`).
- **HUB**: manifesto consolidado (`HUB/manifest.json` e `HUB/loop.json`).

Cada semente gera relatórios (`*.report.json`), markdown explicativo e selo ∆7 em `MYRMIDE/UNO/SEALS/items/` seguindo a lei **VERDADE × INTEGRAR ÷ Δ = ♾️**.
