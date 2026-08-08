#!/usr/bin/env python3
"""
Tag de Preço H! Fit — aplica pill neon de preço, chip de marca e selo H! em fotos de produto.
Identidade: preto #0D0D0D · neon #C6FF00 · pill rotacionada -2° · chip escuro translúcido.
Uso:
  python3 tag_preco.py --input foto.jpg --output final.jpg --preco "R$ 189,90" \
      --extra "pronta entrega!" --marca "VIA MÁFIA" --formato 4x5
"""
import argparse, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

NEON = (198, 255, 0, 255)        # #C6FF00
PRETO = (13, 13, 13, 255)        # #0D0D0D
BRANCO = (255, 255, 255, 255)

FORMATOS = {"4x5": (1080, 1350), "1x1": (1080, 1080), "9x16": (1080, 1920)}

def font_path():
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(here, "..", "assets", "DejaVuSansCondensed-Bold.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            return os.path.abspath(c)
    sys.exit("Nenhuma fonte encontrada — instale DejaVu ou adicione .ttf em assets/")

def cover_crop(img, size):
    """Corta a imagem para preencher o formato (crop central com viés para o topo)."""
    img = ImageOps.exif_transpose(img).convert("RGB")
    tw, th = size
    scale = max(tw / img.width, th / img.height)
    nw, nh = round(img.width * scale), round(img.height * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    left = (nw - tw) // 2
    top = int((nh - th) * 0.30)  # viés para o topo: preserva rosto/torso
    return img.crop((left, top, left + tw, top + th))

def rounded_pill(text, font, pad_x, pad_y, bg, fg):
    tmp = Image.new("RGBA", (10, 10))
    d = ImageDraw.Draw(tmp)
    box = d.textbbox((0, 0), text, font=font)
    w, h = box[2] - box[0], box[3] - box[1]
    img = Image.new("RGBA", (w + 2 * pad_x, h + 2 * pad_y), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = img.height // 2
    d.rounded_rectangle([0, 0, img.width - 1, img.height - 1], radius=r, fill=bg)
    d.text((pad_x - box[0], pad_y - box[1]), text, font=font, fill=fg)
    return img

def paste_with_shadow(base, layer, xy, angle=0.0):
    if angle:
        layer = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    shadow = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    alpha = layer.split()[3].point(lambda a: int(a * 0.45))
    shadow.putalpha(alpha)
    shadow = Image.new("RGBA", layer.size, (0, 0, 0, 115))
    shadow.putalpha(alpha)
    shadow = shadow.filter(ImageFilter.GaussianBlur(6))
    base.alpha_composite(shadow, (xy[0] + 4, xy[1] + 7))
    base.alpha_composite(layer, xy)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--preco", default="", help='ex.: "R$ 189,90" (omitir pula a pill de preço — chip de marca e selo continuam)')
    ap.add_argument("--extra", default="", help='ex.: "pronta entrega!"')
    ap.add_argument("--marca", default="", help='chip: ex. "VIA MÁFIA"')
    ap.add_argument("--formato", default="4x5", choices=list(FORMATOS))
    ap.add_argument("--pos-pill", default="baixo-esq", choices=["baixo-esq", "baixo-dir"])
    ap.add_argument("--sem-logo", action="store_true")
    a = ap.parse_args()

    W, H = FORMATOS[a.formato]
    base = cover_crop(Image.open(a.input), (W, H)).convert("RGBA")
    fp = font_path()
    margin = round(W * 0.032)

    # ---- pill neon de preço (opcional — só na foto de capa do carrossel, por exemplo) ----
    if a.preco:
        texto = a.preco + (f" · {a.extra}" if a.extra else "")
        f_pill = ImageFont.truetype(fp, round(W * 0.040))
        pill = rounded_pill(texto, f_pill, round(W * 0.030), round(W * 0.017), NEON, PRETO)
        max_w = round(W * 0.86)
        if pill.width > max_w:  # preço muito longo -> reduz fonte
            f_pill = ImageFont.truetype(fp, round(W * 0.032))
            pill = rounded_pill(texto, f_pill, round(W * 0.026), round(W * 0.015), NEON, PRETO)
        y_pill = H - pill.height - margin - round(H * 0.006)
        x_pill = margin if a.pos_pill == "baixo-esq" else W - pill.width - margin - 8
        paste_with_shadow(base, pill, (x_pill, y_pill), angle=2.0)

    # ---- chip da marca (canto oposto) ----
    if a.marca:
        f_chip = ImageFont.truetype(fp, round(W * 0.021))
        chip_txt = " ".join(a.marca.upper())  # espaçamento entre letras
        chip = rounded_pill(chip_txt, f_chip, round(W * 0.020), round(W * 0.011),
                            (13, 13, 13, 210), BRANCO)
        x_chip = W - chip.width - margin if a.pos_pill == "baixo-esq" else margin
        base.alpha_composite(chip, (x_chip, H - chip.height - margin))

    # ---- selo H! (canto superior direito) ----
    if not a.sem_logo:
        s = round(W * 0.062)
        selo = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        d = ImageDraw.Draw(selo)
        d.rounded_rectangle([0, 0, s - 1, s - 1], radius=round(s * 0.24), fill=NEON)
        f_selo = ImageFont.truetype(fp, round(s * 0.56))
        tb = d.textbbox((0, 0), "H!", font=f_selo)
        d.text(((s - (tb[2] - tb[0])) / 2 - tb[0], (s - (tb[3] - tb[1])) / 2 - tb[1]),
               "H!", font=f_selo, fill=PRETO)
        base.alpha_composite(selo, (W - s - margin, margin))

    base.convert("RGB").save(a.output, "JPEG", quality=92, optimize=True)
    print(f"OK: {a.output} ({W}x{H}, formato {a.formato})")

if __name__ == "__main__":
    main()
