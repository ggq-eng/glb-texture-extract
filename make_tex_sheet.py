# -*- coding: utf-8 -*-
"""重做贴图总览图: 中文标注 + ORM 三通道拆解"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = r'C:\Users\<你的用户名>\WorkBuddy\2026-09-22-11-02-44\glb_extract\original_textures'
BASE = r'C:\Users\<你的用户名>\WorkBuddy\2026-09-22-11-02-44\glb_extract'


def cjk_font(size):
    for p in [r'C:\Windows\Fonts\msyh.ttc', r'C:\Windows\Fonts\msyhbd.ttc',
              r'C:\Windows\Fonts\simhei.ttf', r'C:\Windows\Fonts\simsun.ttc']:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


F = cjk_font(22)
F2 = cjk_font(17)

bc = Image.open(os.path.join(OUT, 'baseColor.png')).convert('RGB')
orm = Image.open(os.path.join(OUT, 'metallicRoughness_ORM.png')).convert('RGB')
nrm = Image.open(os.path.join(OUT, 'normalGL.png')).convert('RGB')
a = np.asarray(orm)

cells = [
    ('baseColor 基础色贴图', '2048×2048 · 全部颜色信息都在这', bc),
    ('ORM 综合贴图', '2048×2048 · R遮蔽/G粗糙/B金属', orm),
    ('normalGL 法线贴图', '2048×2048 · 几乎全平(纯紫底)', nrm),
    ('R 通道 = 环境光遮蔽', 'min %d max %d' % (a[:, :, 0].min(), a[:, :, 0].max()),
     Image.fromarray(a[:, :, 0]).convert('RGB')),
    ('G 通道 = 粗糙度', 'min %d max %d' % (a[:, :, 1].min(), a[:, :, 1].max()),
     Image.fromarray(a[:, :, 1]).convert('RGB')),
    ('B 通道 = 金属度', 'min %d max %d · 基本为 0' % (a[:, :, 2].min(), a[:, :, 2].max()),
     Image.fromarray(a[:, :, 2]).convert('RGB')),
]

TS = 500
GAP = 14
LBL = 62
cols, rows = 3, 2
W = cols*TS + (cols+1)*GAP
H = rows*(TS + LBL) + (rows+1)*GAP
canvas = Image.new('RGB', (W, H), (250, 250, 252))
dr = ImageDraw.Draw(canvas)

for i, (title, sub, im) in enumerate(cells):
    c, r = i % cols, i//cols
    x = GAP + c*(TS + GAP)
    y = GAP + r*(TS + LBL + GAP)
    dr.rectangle([x, y, x+TS, y+LBL-6], fill=(31, 56, 100))
    dr.text((x+12, y+7), title, font=F, fill=(255, 255, 255))
    dr.text((x+12, y+34), sub, font=F2, fill=(180, 205, 240))
    canvas.paste(im.resize((TS, TS), Image.LANCZOS), (x, y+LBL))
    dr.rectangle([x, y+LBL, x+TS, y+LBL+TS], outline=(200, 200, 205))

p = os.path.join(BASE, 'original_textures_sheet.png')
canvas.save(p)
print('saved', p, canvas.size)
