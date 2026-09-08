# Build the muscle model for 一万日 from BodyParts3D (is-a tree, v4.0).
#   input : isa_BP3D_4.0_obj_99.zip, isa_element_parts.txt (same folder)
#   output: muscles.bin (custom binary, see below) + muscles.json (catalog)
# Binary: 'MUSC' | uint32 jsonLen | json | pad4 | uint16 positions (3/vertex, quantized to bbox) | uint16 indices
import zipfile, json, io, sys, struct, math
import numpy as np
import trimesh
import fast_simplification

HERE = sys.path[0]
ZIP = f'{HERE}/isa_BP3D_4.0_obj_99.zip'
ELEMENTS = f'{HERE}/isa_element_parts.txt'

# app id -> (ja, group, [FMA concept ids whose elements are merged])
MUSCLES = {
    'pectoralis_major':   ('大胸筋',        '胸',   ['FMA34686']),
    'pectoralis_minor':   ('小胸筋',        '胸',   ['FMA13109']),
    'serratus_anterior':  ('前鋸筋',        '胸',   ['FMA13397']),
    'deltoid_front':      ('三角筋 前部',    '肩',   ['FMA34677']),
    'deltoid_mid':        ('三角筋 中部',    '肩',   ['FMA34678']),
    'deltoid_rear':       ('三角筋 後部',    '肩',   ['FMA34679']),
    'supraspinatus':      ('棘上筋',        '肩',   ['FMA9629']),
    'infraspinatus':      ('棘下筋',        '肩',   ['FMA32546']),
    'teres_minor':        ('小円筋',        '肩',   ['FMA32550']),
    'subscapularis':      ('肩甲下筋',      '肩',   ['FMA13413']),
    'trapezius_upper':    ('僧帽筋 上部',    '背中', ['FMA32557']),
    'trapezius_middle':   ('僧帽筋 中部',    '背中', ['FMA32556']),
    'trapezius_lower':    ('僧帽筋 下部',    '背中', ['FMA32555']),
    'rhomboids':          ('菱形筋',        '背中', ['FMA13379', 'FMA13380']),
    'teres_major':        ('大円筋',        '背中', ['FMA32549']),
    'levator_scapulae':   ('肩甲挙筋',      '背中', ['FMA32519']),
    'erector_spinae':     ('脊柱起立筋',    '背中', ['FMA77177', 'FMA77178', 'FMA77179']),
    'biceps_brachii':     ('上腕二頭筋',    '腕',   ['FMA37682', 'FMA37683']),
    'brachialis':         ('上腕筋',        '腕',   ['FMA37667']),
    'coracobrachialis':   ('烏口腕筋',      '腕',   ['FMA37664']),
    'triceps_brachii':    ('上腕三頭筋',    '腕',   ['FMA37692', 'FMA37693', 'FMA37694']),
    'forearm_flexors':    ('前腕屈筋群',    '腕',   ['FMA38485', 'FMA38459', 'FMA38462', 'FMA38615', 'FMA38616', 'FMA38469', 'FMA38558', 'FMA38559']),
    'forearm_extensors':  ('前腕伸筋群',    '腕',   ['FMA38500', 'FMA38494', 'FMA38495', 'FMA38506']),
    'external_oblique':   ('外腹斜筋',      '腹筋', ['FMA13335']),
    'iliopsoas':          ('腸腰筋',        '腹筋', ['FMA18060', 'FMA22310']),
    'gluteus_maximus':    ('大臀筋',        '足',   ['FMA22314']),
    'gluteus_medius':     ('中臀筋',        '足',   ['FMA22315']),
    'gluteus_minimus':    ('小臀筋',        '足',   ['FMA22317']),
    'tensor_fasciae_latae': ('大腿筋膜張筋', '足',  ['FMA22423']),
    'rectus_femoris':     ('大腿直筋',      '足',   ['FMA22430']),
    'vastus_lateralis':   ('外側広筋',      '足',   ['FMA22431']),
    'vastus_medialis':    ('内側広筋',      '足',   ['FMA22432']),
    'vastus_intermedius': ('中間広筋',      '足',   ['FMA22433']),
    'biceps_femoris':     ('大腿二頭筋',    '足',   ['FMA45887', 'FMA45890']),
    'semitendinosus':     ('半腱様筋',      '足',   ['FMA22357']),
    'semimembranosus':    ('半膜様筋',      '足',   ['FMA22438']),
    'adductors':          ('内転筋群',      '足',   ['FMA22443', 'FMA22441', 'FMA22442', 'FMA43882', 'FMA22440']),
    'sartorius':          ('縫工筋',        '足',   ['FMA22353']),
    'gastrocnemius':      ('腓腹筋',        '足',   ['FMA45956', 'FMA45959']),
    'soleus':             ('ヒラメ筋',      '足',   ['FMA22542']),
    'tibialis_anterior':  ('前脛骨筋',      '足',   ['FMA22532']),
    'fibularis_longus':   ('長腓骨筋',      '足',   ['FMA22539']),
    'sternocleidomastoid': ('胸鎖乳突筋',   'その他', ['FMA13407']),
}
SKIN = 'FMA7163'
TOTAL_TRIS = 110000     # budget for all muscles (both sides)
SKIN_TRIS = 7000
MIN_TRIS = 400

