#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to process a file
process_file() {
    local file=$1
    local dry_run=$2
    
    if [ "$dry_run" = true ]; then
        echo -e "${YELLOW}Would process${NC}: $file"
        # Show what would be changed using grep
        echo "Functions that would be modified:"
        grep -E '^[[:space:]]*(async )?def test_[^-][^:]+:' "$file" || true
        grep -E '^[[:space:]]*@pytest\.fixture.*\n[[:space:]]*def [^-][^:]+:' "$file" || true
    else
        echo -e "${BLUE}Processing${NC}: $file"
        # Add -> None to async test functions without return type
        sed -i -E '/^[[:space:]]*async def test_[^-][^:]+:[[:space:]]*$/s/:/ -> None:/' "$file"
        
        # Add -> None to regular test functions without return type
        sed -i -E '/^[[:space:]]*def test_[^-][^:]+:[[:space:]]*$/s/:/ -> None:/' "$file"
        
        # Add -> None to fixture functions without return type
        sed -i -E '/^[[:space:]]*@pytest\.fixture.*\n[[:space:]]*def [^-][^:]+:[[:space:]]*$/s/:/ -> None:/' "$file"
        
        # Add -> None to test class methods without return type
        sed -i -E '/^[[:space:]]*def test_[^-][^:]+\(self[^:]*\):[[:space:]]*$/s/:/ -> None:/' "$file"
        sed -i -E '/^[[:space:]]*async def test_[^-][^:]+\(self[^:]*\):[[:space:]]*$/s/:/ -> None:/' "$file"
    fi
}

# Find first test file
first_test_file=$(find tests -type f \( -name "test_*.py" -o -name "conftest.py" \) | head -n 1)

if [ -n "$first_test_file" ]; then
    # First show what would be changed
    process_file "$first_test_file" true
    
    echo -e "\n${YELLOW}Do you want to process this file? (y/n)${NC}"
    read -r answer
    
    if [ "$answer" = "y" ]; then
        process_file "$first_test_file" false
        echo -e "${GREEN}Done!${NC}"
    else
        echo "Aborted"
    fi
else
    echo "No test files found"
fi
