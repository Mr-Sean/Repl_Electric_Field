import numpy as np

class ElectricField:
    def __init__(self, charge, position):
        """
        Initialize electric field calculator
        
        Args:
            charge (float): Charge value in Coulombs
            position (tuple): (x, y) position of the charge
        """
        self.charge = charge
        self.position = np.array(position)
        self.k = 8.99e9  # Coulomb's constant
        
    def calculate_field_at_point(self, point):
        """
        Calculate electric field at a given point
        
        Args:
            point (np.array): Point coordinates [x, y]
            
        Returns:
            np.array: Electric field vector [Ex, Ey]
        """
        r = point - self.position
        r_magnitude = np.linalg.norm(r)
        
        if r_magnitude < 1e-10:  # Avoid division by zero
            return np.zeros(2)
            
        r_hat = r / r_magnitude
        E = self.k * self.charge * r_hat / (r_magnitude ** 2)
        
        return E
        
    def calculate_field_grid(self, x_range, y_range, n_points):
        """
        Calculate electric field on a grid of points
        
        Args:
            x_range (tuple): (min_x, max_x)
            y_range (tuple): (min_y, max_y)
            n_points (int): Number of points in each dimension
            
        Returns:
            tuple: (X, Y, Ex, Ey) arrays
        """
        x = np.linspace(x_range[0], x_range[1], n_points)
        y = np.linspace(y_range[0], y_range[1], n_points)
        X, Y = np.meshgrid(x, y)
        
        Ex = np.zeros_like(X)
        Ey = np.zeros_like(Y)
        
        for i in range(n_points):
            for j in range(n_points):
                point = np.array([X[i,j], Y[i,j]])
                E = self.calculate_field_at_point(point)
                Ex[i,j] = E[0]
                Ey[i,j] = E[1]
                
        return X, Y, Ex, Ey
