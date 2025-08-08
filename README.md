# 🚀 HarmonyMigrator

A tool to help migrate OpenAI API calls to local models.

## 🎯 Current Features (v0.1)

- ✅ **API Call Detection**: Scan your codebase for OpenAI API usage
- ✅ **Cost Analysis**: Estimate current API costs
- ✅ **Usage Patterns**: Identify common API patterns
- ✅ **Basic Chat Migration**: Simple chat completion migration to local models

## 🚧 Planned Features

- Function calling and tools
- Embeddings migration
- Streaming responses
- Multi-turn conversations
- Fine-tuning migration
- Multiple model backends

## 🛠️ Installation

```bash
pip install -r requirements.txt
```

## 📊 Usage

Scan your codebase:
```bash
python -m harmony_migrator scan /path/to/your/code
```

Get cost estimates:
```bash
python -m harmony_migrator analyze /path/to/your/code
```

Basic chat migration:
```bash
python -m harmony_migrator migrate /path/to/your/code --type chat
```

## 📈 Example Output

```
Scanning repository: /path/to/your/code
Found OpenAI API calls:
- chat_service.py:20 (chat completion)
- embedding_service.py:15 (embedding)

Estimated monthly cost: $123.45
Potential savings with local models: $100.00
```

## 🤝 Contributing

This is an early version focused on basic functionality. We welcome:
- Bug reports
- Feature requests
- Documentation improvements
- Code contributions

## 📝 License

MIT License
