import json, glob, struct, os

cands = glob.glob(r'C:\Users\<你的用户名>\WorkBuddy\2026-09-22-11-02-44\glb_extract\*.glb')
GLB = cands[0]
with open(GLB,'rb') as f:
    data = f.read()
off=12; chunks=[]
while off<len(data):
    clen,ctype=struct.unpack('<II',data[off:off+8])
    chunks.append((ctype,data[off+8:off+8+clen]))
    off+=8+clen
g=json.loads([c for c in chunks if c[0]==0x4E4F534A][0][1].decode('utf-8'))
bin_=[c for c in chunks if c[0]==0x004E4942][0][1]

prim = g['meshes'][0]['primitives'][0]
print('=== primitive 属性 ===')
for attr,acc in prim.get('attributes',{}).items():
    a=g['accessors'][acc]
    print(f'  {attr}: type={a.get("type")} count={a.get("count")} ctype={a.get("componentType")}')
print('  indices accessor:', prim.get('indices'))

print('\n=== 贴图分辨率(解析JPEG头) ===')
def jpeg_size(b):
    i=2
    while i<len(b):
        if b[i]!=0xFF: i+=1; continue
        m=b[i+1]
        if m in (0xC0,0xC1,0xC2,0xC3):
            h=struct.unpack('>H',b[i+5:i+7])[0]
            w=struct.unpack('>H',b[i+7:i+9])[0]
            return w,h
        seg=struct.unpack('>H',b[i+2:i+4])[0]
        i+=2+seg
    return None
for img in g.get('images',[]):
    bv=g['bufferViews'][img['bufferView']]
    b=bin_[bv['byteOffset']:bv['byteOffset']+bv['byteLength']]
    sz=jpeg_size(b)
    print(f'  {img.get("name")}: {sz}  ({bv["byteLength"]} bytes)')

# 总BIN占用、texture bufferViews是否含mip/分辨率分布
print('\n=== 几何精度判断 ===')
pos=g['accessors'][prim['attributes']['POSITION']]
print('顶点数:', pos['count'])
print('包围盒边长: 2.0 (已归一化到单位立方体)')
print('平均每个三角形边间距估算(对角线方向):', round((2.0/ (pos['count']**0.3333)),4))