# concept -> element ids (FJxxxx = right / unpaired, FJxxxxM = mirrored left)
elements = {}
for line in open(ELEMENTS, encoding='utf-8'):
    parts = line.rstrip('\n').split('\t')
    if len(parts) < 3 or not parts[0].startswith('FMA'): continue
    elements.setdefault(parts[0], []).append(parts[2].strip())

z = zipfile.ZipFile(ZIP)
zpaths = {n.split('/')[-1][:-4]: n for n in z.namelist() if n.endswith('.obj')}

def load_element(eid):
    if eid not in zpaths: return None
    data = z.read(zpaths[eid])
    m = trimesh.load(io.BytesIO(data), file_type='obj', process=True, force='mesh')
    if isinstance(m, trimesh.Scene):
        m = trimesh.util.concatenate([g for g in m.geometry.values()])
    return m

def decimate(m, target):
    if len(m.faces) <= target: return m
    v, f = fast_simplification.simplify(m.vertices.astype(np.float64), m.faces.astype(np.int64), target_count=target)
    out = trimesh.Trimesh(v, f, process=True)
    out.remove_unreferenced_vertices()
    return out

# 1) load everything
raw = {}   # (id, side) -> list of meshes
missing = []
for mid, (ja, group, fmas) in MUSCLES.items():
    for fma in fmas:
        els = elements.get(fma)
        if not els: missing.append((mid, fma)); continue
        for e in els:
            side = 'L' if e.endswith('M') else 'R'
            m = load_element(e)
            if m is None: missing.append((mid, fma, e)); continue
            raw.setdefault((mid, side), []).append(m)
print('missing:', missing)
merged = {}
for key, ms in raw.items():
    merged[key] = trimesh.util.concatenate(ms) if len(ms) > 1 else ms[0]
total_faces = sum(len(m.faces) for m in merged.values())
total_area = sum(m.area for m in merged.values())
print('muscle parts:', len(merged), 'faces before:', total_faces)

# 2) decimate by area share
out_meshes = []
for (mid, side), m in sorted(merged.items()):
    target = int(max(MIN_TRIS, TOTAL_TRIS * (m.area / total_area)))
    d = decimate(m, target)
    out_meshes.append((mid, side, d))
