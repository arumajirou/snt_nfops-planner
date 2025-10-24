# -*- coding: utf-8 -*-
from nfops_planner.plan_engine.sec_model import extract_features
from nfops_planner.plan_engine.spec_loader import load_spec

def test_extract_features_has_expected_keys():
    spec = load_spec("configs/examples/matrix_spec.yaml")
    f = extract_features(spec)
    for k in ["n_models","sum_card","max_card","combos_sum","cont_width_sum"]:
        assert k in f
