# Use Alpine Linux as base image
FROM alpine:latest

# Install necessary packages
RUN apk add --no-cache \
    bash \
    wget \
    ca-certificates \
    gcompat \
    && rm -rf /var/cache/apk/*

# Download and install Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh \
    && bash miniconda.sh -b -p /opt/conda \
    && rm miniconda.sh

# Add conda to PATH
ENV PATH=/opt/conda/bin:$PATH

# Copy the backend folder
COPY backend /app/backend

# Set working directory
WORKDIR /app

# Create conda environment from environment.yml
RUN conda env create -f backend/enviroment.yml

# Activate the environment (for runtime)
ENV CONDA_DEFAULT_ENV=DrinkBackend
ENV PATH=/opt/conda/envs/DrinkBackend/bin:$PATH

# Expose port 8000
EXPOSE 8000

# Run the application
CMD ["python", "./backend/main.py"]