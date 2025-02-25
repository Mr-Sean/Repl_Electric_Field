import numpy as np
import json
import streamlit as st

class FieldVisualizer:
    def __init__(self):
        """Initialize the field visualizer"""
        self.colors = {
            'positive': '#FF6B6B',
            'negative': '#4ECDC4',
            'vectors': '#2C3E50'
        }

    def create_scene(self, field, show_vectors=True):
        """Create the 3D visualization data"""
        # Calculate field on spherical grid
        radius = 2.0  # Sphere radius
        n_points = 20
        X, Y, Z, Ex, Ey, Ez = field.calculate_field_grid(radius, n_points)

        # Convert grid points and field vectors to lists
        points = []
        vectors = []
        for i in range(n_points):
            for j in range(n_points):
                point = [float(X[i,j]), float(Y[i,j]), float(Z[i,j])]
                E = [float(Ex[i,j]), float(Ey[i,j]), float(Ez[i,j])]

                # Normalize field vector
                E_mag = np.sqrt(sum(x*x for x in E))
                if E_mag > 1e-10:
                    E = [x/E_mag for x in E]
                else:
                    E = [0.0, 0.0, 0.0]

                points.append(point)
                vectors.append(E)

        # Create scene data with all values converted to standard Python types
        scene_data = {
            'points': points,
            'vectors': vectors,
            'charge': {
                'position': [float(x) for x in field.position],
                'value': float(field.charge),
            },
            'radius': float(radius),
            'showVectors': bool(show_vectors),
        }

        return scene_data

    def create_visualization(self, field, show_vectors=True):
        """Create the 3D visualization data"""
        scene_data = self.create_scene(field, show_vectors)
        return scene_data

# Example usage in a Streamlit app:
# (assuming you have a 'field' object defined elsewhere)

st.title("3D Electric Field Visualization")

# Dummy field object for demonstration
class DummyField:
    def __init__(self):
        self.position = np.array([0, 0, 0])
        self.charge = 1.0

    def calculate_field_at_point(self, point):
        distance = np.linalg.norm(point)
        if distance > 1e-6:
            return point / distance**3
        else:
            return np.array([0,0,0])

    def calculate_field_grid(self, radius, n_points):
        phi = np.linspace(0, 2*np.pi, n_points)
        theta = np.linspace(0, np.pi, n_points)
        phi, theta = np.meshgrid(phi, theta)
        x = radius * np.sin(theta) * np.cos(phi)
        y = radius * np.sin(theta) * np.sin(phi)
        z = radius * np.cos(theta)
        Ex = np.zeros((n_points,n_points))
        Ey = np.zeros((n_points,n_points))
        Ez = np.zeros((n_points,n_points))
        for i in range(n_points):
            for j in range(n_points):
                point = np.array([x[i,j],y[i,j],z[i,j]])
                E = self.calculate_field_at_point(point)
                Ex[i,j] = E[0]
                Ey[i,j] = E[1]
                Ez[i,j] = E[2]

        return x, y, z, Ex, Ey, Ez



field = DummyField()
visualizer = FieldVisualizer()
visualization_data = visualizer.create_visualization(field)

# Display the JSON output (you'll need to adapt this part to display it correctly in Streamlit)
st.write(visualization_data)

#Example of how to display in HTML using Streamlit
st.components.v1.html(
    f"""
    <div id="visualization"></div>
    <script>
      const sceneData = {json.dumps(visualization_data)};
      // Add your 3D visualization logic here using sceneData and a library like Three.js
    </script>
    """
)