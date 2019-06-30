if [ ! -f textpack/tests/craigslistVehicles.csv ]; then # state files
  kaggle datasets download -d austinreese/craigslist-carstrucks-data -p textpack/tests
  unzip -o textpack/tests/craigslist-carstrucks-data.zip -d textpack/tests
  chmod 644 textpack/tests/craigslistVehicles.csv 
  rm -rf textpack/tests/craigslistVehiclesFull.csv textpack/tests/craigslist-carstrucks-data.zip
fi

python -m unittest discover -s textpack/tests

# Delete the craigslistVehicles file (1.1GB)
# rm -rf textpack/tests/craigslistVehicles.csv
