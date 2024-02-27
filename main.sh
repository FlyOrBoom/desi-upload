release="$DESI_ROOT/public/edr"

make find

echo "Finding directories..."
./find "$release" > find.json

echo "Selecting large directories..."
python3 select.py "$release" > select.txt

echo "Uploading large directories..."
python3 upload.py "$release" 2> upload_errors.txt
