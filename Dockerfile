# Use AWS Lambda Python 3.9 base image
FROM public.ecr.aws/lambda/python:3.9

# Set work directory
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy application code
COPY . ${LAMBDA_TASK_ROOT}

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Lambda entry point
CMD ["app.lambda_handler"]
