FROM python:3.9-alpine AS base
ARG PROJECT_NAME=onsite_alohi
ARG HOME="/home/app"
WORKDIR ${HOME}/${PROJECT_NAME}

COPY requirements.txt requirements.txt

RUN apk add --no-cache --virtual build-dependencies gcc musl-dev && \
    pip install -r requirements.txt && \
    apk del --no-cache build-dependencies

FROM base AS base_unit_tests
COPY tests/unit_tests/requirements.txt tests/unit_tests/requirements.txt
RUN apk add --no-cache --virtual build-dependencies gcc musl-dev && \
    pip install -r tests/unit_tests/requirements.txt && \
    apk del --no-cache build-dependencies

FROM base_unit_tests AS unit_tests
COPY . .
RUN pytest tests/unit_tests || true

FROM base AS base_package
RUN apk add --no-cache git
RUN pip install --upgrade setuptools pip wheel

FROM base_package AS package
COPY . .
RUN python setup.py bdist_wheel --dist-dir=/tmp/dist

COPY --from=package /tmp/dist /tmp/dist
RUN pip install /tmp/dist/*.whl

CMD python -m ${PROJECT_NAME}

