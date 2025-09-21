# Nightingale VoiceAI

专业医疗语音AI系统，提供隐私保护的患者护理体验。

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 启动系统
./start_system.sh
```

## 访问系统

- **患者门户**: http://localhost:8501
- **管理控制台**: http://localhost:8502  
- **API文档**: http://localhost:8888/docs

## 主要功能

- 🛡️ 隐私保护：自动PHI检测和数据脱敏
- 🎤 语音处理：高精度转录和智能分析
- 📋 智能摘要：患者和医护版差异化摘要
- 🏥 专业界面：符合医疗标准的用户体验

## 使用流程

1. 访问患者门户 (http://localhost:8501)
2. 填写数字同意书
3. 上传音频文件
4. 查看智能摘要结果

## Documentation

- [User Guide](docs/GUIDE.md) - Complete usage instructions
- [Project Summary](docs/PROJECT_SUMMARY.md) - Technical architecture and features
- [Technical Brief](docs/candidate_brief.md) - Comprehensive technical documentation

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Patient App   │    │   Clinician App  │    │   Admin Panel   │
└─────────┬───────┘    └──────────┬───────┘    └─────────┬───────┘
          │                       │                      │
          └───────────────────────┼──────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │      API Gateway          │
                    │   (Auth + Rate Limiting)  │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │    Nightingale Core       │
                    │  ┌─────────────────────┐  │
                    │  │  Consent Manager    │  │
                    │  ├─────────────────────┤  │
                    │  │  PHI Redactor       │  │
                    │  ├─────────────────────┤  │
                    │  │  Voice Processor    │  │
                    │  ├─────────────────────┤  │
                    │  │  Provenance Engine  │  │
                    │  ├─────────────────────┤  │
                    │  │  Summary Generator  │  │
                    │  └─────────────────────┘  │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │    Secure Database        │
                    │   (Encrypted at Rest)     │
                    └───────────────────────────┘
```

## Project Structure

```
nightingale-voiceai/
├── src/
│   ├── auth/                   # Authentication & authorization
│   ├── consent/               # Consent management
│   ├── redaction/             # PHI detection & redaction
│   ├── transcription/         # Voice processing
│   ├── provenance/            # Provenance tracking
│   ├── summarization/         # Summary generation
│   ├── database/              # Database operations
│   └── api/                   # API endpoints
├── tests/
│   ├── test_grounding.py      # Provenance validation tests
│   ├── test_redaction.py      # PHI redaction tests
│   ├── test_latency.py        # Performance profiling tests
│   └── test_summary.py        # Summary comparison tests
├── docs/
│   └── candidate_brief.md     # Detailed project brief
├── config/
│   ├── settings.py            # Configuration management
│   └── phi_patterns.json      # PHI detection patterns
├── requirements.txt           # Python dependencies
└── attribution.txt            # License attributions
```

## Testing

Four critical micro-tests ensure system reliability:

1. **test_grounding.py**: Validates every summary bullet point has proper provenance links
2. **test_redaction.py**: Tests synthetic PHI detection and redaction without leakage
3. **test_latency.py**: Profiles redaction and provenance pipeline performance (P50/P95)
4. **test_summary.py**: Compares clinician vs patient summaries from identical consultations

## Development

### Running Locally
```bash
# Start the development server
python src/main.py --dev

# Run with debugging
python src/main.py --debug --log-level DEBUG
```

### Configuration
Edit `config/settings.py` to modify:
- Database connections
- LLM model settings
- PHI redaction patterns
- Audio processing parameters

### Logging

- Default log file path: `app_logs/nightingale.log` (folder is at the same level as `src`)
- Directory is auto-created at startup if missing
- Rotation: size-based, max 10MB per file, keep 5 backups
- Console logs remain enabled for local debugging

Environment overrides:

- `NIGHTINGALE_LOG_DIR`: override the log directory (e.g., `/var/log/nightingale` or `~/my_logs`)
- `NIGHTINGALE_LOG_FILE`: override the full log file path (e.g., `/var/log/nightingale/server.log`)
- `NIGHTINGALE_LOG_LEVEL`: set log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`), default `INFO`

Examples (zsh):

```zsh
export NIGHTINGALE_LOG_DIR="$(pwd)/app_logs"
export NIGHTINGALE_LOG_LEVEL=DEBUG
./start_system.sh
```

## Security Considerations

- All patient data encrypted at rest using AES-256
- TLS 1.3 for data in transit
- Consent checks before every operation
- PHI redaction before LLM processing
- Audit trails for all operations
- RBAC with principle of least privilege

## License

[License details to be determined based on commercial use requirements]

## Contributing

See `docs/candidate_brief.md` for detailed architecture decisions and trade-offs.

## Support

This is a weekend build prototype. For production deployment, additional hardening and compliance review required.
