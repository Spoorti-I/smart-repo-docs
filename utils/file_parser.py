import os
import pathspec

# Default ignored directories and files
DEFAULT_IGNORED = [
    ".git", "__pycache__", "node_modules", "venv", "env", ".env",
    "dist", "build", ".next", ".cache", "coverage", ".idea", ".vscode",
    "*.pyc", "*.pyo", "*.pyd", "*.so", "*.dll", "*.class",
    # Images, video, audio
    "*.png", "*.jpg", "*.jpeg", "*.gif", "*.svg", "*.ico", "*.webp",
    "*.mp4", "*.webm", "*.mp3", "*.wav",
    # Binaries, archives, fonts
    "*.exe", "*.bin", "*.zip", "*.tar", "*.gz", "*.7z",
    "*.ttf", "*.otf", "*.woff", "*.woff2",
    # Lock files
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "Poetry.lock", "Pipfile.lock"
]

def load_gitignore(base_path: str) -> pathspec.PathSpec:
    """Loads .gitignore patterns if present."""
    patterns = list(DEFAULT_IGNORED)
    gitignore_path = os.path.join(base_path, '.gitignore')
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            patterns.extend(f.readlines())
    
    return pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, patterns)

def is_text_file(filepath: str) -> bool:
    """Very rudimentary check if a file is text or binary."""
    try:
        with open(filepath, 'tr') as check_file:
            check_file.read(1024)
            return True
    except UnicodeDecodeError:
        return False

def build_project_context(directory_path: str) -> str:
    """
    Recursively reads a directory, skipping ignored files, 
    and returns a concatenated string of file paths and contents.
    """
    if not os.path.isdir(directory_path):
        raise ValueError(f"Path is not a valid directory: {directory_path}")

    spec = load_gitignore(directory_path)
    project_context = f"Project Path: {directory_path}\n=================\n\n"

    for root, dirs, files in os.walk(directory_path):
        # Filter directories in-place to prevent walking into ignored ones
        dirs[:] = [d for d in dirs if not spec.match_file(os.path.relpath(os.path.join(root, d), directory_path))]

        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, directory_path)
            
            if spec.match_file(rel_path):
                continue
                
            if not is_text_file(file_path):
                continue

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    project_context += f"--- {rel_path} ---\n```\n{content}\n```\n\n"
            except Exception as e:
                project_context += f"--- {rel_path} ---\n[Error reading file: {e}]\n\n"

    return project_context
