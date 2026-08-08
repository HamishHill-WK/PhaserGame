# Phaser Game Research Platform

A web-based research platform for studying game development and AI-assisted coding using a Phaser.js breakout game implementation.

## Overview

This is a Flask-based web application designed for conducting research experiments on game development with and without AI assistance. Participants interact with a breakout game built using Phaser.js and can modify the game code through a web-based code editor.

## Features

- **Breakout Game**: Classic breakout game implemented with Phaser.js 3.60.0
- **Code Editor**: Web-based code editor with syntax highlighting using ACE Editor
- **AI Assistant**: Optional AI-powered coding assistant for participants
- **Experiment Management**: Randomized condition assignment (AI vs control)
- **Data Collection**: Comprehensive logging of user interactions, code changes, and survey responses
- **Survey System**: Pre and post-task surveys including SUS (System Usability Scale)

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Game Engine**: Phaser.js 3.60.0
- **Code Editor**: ACE Editor
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI Integration**: OpenAI API
- **Deployment**: AWS Elastic Beanstalk (previously hosted)
- **Data Storage**: AWS-managed database services (not directly available in this repository)

## Deployment & Data Storage

**Note**: This application was originally hosted on AWS Elastic Beanstalk with AWS-managed database services handling all data storage and management. The data storage functionality is not directly available in this repository as it relied on AWS infrastructure.

The `local-folder/` directory contains exported data samples from the AWS database for reference.

## Local Development Setup

To run this application locally (note that database functionality will be limited without AWS infrastructure):

1. Install Python dependencies:
	```bash
	pip install -r requirements.txt
	```

2. Set up environment variables in `.env`:
	```
	SECRET_KEY=your_secret_key
	DATABASE_URL=your_local_database_url
	OPENAI_API_KEY=your_openai_api_key
	```

3. Initialize a local database (if available):
	```bash
	python setup_database.py
	```

4. Run the application:
	```bash
	python application.py
	```

## Project Structure

```
PhaserGame/
├── application.py          # Main Flask application
├── application_helper.py   # Helper functions for experiment logic
├── assistant.py           # AI assistant integration
├── data.py               # Database models and configuration
├── setup_database.py     # Database initialization script
├── static/
│   ├── assets/           # Game assets and images
│   ├── css/             # Stylesheets
│   └── js/              # JavaScript files including game logic
├── templates/           # HTML templates
└── requirements.txt     # Python dependencies
```

## Key Components

### Game Implementation
- `static/js/game.js`: Core breakout game logic using Phaser.js
- `static/assets/breakout/`: Game sprites and assets
- Real-time code execution and game reloading

### Experiment System
- Randomized condition assignment (AI assistant vs control)
- Session management and participant tracking
- Comprehensive data logging for research analysis

### Data Collection
- User interactions and game events
- Code changes with timestamps and diffs
- Survey responses and usability metrics
- Task completion tracking

## Usage

1. Participants start at the index page and provide consent
2. Complete demographic and experience surveys
3. Assigned to either AI-assisted or control condition
4. Complete game modification tasks
5. Fill out post-task surveys including SUS scale

## Research Applications

This platform is designed for studying:
- Human-AI collaboration in programming tasks
- Code comprehension and modification patterns
- Impact of AI assistance on task performance
- User experience with AI-powered development tools

## License

[Add your license information here]

## Contributors

[Add contributor information here]