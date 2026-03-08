class Fusionchmingest < Formula
  desc "Convert Fusion360 API documentation to vector embeddings for AI coding agents"
  homepage "https://github.com/BoraSport/FusionCHMIngest"
  url "https://github.com/BoraSport/FusionCHMIngest/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "21ec54d5a9536e5d75218c49803bb754c0a07ed28917c2cab7fc471cbf781427"
  license "MIT"
  head "https://github.com/wschramm/FusionCHMIngest.git"

  depends_on "python@3.11"

  def install
    venv = Language::Python::Virtualenv.new(
      Formula["python@3.11"].opt_bin/"python3",
      venv_root: Pathname.new(prefix)/"libexec"
    )
    venv.pip_install_and_link "."
    bin.write_script_content <<~PYTHON
      #!/bin/bash
      "#{prefix}/libexec/bin/python3" -m fusionchmingest "$@"
    PYTHON
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
