# meetuplytix

Simple Meetup groups analytics using [pandas](https://pandas.pydata.org/) and [matplotlib](https://matplotlib.org/)

# Get started

Build a Docker image:

```
docker build -t meetuplytix .
```
Run the `iPython` notebook server:

```
docker run -d -p 443:8888 -v $(PWD)/data/:/notebooks/data -v $(PWD)/notebooks:/notebooks -e "PASSWORD=password" meetuplytix
```

Access the notebook via browser:

```
https://localhost
```

# Meetup events data

There is a small utility stcript in `utils` subdirectory of this project which pulls down data from Kubernetes London group. You can easily modify to pull down data from any Meetup group
