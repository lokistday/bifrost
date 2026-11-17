"""Bake a textured, posed CC0 human and surface-sampled hologram particles.

Reads the MakeHuman core assets cached in output/. Browser assets are entirely
local and contain geometry/UVs/material data, not MakeHuman application code.
"""
from array import array
import base64
from bisect import bisect_left
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import random
import re
import struct
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'output/system-assets'
OUT = ROOT / 'assets/traveler'
OUT.mkdir(exist_ok=True)


def obj(path, body_only=False):
    positions, uvs, faces = [], [], []
    group = ''
    for line in path.read_text(encoding='utf-8-sig').splitlines():
        p = line.split()
        if not p:
            continue
        if p[0] == 'v':
            positions.append(tuple(map(float, p[1:4])))
        elif p[0] == 'vt':
            uvs.append(tuple(map(float, p[1:3])))
        elif p[0] == 'g':
            group = p[1]
        elif p[0] == 'f' and (not body_only or group == 'body'):
            face, tex = [], []
            for field in p[1:]:
                parts = field.split('/')
                face.append(int(parts[0]) - 1)
                tex.append(uvs[int(parts[1]) - 1])
            faces.append((face, tex))
    return positions, faces


base, base_faces = obj(ROOT / 'output/traveler-base.obj', True)
rig = json.loads((ROOT / 'output/traveler-rig.json').read_text(encoding='utf-8-sig'))
weights = json.loads((ROOT / 'output/traveler-weights.json').read_text(encoding='utf-8-sig'))['weights']
identity = [[float(i == j) for j in range(4)] for i in range(4)]


