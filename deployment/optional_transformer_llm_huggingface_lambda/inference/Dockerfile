ARG FUNCTION_DIR="/function/"

FROM huggingface/transformers-pytorch-cpu as build-image


# Include global arg in this stage of the build
ARG FUNCTION_DIR

# Install aws-lambda-cpp build dependencies
RUN apt-get update && \
  apt-get install -y \
  g++ \
  make \
  cmake \
  unzip \
  libcurl4-openssl-dev


# Create function directory
RUN mkdir -p ${FUNCTION_DIR}

# Copy handler function
COPY *.py ${FUNCTION_DIR}

# Install the function's dependencies
RUN pip uninstall --yes jupyter
RUN pip install --target ${FUNCTION_DIR} awslambdaric
RUN pip install --target ${FUNCTION_DIR} sentencepiece protobuf

FROM huggingface/transformers-pytorch-cpu

# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}

RUN pip install --target ${FUNCTION_DIR} sentence-transformers==2.2.2

# Copy in the built dependencies
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}

ENV PYTHONIOENCODING="utf8"
ENV HF_DATASETS_CACHE=/mnt/hf_models_cache
ENV HUGGINGFACE_HUB_CACHE=/mnt/hf_models_cache
ENV HF_HOME=/mnt/hf_models_cache
ENV TRANSFORMERS_CACHE=/mnt/hf_models_cache
ENV SENTENCE_TRANSFORMERS_HOME=/mnt/hf_models_cache

ENTRYPOINT [ "python3", "-m", "awslambdaric" ]

# This will get replaced by the proper handler by the CDK script
CMD [ "vectorisation.handler" ]
