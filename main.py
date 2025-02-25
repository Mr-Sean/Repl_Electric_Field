import streamlit as st
import numpy as np
from electric_field import ElectricField
from visualization import FieldVisualizer
from utils import format_scientific_notation

st.set_page_config(
    page_title="3D Electric Field Visualizer",
    layout="wide"
)

st.title("3D Electric Field Visualizer")

def main():
    # Sidebar controls
    st.sidebar.header("Controls")

    # Charge controls
    st.sidebar.subheader("Point Charge")
    charge = st.sidebar.number_input(
        "Charge (Coulombs)",
        value=1.0e-9,
        format="%.2e",
        help="Enter the charge value in Coulombs"
    )

    # 3D Position controls
    st.sidebar.subheader("Position (meters)")
    col1, col2, col3 = st.sidebar.columns(3)
    with col1:
        x_pos = st.number_input("X", value=0.0, step=0.1, max_value=2.0, min_value=-2.0)
    with col2:
        y_pos = st.number_input("Y", value=0.0, step=0.1, max_value=2.0, min_value=-2.0)
    with col3:
        z_pos = st.number_input("Z", value=0.0, step=0.1, max_value=2.0, min_value=-2.0)

    # Visualization controls
    st.sidebar.subheader("Visualization Settings")
    show_vectors = st.sidebar.checkbox("Show Field Vectors", value=True)

    # Create field calculator
    field = ElectricField(charge, (x_pos, y_pos, z_pos))

    # Create visualization
    visualizer = FieldVisualizer()

    # Main display area
    st.subheader("Electric Field Visualization")

    fig = visualizer.create_plot(
        field,
        show_vectors=show_vectors
    )
    st.plotly_chart(fig, use_container_width=True)

    # Field information
    st.subheader("Field Information")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Charge Properties**")
        st.write(f"Charge: {format_scientific_notation(charge)} C")
        st.write(f"Position: ({x_pos}, {y_pos}, {z_pos}) m")

    with col2:
        # Calculate field strength at origin for reference
        E_ref = field.calculate_field_at_point(np.array([0, 0, 0]))
        E_magnitude = np.linalg.norm(E_ref)
        st.markdown("**Field Properties**")
        st.write("Field strength at origin:")
        st.write(f"{format_scientific_notation(E_magnitude)} N/C")

if __name__ == "__main__":
    main()