def multiply(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def transform(matrix, p):
    return tuple(sum(matrix[i][j] * p[j] for j in range(3)) + matrix[i][3] for i in range(3))


def rotation(pivot, angles):
    x, y, z = angles
    cx, sx, cy, sy, cz, sz = math.cos(x), math.sin(x), math.cos(y), math.sin(y), math.cos(z), math.sin(z)
    result = multiply([[cz,-sz,0,0],[sz,cz,0,0],[0,0,1,0],[0,0,0,1]], multiply(
        [[cy,0,sy,0],[0,1,0,0],[-sy,0,cy,0],[0,0,0,1]],
        [[1,0,0,0],[0,cx,-sx,0],[0,sx,cx,0],[0,0,0,1]]))
    for i in range(3):
        result[i][3] = pivot[i] - sum(result[i][j] * pivot[j] for j in range(3))
    return result


pose = {
    'upperarm01.L': (.10,-.04,-.23), 'lowerarm01.L': (.38,0,.04),
    'upperarm01.R': (.12,.03,.36), 'lowerarm01.R': (.27,0,-.04),
    'upperleg01.L': (-.13,0,-.14), 'lowerleg01.L': (.47,0,0),
    'upperleg01.R': (.015,0,.11), 'lowerleg01.R': (.16,0,0),
    'foot.L': (.18,0,0), 'foot.R': (.26,0,0),
    'spine02': (.025,.025,-.008), 'head': (.02,-.025,0)
}
for side in ['L', 'R']:
    for finger in range(2, 6):
        for joint, angle in [(1,-.13),(2,-.20),(3,-.10)]:
            pose[f'finger{finger}-{joint}.{side}'] = (angle,0,0)
matrices = {}


def head(name):
    ids = rig['joints'][rig['bones'][name]['head']]
    return tuple(sum(base[index][i] for index in ids) / len(ids) for i in range(3))


def matrix(name):
    if name not in matrices:
        parent = rig['bones'][name]['parent']
        matrices[name] = multiply(matrix(parent) if parent else identity, rotation(head(name), pose.get(name,(0,0,0))))
    return matrices[name]


influences = defaultdict(dict)
for bone, members in weights.items():
    matrix(bone)
    for index, weight in members:
        if weight > 0:
            influences[index][bone] = weight


def skin(p, members):
    total = sum(members.values())
    if total < .00001:
        return p
    transformed = [(transform(matrices[name],p), weight / total) for name, weight in members.items()]
    return tuple(sum(point[i] * weight for point, weight in transformed) for i in range(3))


def finger_weight(members):
    return min(1, sum(weight for name, weight in members.items() if name.startswith('finger')))


body_posed = [skin(p, influences[i]) for i, p in enumerate(base)]
visible_ids = {i for face,_ in base_faces for i in face}
low = min(body_posed[i][1] for i in visible_ids)
high = max(body_posed[i][1] for i in visible_ids)
scale, center = 3.4 / (high - low), (high + low) / 2


def normalize(p):
    return (p[0] * scale, (p[1] - center) * scale, p[2] * scale)


def proxy(stem):
    original, faces = obj(RAW / (stem + '.obj'))
    mapping, deleted = [], set()
    scales = [1.,1.,1.]
    mode = ''
    for line in (RAW / (stem + '.mhclo')).read_text(encoding='utf-8-sig').splitlines():
        p = line.split()
        if not p or p[0].startswith('#'):
            continue
        if p[0] in ['x_scale','y_scale','z_scale']:
            axis = ['x_scale','y_scale','z_scale'].index(p[0])
            scales[axis] = abs(base[int(p[1])][axis] - base[int(p[2])][axis]) / float(p[3])
        elif p[0] == 'verts':
            mode = 'verts'
        elif p[0] == 'delete_verts':
            mode = 'delete'
        elif mode == 'verts' and p[0][0].isdigit():
            if len(p) == 1:
                mapping.append(([int(p[0])],[1.],[0.,0.,0.]))
            elif len(p) >= 9:
                mapping.append((list(map(int,p[:3])),list(map(float,p[3:6])),list(map(float,p[6:9]))))
        elif mode == 'delete':
            tokens = re.findall(r'\d+|-',line)
            index = 0
            while index < len(tokens):
                first = int(tokens[index])
                if index + 2 < len(tokens) and tokens[index + 1] == '-':
                    deleted.update(range(first,int(tokens[index + 2]) + 1)); index += 3
                else:
                    deleted.add(first); index += 1
    assert len(original) == len(mapping), (stem,len(original),len(mapping))
    points, rest, motion = [], [], []
    for refs, factors, offset in mapping:
        p = tuple(sum(base[ref][axis] * factor for ref, factor in zip(refs,factors)) + offset[axis] * scales[axis] for axis in range(3))
        members = defaultdict(float)
        for ref, factor in zip(refs,factors):
            for bone, weight in influences[ref].items():
                members[bone] += factor * weight
        members = {bone:max(0,weight) for bone, weight in members.items()}
        if sum(members.values()) < .0001:
            closest = min(visible_ids,key=lambda i:sum((base[i][axis]-p[axis])**2 for axis in range(3)))
            members = influences[closest]
        points.append(normalize(skin(p,members)))
        rest.append(p)
        motion.append(finger_weight(members))
    return points,rest,motion,faces,deleted


cloth,cloth_rest,cloth_motion,cloth_faces,deleted = proxy('male_casualsuit01')
eyes,eye_rest,eye_motion,eye_faces,_ = proxy('high-poly')
body_data = [normalize(body_posed[i]) + base[i] + (finger_weight(influences[i]),) for i in range(len(base))]


def average(points):
    return tuple(sum(p[i] for p in points) / len(points) for i in range(len(points[0])))


def subdivide(points, faces):
    """One Catmull-Clark step, including face-varying UVs, before visible-face filtering."""
    face_points = [average([points[i] for i in face]) for face,_ in faces]
    edge_faces = defaultdict(list)
    vertex_faces = defaultdict(list)
    vertex_edges = defaultdict(set)
    for fi,(face,_) in enumerate(faces):
        for j,index in enumerate(face):
            edge = tuple(sorted((index,face[(j+1)%len(face)])))
            edge_faces[edge].append(fi)
            vertex_faces[index].append(fi)
            vertex_edges[index].add(edge)
            vertex_edges[face[(j+1)%len(face)]].add(edge)
    result = list(points)
    for index, connected in vertex_faces.items():
        p = points[index]
        boundary = [b if a == index else a for (a,b) in vertex_edges[index] if len(edge_faces[(a,b)]) == 1]
        if len(boundary) >= 2:
            result[index] = tuple(.75*p[axis]+.125*sum(points[n][axis] for n in boundary[:2]) for axis in range(len(p)))
        else:
            f = average([face_points[i] for i in connected])
            e = average([average([points[a],points[b]]) for a,b in vertex_edges[index]])
            n = len(connected)
            result[index] = tuple((f[axis]+2*e[axis]+(n-3)*p[axis])/n for axis in range(len(p)))
    edge_ids = {}
    for edge, linked in edge_faces.items():
        edge_ids[edge] = len(result)
        result.append(average([points[i] for i in edge] + ([face_points[i] for i in linked] if len(linked) == 2 else [])))
    face_offset = len(result)
    result.extend(face_points)
    refined = []
    for fi,(face,uvs) in enumerate(faces):
        uv_center = average(uvs)
        covered = all(index in deleted for index in face)
        if covered:
            continue
        for j,index in enumerate(face):
            next_index,previous_index = face[(j+1)%len(face)],face[(j-1)%len(face)]
            refined.append(([index,edge_ids[tuple(sorted((index,next_index)))],face_offset+fi,edge_ids[tuple(sorted((previous_index,index)))]],
                [uvs[j],average([uvs[j],uvs[(j+1)%len(face)]]),uv_center,average([uvs[(j-1)%len(face)],uvs[j]])]))
    return result,refined


body_data,body_faces = subdivide(body_data,base_faces)
body = [p[:3] for p in body_data]
body_rest = [p[3:6] for p in body_data]
body_motion = [p[6] for p in body_data]


def dot(a,b):
    return sum(x*y for x,y in zip(a,b))


def cross(a,b):
    return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])


