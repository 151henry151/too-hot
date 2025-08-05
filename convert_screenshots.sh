#!/bin/bash

# Script to convert PNG screenshots to 24-bit RGB format for App Store Connect
# This removes the alpha channel which is often the cause of "wrong format" errors

echo "Converting PNG screenshots to 24-bit RGB format for App Store Connect..."

# Create output directory
mkdir -p metadata/iphonescreenshots/converted

# Convert the individual PNG files (screen02.png through screen06.png)
for file in metadata/iphonescreenshots/screen0[2-6].png; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        echo "Converting $filename..."
        convert "$file" -background white -alpha remove -alpha off "metadata/iphonescreenshots/converted/$filename"
    fi
done

# Extract and convert the files from the tar archive (screen01.png)
echo "Extracting and converting files from screen01.png (tar archive)..."
mkdir -p metadata/iphonescreenshots/temp_extract
tar -xf metadata/iphonescreenshots/screen01.png -C metadata/iphonescreenshots/temp_extract

# Convert the extracted PNG files
for file in metadata/iphonescreenshots/temp_extract/*.png; do
    if [ -f "$file" ] && [[ ! "$file" =~ "\._" ]]; then  # Skip hidden files
        filename=$(basename "$file")
        echo "Converting extracted file: $filename..."
        convert "$file" -background white -alpha remove -alpha off "metadata/iphonescreenshots/converted/$filename"
    fi
done

# Clean up temporary files
rm -rf metadata/iphonescreenshots/temp_extract
rm -rf metadata/iphonescreenshots/extracted

echo ""
echo "Conversion complete! All files are now in metadata/iphonescreenshots/converted/"
echo "These files should be compatible with App Store Connect."
echo ""
echo "Original files:"
echo "- screen01.png: tar archive containing multiple PNG files"
echo "- screen02.png through screen06.png: individual PNG files"
echo ""
echo "Converted files:"
ls -la metadata/iphonescreenshots/converted/ 