# Palavra Viva — TikTok: 1 execucao (chamada pelo Agendador 3x/dia).
# 1) reabastece a biblioteca se estiver acabando; 2) posta 1 video.

$ErrorActionPreference = "Stop"
$repo = "C:\Users\NOTE\Desktop\Projetos\Palavra-Viva-3x"
Set-Location $repo

# Quantos videos ainda nao publicados existem?
$naoPublicados = & python -c @'
import json,sys
from pathlib import Path
f = Path(r"tiktok/biblioteca/fila.json")
d = json.loads(f.read_text(encoding="utf-8")) if f.exists() else []
print(sum(1 for x in d if not x.get("publicado")))
'@

if ([int]$naoPublicados -lt 4) {
    Write-Output "Buffer baixo ($naoPublicados). Renderizando mais 4..."
    & python "tiktok\montar_biblioteca_tiktok.py" --quantidade 4
}

# Posta 1. Troque para incluir --dry-run enquanto estiver testando.
& python "tiktok\poster\poster.py"
