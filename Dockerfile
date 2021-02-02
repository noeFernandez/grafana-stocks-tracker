FROM python:3.8.5
RUN pip3 install yfinance
RUN pip3 install pyyaml
RUN pip3 install graphyte
COPY . /source
ENTRYPOINT ["/usr/local/bin/python", "/source/tracker.py"]