"""Bake a floating pose from MakeHuman's CC0 hm08 mesh and rig assets.

Source files: output/traveler-{base.obj,rig.json,weights.json}.
These are graphical assets, not MakeHuman application source code.
"""
import base64
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]
vertices = []
faces = []
group = ''
source = ROOT / 'output/traveler-base.obj'
for line in source.read_text(encoding='utf-8-sig').splitlines():
    fields = line.split()
    if not fields:
        continue
    if fields[0] == 'v':
        vertices.append(tuple(map(float, fields[1:4])))
    elif fields[0] == 'g':
        group = fields[1]
    elif fields[0] == 'f' and group == 'body':
        face = [int(value.split('/')[0]) - 1 for value in fields[1:]]
        faces.extend((face[0], face[i], face[i + 1]) for i in range(1, len(face) - 1))
rig = json.loads((ROOT / 'output/traveler-rig.json').read_text(encoding='utf-8-sig'))
weights = json.loads((ROOT / 'output/traveler-weights.json').read_text(encoding='utf-8-sig'))['weights']
identity = [[float(row == column) for column in range(4)] for row in range(4)]


def multiply(a, b):
    return [[sum(a[row][k] * b[k][column] for k in range(4)) for column in range(4)] for row in range(4)]


def transform(matrix, point):
    return tuple(sum(matrix[row][column] * point[column] for column in range(3)) + matrix[row][3] for row in range(3))


def pivot_rotation(point, angles):
    x, y, z = angles
    cx, sx, cy, sy, cz, sz = math.cos(x), math.sin(x), math.cos(y), math.sin(y), math.cos(z), math.sin(z)
    rx = [[1,0,0,0],[0,cx,-sx,0],[0,sx,cx,0],[0,0,0,1]]
    ry = [[cy,0,sy,0],[0,1,0,0],[-sy,0,cy,0],[0,0,0,1]]
    rz = [[cz,-sz,0,0],[sz,cz,0,0],[0,0,1,0],[0,0,0,1]]
    result = multiply(rz, multiply(ry, rx))
    for row in range(3):
        result[row][3] = point[row] - sum(result[row][column] * point[column] for column in range(3))
    return result


pose = {
    'upperarm01.L': (.18, -.08, .26), 'lowerarm01.L': (.66, 0, .09),
    'upperarm01.R': (.25, .05, .12), 'lowerarm01.R': (.40, 0, -.06),
    'upperleg01.L': (-.30, 0, -.20), 'lowerleg01.L': (.95, 0, 0),
    'upperleg01.R': (.01, 0, .13), 'lowerleg01.R': (.25, 0, 0),
    'foot.L': (.18, 0, 0), 'foot.R': (.45, 0, 0),
    'spine02': (.035, .04, -.015), 'head': (.025, -.025, 0),
}
matrices = {}


def bone_head(name):
    ids = rig['joints'][rig['bones'][name]['head']]
    return tuple(sum(vertices[index][axis] for index in ids) / len(ids) for axis in range(3))


def bone_matrix(name):
    if name not in matrices:
        parent = rig['bones'][name]['parent']
        inherited = bone_matrix(parent) if parent else identity
        local = pivot_rotation(bone_head(name), pose.get(name, (0, 0, 0)))
        matrices[name] = multiply(inherited, local)
    return matrices[name]


used = sorted({index for face in faces for index in face})
influences = defaultdict(list)
for bone, members in weights.items():
    matrix = bone_matrix(bone)
    for index, weight in members:
        if weight > 0:
            influences[index].append((matrix, weight))
posed = []
for index in used:
    members = influences[index]
    total = sum(weight for _, weight in members)
    if not total:
        posed.append(vertices[index])
        continue
    samples = [(transform(matrix, vertices[index]), weight / total) for matrix, weight in members]
    posed.append(tuple(sum(point[axis] * weight for point, weight in samples) for axis in range(3)))
minimum = min(point[1] for point in posed)
maximum = max(point[1] for point in posed)
scale = 3.4 / (maximum - minimum)
center = (minimum + maximum) / 2
posed = [(point[0] * scale, (point[1] - center) * scale, point[2] * scale) for point in posed]
remap = {original: index for index, original in enumerate(used)}
triangles = [tuple(remap[index] for index in face) for face in faces]
normals = [[0., 0., 0.] for _ in posed]
for face in triangles:
    a, b, c = (posed[index] for index in face)
    u, v = [b[i] - a[i] for i in range(3)], [c[i] - a[i] for i in range(3)]
    normal = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
    for index in face:
        for axis in range(3):
            normals[index][axis] += normal[axis]
packed_vertices = bytearray()
for point, normal in zip(posed, normals):
    length = math.sqrt(sum(value * value for value in normal)) or 1
    packed_vertices += struct.pack('<3h3bx', *(round(value * 8192) for value in point), *(round(value / length * 127) for value in normal))
packed_indices = struct.pack('<' + 'H' * (len(triangles) * 3), *(index for face in triangles for index in face))
anchors = []
for name in ['wrist.L', 'wrist.R', 'foot.L', 'foot.R', 'spine03']:
    p = transform(bone_matrix(name), bone_head(name))
    anchors.append([round(p[0] * scale, 5), round((p[1] - center) * scale, 5), round(p[2] * scale, 5)])
asset = {
    'license': 'CC0-1.0',
    'source': 'https://github.com/makehumancommunity/makehuman/tree/master/makehuman/data',
    'sourceSha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'vertexCount': len(posed), 'indexCount': len(triangles) * 3, 'anchors': anchors,
    'vertices': base64.b64encode(packed_vertices).decode('ascii'),
    'indices': base64.b64encode(packed_indices).decode('ascii'),
}
destination = ROOT / 'js/traveler-mesh.js'
destination.write_text('/* Posed anatomical mesh derived from MakeHuman CC0 graphical assets. */\nwindow.BifrostTravelerMesh=' + json.dumps(asset, separators=(',', ':')) + ';\n', encoding='utf-8')
print(f'Baked {len(posed):,} vertices, {len(triangles):,} triangles; {destination.stat().st_size:,} bytes.')
