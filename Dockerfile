FROM ipython/scipyserver

COPY requirements.txt /notebooks/
RUN pip install --upgrade pip && \
            pip3 install --ignore-installed -r requirements.txt

COPY notebook.sh /notebook.sh

CMD ["/notebook.sh"]
