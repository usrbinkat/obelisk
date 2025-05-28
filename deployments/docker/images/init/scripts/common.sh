#!/bin/bash
# Common functions for init scripts

# Function to wait for a service to be ready
wait_for_service() {
    local url="$1"
    local timeout="${2:-30}"
    local count=0
    
    echo "Waiting for $url to be ready..."
    
    while [ $count -lt $timeout ]; do
        if curl -s -f "$url" >/dev/null 2>&1; then
            echo "Service at $url is ready"
            return 0
        fi
        sleep 1
        count=$((count + 1))
    done
    
    echo "Timeout waiting for $url"
    return 1
}

# Function to check if a URL returns a specific status code
check_http_status() {
    local url="$1"
    local expected_status="$2"
    
    local status=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    
    if [ "$status" = "$expected_status" ]; then
        return 0
    else
        return 1
    fi
}

# Function to safely source environment files
source_env_file() {
    local file="$1"
    
    if [ -f "$file" ]; then
        source "$file"
        echo "Sourced environment from $file"
    else
        echo "Warning: Environment file $file not found"
        return 1
    fi
}

# Export functions for use in other scripts
export -f wait_for_service
export -f check_http_status
export -f source_env_file