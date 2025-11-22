FROM python:3.10-slim

WORKDIR /app

# Copy requirements
COPY ./src/app/requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Copy app code
COPY ./src/app /app/src/app

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "src/app/main.py", "--server.address=0.0.0.0"]