def unit(p):
    length = math.sqrt(dot(p,p)) or 1
    return tuple(value/length for value in p)


records,triangles = [],[]
for material,(points,rest,motion,faces) in enumerate([(body,body_rest,body_motion,body_faces),(cloth,cloth_rest,cloth_motion,cloth_faces),(eyes,eye_rest,eye_motion,eye_faces)]):
    normals = [[0.,0.,0.] for _ in points]
    neighbors = defaultdict(set)
    for face,_ in faces:
        for j in range(1,len(face)-1):
            ids = [face[0],face[j],face[j+1]]
            a,b,c = (points[index] for index in ids)
            n = cross(tuple(b[k]-a[k] for k in range(3)),tuple(c[k]-a[k] for k in range(3)))
            for index in ids:
                for k in range(3): normals[index][k] += n[k]
                neighbors[index].update(ids)
    normals = [unit(n) for n in normals]
    curvature = []
    for i,n in enumerate(normals):
        linked = neighbors[i] - {i}
        curvature.append(min(1.,math.sqrt(sum(max(0,1-dot(n,normals[j])) for j in linked)/max(1,len(linked)))*2.5))
    lookup = {}
    tangents,bitangents = {},{}
    for face,uvs in faces:
        ids = []
        for index,uv in zip(face,uvs):
            key = (index,round(uv[0],7),round(uv[1],7))
            if key not in lookup:
                region = 4 if material == 2 else 3 if material == 1 else 1 if rest[index][1] > 5.65 else 2 if abs(rest[index][0]) > 3.55 else 0
                lookup[key] = len(records)
                records.append({'p':points[index],'n':normals[index],'uv':uv,'material':material,'region':region,'crease':curvature[index],'motion':motion[index]})
                tangents[len(records)-1] = [0.,0.,0.]
                bitangents[len(records)-1] = [0.,0.,0.]
            ids.append(lookup[key])
        for j in range(1,len(ids)-1):
            tri = (ids[0],ids[j],ids[j+1]); triangles.append(tri)
            a,b,c = (records[i] for i in tri)
            e1 = tuple(b['p'][k]-a['p'][k] for k in range(3)); e2 = tuple(c['p'][k]-a['p'][k] for k in range(3))
            du1,dv1 = b['uv'][0]-a['uv'][0],b['uv'][1]-a['uv'][1]
            du2,dv2 = c['uv'][0]-a['uv'][0],c['uv'][1]-a['uv'][1]
            determinant = du1*dv2-du2*dv1
            factor = 1/determinant if abs(determinant) > 1e-10 else 0
            for i in tri:
                for k in range(3):
                    tangents[i][k] += (e1[k]*dv2-e2[k]*dv1)*factor
                    bitangents[i][k] += (e2[k]*du1-e1[k]*du2)*factor
    for i,t in tangents.items():
        n = records[i]['n']; projection = dot(n,t)
        tangent = unit(tuple(t[k]-n[k]*projection for k in range(3)))
        if dot(tangent,tangent) < .1: tangent = unit(cross(n,(0,1,0)))
        sign = -1 if dot(cross(n,tangent),bitangents[i]) < 0 else 1
        records[i]['t'] = tangent + (sign,)

textures = {}
for name,source_name,size in [
    ('skin','young_lightskinned_male_diffuse.png',2048),
    ('cloth','male_casualsuit01_diffuse.png',2048),
    ('eyes','grey_eye.png',1024)
]:
    image = Image.open(RAW/source_name).convert('RGB')
    image.thumbnail((size,size),Image.Resampling.LANCZOS)
    image.save(OUT/(name+'.webp'),quality=94,method=6)
    textures[name] = image
normal = Image.open(RAW/'male_casualsuit01_normal.png').convert('RGB').resize((1024,1024),Image.Resampling.LANCZOS)
ao = Image.open(RAW/'male_casualsuit01_ao.png').convert('L').resize((1024,1024),Image.Resampling.LANCZOS)
normal.putalpha(ao)
normal.save(OUT/'cloth-surface.webp',lossless=True,method=6)


