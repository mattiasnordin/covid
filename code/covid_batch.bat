echo on
set root=D:\covid
call "C:\Users\menor\AppData\Local\Continuum\anaconda3\Scripts\activate.bat"
CD /D %root%
python -W ignore "code\covid_intl.py"
git checkout dev
git add .
git commit -m "Automatic commit"
git push
echo Press Enter...
read
