# Geodesic sphere generation using pyDome-inspired logic
# Adapted for Fusion 360
import math
import adsk.core
import adsk.fusion

class GeodesicCalculator:
    def __init__(self, radius, frequency):
        self.radius = radius
        self.frequency = frequency
        self.points = []
        self.faces = []

    def calculate(self):
        """Generate geodesic sphere using icosahedron subdivision"""
        # Create icosahedron
        ico_verts, ico_faces = self._create_icosahedron()
        
        # Subdivide each face
        all_verts = []
        all_faces = []
        
        for face_idx, face in enumerate(ico_faces):
            v0 = ico_verts[face[0]]
            v1 = ico_verts[face[1]]
            v2 = ico_verts[face[2]]
            
            # Subdivide this face into a grid
            face_verts, face_faces = self._subdivide_triangle(v0, v1, v2, self.frequency)
            
            # Offset face vertex indices
            offset = len(all_verts)
            all_verts.extend(face_verts)
            all_faces.extend([(f[0] + offset, f[1] + offset, f[2] + offset) for f in face_faces])
        
        # Merge duplicate vertices (vertices that are very close)
        self.points, self.faces = self._merge_duplicates(all_verts, all_faces)
        
        # Convert to Point3D objects
        self.points = [adsk.core.Point3D.create(p[0], p[1], p[2]) for p in self.points]

    def _create_icosahedron(self):
        """Create icosahedron vertices and faces"""
        # Using pyDome's approach with sine/cosine of phi
        sine_of_phi = 2.0 / math.sqrt(5.0)
        cosine_of_phi = 0.5 * sine_of_phi
        PI = math.pi
        
        verts = [
            (0.0, 0.0, 1.0),
            (sine_of_phi, 0.0, cosine_of_phi),
            (sine_of_phi * math.cos(0.4*PI), sine_of_phi * math.sin(0.4*PI), cosine_of_phi),
            (sine_of_phi * math.cos(0.8*PI), sine_of_phi * math.sin(0.8*PI), cosine_of_phi),
            (sine_of_phi * math.cos(0.8*PI), -sine_of_phi * math.sin(0.8*PI), cosine_of_phi),
            (sine_of_phi * math.cos(0.4*PI), -sine_of_phi * math.sin(0.4*PI), cosine_of_phi),
            (-sine_of_phi * math.cos(0.8*PI), -sine_of_phi * math.sin(0.8*PI), -cosine_of_phi),
            (-sine_of_phi * math.cos(0.8*PI), sine_of_phi * math.sin(0.8*PI), -cosine_of_phi),
            (-sine_of_phi * math.cos(0.4*PI), sine_of_phi * math.sin(0.4*PI), -cosine_of_phi),
            (-sine_of_phi, 0.0, -cosine_of_phi),
            (-sine_of_phi * math.cos(0.4*PI), -sine_of_phi * math.sin(0.4*PI), -cosine_of_phi),
            (0.0, 0.0, -1.0)
        ]
        
        # Normalize and scale vertices
        verts = [self._normalize_and_scale(v) for v in verts]
        
        # Icosahedron faces (pyDome ordering)
        faces = [
            (1, 2, 0), (2, 3, 0), (3, 4, 0), (4, 5, 0), (5, 1, 0),
            (5, 6, 1), (1, 7, 2), (2, 8, 3), (3, 9, 4), (4, 10, 5),
            (1, 6, 7), (2, 7, 8), (3, 8, 9), (4, 9, 10), (5, 10, 6),
            (6, 11, 7), (7, 11, 8), (8, 11, 9), (9, 11, 10), (10, 11, 6)
        ]
        
        return verts, faces

    def _subdivide_triangle(self, v0, v1, v2, freq):
        """Subdivide a triangle into smaller triangles"""
        verts = []
        faces = []
        vert_map = {}
        
        # Build grid of vertices
        grid = []
        for i in range(freq + 1):
            row = []
            for j in range(freq + 1 - i):
                # Barycentric coordinates
                if freq > 0:
                    a = i / freq
                    b = j / freq
                else:
                    a = 0
                    b = 0
                c = 1 - a - b
                
                # Interpolate position
                x = a * v0[0] + b * v1[0] + c * v2[0]
                y = a * v0[1] + b * v1[1] + c * v2[1]
                z = a * v0[2] + b * v1[2] + c * v2[2]
                
                # Project to sphere
                pt = self._normalize_and_scale((x, y, z))
                
                # Add to vertex list
                key = tuple(round(coord, 8) for coord in pt)
                if key not in vert_map:
                    vert_map[key] = len(verts)
                    verts.append(pt)
                
                row.append(vert_map[key])
            grid.append(row)
        
        # Create faces from grid
        for i in range(freq):
            for j in range(freq - i):
                # First triangle
                vA = grid[i][j]
                vB = grid[i + 1][j]
                vC = grid[i][j + 1]
                faces.append((vA, vB, vC))
                
                # Second triangle (if not at edge)
                if j < freq - i - 1:
                    vD = grid[i + 1][j + 1]
                    faces.append((vB, vD, vC))
        
        return verts, faces

    def _normalize_and_scale(self, v):
        """Normalize vector and scale to radius"""
        x, y, z = v
        length = math.sqrt(x*x + y*y + z*z)
        if length == 0:
            return (0, 0, 0)
        return (
            self.radius * x / length,
            self.radius * y / length,
            self.radius * z / length
        )

    def _merge_duplicates(self, verts, faces):
        """Merge duplicate vertices that are very close together"""
        threshold = 1e-6
        vert_map = {}
        unique_verts = []
        
        for i, v in enumerate(verts):
            # Round to avoid floating point issues
            key = tuple(round(coord, 8) for coord in v)
            
            if key not in vert_map:
                vert_map[i] = len(unique_verts)
                unique_verts.append(v)
            else:
                # Map to existing vertex
                vert_map[i] = vert_map[key] if isinstance(vert_map[key], int) else vert_map[key]
        
        # Create vertex mapping
        final_map = {}
        for i in range(len(verts)):
            key = tuple(round(coord, 8) for coord in verts[i])
            if key not in final_map:
                final_map[key] = len(unique_verts)
                unique_verts.append(verts[i])
        
        # Rebuild with correct mapping
        unique_verts = []
        index_map = {}
        for i, v in enumerate(verts):
            key = tuple(round(coord, 8) for coord in v)
            if key not in index_map:
                index_map[key] = len(unique_verts)
                unique_verts.append(v)
            
        # Remap faces
        new_faces = []
        for face in faces:
            v0_key = tuple(round(coord, 8) for coord in verts[face[0]])
            v1_key = tuple(round(coord, 8) for coord in verts[face[1]])
            v2_key = tuple(round(coord, 8) for coord in verts[face[2]])
            
            new_face = (index_map[v0_key], index_map[v1_key], index_map[v2_key])
            # Avoid degenerate triangles
            if new_face[0] != new_face[1] and new_face[1] != new_face[2] and new_face[0] != new_face[2]:
                new_faces.append(new_face)
        
        return unique_verts, new_faces

    def get_fusion360_points(self):
        return self.points

    def get_faces(self):
        return self.faces
