# Sinusoidal Noise Detector Makefile

# Variables
BINARY_NAME=sinusoidal-noise-detector
BUILD_DIR=build
MAIN_PACKAGE=.
VERSION?=v1.0.0
COMMIT?=$(shell git rev-parse --short HEAD)
BUILD_TIME?=$(shell date -u '+%Y-%m-%d_%H:%M:%S')

# Build flags
LDFLAGS=-ldflags "-X main.Version=${VERSION} -X main.Commit=${COMMIT} -X main.BuildTime=${BUILD_TIME}"

# Go commands
GOCMD=go
GOBUILD=$(GOCMD) build
GOCLEAN=$(GOCMD) clean
GOTEST=$(GOCMD) test
GOGET=$(GOCMD) get
GOMOD=$(GOCMD) mod

# Default target
.PHONY: all
all: clean deps test build

# Build the application
.PHONY: build
build:
	@echo "Building ${BINARY_NAME}..."
	@mkdir -p ${BUILD_DIR}
	$(GOBUILD) $(LDFLAGS) -o ${BUILD_DIR}/${BINARY_NAME} $(MAIN_PACKAGE)
	@echo "Build complete: ${BUILD_DIR}/${BINARY_NAME}"

# Build for multiple platforms
.PHONY: build-all
build-all: clean deps
	@echo "Building for multiple platforms..."
	@mkdir -p ${BUILD_DIR}
	
	# Linux
	GOOS=linux GOARCH=amd64 $(GOBUILD) $(LDFLAGS) -o ${BUILD_DIR}/${BINARY_NAME}-linux-amd64 $(MAIN_PACKAGE)
	
	# Windows
	GOOS=windows GOARCH=amd64 $(GOBUILD) $(LDFLAGS) -o ${BUILD_DIR}/${BINARY_NAME}-windows-amd64.exe $(MAIN_PACKAGE)
	
	# macOS
	GOOS=darwin GOARCH=amd64 $(GOBUILD) $(LDFLAGS) -o ${BUILD_DIR}/${BINARY_NAME}-darwin-amd64 $(MAIN_PACKAGE)
	GOOS=darwin GOARCH=arm64 $(GOBUILD) $(LDFLAGS) -o ${BUILD_DIR}/${BINARY_NAME}-darwin-arm64 $(MAIN_PACKAGE)
	
	@echo "Multi-platform build complete"

# Download dependencies
.PHONY: deps
deps:
	@echo "Downloading dependencies..."
	$(GOMOD) download
	$(GOMOD) tidy

# Run tests
.PHONY: test
test:
	@echo "Running tests..."
	$(GOTEST) -v ./...

# Run tests with coverage
.PHONY: test-coverage
test-coverage:
	@echo "Running tests with coverage..."
	$(GOTEST) -v -coverprofile=coverage.out ./...
	$(GOCMD) tool cover -html=coverage.out -o coverage.html
	@echo "Coverage report generated: coverage.html"

# Clean build artifacts
.PHONY: clean
clean:
	@echo "Cleaning..."
	$(GOCLEAN)
	rm -rf ${BUILD_DIR}
	rm -f coverage.out coverage.html

# Install the application to GOPATH/bin
.PHONY: install
install:
	@echo "Installing ${BINARY_NAME}..."
	$(GOBUILD) $(LDFLAGS) -o $(GOPATH)/bin/${BINARY_NAME} $(MAIN_PACKAGE)

# Run the application with example parameters
.PHONY: run
run: build
	@echo "Running ${BINARY_NAME} with help..."
	./${BUILD_DIR}/${BINARY_NAME} -help

# Format code
.PHONY: fmt
fmt:
	@echo "Formatting code..."
	$(GOCMD) fmt ./...

# Lint code (requires golangci-lint)
.PHONY: lint
lint:
	@echo "Linting code..."
	golangci-lint run

# Vet code
.PHONY: vet
vet:
	@echo "Vetting code..."
	$(GOCMD) vet ./...

# Security scan (requires gosec)
.PHONY: security
security:
	@echo "Running security scan..."
	gosec ./...

# Generate documentation
.PHONY: docs
docs:
	@echo "Generating documentation..."
	$(GOCMD) doc -all ./...

# Check for outdated dependencies
.PHONY: check-deps
check-deps:
	@echo "Checking for outdated dependencies..."
	$(GOCMD) list -u -m all

# Update dependencies
.PHONY: update-deps
update-deps:
	@echo "Updating dependencies..."
	$(GOGET) -u ./...
	$(GOMOD) tidy

# Create a release archive
.PHONY: package
package: build-all
	@echo "Creating release packages..."
	@mkdir -p ${BUILD_DIR}/releases
	
	# Linux package
	tar -czf ${BUILD_DIR}/releases/${BINARY_NAME}-${VERSION}-linux-amd64.tar.gz -C ${BUILD_DIR} ${BINARY_NAME}-linux-amd64 -C .. README.md
	
	# Windows package
	zip -j ${BUILD_DIR}/releases/${BINARY_NAME}-${VERSION}-windows-amd64.zip ${BUILD_DIR}/${BINARY_NAME}-windows-amd64.exe README.md
	
	# macOS packages
	tar -czf ${BUILD_DIR}/releases/${BINARY_NAME}-${VERSION}-darwin-amd64.tar.gz -C ${BUILD_DIR} ${BINARY_NAME}-darwin-amd64 -C .. README.md
	tar -czf ${BUILD_DIR}/releases/${BINARY_NAME}-${VERSION}-darwin-arm64.tar.gz -C ${BUILD_DIR} ${BINARY_NAME}-darwin-arm64 -C .. README.md
	
	@echo "Release packages created in ${BUILD_DIR}/releases/"

# Development setup
.PHONY: dev-setup
dev-setup:
	@echo "Setting up development environment..."
	$(GOGET) github.com/golangci/golangci-lint/cmd/golangci-lint@latest
	$(GOGET) github.com/securecodewarrior/gosec/v2/cmd/gosec@latest
	@echo "Development tools installed"

# Full quality check
.PHONY: quality
quality: fmt vet lint test-coverage
	@echo "Quality check complete"

# Help target
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  build         - Build the application"
	@echo "  build-all     - Build for multiple platforms"
	@echo "  deps          - Download dependencies"
	@echo "  test          - Run tests"
	@echo "  test-coverage - Run tests with coverage report"
	@echo "  clean         - Clean build artifacts"
	@echo "  install       - Install to GOPATH/bin"
	@echo "  run           - Build and run with help"
	@echo "  fmt           - Format code"
	@echo "  lint          - Lint code (requires golangci-lint)"
	@echo "  vet           - Vet code"
	@echo "  security      - Run security scan (requires gosec)"
	@echo "  docs          - Generate documentation"
	@echo "  check-deps    - Check for outdated dependencies"
	@echo "  update-deps   - Update dependencies"
	@echo "  package       - Create release packages"
	@echo "  dev-setup     - Setup development tools"
	@echo "  quality       - Run full quality check"
	@echo "  all           - Clean, deps, test, and build"
	@echo "  help          - Show this help message"