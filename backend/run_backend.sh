if [ ! -d "tmp" ]; then
    mkdir tmp
    chmod -R 777 tmp
fi

alembic upgrade head


uvicorn main:app --host 0.0.0.0