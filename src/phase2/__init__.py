import warnings
warnings.warn("phase2 is deprecated; use nfops_phase2", DeprecationWarning)
# 互換方針: ここで nfops_phase2 を import しない（存在しない環境で落ちるため）。
# 必要な下位モジュール（例: phase2.dq_runner）は呼出し側が直接 import する。
