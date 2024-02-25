# Use a Python base image
FROM python:3.9

RUN useradd -m -u 1000 user

USER user

ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Copy the required files to the working directory
COPY app.py .
COPY ./templates/index.html /code/templates/index.html 
COPY ./requirements.txt /code/requirements.txt
COPY ./book_embeddings.json /code/book_embeddings.json

# Install the required packages
RUN pip install --no-cache-dir -r /code/requirements.txt

# Get secret SECRET_EXAMPLE and clone it as repo at buildtime
RUN --mount=type=secret,id=GEMINI_API_KEY,mode=0444,required=true

COPY --chown=user . $HOME/app

# Expose the port that the Flask app will run on
EXPOSE 7860

# Start the Flask app
CMD ["python", "app.py"]