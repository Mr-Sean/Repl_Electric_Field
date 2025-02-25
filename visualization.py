import numpy as np
import plotly.graph_objects as go
import time

class FieldVisualizer:
    def __init__(self):
        """Initialize the field visualizer"""
        self.colors = {
            'positive': '#FF6B6B',
            'negative': '#4ECDC4',
            'neutral': '#95A5A6',
            'vectors': '#2C3E50'
        }

    def create_plot(self, field, show_vectors=True):
        """
        Create the 3D field visualization plot with continuous animation

        Args:
            field (ElectricField): Electric field calculator
            show_vectors (bool): Whether to show field vectors

        Returns:
            go.Figure: Plotly figure object
        """
        # Calculate field on spherical grid
        radius = 2.0  # Sphere radius
        n_points = 20
        X, Y, Z, Ex, Ey, Ez = field.calculate_field_grid(radius, n_points)

        # Normalize field vectors
        E_magnitude = np.sqrt(Ex**2 + Ey**2 + Ez**2)
        Ex_norm = Ex / (E_magnitude + 1e-10)
        Ey_norm = Ey / (E_magnitude + 1e-10)
        Ez_norm = Ez / (E_magnitude + 1e-10)

        # Create data list for the figure
        data = []

        # Calculate current animation phase based on time
        t = time.time()
        pulse_factor = 1 + 0.3 * np.sin(2 * np.pi * t)

        if show_vectors:
            scale = 0.2 * pulse_factor  # Scale factor for arrow size
            for i in range(n_points):
                for j in range(n_points):
                    x_start = X[i,j]
                    y_start = Y[i,j]
                    z_start = Z[i,j]
                    dx = Ex_norm[i,j] * scale
                    dy = Ey_norm[i,j] * scale
                    dz = Ez_norm[i,j] * scale

                    # 3D arrow
                    data.append(go.Scatter3d(
                        x=[x_start, x_start + dx],
                        y=[y_start, y_start + dy],
                        z=[z_start, z_start + dz],
                        mode='lines',
                        line=dict(color=self.colors['vectors'], width=2 * pulse_factor),
                        showlegend=False
                    ))

        # Add charge point
        data.append(go.Scatter3d(
            x=[field.position[0]],
            y=[field.position[1]],
            z=[field.position[2]],
            mode='markers',
            marker=dict(
                size=15 * pulse_factor,
                color=self.colors['positive'] if field.charge > 0 else self.colors['negative']
            ),
            name='Point Charge'
        ))

        # Create figure
        fig = go.Figure(data=data)

        # Update layout with 3D settings
        fig.update_layout(
            scene=dict(
                xaxis_title="X Position (m)",
                yaxis_title="Y Position (m)",
                zaxis_title="Z Position (m)",
                aspectmode='cube',
                camera=dict(
                    up=dict(x=0, y=0, z=1),
                    center=dict(x=0, y=0, z=0),
                    eye=dict(x=1.5, y=1.5, z=1.5)
                )
            ),
            showlegend=True,
            title="3D Electric Field Visualization"
        )

        return fig