import numpy as np
import trimesh
from scipy.ndimage import gaussian_filter
import qrcode

DOT_RADIUS   = 0.75
DOT_HEIGHT   = 0.6
CELL_SPACING = 6.0

BRAILLE_ALPHABET = {
    'a':0x01,'b':0x03,'c':0x09,'d':0x19,'e':0x11,
    'f':0x0B,'g':0x1B,'h':0x13,'i':0x0A,'j':0x1A,
    'k':0x05,'l':0x07,'m':0x0D,'n':0x1D,'o':0x15,
    'p':0x0F,'q':0x1F,'r':0x17,'s':0x0E,'t':0x1E,
    'u':0x25,'v':0x27,'w':0x3A,'x':0x2D,'y':0x3D,
    'z':0x35,' ':0x00,',':0x02,'.':0x32,
}


def _make_cylinder(cx, cy, radius, height, sections=12):
    angles = np.linspace(0, 2 * np.pi, sections, endpoint=False)
    top    = [[cx + radius*np.cos(a), cy + radius*np.sin(a), height] for a in angles]
    bottom = [[cx + radius*np.cos(a), cy + radius*np.sin(a), 0.0]   for a in angles]
    center_top    = [cx, cy, height]
    center_bottom = [cx, cy, 0.0]
    verts = top + bottom + [center_top, center_bottom]
    verts = np.array(verts, dtype='float32')
    n = sections
    faces = []
    for i in range(n):
        faces.append([2*n, i, (i+1) % n])
    for i in range(n):
        faces.append([2*n+1, n+(i+1)%n, n+i])
    for i in range(n):
        j = (i+1) % n
        faces.append([i, n+i, j])
        faces.append([j, n+i, n+j])
    return trimesh.Trimesh(vertices=verts, faces=np.array(faces))


def _braille_dots_for_text(text, x_offset, y_offset, base_z):
    meshes = []
    DOT_MAP = {0:(0,0),1:(0,1),2:(0,2),3:(1,0),4:(1,1),5:(1,2),6:(0,3),7:(1,3)}
    for ci, char in enumerate(text.lower()):
        bits = BRAILLE_ALPHABET.get(char, 0x00)
        cell_x = x_offset + ci * CELL_SPACING
        for bit in range(8):
            if bits & (1 << bit):
                col, row = DOT_MAP[bit]
                cx = cell_x + col * 2.5
                cy = y_offset + row * 2.5
                dot = _make_cylinder(cx, cy, DOT_RADIUS, base_z + DOT_HEIGHT)
                meshes.append(dot)
    return meshes


def _qr_dots(url, x_offset, y_offset, base_z, module_size=2.0):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=1, border=1)
    qr.add_data(url)
    qr.make(fit=True)
    matrix = qr.get_matrix()
    meshes = []
    for row_i, row in enumerate(matrix):
        for col_i, cell in enumerate(row):
            if cell:
                cx = x_offset + col_i * module_size + module_size/2
                cy = y_offset + (len(matrix)-row_i)*module_size - module_size/2
                dot = _make_cylinder(cx, cy, module_size*0.4, base_z+DOT_HEIGHT)
                meshes.append(dot)
    return meshes, len(matrix) * module_size


def generate_label_plate_stl(name, url, output_path,
                              base_thickness=2.5, module_size=2.0):
    qr_temp = qrcode.QRCode(version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=1, border=1)
    qr_temp.add_data(url)
    qr_temp.make(fit=True)
    matrix_size = len(qr_temp.get_matrix())
    qr_width    = matrix_size * module_size
    braille_chars = len(name)
    plate_width  = max(braille_chars * CELL_SPACING + 20, qr_width + 20)
    braille_h    = 14.0
    qr_h         = qr_width
    plate_height = braille_h + qr_h + 25
    base = trimesh.creation.box([plate_width, plate_height, base_thickness])
    base.apply_translation([plate_width/2, plate_height/2, base_thickness/2])
    meshes = [base]
    braille_x = 10.0
    braille_y = qr_h + 18
    meshes += _braille_dots_for_text(name, braille_x, braille_y, base_thickness)
    qr_x = (plate_width - qr_width) / 2
    qr_y = 8.0
    qr_meshes, _ = _qr_dots(url, qr_x, qr_y, base_thickness, module_size)
    meshes += qr_meshes
    combined = trimesh.util.concatenate(meshes)
    combined.export(output_path)
    return output_path


