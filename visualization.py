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
        Create the field visualization plot

        Args:
            field (ElectricField): Electric field calculator
            show_field_lines (bool): Whether to show field lines
            show_vectors (bool): Whether to show field vectors

        Returns:
            go.Figure: Plotly figure object
        """
        # Create figure
        fig = go.Figure()

        # Calculate field on grid
        x_range = (-2, 2)
        y_range = (-2, 2)
        n_points = 20
        X, Y, Ex, Ey = field.calculate_field_grid(x_range, y_range, n_points)

        # Normalize field vectors
        E_magnitude = np.sqrt(Ex**2 + Ey**2)
        Ex_norm = Ex / (E_magnitude + 1e-10)
        Ey_norm = Ey / (E_magnitude + 1e-10)

        if show_vectors:
            # Create arrow vectors using scatter plots
            scale = 0.2  # Scale factor for arrow size

            for i in range(n_points):
                for j in range(n_points):
                    x_start = X[i,j]
                    y_start = Y[i,j]
                    dx = Ex_norm[i,j] * scale
                    dy = Ey_norm[i,j] * scale

                    # Arrow body
                    fig.add_trace(go.Scatter(
                        x=[x_start, x_start + dx],
                        y=[y_start, y_start + dy],
                        mode='lines',
                        line=dict(color=self.colors['vectors'], width=1),
                        showlegend=False
                    ))

                    # Arrow head
                    head_scale = 0.1
                    head_dx = dx * head_scale
                    head_dy = dy * head_scale

                    fig.add_trace(go.Scatter(
                        x=[x_start + dx, x_start + dx - head_dx - head_dy,
                           x_start + dx, x_start + dx - head_dx + head_dy],
                        y=[y_start + dy, y_start + dy - head_dy + head_dx,
                           y_start + dy, y_start + dy - head_dy - head_dx],
                        mode='lines',
                        line=dict(color=self.colors['vectors'], width=1),
                        showlegend=False
                    ))

        if show_field_lines:
            # Add field lines
            n_lines = 16
            theta = np.linspace(0, 2*np.pi, n_lines)

            for th in theta:
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

                fig.add_trace(go.Scatter(
                    x=x_line,
                    y=y_line,
                    mode='lines',
                    line=dict(color=self.colors['positive'] if field.charge > 0 else self.colors['negative']),
                    showlegend=False
                ))

        # Add charge point
        fig.add_trace(go.Scatter(
            x=[field.position[0]],
            y=[field.position[1]],
            mode='markers',
            marker=dict(
                size=15,
                color=self.colors['positive'] if field.charge > 0 else self.colors['negative']
            ),
            name='Point Charge'
        ))

        # Update layout
        fig.update_layout(
            xaxis_title="X Position (m)",
            yaxis_title="Y Position (m)",
            xaxis=dict(range=x_range),
            yaxis=dict(range=y_range),
            showlegend=True,
            title="Electric Field Visualization",
            plot_bgcolor='white'
        )

        return fig