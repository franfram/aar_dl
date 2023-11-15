#!/bin/bash


# Check if a directory has been provided
if [ $# -eq 0 ]; then
    echo "Please provide a directory."
    exit 1
fi

directory=$1

# Check if the provided directory exists
if [ ! -d "$directory" ]; then
    echo "The provided directory does not exist."
    exit 1
fi

# Initialize JSON output
json="{}"

# Use grep to find "minmax" matches, and awk to extract surrounding text
while IFS= read -r line; do
    file=$(echo "$line" | cut -d: -f1)
    pos=$(echo "$line" | cut -d: -f2)
    content=$(echo "$line" | cut -d: -f3-)

    # Extract 50 characters before and after, and escape double quotes for JSON compatibility
    extract=$(echo "$content" | awk -v pos="$pos" '{print substr($0, (pos < 50 ? 1 : pos-50), 100)}' | sed 's/"/\\"/g')

    # Add to JSON output
    json=$(echo "$json" | jq --arg file "$file" --arg extract "$extract" '. + {($file): $extract}')
done < <(grep -riboP --exclude-dir=.git '\bminmax\b' "$directory")

# Print JSON output
echo "$json" | jq .







