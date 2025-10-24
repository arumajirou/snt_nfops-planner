# Phase 7 - Evaluation and Statistical Testing

## �@�\

- �f�[�^����: �\���Ǝ����̌���
- �w�W�v�Z: SMAPE/MAE/RMSE/MAPE
- ���v����: Diebold-Mariano����
- �핢������: �񍀌���
- ���ʗ�: Cliff's delta/A12/Hedges' g
- ���d��r�␳: BH/Holm�@
- �]�����|�[�g: HTML�o��

## �g�p���@

```bash
# �T���v���f�[�^����
python examples\phase7\sample_data_phase7.py

# �]�����s
python -m nfops_eval.eval_runner \
  --preds examples\phase7\test_preds.parquet \
  --actuals examples\phase7\test_actuals.parquet \
  --baseline-run test_run \
  --metrics SMAPE,MAE,RMSE \
  --out-dir eval

# �e�X�g���s
pytest tests\phase7 -v
```

## �o��

- eval/eval_report.html: �]�����|�[�g
- eval/tests.json: ���茋��
- eval/compare_table.parquet: ��r�e�[�u��

## ���g���N�X

- SMAPE: Symmetric MAPE
- MAE: Mean Absolute Error
- RMSE: Root Mean Squared Error
- MAPE: Mean Absolute Percentage Error
- CRPS: Continuous Ranked Probability Score (planned)
