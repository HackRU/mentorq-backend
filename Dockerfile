# Commands to build and run
# docker build -t mentorq-backend .
# docker run -p 8000:8000 -it --name django mentorq-backend

# Use python:3 as the base
FROM python:3

# use the mentorq_backend as the work dir
WORKDIR mentorq_backend

# copy and install the dependencies in requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy all the files over to the work dir
COPY . .

# run the Django migrations
# RUN python manage.py makemigrations
# RUN python manage.py migrate

# run the Django server
ENTRYPOINT ["python", "manage.py", "runserver", "0.0.0.0:8000"]
