cd ..

set PYTHONPATH=./src
set build_environment=prod
%cd%/iia_env/scripts/activate & python create_server_config.py & hypercorn intent.__main__ --config config/server_config.toml