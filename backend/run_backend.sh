if [ ! -d "tmp" ]; then
    mkdir tmp
    chmod -R 777 tmp
fi

if [ ! -d "logs" ]; then
    mkdir logs
    chmod -R 777 logs
fi



uvicorn main:app --host 0.0.0.0