import numpy as np
import plotly.graph_objects as go

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
        Create the 3D field visualization plot with animation

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

        # Create initial frame data
        frame_data = []
        frames = []
        n_frames = 60  # Increased frame count for smoother animation

        if show_vectors:
            scale = 0.2  # Initial scale factor for arrow size
            for i in range(n_points):
                for j in range(n_points):
                    x_start = X[i,j]
                    y_start = Y[i,j]
                    z_start = Z[i,j]
                    dx = Ex_norm[i,j] * scale
                    dy = Ey_norm[i,j] * scale
                    dz = Ez_norm[i,j] * scale

                    # 3D arrow
                    frame_data.append(go.Scatter3d(
                        x=[x_start, x_start + dx],
                        y=[y_start, y_start + dy],
                        z=[z_start, z_start + dz],
                        mode='lines',
                        line=dict(color=self.colors['vectors'], width=2),
                        showlegend=False
                    ))

        # Add charge point
        frame_data.append(go.Scatter3d(
            x=[field.position[0]],
            y=[field.position[1]],
            z=[field.position[2]],
            mode='markers',
            marker=dict(
                size=15,
                color=self.colors['positive'] if field.charge > 0 else self.colors['negative']
            ),
            name='Point Charge'
        ))

        # Create frames for animation
        for frame_idx in range(n_frames):
            frame_traces = []
            # Smoother pulsation using sine wave
            pulse_factor = 1 + 0.3 * np.sin(2 * np.pi * frame_idx / n_frames)

            for trace in frame_data:
                # Create new trace with updated properties
                new_trace = go.Scatter3d(
                    x=trace.x,
                    y=trace.y,
                    z=trace.z,
                    mode=trace.mode,
                    showlegend=trace.showlegend,
                    name=trace.name
                )

                if trace.name == 'Point Charge':
                    new_trace.marker = dict(
                        size=15 * pulse_factor,
                        color=trace.marker.color
                    )
                else:
                    new_trace.line = dict(
                        color=trace.line.color,
                        width=2 * pulse_factor
                    )

                frame_traces.append(new_trace)

            frames.append(go.Frame(
                data=frame_traces,
                name=f'frame{frame_idx}'
            ))

        # Create figure with initial data
        fig = go.Figure(data=frame_data)
        fig.frames = frames

        # Update layout with animation and 3D settings
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
            title="3D Electric Field Visualization",
            updatemenus=[{
                'type': 'buttons',
                'showactive': False,
                'x': 0.1,
                'y': 0,
                'xanchor': 'right',
                'yanchor': 'top',
                'buttons': [{
                    'label': 'Play',
                    'method': 'animate',
                    'args': [None, {
                        'frame': {'duration': 30, 'redraw': True},  # Faster frame rate
                        'fromcurrent': True,
                        'transition': {'duration': 0},
                        'mode': 'immediate',
                        'loop': True  # Enable continuous looping
                    }]
                }]
            }]
        )

        return fig