From python:2.7-wheezy
EXPOSE 5000
ADD kub.py kub.py
RUN pip install flask redis
CMD ["python", "kub.py"]
