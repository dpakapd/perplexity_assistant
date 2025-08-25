# Perplexity Voice Assistant for Raspberry Pi
This project is a hands-free, voice-activated AI assistant that runs on a Raspberry Pi. It uses a custom wake word to activate, listens for spoken commands, and leverages the Perplexity API to provide fast, accurate, and up-to-date answers.

This assistant is designed to be a standalone device, perfect for a desk or workshop, providing quick, conversational access to information without needing to interact with a screen.

# Features
Hands-Free Activation: Uses a custom wake word ("Krishna") powered by the highly accurate PicoVoice Porcupine engine.

Real-Time Answers: Integrates with the Perplexity API (llama-3-sonar-large-32k-online) to answer questions using live web search.

Voice Interaction: Uses Google's Text-to-Speech for natural-sounding responses and the SpeechRecognition library for transcribing user commands.

Standalone Operation: Designed to run automatically on boot as a systemd service on a headless Raspberry Pi.

Robust Audio Handling: Utilizes a single, continuous audio stream to prevent hardware conflicts between the wake word engine and the command listener.

# Hardware Requirements
Raspberry Pi 4 or 5 (Raspberry Pi 5 recommended)

A high-quality USB Microphone

A USB-powered Speaker

A reliable Power Supply for the Raspberry Pi

A microSD Card (16GB or larger)

# Software & API Setup
Before you begin, you will need to sign up for two free services to get the necessary API keys.

Perplexity API Key:

Go to the Perplexity Labs Platform and create a free account.

Generate a new API key and save it.

PicoVoice Porcupine Access Key & Wake Word:

Create a free account at the PicoVoice Console.

Copy your AccessKey from the main dashboard.

Go to the Porcupine tab, train a custom wake word (e.g., "Krishna"), and select Raspberry Pi as the platform.

Download the resulting .ppn model file.

