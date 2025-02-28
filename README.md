# Integration QA

Automated Quality Assurance testing framework for Weaviate integrations, implemented through GitHub Actions.

## Overview

This repository contains automated tests for various Weaviate integrations, executed through GitHub Actions workflows. The automated QA pipeline ensures that each integration works correctly with Weaviate's core functionality through continuous testing and validation.

## Available Integrations

- LangChain - Test vector store operations with LangChain integration

## Project Structure

```
integration-qa/
├── .github/workflows/
│   ├── crud-test-template.yml
│   └── run-all-tests.yml
├── integrations/
│   └── langchain/
│       ├── test_crud.py
│       └── requirements.txt
└── README.md
```

## Local Testing with Act

You can test GitHub Actions workflows locally using [Act](https://github.com/nektos/act). This allows you to debug workflows without pushing to GitHub.

Note: Act requires Docker to be installed and running.

## Contributing

1. Add your integration in the `integrations/` directory
2. Follow the existing test structure in `test_crud.py`
3. Update requirements.txt with necessary dependencies
4. Test locally before submitting a PR