def depth_to_bas_relief(depth_map, output_path,
                        base_mm=3.0, relief_mm=8.0,
                        width_mm=100.0, smooth=1.5):
    depth = gaussian_filter(depth_map, sigma=smooth)
    h, w = depth.shape
    x_scale = width_mm / w
    y_scale = (width_mm * h / w) / h

    top_verts = []
    for row in range(h):
        for col in range(w):
            x = col * x_scale
            y = (h - row) * y_scale
            z = base_mm + depth[row, col] * relief_mm
            top_verts.append([x, y, z])

    bot_verts = [[v[0], v[1], 0.0] for v in top_verts]
    all_verts = np.array(top_verts + bot_verts, dtype='float32')
    off = h * w

    faces = []

    for row in range(h - 1):
        for col in range(w - 1):
            i = row * w + col
            faces.append([i, i + w, i + 1])
            faces.append([i + 1, i + w, i + w + 1])

    for row in range(h - 1):
        for col in range(w - 1):
            i = row * w + col + off
            faces.append([i, i + 1, i + w])
            faces.append([i + 1, i + w + 1, i + w])

    for row in range(h - 1):
        t0 = row * w
        t1 = (row + 1) * w
        b0 = t0 + off
        b1 = t1 + off
        faces.append([t0, b0, t1])
        faces.append([t1, b0, b1])

    for row in range(h - 1):
        t0 = row * w + (w - 1)
        t1 = (row + 1) * w + (w - 1)
        b0 = t0 + off
        b1 = t1 + off
        faces.append([t0, t1, b0])
        faces.append([t1, b1, b0])

    for col in range(w - 1):
        t0 = col
        t1 = col + 1
        b0 = t0 + off
        b1 = t1 + off
        faces.append([t0, t1, b0])
        faces.append([t1, b1, b0])

    for col in range(w - 1):
        t0 = (h - 1) * w + col
        t1 = (h - 1) * w + col + 1
        b0 = t0 + off
        b1 = t1 + off
        faces.append([t0, b0, t1])
        faces.append([t1, b0, b1])

    mesh = trimesh.Trimesh(
        vertices=all_verts,
        faces=np.array(faces, dtype='int64')
    )
    trimesh.repair.fix_normals(mesh)
    trimesh.repair.fix_winding(mesh)
    mesh.export(output_path)
    return output_path


def depth_to_lithophane(depth_map, output_path,
                        width_mm=100.0, min_thick=0.8,
                        max_thick=4.0, smooth=1.0):
    depth = gaussian_filter(depth_map, sigma=smooth)
    inverted = 1.0 - depth
    thickness = min_thick + inverted * (max_thick - min_thick)

    h, w = thickness.shape
    x_scale = width_mm / w
    y_scale = (width_mm * h / w) / h

    top_verts = []
    for row in range(h):
        for col in range(w):
            x = col * x_scale
            y = (h - row) * y_scale
            z = thickness[row, col]
            top_verts.append([x, y, z])

    bot_verts = [[v[0], v[1], 0.0] for v in top_verts]
    all_verts = np.array(top_verts + bot_verts, dtype='float32')
    off = h * w

    faces = []

    for row in range(h - 1):
        for col in range(w - 1):
            i = row * w + col
            faces.append([i, i + w, i + 1])
            faces.append([i + 1, i + w, i + w + 1])

    for row in range(h - 1):
        for col in range(w - 1):
            i = row * w + col + off
            faces.append([i, i + 1, i + w])
            faces.append([i + 1, i + w + 1, i + w])

    for row in range(h - 1):
        t0 = row * w
        t1 = (row + 1) * w
        b0 = t0 + off
        b1 = t1 + off
        faces.append([t0, b0, t1])
        faces.append([t1, b0, b1])

    for row in range(h - 1):
        t0 = row * w + (w - 1)
        t1 = (row + 1) * w + (w - 1)
        b0 = t0 + off
        b1 = t1 + off
        faces.append([t0, t1, b0])
        faces.append([t1, b1, b0])

    for col in range(w - 1):
        t0 = col
        t1 = col + 1
        b0 = t0 + off
        b1 = t1 + off
        faces.append([t0, t1, b0])
        faces.append([t1, b1, b0])

    for col in range(w - 1):
        t0 = (h - 1) * w + col
        t1 = (h - 1) * w + col + 1
        b0 = t0 + off
        b1 = t1 + off
        faces.append([t0, b0, t1])
        faces.append([t1, b0, b1])

    mesh = trimesh.Trimesh(
        vertices=all_verts,
        faces=np.array(faces, dtype='int64')
    )
    trimesh.repair.fix_normals(mesh)
    trimesh.repair.fix_winding(mesh)
    mesh.export(output_path)
    return output_path
