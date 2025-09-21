# Nightingale VoiceAI

Professional medical voice AI system providing privacy-protected patient care experiences.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start the system
./start_system.sh
```

## Access Points

- **Patient Portal**: http://localhost:8501
- **Admin Dashboard**: http://localhost:8502  
- **API Documentation**: http://localhost:8888/docs

## Key Features

- 🛡️ **Privacy Protection**: Automatic PHI detection and data redaction
- 🎤 **Voice Processing**: High-precision transcription and intelligent analysis
- 📋 **Intelligent Summaries**: Differentiated summaries for patients and healthcare providers
- 🏥 **Professional Interface**: User experience compliant with medical standards

## Usage Flow

1. Access the patient portal (http://localhost:8501)
2. Complete digital consent form
3. Upload audio files
4. Review intelligent summary results

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
