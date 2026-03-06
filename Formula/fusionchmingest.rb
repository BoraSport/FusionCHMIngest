class Fusionchmingest < Formula
  desc "Convert Fusion360 API documentation to vector embeddings for AI coding agents"
  homepage "https://github.com/wschramm/FusionCHMIngest"
  url "https://github.com/wschramm/FusionCHMIngest/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "b8b182404cac3e2057eb992a043fa02d8da3898b0d1bf8438a1455a70ab0ecd0"
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

  test do
    assert_match "FusionCHMIngest", shell_output("#{bin}/fusionchmingest --version")
  end
end
