# Homebrew-Native Installation Plan

> **Note:** This formula has not been submitted to Homebrew core yet. These steps set up a local tap for testing.

## Goal
Enable users to install FusionCHMIngest via `brew install fusionchmingest` with no Python knowledge required.

## Approach: Traditional Homebrew Formula with venv

### How It Works

1. **Formula Dependencies**: Homebrew's Python 3.11+ is used
2. **Virtual Environment**: Formula creates an isolated venv during installation
3. **Dependency Installation**: pip installs all Python dependencies inside the venv
4. **CLI Wrapping**: Formula creates shell wrappers that call the venv's Python

### Benefits
- No pip/pipx/uv knowledge required for users
- Dependencies isolated from system Python
- Follows Homebrew conventions
- Works offline after initial install

---

## Implementation

### 1. Homebrew Formula

**File:** `Formula/fusionchmingest.rb`

```ruby
class Fusionchmingest < Formula
  desc "Convert Fusion360 API documentation to vector embeddings for AI coding agents"
  homepage "https://github.com/BoraSport/FusionCHMIngest"
  url "https://github.com/BoraSport/FusionCHMIngest/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "21ec54d5a9536e5d75218c49803bb754c0a07ed28917c2cab7fc471cbf781427"
  license "MIT"
  head "https://github.com/BoraSport/FusionCHMIngest.git"

  depends_on "python@3.11"
  depends_on "p7zip"

  def install
    python = Pathname.new("#{HOMEBREW_PREFIX}/bin/python3.11")
    
    # Create virtual environment using Python's built-in venv
    system python, "-m", "venv", prefix/"libexec"
    
    # Upgrade pip in the venv
    system prefix/"libexec/bin/pip", "install", "--upgrade", "pip"
    
    # Remove conflicting file that causes pip to fail
    rm_rf buildpath/"fusionchmingest"
    
    # Install the package in editable mode
    system prefix/"libexec/bin/pip", "install", "-e", "."
    
    # Create a wrapper script that uses the venv properly
    wrapper = buildpath/"fusionchmingest"
    wrapper.write <<~WRAPPER
      #!/bin/bash
      exec "#{prefix}/libexec/bin/python3.11" -m fusionchmingest "$@"
    WRAPPER
    wrapper.chmod(0755)
    bin.install wrapper
  end

  def caveats
    <<~EOS
      User data is NOT removed on uninstall:
      - Vector store: ~/.fusionchmingest/
      
      To remove manually:
        rm -rf ~/.fusionchmingest
      
      Or use 'brew zap' to remove user data automatically.
    EOS
  end

  def zap
    rm_rf "~/.fusionchmingest"
  end

  test do
    assert_match "FusionCHMIngest", shell_output("#{bin}/fusionchmingest --version")
  end
end
```

### 2. CI Workflow

**File:** `.github/workflows/test.yml`

Uses venv approach similar to formula for consistency.

---

## Installation Steps (Local Tap)

### Prerequisites
- Homebrew installed on macOS
- Git tag `v1.0.0` pushed to GitHub

### Step 1: Create Local Tap

```bash
mkdir -p /opt/homebrew/Library/Taps/fusionchmingest
cp Formula/fusionchmingest.rb /opt/homebrew/Library/Taps/fusionchmingest/
```

### Step 2: Dry Run (verify formula)

```bash
brew install --dry-run /opt/homebrew/Library/Taps/fusionchmingest/fusionchmingest.rb
```

### Step 3: Install

```bash
brew install /opt/homebrew/Library/Taps/fusionchmingest/fusionchmingest.rb
```

> ⚠️ This will take 5-15 minutes due to torch, sentence-transformers, and chromadb downloads

### Step 4: Verify CLI works

```bash
fusionchmingest --version
```

### Step 5: Test installation

```bash
brew test fusionchmingest
```

---

### Tap Location

After installation, the tap is at:
```
/opt/homebrew/Library/Taps/fusionchmingest/fusionchmingest.rb
```

Install command (after tap is created):
```bash
brew install fusionchmingest
```

Test command:
```bash
brew test fusionchmingest
```

---

### Uninstall

```bash
brew uninstall fusionchmingest
rm -rf /opt/homebrew/Library/Taps/fusionchmingest
```

## Dependencies in venv

| Package | Purpose |
|---------|---------|
| beautifulsoup4 | HTML parsing |
| html2text | HTML to Markdown |
| aiofiles | Async file I/O |
| chromadb | Vector database |
| sentence-transformers | Embedding model |
| torch | ML framework |
| click | CLI framework |
| tiktoken | Token counting |
| chardet | Encoding detection |
| mcp | MCP server |
| pytest | Testing |

---

## Testing Strategy

1. **Formula Test Block**: Verifies CLI works after install
2. **CI Workflow**: Runs all tests on macOS
3. **Coverage**: Upload to GitHub Actions artifacts
