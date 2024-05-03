FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

# Copy requirements.txt
COPY requirements.txt .

# Install the specified packages
RUN pip install -r requirements.txt

# Copy the lambda function code
COPY sql_queries.py .
COPY archive.py .

CMD [ "archive.handler" ]