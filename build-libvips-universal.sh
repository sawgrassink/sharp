#!/bin/bash

# Define the source and destination directories
src_dir="vendor/8.14.2/darwin-x64"
dest_dir="vendor/8.14.2/darwin-universal"

# Function to check the architecture of a file
check_architecture() {
  file="$1"
  # Use the 'file' command to check the architecture
  arch=$(file "$file" | grep -o 'x86_64\|arm64')
  if [ "$arch" = "x86_64" ]; then
    return 0  # x86_64 architecture
  elif [ "$arch" = "arm64" ]; then
    return 1  # arm64 architecture
  else
    return 2  # Other architecture or unknown
  fi
}

# Iterate through all files in src_dir and its subdirectories
find "$src_dir" -type f -print0 | while IFS= read -r -d $'\0' file; do
  # Get the relative path of the file
  rel_path="${file#$src_dir/}"
  # Define the corresponding file in the arm64 directory
  arm64_file="vendor/8.14.2/darwin-arm64v8/$rel_path"
  # Define the destination file in the universal directory
  universal_file="$dest_dir/$rel_path"

  if check_architecture "$file"; then
    # If the file has x86_64 architecture, run lipo on both x86_64 and arm64 files
    mkdir -p "$(dirname "$universal_file")"
    lipo "$file" "$arm64_file" -output "$universal_file" -create
    echo "Created universal version for: $rel_path"
  else
    # If the file has a different or unknown architecture, simply copy it
    mkdir -p "$(dirname "$universal_file")"
    cp "$file" "$universal_file"
    echo "Copied: $rel_path"
  fi
done

echo "Task completed."
