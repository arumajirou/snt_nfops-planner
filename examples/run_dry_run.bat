@echo off
echo Dry-run���s��...
call ..\venv\Scripts\activate.bat
planner --dry-run --spec matrix_spec.yaml --invalid invalid_values.csv --max-combos 500
pause
