// Configure marked.js to use highlight.js
marked.setOptions({
    highlight: function(code, lang) {
        const language = hljs.getLanguage(lang) ? lang : 'plaintext';
        return hljs.highlight(code, { language }).value;
    },
    langPrefix: 'hljs language-',
    breaks: true
});

document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const generateBtn = document.getElementById('generate-btn');
    const pathInput = document.getElementById('source-path');
    const tabs = document.querySelectorAll('.tab-btn');
    const helperText = document.getElementById('helper-text');
    const inputIcon = document.getElementById('input-icon');
    
    const loader = document.getElementById('loader');
    const outputContainer = document.getElementById('output-container');
    const markdownContent = document.getElementById('markdown-content');
    const rawMarkdownArea = document.getElementById('raw-markdown');
    
    const copyBtn = document.getElementById('copy-btn');
    const rawBtn = document.getElementById('raw-btn');
    const toast = document.getElementById('toast');
    
    let rawMarkdown = "";
    let currentSourceType = "github"; // default
    let showingRaw = false;

    // UI Text Configurations
    const uiConfig = {
        github: {
            placeholder: "https://github.com/username/repository",
            helper: "Just paste the public link to the repository you want to document!",
            icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>`
        },
        local: {
            placeholder: "C:\\Users\\Path\\To\\Your\\Project...",
            helper: "Enter the absolute path to a local directory on your machine.",
            icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>`
        }
    };

    // Tab Switching
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            currentSourceType = tab.dataset.type;
            const config = uiConfig[currentSourceType];
            
            pathInput.placeholder = config.placeholder;
            helperText.textContent = config.helper;
            inputIcon.innerHTML = config.icon;
            pathInput.value = "";
            pathInput.focus();
        });
    });

    function showToast(message, type = 'success') {
        toast.textContent = message;
        toast.className = `toast ${type} show`;
        setTimeout(() => {
            toast.className = `toast ${type}`;
        }, 3000);
    }

    // Toggle Raw View
    rawBtn.addEventListener('click', () => {
        showingRaw = !showingRaw;
        if (showingRaw) {
            markdownContent.style.display = 'none';
            rawMarkdownArea.style.display = 'block';
            rawMarkdownArea.value = rawMarkdown;
            rawBtn.textContent = "View Rendered";
        } else {
            markdownContent.style.display = 'block';
            rawMarkdownArea.style.display = 'none';
            rawBtn.textContent = "View Raw";
        }
    });

    // Generate Request
    generateBtn.addEventListener('click', async () => {
        const path = pathInput.value.trim();
        
        if (!path) {
            showToast("Please enter a URL or path.", "error");
            return;
        }

        // UI State: Loading
        generateBtn.disabled = true;
        loader.style.display = 'flex';
        outputContainer.style.display = 'none';
        
        // Reset raw view
        showingRaw = false;
        markdownContent.style.display = 'block';
        rawMarkdownArea.style.display = 'none';
        rawBtn.textContent = "View Raw";

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    source_type: currentSourceType,
                    source_path: path 
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Failed to generate documentation');
            }

            // UI State: Success
            rawMarkdown = data.documentation;
            markdownContent.innerHTML = marked.parse(rawMarkdown);
            rawMarkdownArea.value = rawMarkdown;
            
            outputContainer.style.display = 'block';
            outputContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
            
            showToast("Documentation generated successfully!");

        } catch (error) {
            console.error(error);
            showToast(error.message, "error");
        } finally {
            // UI State: Reset Loading
            generateBtn.disabled = false;
            loader.style.display = 'none';
        }
    });

    // Copy Markdown
    copyBtn.addEventListener('click', () => {
        if (!rawMarkdown) return;
        
        navigator.clipboard.writeText(rawMarkdown).then(() => {
            showToast("Markdown copied to clipboard!");
            
            const originalText = copyBtn.innerHTML;
            copyBtn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg> Copied!`;
            copyBtn.style.color = "var(--success)";
            copyBtn.style.borderColor = "var(--success)";
            
            setTimeout(() => {
                copyBtn.innerHTML = originalText;
                copyBtn.style.color = "";
                copyBtn.style.borderColor = "";
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy', err);
            showToast("Failed to copy to clipboard", "error");
        });
    });

    // Press enter to submit
    pathInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            generateBtn.click();
        }
    });
});
