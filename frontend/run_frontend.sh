# load .env if present
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

streamlit run app.py --server.port ${PORT:-8501} --server.address 0.0.0.0
