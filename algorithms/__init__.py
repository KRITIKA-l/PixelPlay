from .dda import dda_line
from .bresenham import bresenham_line, polygon_outline
from .midpoint_circle import midpoint_circle
from .bresenham_circle import bresenham_circle
from .polar_circle import polar_circle
from .boundary_fill import boundary_fill
from .flood_fill import flood_fill
from .scanline_fill import scanline_fill
from .transform2d import translation, scaling, rotation, reflection, composite
from .transform3d import transform3d
from .line_clipping import cohen_sutherland
from .cyrus_beck import cyrus_beck
from .polygon_clipping import sutherland_hodgman
from .curves import bezier_curve, bspline_curve, hermite_curve
# Unit 6: hidden surfaces, images, illumination, shading, shadows
from .zbuffer import zbuffer
from .backface import backface_culling
from .area_subdivision import area_subdivision
from .scanline_hsr import scanline_hsr
from .image_filter import image_filter
from .image_geometry import image_geometry
from .illumination import illumination
from .shading import shade_triangle
from .transparency import transparency
from .shadows import shadows