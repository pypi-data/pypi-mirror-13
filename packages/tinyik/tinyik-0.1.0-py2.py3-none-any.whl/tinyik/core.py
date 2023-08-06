"""Core features."""

from numbers import Number
from functools import reduce

import autograd.numpy as np
import autograd


class Actuator(object):
    """Represents an actuator as a set of links and revolute joints."""

    def __init__(self, *args):
        """Create an actuator from specified link lengths and joint axes."""
        components = []
        for arg in args:
            if isinstance(arg, Number):
                components.append(Link(arg))
            elif isinstance(arg, str) and arg in {'x', 'y', 'z'}:
                components.append(Joint(arg))
            else:
                raise ValueError(
                    'the arguments need to be '
                    'link length or joint axis: {}'.format(arg)
                )

        self._fk = FKSolver(components)
        self._ik = IKSolver(self._fk)

        self.angles = [0.] * len(
            [c for c in components if isinstance(c, Joint)]
        )

    @property
    def angles(self):
        """The joint angles."""
        return self._angles

    @angles.setter
    def angles(self, angles):
        self._angles = np.array(angles)

    @property
    def ee(self):
        """The end-effector position."""
        return self._fk.solve(self.angles)

    @ee.setter
    def ee(self, position):
        self.angles = self._ik.solve(position, self.angles)


class FKSolver(object):
    """A forward kinematics solver."""

    def __init__(self, components):
        """Generate a FK solver from link and joint instances."""
        joint_indexes = [
            i for i, c in enumerate(components) if isinstance(c, Joint)
        ]

        def matrices(angles):
            joints = dict(zip(joint_indexes, angles))
            a = [joints.get(i, None) for i in range(len(components))]
            return [c.matrix(a[i]) for i, c in enumerate(components)]

        self._matrices = matrices

    def solve(self, angles):
        """Calculate a position of the end-effector and return it."""
        return reduce(
            lambda a, m: np.dot(m, a),
            reversed(self._matrices(angles)),
            np.array([0., 0., 0., 1.])
        )[:3]


class NewtonOptimizer(object):
    """An optimizer based on Newton's method."""

    def __init__(self, f, tol=1.48e-08, maxiter=50):
        """Generate an optimizer from an objective function."""
        self.g = autograd.grad(f)
        self.h = autograd.hessian(f)
        self.tol = tol
        self.maxiter = maxiter

    def optimize(self, x0, target):
        """Calculate an optimum argument of an objective function."""
        x = x0
        for _ in range(self.maxiter):
            delta = np.linalg.solve(self.h(x, target), -self.g(x, target))
            x = x + delta
            if np.linalg.norm(delta) < self.tol:
                break
        return x


class SDOptimizer(object):
    """An optimizer based on steepest descent method."""

    def __init__(self, f, tol=1.48e-08, maxiter=50, alpha=1):
        """Generate an optimizer from an objective function."""
        self.g = autograd.grad(f)
        self.tol = tol
        self.maxiter = maxiter
        self.alpha = alpha

    def optimize(self, x0, target):
        """Calculate an optimum argument of an objective function."""
        x = x0
        for _ in range(self.maxiter):
            delta = self.alpha * self.g(x, target)
            x = x - delta
            if np.linalg.norm(delta) < self.tol:
                break
        return x


class IKSolver(object):
    """An inverse kinematics solver."""

    def __init__(self, fk_solver, opt_cls=NewtonOptimizer, opt_params=None):
        """Generate an IK solver from a FK solver instance."""
        def distance_squared(angles, target):
            x = target - fk_solver.solve(angles)
            return np.sum(np.power(x, 2))

        if opt_params is None:
            opt_params = {}
        self.optimizer = opt_cls(distance_squared, **opt_params)

    def solve(self, target, angles0):
        """Calculate joint angles and returns it."""
        return self.optimizer.optimize(np.array(angles0), target)


class Link(object):
    """Represents a link."""

    def __init__(self, length):
        """Create a link from a specified length."""
        self.length = length

    def matrix(self, _):
        """Return translation matrix in homogeneous coordinates."""
        return np.array([
            [1., 0., 0., self.length],
            [0., 1., 0., 0.],
            [0., 0., 1., 0.],
            [0., 0., 0., 1.]
        ])


class Joint(object):
    """Represents a revolute joint."""

    def __init__(self, axis):
        """Create a revolute joint from a specified axis."""
        self.axis = axis

    def matrix(self, angle):
        """Return rotation matrix in homogeneous coordinates."""
        _rot_mat = {
            'x': self._x_rot,
            'y': self._y_rot,
            'z': self._z_rot
        }
        return _rot_mat[self.axis](angle)

    def _x_rot(self, angle):
        return np.array([
            [1., 0., 0., 0.],
            [0., np.cos(angle), -np.sin(angle), 0.],
            [0., np.sin(angle), np.cos(angle), 0.],
            [0., 0., 0., 1.]
        ])

    def _y_rot(self, angle):
        return np.array([
            [np.cos(angle), 0., np.sin(angle), 0.],
            [0., 1., 0., 0.],
            [-np.sin(angle), 0., np.cos(angle), 0.],
            [0., 0., 0., 1.]
        ])

    def _z_rot(self, angle):
        return np.array([
            [np.cos(angle), -np.sin(angle), 0., 0.],
            [np.sin(angle), np.cos(angle), 0., 0.],
            [0., 0., 1., 0.],
            [0., 0., 0., 1.]
        ])
