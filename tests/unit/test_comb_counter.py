"""test_comb_counter.py"""
import pytest
from nfops_planner.core import CombCounter, Spec


class TestCombCounter:
    def test_simple_count(self):
        spec = Spec(
            models=[
                {
                    'name': 'TestModel',
                    'active': True,
                    'params': {
                        'a': [1, 2],
                        'b': [10, 20, 30]
                    }
                }
            ]
        )
        counter = CombCounter()
        result = counter.count(spec, [])
        assert result.total_combos == 6
        assert result.per_model['TestModel'] == 6
