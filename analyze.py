import struct, json, os

GLB = r'C:\Users\<你的用户名>\WorkBuddy\2026-09-22-11-02-44\glb_extract\20260907225145_爱给网_aigei_com.glb'
# 文件名含中文，用glob定位
import glob
cands = glob.glob(r'C:\Users\<你的用户名>\WorkBuddy\2026-09-22-11-02-44\glb_extract\*.glb')
GLB = cands[0]
print('GLB 路径:', GLB)
print('GLB 大小:', os.path.getsize(GLB), 'bytes')

with open(GLB, 'rb') as f:
    data = f.read()

# GLB header
magic, version, total_len = struct.unpack('<4sII', data[:12])
print('magic:', magic, 'version:', version, 'declared total len:', total_len, 'actual:', len(data))

# parse chunks
off = 12
chunks = []
while off < len(data):
    clen, ctype = struct.unpack('<II', data[off:off+8])
    cdata = data[off+8:off+8+clen]
    chunks.append((ctype, cdata))
    off += 8 + clen

glb_json = None
glb_bin = None
for ctype, cdata in chunks:
    if ctype == 0x4E4F534A:  # JSON
        glb_json = json.loads(cdata.decode('utf-8'))
    elif ctype == 0x004E4942:  # BIN
        glb_bin = cdata

g = glb_json
print('\n=== glTF 基本信息 ===')
print('asset:', g.get('asset'))
print('generator:', g.get('asset', {}).get('generator'))
print('scenes:', len(g.get('scenes', [])))
print('nodes:', len(g.get('nodes', [])))
print('meshes:', len(g.get('meshes', [])))
print('materials:', len(g.get('materials', [])))
print('textures:', len(g.get('textures', [])))
print('images:', len(g.get('images', [])))
print('accessors:', len(g.get('accessors', [])))
print('bufferViews:', len(g.get('bufferViews', [])))
print('animations:', len(g.get('animations', [])))
print('skins:', len(g.get('skins', [])))
print('cameras:', len(g.get('cameras', [])))
print('extensionsUsed:', g.get('extensionsUsed'))
print('extensionsRequired:', g.get('extensionsRequired'))

# accessor component type sizes
CT = {5120:1,5121:1,5122:2,5123:2,5125:4,5126:4}
NC = {5120:'BYTE',5121:'UNSIGNED_BYTE',5122:'SHORT',5123:'UNSIGNED_SHORT',5125:'UNSIGNED_INT',5126:'FLOAT'}

# compute vertices & triangles per mesh primitive
print('\n=== 网格/几何统计 ===')
total_verts = 0
total_tris = 0
for mi, mesh in enumerate(g.get('meshes', [])):
    name = mesh.get('name', f'mesh_{mi}')
    for pi, prim in enumerate(mesh.get('primitives', [])):
        mode = prim.get('mode', 4)
        attrs = prim.get('attributes', {})
        pos_acc = prim.get('attributes', {}).get('POSITION')
        idx_acc = prim.get('indices')
        vcount = 0
        if pos_acc is not None:
            ac = g['accessors'][pos_acc]
            vcount = ac.get('count', 0)
        tcount = 0
        if idx_acc is not None:
            iac = g['accessors'][idx_acc]
            ic = iac.get('count', 0)
            tcount = ic // 3 if mode == 4 else 0
        elif pos_acc is not None:
            tcount = vcount // 3 if mode == 4 else 0
        total_verts += vcount
        total_tris += tcount
        mat = prim.get('material')
        matname = g['materials'][mat]['name'] if (mat is not None and g.get('materials')) else None
        print(f'  [{mi}] {name} prim{pi}: verts={vcount} tris={tcount} mode={mode} mat={matname}')

print(f'\n合计: 顶点≈{total_verts}  三角形≈{total_tris}')

# bounds from POSITION accessors min/max
print('\n=== 包围盒 (POSITION min/max) ===')
xs=[];ys=[];zs=[]
for ac in g.get('accessors', []):
    if ac.get('type')=='VEC3' and 'min' in ac and 'max' in ac and ac.get('componentType')==5126:
        xs += ac['min'][:1]+ac['max'][:1]
        ys += ac['min'][1:2]+ac['max'][1:2]
        zs += ac['min'][2:3]+ac['max'][2:3]
if xs:
    print(f'  X: [{min(xs):.3f}, {max(xs):.3f}]')
    print(f'  Y: [{min(ys):.3f}, {max(ys):.3f}]')
    print(f'  Z: [{min(zs):.3f}, {max(zs):.3f}]')

# images detail
print('\n=== 贴图/图像 ===')
for ii, img in enumerate(g.get('images', [])):
    uri = img.get('uri')
    bufv = img.get('bufferView')
    mime = img.get('mimeType')
    if bufv is not None:
        bv = g['bufferViews'][bufv]
        size = bv.get('byteLength', 0)
    else:
        size = '(外部uri)'
    print(f'  img{ii}: name={img.get("name")} mime={mime} bufView={bufv} bytes={size} uri={uri}')

# materials summary
print('\n=== 材质 ===')
for mi2, mat in enumerate(g.get('materials', [])):
    pbr = mat.get('pbrMetallicRoughness', {})
    base = pbr.get('baseColorTexture')
    nrml = mat.get('normalTexture')
    emi = mat.get('emissiveTexture')
    print(f'  mat{mi2}: name={mat.get("name")} baseColorTex={base.get("index") if base else None} normalTex={nrml.get("index") if nrml else None} emissiveTex={emi.get("index") if emi else None} alphaMode={mat.get("alphaMode")} doubleSided={mat.get("doubleSided")}')

# animations summary
print('\n=== 动画 ===')
for ai, anim in enumerate(g.get('animations', [])):
    chs = anim.get('channels', [])
    samps = anim.get('samplers', [])
    dur = 0
    for s in samps:
        in_acc = g['accessors'][s.get('input')]
        mx = in_acc.get('max')
        if mx: dur = max(dur, mx[0])
    print(f'  anim{ai}: name={anim.get("name")} channels={len(chs)} samplers={len(samps)} 时长≈{dur:.3f}s')

# node tree depth / names
print('\n=== 场景节点 ===')
def walk(node_idx, depth, g):
    n = g['nodes'][node_idx]
    nm = n.get('name','?')
    kids = n.get('children', [])
    indent='  '*depth
    mesh = n.get('mesh')
    skin = n.get('skin')
    print(f'{indent}- {nm}  mesh={mesh} skin={skin} children={len(kids)}')
    for k in kids:
        walk(k, depth+1, g)
for si, scene in enumerate(g.get('scenes', [])):
    print(f'scene{si}: name={scene.get("name")} nodes={scene.get("nodes")}')
    for n0 in scene.get('nodes', []):
        walk(n0, 1, g)
