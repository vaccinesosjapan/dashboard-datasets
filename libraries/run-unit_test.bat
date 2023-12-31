@echo off
setlocal

pytest --maxfail=10 exfuncs.py
pytest --maxfail=10 exfuncs-test.py
pytest --maxfail=10 excertified-test.py
pytest --maxfail=10 exdeath-test.py

endlocal