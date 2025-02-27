import streamlit as st
import numpy as np
import json
from electric_field import ElectricField
from visualization import FieldVisualizer
from utils import format_scientific_notation

st.set_page_config(page_title="3D Electric Field Visualizer", layout="wide")

st.title("3D Electric Field Visualizer")


def main():
    # Sidebar controls
    st.sidebar.header("Controls")

    # Charge controls
    st.sidebar.subheader("Point Charge")
    charge = st.sidebar.number_input("Charge (Coulombs)",
                                     value=1.0e-9,
                                     format="%.2e",
                                     help="Enter the charge value in Coulombs")

    # Position controls
    st.sidebar.subheader("Position (meters)")
    col1, col2, col3 = st.sidebar.columns(3)
    with col1:
        x_pos = st.number_input("X",
                                value=0.0,
                                step=0.1,
                                max_value=2.0,
                                min_value=-2.0)
    with col2:
        y_pos = st.number_input("Y",
                                value=0.0,
                                step=0.1,
                                max_value=2.0,
                                min_value=-2.0)
    with col3:
        z_pos = st.number_input("Z",
                                value=0.0,
                                step=0.1,
                                max_value=2.0,
                                min_value=-2.0)

    # Visualization controls
    st.sidebar.subheader("Visualization Settings")
    show_vectors = st.sidebar.checkbox("Show Field Vectors", value=True)

    # Create field calculator
    field = ElectricField(charge, (x_pos, y_pos, z_pos))

    # Create visualization
    visualizer = FieldVisualizer()
    scene_data = visualizer.create_scene(field, show_vectors=show_vectors)

    # Display the 3D visualization
    st.components.v1.html(f"""
        <div id="container" style="width: 100%; height: 600px;"></div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script>
            /* Initialize Three.js scene with WebGL2 */
            const container = document.getElementById('container');
            const renderer = new THREE.WebGLRenderer({{
                antialias: true,
                powerPreference: "high-performance",
                precision: "highp"
            }});
            renderer.setPixelRatio(window.devicePixelRatio);
            renderer.setSize(container.clientWidth, container.clientHeight);
            container.appendChild(renderer.domElement);

            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0x111111);

            const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);

            /* Load scene data */
            const sceneData = {json.dumps(scene_data)};

            /* Create charge sphere with glow */
            const chargeGeometry = new THREE.SphereGeometry(0.15, 32, 32);
            const chargeMaterial = new THREE.MeshPhongMaterial({{
                color: sceneData.charge.value > 0 ? 0xFF6B6B : 0x4ECDC4,
                shininess: 100,
                emissive: sceneData.charge.value > 0 ? 0xFF6B6B : 0x4ECDC4,
                emissiveIntensity: 0.5
            }});
            const charge = new THREE.Mesh(chargeGeometry, chargeMaterial);
            charge.position.set(...sceneData.charge.position);
            scene.add(charge);

            /* Create optimized vector field */
            if (sceneData.showVectors) {{
                /* Create instanced mesh for arrows */
                const coneGeometry = new THREE.ConeBufferGeometry(0.05, 0.2, 8);
                const coneMaterial = new THREE.MeshPhongMaterial({{ color: 0x2C3E50 }});
                const arrows = new THREE.InstancedMesh(
                    coneGeometry,
                    coneMaterial,
                    sceneData.points.length
                );

                /* Set up matrix and quaternion for transformations */
                const matrix = new THREE.Matrix4();
                const quaternion = new THREE.Quaternion();
                const up = new THREE.Vector3(0, 1, 0);

                /* Initialize arrow instances */
                sceneData.points.forEach((point, i) => {{
                    const position = new THREE.Vector3(...point);
                    const direction = new THREE.Vector3(...sceneData.vectors[i]);

                    quaternion.setFromUnitVectors(up, direction.normalize());
                    matrix.makeRotationFromQuaternion(quaternion);
                    matrix.setPosition(position);

                    arrows.setMatrixAt(i, matrix);
                }});

                scene.add(arrows);
            }}

            /* Add lights */
            const light = new THREE.DirectionalLight(0xffffff, 1);
            light.position.set(5, 5, 5);
            scene.add(light);
            scene.add(new THREE.AmbientLight(0x404040));

            /* Set up camera */
            camera.position.set(6, 6, 6);
            camera.lookAt(0, 0, 0);

            /* Animation loop with performance optimization */
            let animationFrame;
            let lastTime = performance.now();
            const targetFPS = 60;
            const frameInterval = 1000 / targetFPS;

            function animate(currentTime) {{
                animationFrame = requestAnimationFrame(animate);

                /* Throttle to target FPS */
                const deltaTime = currentTime - lastTime;
                if (deltaTime < frameInterval) return;

                /* Update last frame time */
                lastTime = currentTime - (deltaTime % frameInterval);

                /* Smooth rotation */
                const time = currentTime * 0.001;
                const radius = 8;
                camera.position.x = radius * Math.cos(time * 0.3);
                camera.position.z = radius * Math.sin(time * 0.3);
                camera.lookAt(0, 0, 0);

                /* Smooth pulsing */
                if (sceneData.showVectors) {{
                    const scale = 1 + 0.2 * Math.sin(time * 2);
                    scene.children[1].scale.set(scale, scale, scale);
                }}

                /* Update charge glow */
                charge.material.emissiveIntensity = 0.3 + 0.2 * Math.sin(time * 2);

                renderer.render(scene, camera);
            }}

            /* Start animation */
            animate(performance.now());

            /* Handle window resize */
            let resizeTimeout;
            window.addEventListener('resize', () => {{
                if (resizeTimeout) clearTimeout(resizeTimeout);
                resizeTimeout = setTimeout(() => {{
                    const width = container.clientWidth;
                    const height = container.clientHeight;

                    camera.aspect = width / height;
                    camera.updateProjectionMatrix();
                    renderer.setSize(width, height);
                }}, 100);
            }});

            /* Clean up on unmount */
            window.addEventListener('unload', () => {{
                cancelAnimationFrame(animationFrame);
                renderer.dispose();
            }});
        </script>
        """,
                          height=600)

    # Field information
    st.subheader("Field Information")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Charge Properties**")
        st.write(f"Charge: {format_scientific_notation(charge)} C")
        st.write(f"Position: ({x_pos}, {y_pos}, {z_pos}) m")

    with col2:
        E_ref = field.calculate_field_at_point(np.array([0, 0, 0]))
        E_magnitude = np.linalg.norm(E_ref)
        st.markdown("**Field Properties**")
        st.write("Field strength at origin:")
        st.write(f"{format_scientific_notation(E_magnitude)} N/C")


if __name__ == "__main__":
    main()
