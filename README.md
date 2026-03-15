#     Autodoc.AI - Smart Documentation Generator

## Overview / Description

Autodoc.AI is a web-based application designed to streamline the process of generating comprehensive technical documentation for software projects. It provides a user-friendly interface where developers can input either a GitHub repository URL or a local project directory path. The system then analyzes the codebase, extracts relevant information, and leverages a powerful generative text service to produce high-quality, structured Markdown documentation. This tool aims to significantly reduce the manual effort involved in creating and maintaining project documentation, making it easier for teams to keep their projects well-documented.

## Architecture & Tech Stack

The project follows a client-server architecture, with a Python-based backend API and a modern web frontend.

**Backend:**
*   **Language:** Python 3.x
*   **Web Framework:** FastAPI
*   **ASGI Server:** Uvicorn
*   **Dependency Management:** `requirements.txt`
*   **Environment Variables:** `python-dotenv`
*   **File System Utilities:** `pathspec` (for `.gitignore` parsing), `os`, `shutil`, `tempfile`, `subprocess`
*   **Generative Text Service Integration:** `google-genai` (for interacting with the generative text model)

**Frontend:**
*   **Languages:** HTML, CSS, JavaScript
*   **Markdown Rendering:** `marked.js`
*   **Code Highlighting:** `highlight.js`
*   **Styling:** Custom CSS (`static/styles.css`) with a modern, dark theme.

**Generative Text Model:**
*   The system integrates with a highly capable generative text model (specifically `gemini-2.5-flash`) to process codebase context and generate documentation.

## Directory Structure

The project maintains a clear and organized directory structure:

```
.
├── main.py                     # Main FastAPI application entry point
├── requirements.txt            # Python dependencies
├── static/                     # Frontend static assets
│   ├── index.html              # Main frontend HTML page
│   ├── script.js               # Frontend JavaScript logic
│   └── styles.css              # Frontend CSS styling
└── utils/                      # Utility modules
    ├── ai_generator.py         # Handles interaction with the generative text service
    └── file_parser.py          # Parses project directories and builds codebase context
```

## Core Components / Modules

### `main.py`

This is the central entry point for the FastAPI application. It sets up the web server, defines API routes, and orchestrates the documentation generation workflow.

*   **FastAPI Application:** Initializes the FastAPI app with CORS middleware for development.
*   **Static File Serving:** Mounts the `static/` directory to serve the frontend assets (`index.html`, `script.js`, `styles.css`).
*   **Root Endpoint (`/`):** Serves the `index.html` file, acting as the main interface for the application.
*   **Documentation Generation Endpoint (`/api/generate`):**
    *   Accepts `source_type` (either "github" or "local") and `source_path` (GitHub URL or local directory path).
    *   For GitHub URLs, it clones the repository into a temporary directory using `git clone`.
    *   For local paths, it validates the directory existence.
    *   Calls `utils.file_parser.build_project_context` to create a comprehensive string representation of the codebase.
    *   Invokes `utils.ai_generator.generate_documentation` to send the context to the generative text service and retrieve the Markdown documentation.
    *   Handles errors and cleans up temporary directories.

### `utils/file_parser.py`

This module is responsible for traversing a given project directory and compiling its contents into a single, structured string that can be sent to the generative text service.

*   **`DEFAULT_IGNORED`:** A list of common directories and file patterns (e.g., `.git`, `node_modules`, `__pycache__`, binary files) that should be excluded from the context.
*   **`load_gitignore(base_path)`:** Reads a `.gitignore` file if present in the base path and combines its patterns with the `DEFAULT_IGNORED` list to create a `pathspec.PathSpec` object for efficient matching.
*   **`is_text_file(filepath)`:** A rudimentary check to determine if a file is likely a text file (and thus readable) or a binary file.
*   **`build_project_context(directory_path)`:**
    *   Recursively walks through the specified directory.
    *   Filters out files and directories based on the loaded `.gitignore` patterns.
    *   Reads the content of each included text file.
    *   Concatenates the relative file path and its content into a single string, formatted for easy parsing by the generative text service.

### `utils/ai_generator.py`

This module acts as the interface to the external generative text service, handling the actual documentation generation.

*   **`generate_documentation(project_context)`:**
    *   Retrieves the `GEMINI_API_KEY` from environment variables, ensuring secure access.
    *   Initializes the `google.genai.Client`.
    *   Constructs a detailed `system_instruction` to guide the generative text model on the expected output format and role (expert software engineer/technical writer).
    *   Prepares a `user_prompt` that embeds the `project_context` within a `<project_codebase>` tag.
    *   Sends the prompt to the `gemini-2.5-flash` model with a low temperature setting (0.2) to encourage factual and consistent output.
    *   Returns the generated Markdown documentation.
    *   Includes error handling for API communication failures.

### `static/index.html`

The main frontend HTML file that provides the user interface for Autodoc.AI.

