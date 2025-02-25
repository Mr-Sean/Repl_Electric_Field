import numpy as np

class ElectricField:
    def __init__(self, charge, position):
        """
        Initialize electric field calculator

        Args:
            charge (float): Charge value in Coulombs
            position (tuple): (x, y, z) position of the charge
        """
        self.charge = charge
        self.position = np.array(list(position) + [0.0] if len(position) == 2 else position)
        self.k = 8.99e9  # Coulomb's constant

    def calculate_field_at_point(self, point):
        """
        Calculate electric field at a given point

        Args:
            point (np.array): Point coordinates [x, y, z]

        Returns:
            np.array: Electric field vector [Ex, Ey, Ez]
        """
        # Ensure point is 3D
        if len(point) == 2:
            point = np.array([point[0], point[1], 0.0])

        r = point - self.position
        r_magnitude = np.linalg.norm(r)

        if r_magnitude < 1e-10:  # Avoid division by zero
            return np.zeros(3)

        r_hat = r / r_magnitude
        E = self.k * self.charge * r_hat / (r_magnitude ** 2)

        return E

    def calculate_field_grid(self, radius, n_points):
        """
        Calculate electric field on a spherical grid

        Args:
            radius (float): Radius of the sphere
            n_points (int): Number of points in each dimension

        Returns:
            tuple: (X, Y, Z, Ex, Ey, Ez) arrays
        """
        # Create spherical grid
        phi = np.linspace(0, 2*np.pi, n_points)
        theta = np.linspace(0, np.pi, n_points)
        phi, theta = np.meshgrid(phi, theta)

        X = radius * np.sin(theta) * np.cos(phi)
        Y = radius * np.sin(theta) * np.sin(phi)
        Z = radius * np.cos(theta)

        Ex = np.zeros_like(X)
        Ey = np.zeros_like(Y)
        Ez = np.zeros_like(Z)

        for i in range(n_points):
            for j in range(n_points):
                point = np.array([X[i,j], Y[i,j], Z[i,j]])
                E = self.calculate_field_at_point(point)
                Ex[i,j] = E[0]
                Ey[i,j] = E[1]
                Ez[i,j] = E[2]

        return X, Y, Z, Ex, Ey, Ez