import numpy as np
from colorsys import hsv_to_rgb

from .constants import log

COLORS = {'red'    : [205,59,34],
          'purple' : [150,111,214],
          'blue'   : [119,158,203],
          'brown'  : [160,85,45]}
COLOR_DTYPE = np.uint8
DEFAULT_COLOR = COLORS['purple']

def random_color(dtype=COLOR_DTYPE):
    '''
    Return a random RGB color using datatype specified.
    '''
    hue  = np.random.random() + .61803
    hue %= 1.0
    color = np.array(hsv_to_rgb(hue, .99, .99))
    if np.dtype(dtype).kind in 'iu':
        max_value = (2**(np.dtype(dtype).itemsize * 8)) - 1
        color    *= max_value
    color     = color.astype(dtype)
    return color

def distinct_colors(dtype=COLOR_DTYPE, expected_length=50):
    '''
    Generator for colors 
    '''
    while True:
        yield random_color(dtype)

def average_color(a, b):
    result = (np.array(a) + b) / 2
    return result

def face_to_vertex_color(mesh, face_colors, dtype=COLOR_DTYPE):
    '''
    Convert a set of face colors into a set of vertex colors.
    '''
    
    color_dim = np.shape(face_colors)[1]


    vertex_colors = np.zeros((len(mesh.vertices),3,color_dim))
    population    = np.zeros((len(mesh.vertices),3), dtype=np.bool)

    vertex_colors[[mesh.faces[:,0],0]] = face_colors
    vertex_colors[[mesh.faces[:,1],1]] = face_colors
    vertex_colors[[mesh.faces[:,2],2]] = face_colors

    population[[mesh.faces[:,0], 0]] = True
    population[[mesh.faces[:,1], 1]] = True
    population[[mesh.faces[:,2], 2]] = True

    # clip the population sum to 1, to avoid a division error in edge cases
    populated     = np.clip(population.sum(axis=1), 1, 3)
    vertex_colors = vertex_colors.sum(axis=1) / populated.reshape((-1,1))
    return vertex_colors.astype(dtype)

class VisualAttributes(object):
    '''
    Hold the visual attributes (usually colors) for a mesh. 
    '''
    def __init__(self, mesh, **kwargs):
        self.mesh = mesh

        self._vertex_colors = None
        self._face_colors   = None

        if 'vertex_colors' in kwargs:
            self.vertex_colors = kwargs['vertex_colors']
        if 'face_colors' in kwargs:
            self.face_colors = kwargs['face_colors']

    @property
    def defined(self):
        return self._face_colors is not None

    @property
    def face_colors(self):
        ok = len(self._face_colors.shape) == 2
        ok = ok and len(self._face_colors) == len(self.mesh.faces)
        if not ok:
            log.warn('Faces being set to default color')
            self._face_colors = np.tile(DEFAULT_COLOR,
                                        (len(self.mesh.faces), 1))
        return self._face_colors

    @face_colors.setter
    def face_colors(self, values):
        if np.shape(values) == (3,):
            # case where a single RGB color has been passed to the setter
            # here we apply this color to all faces 
            self.face_colors = np.tile(values, 
                                       (len(self.mesh.faces), 1))
        else:
            self._face_colors = np.array(values)

    @property
    def vertex_colors(self):
        ok = len(self._vertex_colors.shape) == 2
        ok = ok and (len(self._vertex_colors) == len(self.mesh.vertices))
        if not ok:
            log.warn('Vertex colors being generated.')
            self._vertex_colors = face_to_vertex_color(self.mesh, 
                                                       self.face_colors)
        return self._vertex_colors

    @vertex_colors.setter
    def vertex_colors(self, values):
        self._vertex_colors = np.array(values)

    def update_faces(self, mask):
        try:
            self._face_colors = self._face_colors[mask]
        except: 
            log.warn('Face colors not updated')

    def update_vertices(self, mask):
        try:
            self._vertex_colors = self._vertex_colors[mask]
        except: 
            log.warn('Vertex colors not updated')