def texture_sample(material,uv):
    image = textures[['skin','cloth','eyes'][material]]
    x = max(1,min(image.width-2,round(uv[0]*(image.width-1))))
    y = max(1,min(image.height-2,round((1-uv[1])*(image.height-1))))
    rgb = image.getpixel((x,y))
    luma = sum(a*b for a,b in zip(rgb,(.24,.52,.24)))/255
    edge = sum(abs(rgb[k]-image.getpixel((x+1,y))[k])+abs(rgb[k]-image.getpixel((x,y+1))[k]) for k in range(3))/765
    return luma,edge


rng = random.Random(7829)
pdf,weighted_triangles,total = [],[],0.
for tri in triangles:
    a,b,c = (records[i] for i in tri)
    area = math.sqrt(dot(cross(tuple(b['p'][k]-a['p'][k] for k in range(3)),tuple(c['p'][k]-a['p'][k] for k in range(3))),cross(tuple(b['p'][k]-a['p'][k] for k in range(3)),tuple(c['p'][k]-a['p'][k] for k in range(3)))))/2
    if area < 1e-10: continue
    uv = average([a['uv'],b['uv'],c['uv']]); luma,edge = texture_sample(a['material'],uv)
    detail = 2.8 if a['region'] in [1,4] else 4.4 if a['region'] == 2 else 1.
    crease = sum(records[i]['crease'] for i in tri)/3
    total += area*(detail+crease*2.5+min(2.,edge*9))*(.65+luma*.35)
    pdf.append(total);weighted_triangles.append(tri)
particles = []
for _ in range(26000):
    tri = weighted_triangles[min(len(pdf)-1,bisect_left(pdf,rng.random()*total))]
    a,b,c = (records[i] for i in tri)
    root = math.sqrt(rng.random()); q = rng.random()
    bary = (1-root,root*(1-q),root*q)
    particle = dict(a)
    for key in ['p','n','uv','t']:
        particle[key] = tuple(sum(records[index][key][k]*weight for index,weight in zip(tri,bary)) for k in range(len(a[key])))
    particle['n'] = unit(particle['n'])
    for key in ['crease','motion']:
        particle[key] = sum(records[index][key]*weight for index,weight in zip(tri,bary))
    particles.append(particle)


def packed(record,particle=False):
    p,n,uv = record['p'],record['n'],record['uv']
    data = struct.pack('<3h3b4Bx2H',*(round(value*8192) for value in p),*(max(-127,min(127,round(value*127))) for value in n),
        record['material'],record['region'],round(record['crease']*255),round(record['motion']*255),
        *(max(0,min(65535,round(value*65535))) for value in uv))
    if not particle:
        data += struct.pack('<4b',*(max(-127,min(127,round(value*127))) for value in record['t']))
    return data+struct.pack('<H',rng.randrange(65536))


index_width = 2 if len(records) <= 65535 else 4
indices = struct.pack('<'+('H' if index_width == 2 else 'I')*(len(triangles)*3),*(i for tri in triangles for i in tri))
asset = {
    'version':3,'license':'CC0-1.0','vertexCount':len(records),'indexCount':len(triangles)*3,'indexBytes':index_width,
    'vertexStride':24,'particleStride':20,'particleCount':len(particles),
    'vertices':base64.b64encode(b''.join(packed(v) for v in records)).decode(),
    'indices':base64.b64encode(indices).decode(),
    'particles':base64.b64encode(b''.join(packed(v,True) for v in particles)).decode(),
    'landmarks':{'head':[0,1.38,.05],'leftHand':list(normalize(transform(matrix('wrist.L'),head('wrist.L')))),
        'rightHand':list(normalize(transform(matrix('wrist.R'),head('wrist.R'))))},
    'sources':['MakeHuman hm08 base mesh and default rig','MakeHuman system CC0 assets: male_casualsuit01, young_caucasian_male, high-poly eyes'],
}
digest = hashlib.sha256()
for name in ['skin.webp','cloth.webp','eyes.webp','cloth-surface.webp']:
    digest.update((OUT/name).read_bytes())
asset['textureVersion'] = digest.hexdigest()[:12]
(ROOT/'js/hologram-mesh.js').write_text('/* Textured, posed CC0 human; structural surface particles. */\nwindow.BifrostHologramMesh='+json.dumps(asset,separators=(',',':'))+';\n',encoding='utf-8')
summary = {'vertices':len(records),'triangles':len(triangles),'particles':len(particles),'indexBytes':index_width,
    'headParticles':sum(v['region'] in [1,4] for v in particles),'handParticles':sum(v['region']==2 for v in particles),
    'textures':{p.name:p.stat().st_size for p in OUT.glob('*.webp')}}
(ROOT/'output/hologram-asset-report.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
