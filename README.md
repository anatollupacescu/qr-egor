# Datamatrix decoder

## build
```sh
docker build -t datamatrix-decoder .
```

## Process a PDF in current directory
```sh
docker run -v $(pwd):/data datamatrix-decoder input.pdf > output.csv
```
