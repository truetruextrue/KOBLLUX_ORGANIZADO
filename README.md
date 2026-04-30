# KOBLLUX — Roda Narrativa Geométrica Fractal (Python)

Base simbólica para criar prompts, cenas e diretrizes de design a partir dos 12 arquétipos do sistema KOBLLUX.
Inclui:
- Registro de arquétipos com geometrias, cores, símbolos e Trindade (Pai/Filho/Espírito -> Mente/Corpo/Espírito).
- Ciclos 3–6–9, roda viva, e narrativas programáticas.
- Geração de *prompts* textuais para diretores de arte e designers.
- Exportação em JSON e CLI simples.
- Documentos estendidos com frames visuais, como o [Pulso de Ativação KOBLLUX #13](README_PULSO_13.md).

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
```

## Portal Web Experimental

Um protótipo de interface web inspirada no Códice está disponível em `web/index.html`. Basta abrir o arquivo no navegador para testar a visualização 3D, o painel de pulso com reconhecimento de voz (dependente de suporte `webkitSpeechRecognition`) e a integração preparada para as APIs Gemini (informe sua chave no campo `API_KEY`).
