# Phase 8 - XAI and Error Analysis

## �@�\

- ErrorProfiler: ���[�X�g�\���̒��o
- ShapExplainer: SHAP�l�v�Z(���`�ߎ�)
- PermutationExplainer: Permutation�d�v�x
- �f�[�^����: features/preds/actuals����
- XAI���|�[�g: HTML�o��

## �g�p���@

```bash
# �T���v���f�[�^����
python examples\phase8\sample_data_phase8.py

# XAI���͎��s
python -m nfops_xai.xai_runner \
  --features examples\phase8\test_features.parquet \
  --preds examples\phase8\test_preds.parquet \
  --actuals examples\phase8\test_actuals.parquet \
  --methods shap,perm \
  --topk-worst 50 \
  --out-dir artifacts\xai

# �e�X�g���s
pytest tests\phase8 -v
```

## �o��

- artifacts/xai/shap_values.parquet: SHAP�l
- artifacts/xai/permutation_importance.parquet: Permutation�d�v�x
- artifacts/xai/worst_cases.parquet: ���[�X�g�P�[�X
- artifacts/xai/xai_report.html: XAI���|�[�g

## ���g���N�X

- global_importance: �O���[�o�������ʏd�v�x
- local_explanations_count: ���[�J��������
- xai_build_sec: ��������
- worst_cases_analyzed: ���͍ς݃��[�X�g�P�[�X��

## ���ӎ���

- SHAP�����͐��`�ߎ��̊ȈՔ�
- �{�Ԋ��ł� shap ���C�u�����̎g�p�𐄏�
- Permutation�͍ė\���Ȃ��̊ȈՔ�
- ���S�łɂ�Captum�������K�v
