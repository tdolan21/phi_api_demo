# Phi 1.5 API w/Demo Application

This repo is an extension of the phi_1.5_api but includes a chat application demo of the endpoints. Available utilizing the research license provided by Microsoft.

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
  - [Database](#database)
  - [Chat Application](#chat-application)
  - [API](#api)
- [Docker Network](#docker-network)
- [Contributing](#contributing)
- [License](#license)

## Introduction

This project is a comprehensive solution that includes a chat application, an API, and a PostgreSQL database, all hosted in a Docker network. It allows users to interact with the chat application, generate text via the API, and stores questions and answers in a database. The user can then generate a csv of the stored database data.

Make sure you have followed the proper setup instructions for the phi_1.5_api [repository](https://github.com/tdolan21/phi_1.5_api).

## Installation

```bash
git clone https://github.com/tdolan21/phi_api_demo
cd phi_api_demo
docker compose up --build
```
Thats it.


## Usage

The api will be avilable at port:

```
8000
```
The streamlit chat application will be available at port:

```
8501
```
The postgreSQL database will be available at port:

```
5432
```
### Database

The postgreSQL database will store questions and responses from the model for the purpose of analyis in other models or evaluating the performance using other tools.

### Chat Application

The chat application is a simple implementation showing some features that can be built using the api.

### API

The API is built using FastAPI and is responsible for text generation. It is GPU-accelerated and optimized for high performance. The API receives text prompts and generation parameters from the chat application and returns the generated text.

**'/'**: Returns "welcome to phi 1.5 api" to test connection
**'/docs'**: This endpoint is provided by FastAPI to test the endpoints manually
**'/phi'**: Expects a string and max_length integer. Returns the raw model output.
**'/phi/codegen'**: Expects a string and returns formmatted pyhton code.
**'/health'**: Returns a runtime check with stamped datetime.

### Docker Network

These services are all connected through a bridge network:

    web: The chat application
    api: The FastAPI service
    db: The PostgreSQL database

## License

This API is provided using the research license provided by Microsoft. The license will be available here as well. This project follows the guidelines in the license and you are expected to as well.