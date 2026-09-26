# Prépare profils/<id>/ à partir d'un logo sur fond uni :
#   logo.png (fond retiré, recadré) pour la facture et l'app, icônes 180/192/512, manifest.webmanifest.
# Usage : python profil.py <logo source> <dossier Facturation> <id> "<nom>" "<nom court>"
import json, sys
from pathlib import Path
from PIL import Image

src, racine, pid, nom, court = sys.argv[1:6]
out = Path(racine) / 'profils' / pid
out.mkdir(parents=True, exist_ok=True)
im = Image.open(src).convert('RGB')

# Fond = couleur des coins ; « encre » = pixels qui s'en écartent.
w, h = im.size
coins = [im.getpixel(p) for p in ((2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3))]
fond = tuple(sum(c[i] for c in coins) // 4 for i in range(3))
px = im.load()
ecart = lambda c: max(abs(c[i] - fond[i]) for i in range(3))
fortes = [px[x, y] for y in range(h) for x in range(w) if ecart(px[x, y]) > 120]
encre = tuple(sum(c[i] for c in fortes) // len(fortes) for i in range(3))
plein = max(ecart(encre), 1)

# Logo transparent : couleur de l'encre, opacité selon l'écart au fond (bords lissés conservés).
t = Image.new('RGBA', (w, h))
tp = t.load()
for y in range(h):
    for x in range(w):
        a = min(255, round(255 * ecart(px[x, y]) / plein))
        tp[x, y] = (*encre, a if a > 25 else 0)
bbox = t.getbbox()
m = round(0.04 * max(bbox[2] - bbox[0], bbox[3] - bbox[1]))
t = t.crop((max(0, bbox[0] - m), max(0, bbox[1] - m), min(w, bbox[2] + m), min(h, bbox[3] + m)))
t.save(out / 'logo.png', optimize=True)

# Icônes : le logo d'origine, carré, sur son propre fond (le motif reste dans la zone sûre).
cote = max(w, h)
carre = Image.new('RGB', (cote, cote), fond)
carre.paste(im, ((cote - w) // 2, (cote - h) // 2))
for s in (180, 192, 512):
    carre.resize((s, s), Image.LANCZOS).save(out / f'icone-{s}.png', optimize=True)

couleur = '#%02x%02x%02x' % fond
(out / 'manifest.webmanifest').write_text(json.dumps({
    'id': f'../../?profil={pid}', 'name': nom, 'short_name': court, 'lang': 'fr',
    'start_url': f'../../?profil={pid}', 'scope': '../../', 'display': 'standalone',
    'background_color': couleur, 'theme_color': '#1f3a5f',
    'icons': [{'src': 'icone-192.png', 'sizes': '192x192', 'type': 'image/png'},
              {'src': 'icone-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any maskable'}]
}, ensure_ascii=False, indent=2), encoding='utf-8')
print('fond', fond, 'encre', encre, 'logo', t.size, '->', out)
