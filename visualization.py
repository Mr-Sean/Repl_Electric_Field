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
        # Create spherical grid with adaptive resolution
        radius = 2.0
        base_points = 15  # Reduced from 30 for better performance

        # Calculate grid points on sphere surface
        phi = np.linspace(0, 2*np.pi, base_points)
        theta = np.linspace(0, np.pi, base_points)
        phi, theta = np.meshgrid(phi, theta)

        # Convert to Cartesian coordinates
        x = radius * np.sin(theta) * np.cos(phi)
        y = radius * np.sin(theta) * np.sin(phi)
        z = radius * np.cos(theta)

        # Calculate field vectors with adaptive sampling
        vectors = []
        points = []

        # Calculate importance factor for each point
        for i in range(base_points):
            for j in range(base_points):
                point = np.array([x[i,j], y[i,j], z[i,j]])
                distance = np.linalg.norm(point - field.position)

                # Add more detail near the charge
                if distance < radius * 0.5:
                    # Calculate field at higher resolution near charge
                    n_detail = 2  # Subdivision factor
                    for di in range(n_detail):
                        for dj in range(n_detail):
                            # Interpolate position
                            fi = i + di/n_detail
                            fj = j + dj/n_detail
                            detail_point = np.array([
                                radius * np.sin(theta[0,0] + fi/base_points * np.pi) * np.cos(phi[0,0] + fj/base_points * 2*np.pi),
                                radius * np.sin(theta[0,0] + fi/base_points * np.pi) * np.sin(phi[0,0] + fj/base_points * 2*np.pi),
                                radius * np.cos(theta[0,0] + fi/base_points * np.pi)
                            ])
                            E = field.calculate_field_at_point(detail_point)
                            E_norm = E / (np.linalg.norm(E) + 1e-10)
                            vectors.append(E_norm)
                            points.append(detail_point.tolist())
                else:
                    # Use base resolution for points far from charge
                    E = field.calculate_field_at_point(point)
                    E_norm = E / (np.linalg.norm(E) + 1e-10)
                    vectors.append(E_norm)
                    points.append(point.tolist())

        # Create scene data
        scene_data = {
            'points': points,
            'vectors': vectors,
            'charge': {
                'position': field.position.tolist(),
                'value': field.charge,
            },
            'radius': radius,
            'showVectors': show_vectors,
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