skin_el = elements.get(SKIN, [None])[0]
skin_full = load_element(skin_el)
skin = decimate(skin_full, SKIN_TRIS)
# --- proxies: BodyParts3D 4.0 has no latissimus dorsi / rectus abdominis.
# Cut the matching patch of skin, push it 5 mm inward, and mark it approximate.
def skin_patch(select, side_sign):
    c = skin_full.triangles_center; nrm = skin_full.face_normals
    keep = select(c, nrm) & ((c[:, 0] * side_sign) > 0)
    sub = skin_full.submesh([np.where(keep)[0]], append=True)
    sub = trimesh.Trimesh(sub.vertices - sub.vertex_normals * 5.0, sub.faces, process=True)
    return decimate(sub, 1300)
def sel_rectus(c, n):
    return (np.abs(c[:, 0]) <= 70) & (c[:, 2] >= 800) & (c[:, 2] <= 1105) & (c[:, 1] < -120) & (n[:, 1] < -0.2)
def sel_lats(c, n):
    ax = np.abs(c[:, 0]); z = c[:, 2]
    medial = 45 + (z - 960) / (1290 - 960) * (120 - 45)   # medial border slopes out toward the armpit
    zmin = 960 + (ax - 45) / 155 * 100                      # lower edge rises toward the flank (iliac crest -> side)
    return (z >= zmin) & (z <= 1290) & (ax >= medial) & (ax <= 200) & (c[:, 1] > -70) & (n[:, 1] > 0.15)
PROXIES = {'rectus_abdominis': ('腹直筋', '腹筋', sel_rectus), 'latissimus_dorsi': ('広背筋', '背中', sel_lats)}
for pid, (ja, group, sel) in PROXIES.items():
    for side, sign in (('R', -1), ('L', 1)):
        pm = skin_patch(sel, sign)
        print('proxy', pid, side, len(pm.faces), 'faces')
        out_meshes.append((pid, side, pm))
    MUSCLES[pid] = (ja, group, ['approx:skin'])
if skin is not None: out_meshes.append(('skin', 'C', skin))
print('faces after:', sum(len(m.faces) for _, _, m in out_meshes))

# 3) quantize into one bbox
allv = np.vstack([m.vertices for _, _, m in out_meshes])
lo, hi = allv.min(axis=0), allv.max(axis=0)
span = np.maximum(hi - lo, 1e-6)
pos_chunks, idx_chunks, meta = [], [], []
voff = ioff = 0
for mid, side, m in out_meshes:
    q = np.round((m.vertices - lo) / span * 65535).astype(np.uint16)
    idx = m.faces.astype(np.uint32).ravel()
    assert len(m.vertices) < 65536, (mid, side, len(m.vertices))
    pos_chunks.append(q.ravel()); idx_chunks.append(idx.astype(np.uint16))
    bb = m.bounds
    meta.append({'id': mid, 'side': side, 'v': voff, 'vn': len(m.vertices), 'i': ioff, 'in': len(idx),
                 'center': [float(x) for x in ((bb[0] + bb[1]) / 2)]})
    voff += len(m.vertices); ioff += len(idx)
positions = np.concatenate(pos_chunks); indices = np.concatenate(idx_chunks)
header = {'version': 1, 'lo': [float(x) for x in lo], 'span': [float(x) for x in span], 'unit': 'mm', 'meshes': meta,
          'source': 'BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International'}
hj = json.dumps(header, separators=(',', ':')).encode('utf-8')
pad = (4 - (len(hj) % 4)) % 4
with open(f'{HERE}/muscles.bin', 'wb') as f:
    f.write(b'MUSC'); f.write(struct.pack('<I', len(hj) + pad)); f.write(hj); f.write(b' ' * pad)
    f.write(positions.astype('<u2').tobytes()); f.write(indices.astype('<u2').tobytes())
catalog = [{'id': k, 'ja': v[0], 'group': v[1], 'fma': v[2], 'approx': v[2] == ['approx:skin']} for k, v in MUSCLES.items()]
json.dump({'muscles': catalog, 'attribution': header['source']}, open(f'{HERE}/muscles.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
import os
print('muscles.bin bytes:', os.path.getsize(f'{HERE}/muscles.bin'), 'lo', lo, 'hi', hi)
