# Datamatrix pdf decoder

## build
docker build -t datamatrix-decoder .

## Process a PDF in current directory
docker run -v $(pwd):/data datamatrix-decoder input.pdf > output.csv
