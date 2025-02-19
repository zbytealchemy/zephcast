# Documentation Structure

docs/
├── index.md                       # Overview and introduction
├── getting-started/
│   ├── installation.md           # Installation guide
│   ├── quickstart.md            # Basic usage examples
│   └── concepts.md              # Core concepts and terminology
├── user-guide/
│   ├── core/                    # Core functionality
│   │   ├── consumers.md         # Base consumer functionality
│   │   ├── configuration.md     # Base configuration
│   │   └── types.md            # Common types and interfaces
│   ├── sync/                    # Synchronous features
│   │   ├── consumers.md         # Sync consumers and retry
│   │   ├── retry.md            # Sync retry functionality
│   │   └── integrations/        # Sync broker integrations
│   │       ├── kafka.md
│   │       ├── redis.md
│   │       └── rabbit.md
│   └── aio/                     # Async features
│       ├── consumers.md         # Async consumers and retry
│       ├── retry.md            # Async retry functionality
│       └── integrations/        # Async broker integrations
│           ├── kafka.md
│           ├── redis.md
│           └── rabbit.md
├── api-reference/
│   ├── core/
│   ├── sync/
│   └── aio/
├── examples/
│   ├── sync/
│   └── aio/
└── migration-guides/
    └── v1.0.0.md