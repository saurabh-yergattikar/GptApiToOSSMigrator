# HarmonyMigrator 🚀

> **Migrate your OpenAI apps to local GPT-OSS models in one command!**

HarmonyMigrator automates the migration of codebases from paid OpenAI API dependencies to local, offline usage of GPT-OSS models (gpt-oss-20b and gpt-oss-120b) via the Harmony response format.

[![PyPI version](https://badge.fury.io/py/harmony-migrator.svg)](https://badge.fury.io/py/harmony-migrator)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## ✨ Features

- **🔍 Smart Scanning**: Automatically detects OpenAI API calls in your codebase
- **🔄 Seamless Conversion**: Maps OpenAI prompts to Harmony format with roles/channels
- **💰 Cost Savings**: Eliminate API bills with local inference
- **🔒 Privacy First**: All processing happens locally, no data sent externally
- **🛠️ Tool Support**: Migrates function calls to Harmony's native tools
- **📊 Detailed Reports**: Get insights on potential savings and migration success

## 🚀 Quick Start

### Installation

```bash
pip install harmony-migrator
```

### Basic Usage

```bash
# Scan a repository for OpenAI API calls
harmony-migrator scan https://github.com/user/my-ai-app --output report.json

# Convert and apply migrations
harmony-migrator convert --repo . --model gpt-oss-20b --backend ollama --apply
```

## 📖 Examples

### 1. Scan Your Codebase

```bash
# Scan local directory
harmony-migrator scan ./my-project --output scan-report.json

# Scan GitHub repository
harmony-migrator scan https://github.com/username/project --output report.json
```

**Output:**
```json
{
  "summary": {
    "total_files_scanned": 15,
    "api_calls_found": 8,
    "estimated_monthly_savings": "$45.50",
    "migration_complexity": "medium"
  },
  "calls": [
    {
      "file": "app.py",
      "line": 23,
      "type": "chat_completion",
      "complexity": "simple",
      "estimated_tokens": 150
    }
  ]
}
```

### 2. Convert OpenAI Code to Harmony

**Before (OpenAI):**
```python
import openai

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
)
```

**After (Harmony + GPT-OSS):**
```python
from harmony_migrator.inference import LocalInference

inference = LocalInference(model="gpt-oss-20b", backend="ollama")

conversation = Conversation(
    roles=[
        Role(
            name="system",
            content="You are a helpful assistant."
        ),
        Role(
            name="developer",
            content="Hello!"
        )
    ],
    channels=[
        Channel(name="analysis", content=""),
        Channel(name="final", content="")
    ]
)

response = inference.generate(conversation)
```

### 3. Tool Migration

**Before (OpenAI Functions):**
```python
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "What's the weather in NYC?"}],
    functions=[{
        "name": "get_weather",
        "description": "Get weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            }
        }
    }]
)
```

**After (Harmony Tools):**
```python
from harmony_migrator.tools import WeatherTool

conversation = Conversation(
    roles=[
        Role(name="developer", content="What's the weather in NYC?")
    ],
    tools=[WeatherTool()],
    channels=[
        Channel(name="analysis", content=""),
        Channel(name="final", content="")
    ]
)
```

## 🛠️ CLI Reference

### Scan Command

```bash
harmony-migrator scan [REPO_PATH] [OPTIONS]
```

**Options:**
- `--output, -o`: Output file path (default: scan-report.json)
- `--format`: Output format (json, csv, table)
- `--verbose, -v`: Verbose output
- `--exclude`: Exclude patterns (glob)

### Convert Command

```bash
harmony-migrator convert [OPTIONS]
```

**Options:**
- `--repo, -r`: Repository path (default: current directory)
- `--model`: GPT-OSS model (gpt-oss-20b, gpt-oss-120b)
- `--backend`: Inference backend (ollama, vllm, transformers)
- `--apply`: Apply changes (default: dry-run)
- `--dry-run`: Preview changes without applying
- `--reasoning-effort`: Harmony reasoning effort (low, medium, high)
- `--output-dir`: Output directory for converted files

### Global Options

- `--help, -h`: Show help
- `--version`: Show version
- `--quiet, -q`: Suppress output
- `--color`: Force color output

## 🔧 Configuration

Create a `.harmony-migrator.toml` file in your project root:

```toml
[defaults]
model = "gpt-oss-20b"
backend = "ollama"
reasoning_effort = "medium"

[scanning]
exclude_patterns = ["*.test.py", "venv/*", "node_modules/*"]
max_file_size = "10MB"

[conversion]
preserve_comments = true
add_imports = true
backup_files = true

[inference]
ollama_host = "http://localhost:11434"
vllm_host = "http://localhost:8000"
```

## 🏗️ Architecture

```
[User Input: CLI/Command] → [Frontend: Typer CLI Parser]
                                    ↓
[Core Engine: Scanner (AST/Regex Parsers)] → Detect API Calls → Report Generator
                                    ↓
[Converter Module: Harmony Mapper] → Build Conversation Objects → Inject Inference
                                    ↓
[Applier: Git Integration] → Patched Files/PR Creator → Validation Tester
```

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=harmony_migrator

# Run specific test
pytest tests/test_scanner.py::test_detect_openai_calls
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone repository
git clone https://github.com/harmony-migrator/harmony-migrator.git
cd harmony-migrator

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black harmony_migrator/
isort harmony_migrator/

# Type checking
mypy harmony_migrator/
```

## 📊 Roadmap

### v1.0 (Current)
- ✅ Python codebase scanning
- ✅ OpenAI API call detection
- ✅ Harmony format conversion
- ✅ Local inference integration
- ✅ CLI interface

### v1.1 (Next)
- 🔄 JavaScript/TypeScript support
- 🔄 VS Code extension
- 🔄 Web UI (Streamlit)
- 🔄 Fine-tuning integration

### v1.2 (Future)
- 🔄 Multi-language support (Ruby, Go)
- 🔄 Enterprise features
- 🔄 Community extensions
- 🔄 Advanced tool migration

## 📈 Success Metrics

- **GitHub**: 200-300 stars, 100+ forks
- **Usage**: 1k+ downloads, 50+ issues/PRs
- **User Feedback**: NPS >8/10
- **Community**: Active contributors, real-world examples

## ⚠️ Limitations

- Currently supports Python codebases (JS support coming in v1.1)
- Requires local GPT-OSS model setup (Ollama/vLLM)
- Complex tool schemas may need manual review
- Large codebases (>100k lines) may have performance impact

## 🆘 Troubleshooting

### Common Issues

**"No OpenAI API calls found"**
- Ensure your code uses `openai.ChatCompletion.create` or similar patterns
- Check if files are excluded by patterns in config

**"Conversion failed"**
- Review the error message for specific issues
- Try with `--dry-run` to see what would be changed
- Check Harmony format compatibility

**"Inference backend not found"**
- Install and start Ollama: `ollama serve`
- Or install vLLM: `pip install vllm`
- Check backend configuration in `.harmony-migrator.toml`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for the original API design
- Harmony team for the structured format
- Ollama and vLLM teams for local inference
- Open source community for inspiration and feedback

---

**Made with ❤️ for the open-source AI community**

*Migrate to local AI, save costs, preserve privacy.* 