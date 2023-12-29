# 📦Prompts package

Package whose files contain **auxiliary prompts and utilities** for the chatbot prompt engineering.

## Actions

Module with **customizable instructions** _(mostly lambda functions that return strings)_ that can be passed to the virtual assistant's generative model to obtain a specific result.

Some of this instructions are:

- How the Chatbot should say goodbye at the end of a chat session
- How by a given code project structure the AI model should create a `README.md` file
- Hoy by a given programming language the AI model should document a given function

## System

Module with **prompts** _(constant strings)_ that specify the behavior of the virtual assistant.

This prompts give information such as:

- The **identity** that the chatbot must assume
- The **personality** and character of its responses
- Information about its **abilities** and **limitations**
