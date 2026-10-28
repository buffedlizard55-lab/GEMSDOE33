import numpy as np
from gemsdoe33.phcong import phase_congruency

def test_phase_congruency_step_edge():
    fp = np.ones((64, 64), bool)
    field = np.zeros((64, 64), np.float32); field[:, 32:] = 10.0
    pc, c2, s2 = phase_congruency(field, fp)
    assert pc.shape == (64, 64) and np.isfinite(pc).all()
    assert (pc >= 0).all() and (pc <= 1).all()
    # step edge column should exceed flat interior
    assert pc[:, 31:33].mean() > pc[:, 5:10].mean()
