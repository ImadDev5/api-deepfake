#!/bin/bash

# Define the source directory
src_dir="/home/vortex/api-deepfake"

# Define the output file
output_file="output_content.txt"

# List of files and directories to exclude
exclude_list=(
  "frontend"
  "node_modules"
  "__pycache__"
  ".env"
  ".gitignore"
  "efficientNetFFPP.pth"
  "Miniconda3-latest-Linux-x86_64.sh"
  "README.md"
)

# Create an empty output file
> "$output_file"

# Function to check if a file/folder should be excluded
exclude() {
  for excl in "${exclude_list[@]}"; do
    if [[ "$1" == *"$excl"* ]]; then
      return 0  # Exclude
    fi
  done
  return 1  # Include
}

# Recursive function to process files and directories
process_dir() {
  for item in "$1"/*; do
    # Skip if the file/folder is excluded
    if exclude "$item"; then
      continue
    fi

    # If it is a directory, recursively process it
    if [[ -d "$item" ]]; then
      process_dir "$item"
    # If it is a file, append its content to the output file
    elif [[ -f "$item" ]]; then
      # Write the path at the top of the file
      echo "Path: $item" >> "$output_file"
      # Append the content of the file to the output file
      cat "$item" >> "$output_file"
      echo -e "\n\n" >> "$output_file"  # Add some space between file contents
    fi
  done
}

# Start processing the source directory
process_dir "$src_dir"

echo "All content has been copied to $output_file."
