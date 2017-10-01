From python:2.7-onbuild
EXPOSE 5000
#ADD kub.py kub.py
#RUN pip install flask redis MySQL-python
CMD ["python", "kub-multi.py"]
  