*   **Structure:** Contains a header with the project logo and subtitle, an input card for specifying the source (GitHub URL or local path), a loading indicator, and an output container for displaying the generated documentation.
*   **Tabs:** Allows users to switch between "GitHub URL" and "Local Folder" input modes.
*   **Output Display:** Features two views for the documentation: a rendered Markdown view and a raw Markdown text area, along with copy functionality.
*   **External Libraries:** Integrates `marked.js` for Markdown-to-HTML conversion and `highlight.js` for syntax highlighting of code blocks.
*   **Custom Styling:** Links to `static/styles.css` for the application's visual design.

### `static/script.js`

This JavaScript file handles all client-side logic and interactions for the Autodoc.AI frontend.

*   **`marked.js` Configuration:** Configures `marked.js` to use `highlight.js` for code block syntax highlighting.
*   **DOM Element References:** Selects various HTML elements for interaction.
*   **UI State Management:** Manages the active source type (`github` or `local`), toggling between raw and rendered documentation views, and displaying loading states.
*   **Tab Switching Logic:** Updates the input field placeholder, helper text, and icon based on the selected source type.
*   **Toast Notifications:** Implements a simple toast notification system for user feedback (success/error messages).
*   **`generate-btn` Event Listener:**
    *   Triggers an asynchronous `POST` request to `/api/generate` with the user-provided `source_type` and `source_path`.
    *   Updates the UI to show a loading spinner and hides the output container during generation.
    *   Upon successful response, renders the Markdown documentation using `marked.js` and `highlight.js`, then displays it.
    *   Handles and displays any errors returned by the API.
    *   Resets the UI state after completion.
*   **`copy-btn` Event Listener:** Copies the raw Markdown documentation to the user's clipboard.
*   **`raw-btn` Event Listener:** Toggles between the rendered HTML view and the raw Markdown text area.
*   **`pathInput` Keypress Listener:** Allows users to trigger documentation generation by pressing Enter in the input field.

### `static/styles.css`

This CSS file defines the visual styling for the Autodoc.AI web interface.

*   **Variables:** Uses CSS custom properties (`:root`) for consistent theming (colors, fonts).
*   **Global Styles:** Sets basic typography, background, and layout for the entire page.
*   **Decorative Elements:** Includes animated background "blobs" for a modern aesthetic.
*   **Component Styling:** Provides styles for the header, logo, input card, tabs, buttons, loader, and output container.
*   **Markdown Rendering Styles:** Specifically targets HTML elements generated by `marked.js` (headings, paragraphs, lists, code blocks, blockquotes) to ensure a clean and readable presentation within the output container.
*   **Animations:** Defines keyframe animations for UI elements (fade-in, spin, float) to enhance user experience.
*   **Toast Styling:** Styles the transient notification messages.

## Getting Started / Installation

To set up and run the Autodoc.AI project locally, follow these steps:

### Prerequisites

*   **Python 3.8+**: Ensure Python is installed on your system.
*   **Git**: Required for cloning GitHub repositories.
*   **A Generative Text Service API Key**: An API key for the integrated generative text service (e.g., Google Gemini API Key) is essential.

### 1. Clone the Repository

First, clone the project repository to your local machine:

```bash
git clone <repository_url>
cd ai-doc-generator # Or whatever your project directory is named
```

### 2. Set up a Virtual Environment (Recommended)

It's good practice to use a virtual environment to manage project dependencies:

```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

Install the required Python packages using `pip`:

```bash
pip install -r requirements.txt
```
*(Note: The `requirements.txt` file contains `p a t h s p e c` which should be `pathspec`.)*

### 4. Configure Environment Variables

Create a `.env` file in the root directory of the project (`ai-doc-generator/`) and add your generative text service API key:

```
GEMINI_API_KEY="your_api_key_here"
```
Replace `"your_api_key_here"` with your actual API key.

### 5. Run the Application

Start the FastAPI application using Uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
The `--reload` flag is useful for development as it automatically restarts the server on code changes.

### 6. Access the Web Interface

Open your web browser and navigate to:

```
http://localhost:8000
```

You should see the Autodoc.AI frontend, ready to generate documentation.

## API Endpoints

The Autodoc.AI backend exposes the following API endpoints:

### `GET /`

*   **Description:** Serves the main frontend HTML page (`static/index.html`). This is the entry point for the web interface.
*   **Response:** `HTMLResponse` containing the content of `index.html`.

### `POST /api/generate`

*   **Description:** The primary endpoint for initiating documentation generation. It accepts a project source (GitHub URL or local path) and returns the generated Markdown documentation.
*   **Request Body:**
    *   **Type:** `application/json`
    *   **Schema:** `GenerateRequest` (Pydantic model)
        ```json
        {
            "source_type": "string",  // Required. Must be "github" or "local".
            "source_path": "string"   // Required. The GitHub repository URL or absolute local filesystem path.
        }
        ```
*   **Responses:**
    *   **`200 OK`**:
        ```json
        {
            "status": "success",
            "documentation": "string" // The generated documentation in Markdown format.
        }
        ```
    *   **`400 Bad Request`**:
        ```json
        {
            "detail": "string" // Error message, e.g., "Path or URL cannot be empty." or "Invalid local directory path: <path>"
        }
        ```
    *   **`500 Internal Server Error`**:
        ```json
        {
            "detail": "string" // Error message, e.g., "Failed to clone GitHub repository..." or "Generation failed: <error_details>"
        }
        ```
