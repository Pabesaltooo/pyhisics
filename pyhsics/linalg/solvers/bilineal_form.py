from __future__ import annotations
from typing import List, Union

from pyhsics.linalg.structures import Scalar, Vector, Matrix
from pyhsics.linalg.solvers.linear_system import LinearSystem

class BilinealForm(Matrix):
    def ker(self) -> Union[Vector,List[Vector], None]:
        return LinearSystem(self, Vector.zeros(len(self))).solve()
    
    def get_ortogonal_subspace(self, v: Vector) -> Union[Vector,List[Vector], None]:
        return LinearSystem([(self*v).value],[0]).solve()
    
    def find_non_isotropic_vector(self) -> Vector:
        n = len(self)
        for i in range(n):
            vec = [0] * n
            vec[i] = 1
            candidate = Vector(vec)
            if candidate.dot(candidate, form=self) != 0:
                return candidate
        raise ValueError("No non-isotropic vector found")
       
    def find_isotropic_vector(self) -> Union[Vector, List[Vector]]:
        """
        Returns a non-zero vector v such that v^T * A * v = 0.
        """
        
        pass
        
        
    def get_orthogonal_base(self) -> List[Vector]:
        """
        Devuelve una base ortogonal respecto a la forma b (self).
        Método: Gram–Schmidt en el sentido de b resolviendo sistemas M·x=0.
        """
        n, _ = self.shape
        ortogonal_base: List[Vector] = []
        
        # 1) Primer vector: no isotrópico
        w = self.find_non_isotropic_vector()
        ortogonal_base.append(w)
        
        # 2) Iteramos hasta tener n vectores
        while len(ortogonal_base) < n:
            # Construimos las ecuaciones b(v_i, x) = 0 para cada v_i en la base actual
            # Cada fila del sistema es (self * v_i).value
            A_rows = [(self * v_i).value for v_i in ortogonal_base]
            b_vals  = [0] * len(A_rows)
            
            # Resolvemos el sistema homogéneo A_rows · x = 0
            nullspace = LinearSystem(A_rows, b_vals).solve()
            
            # Si no hay soluciones, salimos
            if not nullspace:
                break
            
            # Elegimos la primera solución que no esté ya en la base
            añadimos = False
            for u in nullspace:
                # comprobamos que u no sea proporcional a ninguno de los anteriores
                if all((u - v_i).norm() != 0 for v_i in ortogonal_base):
                    ortogonal_base.append(u)
                    añadimos = True
                    break
            
            # Si no encontramos ningún vector nuevo, terminamos
            if not añadimos:
                break

        return ortogonal_base
    
    
    def get_orthonormal_base(self) -> List[Vector]:
        return [v.norm() for v in self.get_orthogonal_base()]
        
    def get_diagonal_matrix(self) -> Matrix:
        beta = self.get_orthonormal_base()
        return Matrix([[v.dot(w).value for w in beta] for v in beta])
        
    @property
    def signature(self) -> tuple[int, int]:
        """
        Returns the signature of the bilinear form.
        - tuple(positive, negative)
        """
        D = self.get_diagonal_matrix()
        if any(isinstance(D[i][i], complex) for i in range(len(D))):
            raise ValueError("The signature is not defined for complex numbers.")
        positive = sum(1 for i in range(len(D)) if D[i][i] > 0)
        negative = sum(1 for i in range(len(D)) if D[i][i] < 0)
        return (positive, negative)
    
    def __call__(self, v: Vector, w: Vector) -> Scalar:
        """
        Returns the bilinear form of v and w.
        """
        return v.dot(w, form=self)
    
    def get_orthogonal_with_transformations(self) -> List[Vector]:
        """
        Diagonalize the symmetric matrix by congruence (simultaneous
        column and row operations) and track the row operations on I
        to produce an orthogonal basis.

        Returns
        -------
        List[Vector]
            The columns of the accumulated transformation matrix P,
            which form an orthogonal basis for R^n wrt the associated
            bilinear form.
        """
        n = len(self)
        # Copias de trabajo
        A = Matrix([row.copy() for row in self.value])
        P = Matrix([[1 if i == j else 0 for j in range(n)] for i in range(n)])

        # Para cada par (i,j) con j>i, eliminamos A[i][j] manteniendo la simetría:
        for i in range(n):
            # Aseguramos que el pivote A[i][i] ≠ 0 (si no, intercambiaríamos filas/columnas)
            if A.value[i][i] == 0:
                for k in range(i+1, n):
                    if A.value[k][i] != 0:
                        # swap row i ↔ k y col i ↔ k
                        A = A.elemental_row_transformation((i, 1), (k, 0))  # swap via two ops
                        A = A.elemental_row_transformation((k, 1), (i, 0))
                        A = A.elemental_col_transformation((i, 1), (k, 0))
                        A = A.elemental_col_transformation((k, 1), (i, 0))
                        P = P.elemental_row_transformation((i, 1), (k, 0))
                        P = P.elemental_row_transformation((k, 1), (i, 0))
                        break

            for j in range(i+1, n):
                a_ij = A.value[i][j]
                if a_ij != 0:
                    a_ii = A.value[i][i]
                    scale1 = 1
                    scale2 = - a_ij / a_ii
                    # operación en columnas (A)
                    A = A.elemental_col_transformation((i, scale1), (j, scale2))
                    # misma operación en filas (A y P)
                    A = A.elemental_row_transformation((i, scale1), (j, scale2))
                    P = P.elemental_row_transformation((i, scale1), (j, scale2))

        # Ahora A es diagonal. Las columnas de P son la base ortogonal.
        basis: List[Vector] = []
        for col in range(n):
            comp = [P.value[row][col] for row in range(n)]
            basis.append(Vector(comp))