import glob, time, numpy as np, pymeshlab, os

GLB = glob.glob(r'C:\Users\<你的用户名>\WorkBuddy\2026-09-22-11-02-44\glb_extract\*.glb')[0]
CACHE = r'C:\Users\<你的用户名>\WorkBuddy\2026-09-22-11-02-44\glb_extract\mesh_cache.npz'
TARGET = 200000

if os.path.exists(CACHE):
    print('cache exists, skip decimation')
else:
    print('decimating to %d faces (UV-preserving)...' % TARGET)
    t = time.time()
    ms = pymeshlab.MeshSet()
    ms.load_new_mesh(GLB)
    ms.apply_filter('meshing_decimation_quadric_edge_collapse',
                    targetfacenum=TARGET,
                    preserveboundary=True,
                    preservenormal=True,
                    preservetopology=True,
                    optimalplacement=True,
                    autoclean=True)
    m = ms.current_mesh()
    V = m.vertex_matrix().astype(np.float32)
    F = m.face_matrix().astype(np.int32)
    uv = m.wedge_tex_coord_matrix().astype(np.float32).reshape(-1, 3, 2)
    np.savez_compressed(CACHE, V=V, F=F, uv=uv)
    print('  %.1fs  V=%d F=%d uv=%s  saved %s' % (time.time()-t, V.shape[0], F.shape[0], uv.shape, CACHE))

d = np.load(CACHE)
print('cache V', d['V'].shape, 'F', d['F'].shape, 'uv', d['uv'].shape)
