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
