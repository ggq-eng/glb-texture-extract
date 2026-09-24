# -*- coding: utf-8 -*-
"""解释"贴图图集为什么看着像乱码": 把模型部位 -> UV 分布 叠画在图集上"""
import os, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from collections import deque
import renderlib as R

BASE = r'C:\Users\<你的用户名>\WorkBuddy\2026-09-22-11-02-44\glb_extract'
TEX = os.path.join(BASE, 'original_textures')


def font(sz, bold=True):
    for p in ([r'C:\Windows\Fonts\msyhbd.ttc', r'C:\Windows\Fonts\msyh.ttc'] if bold
              else [r'C:\Windows\Fonts\msyh.ttc']):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


# ---------- 1. 文件完好性校验 ----------
print('=== 文件校验 ===')
for f in ['baseColor.png', 'metallicRoughness_ORM.png', 'normalGL.png']:
    p = os.path.join(TEX, f)
    im = Image.open(p)
    im.load()
    arr = np.asarray(im.convert('RGB'))
    print('%-28s %s %-5s  size=%8.1fKB  均值RGB=%s  非零占比=%.1f%%'
          % (f, im.size, im.mode, os.path.getsize(p)/1024,
             arr.reshape(-1, 3).mean(0).round(1),
             100.0*(arr.reshape(-1, 3).sum(1) > 12).mean()))

# ---------- 2. 取几何 + UV ----------
V, F, uv = R.load_mesh(glob.glob(BASE + r'\*.glb')[0],
                       os.path.join(BASE, 'mesh_cache.npz'), target_faces=200000)
cy = V[F][:, :, 1].mean(1)                 # 面重心 Y
ymin, ymax = cy.min(), cy.max()
span = ymax - ymin
HEAD = cy > ymax - 0.42*span               # 头部(含上段双马尾)
BOOT = cy < ymin + 0.11*span               # 靴子/脚
print('\n面数 %d, Y 范围 %.3f ~ %.3f' % (len(F), ymin, ymax))
print('头部面数 %d, 靴子面数 %d' % (HEAD.sum(), BOOT.sum()))

atl = Image.open(os.path.join(TEX, 'baseColor.png')).convert('RGB')
W, H = atl.size


def uv_to_px(u, v):
    """渲染器采样约定: 行 = (1-v)*H, 列 = u*W"""
    return u*W, (1.0-v)*H


def overlay(mask, rgb):
    """把选中面的 UV 三角形半透明叠画到图集上, 并估 UV 岛数量"""
    gray = atl.convert('L').point(lambda v: int(255 - (255-v)*0.20)).convert('RGB')
    ov = Image.new('RGBA', atl.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(ov)
    for k in np.nonzero(mask)[0]:
        p = [uv_to_px(uv[k, i, 0], uv[k, i, 1]) for i in range(3)]
        dr.polygon(p, fill=rgb + (215,))
    out = Image.alpha_composite(gray.convert('RGBA'), ov).convert('RGB')
    # UV 岛数量: 64x64 占据栅格 + 8 邻域连通分量
    g = np.zeros((64, 64), bool)
    for k in np.nonzero(mask)[0]:
        us = uv[k, :, 0]; vs = uv[k, :, 1]
        for i in range(3):
            x = int(np.clip(us[i]*63, 0, 63)); y = int(np.clip(vs[i]*63, 0, 63))
            g[y, x] = True
    seen = np.zeros_like(g); n = 0
    for y0 in range(64):
        for x0 in range(64):
            if g[y0, x0] and not seen[y0, x0]:
                n += 1; q = deque([(y0, x0)]); seen[y0, x0] = True
                while q:
                    y, x = q.popleft()
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            a, b = y+dy, x+dx
                            if 0 <= a < 64 and 0 <= b < 64 and g[a, b] and not seen[a, b]:
                                seen[a, b] = True; q.append((a, b))
    cover = g.mean()*100
    return out, n, cover


head_im, h_isl, h_cov = overlay(HEAD, (255, 40, 40))
boot_im, b_isl, b_cov = overlay(BOOT, (0, 200, 90))
print('头部: 估计 UV 岛 %d 个, 占据 UV 空间 %.1f%%' % (h_isl, h_cov))
print('靴子: 估计 UV 岛 %d 个, 占据 UV 空间 %.1f%%' % (b_isl, b_cov))

# ---------- 3. 拼成解释图 ----------
TS = 620
flat = Image.open(os.path.join(BASE, 'miku_front_flat.png')).convert('RGB')

bar = 92
gap = 16
cv = Image.new('RGB', (TS*3 + gap*4, TS + bar + gap*2), (250, 250, 252))
d = ImageDraw.Draw(cv)
panels = [
    ('① 图集原样（看着像乱码）', 'baseColor 贴图 2048×2048，直接看就是一堆碎色块', atl),
    ('② 红色 = 角色"头部"在图集上的位置', '头部被切成约 %d 块，散布全图 · 仅占图集 %.1f%%' % (h_isl, h_cov), head_im),
    ('③ 贴回模型 = 完整的 Q 版初音', '按 UV 坐标缝合回 3D 几何后，色块才归位', flat),
]
for i, (t1, t2, im) in enumerate(panels):
    x = gap + i*(TS + gap)
    d.rectangle([x, gap, x+TS, gap+bar-8], fill=(31, 56, 100))
    d.text((x+14, gap+10), t1, font=font(23), fill=(255, 255, 255))
    d.text((x+14, gap+45), t2, font=font(17, False), fill=(180, 205, 240))
    cv.paste(im.resize((TS, TS), Image.LANCZOS), (x, gap+bar))
p1 = os.path.join(BASE, 'why_texture_looks_garbled.png')
cv.save(p1)
print('\n已保存', p1, cv.size)

# 单独保存两张标注图集大图
head_im.save(os.path.join(TEX, 'baseColor_region_HEAD.png'))
boot_im.save(os.path.join(TEX, 'baseColor_region_BOOT.png'))
print('已保存 baseColor_region_HEAD.png / baseColor_region_BOOT.png')
