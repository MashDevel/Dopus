<!-- This file is auto-generated. Do not edit it directly. -->

# Contributing to Dopus

Thank you for your interest in contributing to Dopus! We welcome contributions from everyone and are grateful for even the smallest of improvements.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Setting Up the Development Environment](#setting-up-the-development-environment)
3. [Making Changes](#making-changes)
4. [Submitting a Pull Request](#submitting-a-pull-request)
5. [Code Style and Guidelines](#code-style-and-guidelines)
6. [Running Tests](#running-tests)
7. [Reporting Bugs](#reporting-bugs)
8. [Feature Requests](#feature-requests)

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
   ```
   git clone https://github.com/[YourUsername]/dopus.git
   ```
3. Create a new branch for your feature or bug fix
   ```
   git checkout -b feature/your-feature-name
   ```

## Setting Up the Development Environment

1. Ensure you have Python 3.7+ installed on your system.
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up your OpenAI API key in a `.env` file:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Making Changes

1. Make your changes in your feature branch
2. Add your changes
   ```
   git add .
   ```
3. Commit your changes with a descriptive commit message
   ```
   git commit -m "Add a brief description of your changes"
   ```
4. Push your changes to your fork on GitHub
   ```
   git push origin feature/your-feature-name
   ```

## Submitting a Pull Request

1. Go to the original Dopus repository on GitHub
2. Click on "Pull Requests" and then the "New Pull Request" button
3. Select your fork and the feature branch you created
4. Add a title and description for your pull request
5. Click "Create Pull Request"

## Code Style and Guidelines

- Follow PEP 8 guidelines for Python code
- Use meaningful variable and function names
- Write docstrings for classes and functions
- Keep functions small and focused on a single task
- Use type hints where appropriate

## Running Tests

We use the `DopusTest` framework for testing. To run tests:

1. Navigate to the `dopus/test` directory
2. Run the test file:
   ```
   python dopus_test.py
   ```

To add new tests, use the `@test` or `@test_multi` decorators as shown in the existing test files.
