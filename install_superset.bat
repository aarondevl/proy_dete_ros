@echo off
echo Instalando Apache Superset...

:: Crear entorno virtual nuevo
rmdir /s /q superset-env
python -m venv superset-env
call superset-env\Scripts\activate

:: Actualizar pip
python -m pip install --upgrade pip
pip install wheel

:: Instalar dependencias base
pip install numpy==1.23.5
pip install pandas==2.0.3
pip install sqlalchemy-utils==0.38.3

:: Intentar instalar python-geohash desde una fuente alternativa
pip install --only-binary :all: python-geohash || pip install Geohash

:: Continuar con el resto de dependencias
pip install cryptography==42.0.4
pip install redis==4.6.0
pip install flask-migrate==3.1.0
pip install deprecation==2.1.0
pip install flask-caching==2.1.0
pip install flask-compress==1.13
pip install flask-session==0.4.0
pip install flask-talisman==1.0.0
pip install hashids==1.3.1
pip install holidays==0.25
pip install jsonpath-ng==1.6.1
pip install msgpack==1.0.5
pip install nh3==0.2.14
pip install pyarrow==14.0.1
pip install pyparsing==3.0.9
pip install selenium==4.9.1
pip install shillelagh[gsheetsapi]==1.2.18
pip install slack-sdk==3.19.5
pip install sqlglot==25.24.0
pip install sshtunnel==0.4.0
pip install tabulate==0.8.10
pip install wtforms-json
pip install xlsxwriter==3.0.9
pip install waitress

:: Instalar Superset
pip install apache-superset==4.1.0

:: Configurar variables de entorno
set FLASK_APP=superset

:: Inicializar la base de datos y crear usuario admin
superset db upgrade
superset fab create-admin
superset init

:: Iniciar el servidor en el puerto 8088
superset run -h 0.0.0.0 -p 8088 --with-threads --reload

:: Abrir Superset en el navegador
start http://localhost:8088

pause
