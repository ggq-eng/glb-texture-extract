import glob, numpy as np, trimesh
glb = glob.glob(r'C:\Users\<你的用户名>\WorkBuddy\2026-09-22-11-02-44\glb_extract\*.glb')[0]
m = trimesh.load(glb)
print('type:', type(m))
if hasattr(m,'geometry'):
    print('scene, geometries:', list(m.geometry.keys()))
    m = list(m.geometry.values())[0]
print('vertices:', m.vertices.shape, 'faces:', m.faces.shape)
print('visual type:', type(m.visual))
if hasattr(m.visual,'uv') and m.visual.uv is not None:
    print('uv shape:', m.visual.uv.shape)
mat = getattr(m.visual,'material',None)
print('material type:', type(mat))
if mat is not None:
    for k in ['baseColorTexture','baseColorFactor','normalTexture','metallicRoughnessTexture','occlusionTexture']:
        v=getattr(mat,k,None)
        print(' ',k,':', type(v), (v.size if hasattr(v,'size') else v))

# 测试减面是否保留 uv
m2 = m.simplify_quadric_decimation(face_count=120000)
print('\n--- 减面后 ---')
print('faces:', m2.faces.shape, 'verts:', m2.vertices.shape)
print('visual type:', type(m2.visual))
if hasattr(m2.visual,'uv') and m2.visual.uv is not None:
    print('uv preserved shape:', m2.visual.uv.shape)
else:
    print('uv: NONE after decimation')
