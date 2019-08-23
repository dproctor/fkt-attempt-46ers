# FKT Attempt on Adirondack 46ers (unsupported)

![Map of proposed 46ers route](images/46ers.png)

[Planning doc](https://docs.google.com/document/d/1wN7PmH-JsgmIHsFPoYUi2MEByevzwz8eYv4cj-IDyBQ/edit#)

Google Earth is the best way to view all of these files.

## Static resources
### Maps
- `maps/` contains USGS topo maps for the Adirondacks High Peaks.

### Routes
- `routes/2019-fkt-*.gpx` files contain GPX tracks of the current (2019) FKT.
- `routes/2019-fkt-peak-sequence.txt` is an ordered list of peaks of the current (2019)
  FKT.
- `routes/2019-fkt-peak-sequence.gpx` is a GPX file with a track containing the ordered
  peaks of the current (2019) FKT.
- `routes/climbing-optimal-ps.txt` is an ordered list of peaks that minimizes climbing.
- `routes/climbing-optimal-ps.gpx` a GPX file with a track containing is the
  route that minimizes climbing.
- `routes/mileage-optimal-ps.txt` is an ordered list of peaks that minimizes
  total distance.
- `routes/mileage-optimal-ps.gpx` a GPX file with a track containing is the
  route that minimizes total distance.

### Summits
- `summits/coordinates.csv` is a CSV file containing the names of the 46ers,
  along with their elevation and coordinates.

## Scripts
### Routes
- `routes/ps2d.py` takes a peak sequence (like those in `routes/*.txt` files) and
  prints the distance of the route, using a distance matrix provided via a
  Google Sheet csv url.
- `routes/ps2gpx.py` takes a peak sequence (like those in `routes/*.txt` files) and
  prints a corresponding GPX file.
- `routes/solve_tsp.py` solves the Travelling Salesman Problem to compute the
  most efficient tour of the 46ers.

### Summits
- `summits/extract-peak-urls.py` extracts urls of websites with info about each 46er
  from a url containing a list of them.
- `summits/extract-peak-coordinates.py` extracts the GPS coordinates of a peak from a
  list of html documents containing information from it. Designed to take the
  output of `summits/extract-peak-urls`.
