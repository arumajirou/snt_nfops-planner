import numpy as np
def inverse_diff(z, y_T):
    y = [y_T]
    for v in z: y.append(y[-1]+v)
    return np.array(y[1:])
def test_inverse_diff_ok():
    z = np.array([1, -2, 3])
    y = inverse_diff(z, y_T=10)
    assert (y == np.array([11,9,12])).all()
