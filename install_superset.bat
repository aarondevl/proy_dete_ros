@echo off
echo Instalando Apache Superset...

:: Crear entorno virtual nuevo
python -m venv superset-env
call superset-env\Scripts\activate

:: Actualizar pip y herramientas base
python -m pip install --upgrade pip
pip install wheel setuptools

:: Instalar dependencias principales
pip install numpy==1.23.5
pip install pandas==2.0.3
pip install sqlalchemy==1.4.54
pip install sqlalchemy-utils==0.38.3
pip install Geohash
pip install apache-superset==4.1.0
pip install pillow  :: Agregado para resolver advertencias de PIL

:: Configurar variables de entorno
set FLASK_APP=superset
set SUPERSET_CONFIG_PATH=%CD%\superset_config.py

:: Inicializar la base de datos
echo Inicializando base de datos...
superset db upgrade

:: Crear usuario admin
echo.
echo Creando usuario admin...
superset fab create-admin ^
    --username admin ^
    --firstname Superset ^
    --lastname Admin ^
    --email admin@superset.com ^
    --password admin

:: Crear roles y permisos
echo Inicializando roles y permisos...
superset init

:: Iniciar el servidor
echo.
echo Iniciando Superset en http://localhost:8088
superset run -h 0.0.0.0 -p 8088 --with-threads --reload

pause
