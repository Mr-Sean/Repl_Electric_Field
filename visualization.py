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

    def create_plot(self, field, show_field_lines=True, show_vectors=True):
        """
        Create the field visualization plot with animation

        Args:
            field (ElectricField): Electric field calculator
            show_field_lines (bool): Whether to show field lines
            show_vectors (bool): Whether to show field vectors

        Returns:
            go.Figure: Plotly figure object
        """
        # Calculate field on grid
        x_range = (-2, 2)
        y_range = (-2, 2)
        n_points = 20
        X, Y, Ex, Ey = field.calculate_field_grid(x_range, y_range, n_points)

        # Normalize field vectors
        E_magnitude = np.sqrt(Ex**2 + Ey**2)
        Ex_norm = Ex / (E_magnitude + 1e-10)
        Ey_norm = Ey / (E_magnitude + 1e-10)

        # Create initial frame data
        frame_data = []
        frames = []
        n_frames = 20

        if show_vectors:
            scale = 0.2  # Initial scale factor for arrow size
            for i in range(n_points):
                for j in range(n_points):
                    x_start = X[i,j]
                    y_start = Y[i,j]
                    dx = Ex_norm[i,j] * scale
                    dy = Ey_norm[i,j] * scale

                    # Arrow body
                    frame_data.append(go.Scatter(
                        x=[x_start, x_start + dx],
                        y=[y_start, y_start + dy],
                        mode='lines',
                        line=dict(color=self.colors['vectors'], width=1),
                        showlegend=False,
                        name=f'vector_{i}_{j}'
                    ))

        if show_field_lines:
            n_lines = 16
            theta = np.linspace(0, 2*np.pi, n_lines)

            for idx, th in enumerate(theta):
                x_start = field.position[0] + 0.1*np.cos(th)
                y_start = field.position[1] + 0.1*np.sin(th)

                x_line = [x_start]
                y_line = [y_start]

                for _ in range(50):
                    point = np.array([x_line[-1], y_line[-1]])
                    E = field.calculate_field_at_point(point)
                    E_norm = E / (np.linalg.norm(E) + 1e-10)

                    new_x = x_line[-1] + 0.1 * E_norm[0]
                    new_y = y_line[-1] + 0.1 * E_norm[1]

                    if abs(new_x) > 2 or abs(new_y) > 2:
                        break

                    x_line.append(new_x)
                    y_line.append(new_y)

                frame_data.append(go.Scatter(
                    x=x_line,
                    y=y_line,
                    mode='lines',
                    line=dict(
                        color=self.colors['positive'] if field.charge > 0 else self.colors['negative'],
                        width=1.5
                    ),
                    showlegend=False,
                    name=f'field_line_{idx}'
                ))

        # Add charge point
        frame_data.append(go.Scatter(
            x=[field.position[0]],
            y=[field.position[1]],
            mode='markers',
            marker=dict(
                size=15,
                color=self.colors['positive'] if field.charge > 0 else self.colors['negative']
            ),
            name='Point Charge'
        ))

        # Create figure with initial data
        fig = go.Figure(data=frame_data)

        # Create frames for animation
        for frame_idx in range(n_frames):
            frame_traces = []
            pulse_factor = 1 + 0.5 * np.sin(2 * np.pi * frame_idx / n_frames)

            if show_vectors:
                scale = 0.2 * pulse_factor
                for i in range(n_points):
                    for j in range(n_points):
                        x_start = X[i,j]
                        y_start = Y[i,j]
                        dx = Ex_norm[i,j] * scale
                        dy = Ey_norm[i,j] * scale

                        frame_traces.append(go.Scatter(
                            x=[x_start, x_start + dx],
                            y=[y_start, y_start + dy],
                            mode='lines',
                            line=dict(color=self.colors['vectors'], width=1),
                            showlegend=False,
                            name=f'vector_{i}_{j}'
                        ))

            if show_field_lines:
                for idx, th in enumerate(theta):
                    x_start = field.position[0] + 0.1*np.cos(th)
                    y_start = field.position[1] + 0.1*np.sin(th)

                    x_line = [x_start]
                    y_line = [y_start]

                    for _ in range(50):
                        point = np.array([x_line[-1], y_line[-1]])
                        E = field.calculate_field_at_point(point)
                        E_norm = E / (np.linalg.norm(E) + 1e-10)

                        new_x = x_line[-1] + 0.1 * E_norm[0]
                        new_y = y_line[-1] + 0.1 * E_norm[1]

                        if abs(new_x) > 2 or abs(new_y) > 2:
                            break

                        x_line.append(new_x)
                        y_line.append(new_y)

                    frame_traces.append(go.Scatter(
                        x=x_line,
                        y=y_line,
                        mode='lines',
                        line=dict(
                            color=self.colors['positive'] if field.charge > 0 else self.colors['negative'],
                            width=1.5 * pulse_factor
                        ),
                        showlegend=False,
                        name=f'field_line_{idx}'
                    ))

            # Add pulsating charge point
            frame_traces.append(go.Scatter(
                x=[field.position[0]],
                y=[field.position[1]],
                mode='markers',
                marker=dict(
                    size=15 * pulse_factor,
                    color=self.colors['positive'] if field.charge > 0 else self.colors['negative']
                ),
                name='Point Charge'
            ))

            frames.append(go.Frame(
                data=frame_traces,
                name=f'frame{frame_idx}'
            ))

        fig.frames = frames

        # Update layout with animation settings
        fig.update_layout(
            xaxis_title="X Position (m)",
            yaxis_title="Y Position (m)",
            xaxis=dict(range=x_range),
            yaxis=dict(range=y_range),
            showlegend=True,
            title="Electric Field Visualization",
            plot_bgcolor='white',
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
                        'frame': {'duration': 50, 'redraw': True},
                        'fromcurrent': True,
                        'transition': {'duration': 0}
                    }]
                }]
            }]
        )

        return fig