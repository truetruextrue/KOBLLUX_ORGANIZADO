from fastapi import FastAPI, HTTPException
from .archetypes import ARCHETYPES
from .narrative import roda_viva, visual_prompt
from .fractal import weave
from .system_prompt import SYSTEM_PROMPT

app = FastAPI(title="KOBLLUX API", version="0.1.0")

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/system")
def system():
    return {"system_prompt": SYSTEM_PROMPT}

@app.get("/archetypes")
def list_archetypes():
    return {"archetypes": list(ARCHETYPES.keys())}

@app.get("/roda")
def roda():
    return {"roda": roda_viva()}

@app.get("/prompt/{name}")
def prompt(name: str):
    if name not in ARCHETYPES:
        raise HTTPException(status_code=404, detail="Arquétipo não encontrado")
    return {"name": name, "prompt": visual_prompt(name)}

@app.get("/fractal")
def fractal(depth: int = 2):
    depth = max(1, min(depth, 4))
    return weave(depth=depth)
