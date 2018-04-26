FROM tensorflow/tensorflow:latest-devel-py3

RUN pip install gunicorn
RUN pip install picasso-viz

EXPOSE 80
ENTRYPOINT gunicorn picasso:app --bind=0.0.0.0:80
