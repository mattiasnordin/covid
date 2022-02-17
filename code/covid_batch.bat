echo on
set root=D:\covid
CD /D %root%
python -W ignore "code\covid_intl.py"
timeout 5
"code\covid_bash.sh"
