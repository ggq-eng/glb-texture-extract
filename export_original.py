# -*- coding: utf-8 -*-
"""导出 GLB 内嵌的原始贴图 (原图), 并渲染一版"零光照纯原色"对照图"""
import glob, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, trimesh
from PIL import Image, ImageDraw
import renderlib as R

BASE = r'C:\Users\<你的用户名>\WorkBuddy\2026-09-22-11-02-44\glb_extract'
OUT = os.path.join(BASE, 'original_textures')
os.makedirs(OUT, exist_ok=True)
GLB = glob.glob(BASE + r'\*.glb')[0]

# ---------- 1. 模型元信息 ----------
scene = trimesh.load(GLB)
geoms = list(scene.geometry.values()) if hasattr(scene, 'geometry') else [scene]
g = geoms[0]
v = g.visual
mat = v.material
print('geometry      :', g.metadata.get('name', '(unnamed)'))
print('verts/faces   :', len(g.vertices), len(g.faces))
print('material name :', getattr(mat, 'name', None))
print('double_sided  :', getattr(mat, 'doubleSided', None))
print('baseColorFactor:', getattr(mat, 'baseColorFactor', None))
print('metallic/rough:', getattr(mat, 'metallicFactor', None), getattr(mat, 'roughnessFactor', None))

# ---------- 2. 导出内嵌贴图 ----------
def save(tex, name):
    if tex is None:
        print('  %-14s : (无)' % name); return None
    im = tex if isinstance(tex, Image.Image) else Image.fromarray(np.asarray(tex))
    im = im.convert('RGB')
    p = os.path.join(OUT, name + '.png')
    im.save(p)
    print('  %-14s : %s  %s' % (name, im.size, os.path.basename(p)))
    return im

print('\n内嵌贴图:')
bc  = save(getattr(mat, 'baseColorTexture', None), 'baseColor')
orm = save(getattr(mat, 'metallicRoughnessTexture', None), 'metallicRoughness_ORM')
nrm = save(getattr(mat, 'normalTexture', None), 'normalGL')
occ = getattr(mat, 'occlusionTexture', None)
if occ is not None:
    save(occ, 'occlusion')
srgb = getattr(mat, 'baseColorFactor', None)

# ORM 三通道拆解 (R=遮蔽 G=粗糙 B=金属)
if orm is not None:
    a = np.asarray(orm)
    ch = {'R_occlusion': a[:, :, 0], 'G_roughness': a[:, :, 1], 'B_metallic': a[:, :, 2]}
    strip = Image.new('RGB', (orm.width*3 + 40, orm.height), (255, 255, 255))
    dr = ImageDraw.Draw(strip)
    for i, (k, arr) in enumerate(ch.items()):
        x = i*(orm.width + 20)
        strip.paste(Image.fromarray(arr).convert('RGB'), (x, 0))
        dr.text((x+8, 8), '%s   min=%d max=%d' % (k, arr.min(), arr.max()), fill=(255, 80, 80))
    strip.save(os.path.join(OUT, 'ORM_channels.png'))
    print('  ORM 通道拆解   :', strip.size, '-> ORM_channels.png')

# ---------- 3. 贴图总览图 ----------
tiles = [('baseColor  (基础色 / 2048)', bc),
         ('metallicRoughness  ORM (2048)', orm),
         ('normalGL  (法线 / 2048)', nrm)]
tiles = [(n, t) for n, t in tiles if t is not None]
tsz = 512
sheet = Image.new('RGB', (tsz*len(tiles), tsz + 34), (255, 255, 255))
dr = ImageDraw.Draw(sheet)
for i, (n, t) in enumerate(tiles):
    sheet.paste(t.resize((tsz, tsz), Image.LANCZOS), (i*tsz, 34))
    dr.text((i*tsz + 10, 11), n, fill=(20, 20, 20))
sheet.save(os.path.join(BASE, 'original_textures_sheet.png'))
print('\n贴图总览:', sheet.size, '-> original_textures_sheet.png')

# ---------- 4. 零光照"原色"渲染 ----------
T = R.load_texture(GLB)
V, F, uvi = R.load_mesh(GLB, os.path.join(BASE, 'mesh_cache.npz'), target_faces=200000)
t = time.time()
flat = R.render(V, F, uvi, T, R.dvec(90, 8), (0, 1, 0), target=1000, ss=1.3,
                ambient=1.0, key=0.0, fill=0.0, rim=0.0)
flat.save(os.path.join(BASE, 'miku_albedo_flat.png'))
print('原色渲染 %.1fs -> miku_albedo_flat.png' % (time.time()-t))
