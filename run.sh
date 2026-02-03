#!/bin/bash

# Default values
# Default values
TYPE="local"
TAG="paco:latest"
CLEAN=false
IS_DOCKER=false
IS_LOCAL=false

# Help function
usage() {
    echo "PACO Run Script"
    echo "Usage: ./run.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --docker                Use Docker mode (builds & runs image)"
    echo "  --local                 Use Local mode (installs deps & runs) [Default]"
    echo "  --clean                 Clean temporary files (__pycache__, etc.)"
    echo "  --help                  Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run.sh"
}

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --docker) TYPE="docker"; IS_DOCKER=true ;;
        --local) TYPE="local"; IS_LOCAL=true ;;
        --clean) CLEAN=true ;;
        --help) usage; exit 0 ;;
        *) echo "Unknown parameter passed: $1"; usage; exit 1 ;;
    esac
    shift
done

# Check for conflicting arguments
if [ "$IS_DOCKER" = true ] && [ "$IS_LOCAL" = true ]; then
    echo "Error: --local and --docker cannot be used together."
    echo ""
    usage
    exit 1
fi

# Clean step
if [ "$CLEAN" = true ]; then
    echo "Cleaning temporary files..."
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete
    echo "Cleanup complete."
fi

# Build & Run step
echo "Starting process for: $TYPE"

if [ "$TYPE" == "local" ]; then
    echo "Installing Python dependencies..."
    
    # check pip available
    if ! command -v pip &> /dev/null; then
        echo "Error: pip not found. Please install Python and pip."
        exit 1
    fi

    pip install -r requirements.txt
    if [ -f "gui/requirements.txt" ]; then
        pip install -r gui/requirements.txt
    fi
    if [ -f "simulator/requirements.txt" ]; then
        pip install -r simulator/requirements.txt
    fi
    
    echo "Local setup complete. Starting application..."
    python3 src --gui

elif [ "$TYPE" == "docker" ]; then
    echo "Building Docker image: $TAG"
    
    if ! command -v docker &> /dev/null; then
        echo "Error: docker not found. Please install Docker."
        exit 1
    fi

    docker build -t "$TAG" .
    
    if [ $? -eq 0 ]; then
        echo "Docker build successful. Starting application..."
        # Stop existing if any (optional? No, simple run)
        # Use interactive so user can see logs/stop it
        docker run -p 8000:8000 -p 8050:8050 -p 8888:8888 -p 8001:8001 -it "$TAG"
    else
        echo "Docker build failed."
        exit 1
    fi

else
    echo "Invalid build type: $TYPE"
    usage
    exit 1
fi
