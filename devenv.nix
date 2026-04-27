{ pkgs, lib, config, inputs, ... }:
{
  # https://devenv.sh/basics/
  env.AWS_DEFAULT_REGION = "us-east-1";
  env.AWS_ENDPOINT_URL="http://localhost.localstack.cloud:4566";
  env.AWS_ACCESS_KEY_ID="access-key-id";
  env.AWS_SECRET_ACCESS_KEY="secret-access-key";
  env.GAUSERAPI_CONFIG_TOML="config.toml.template";

  # confluent-kafka<=2.5.3 only ships wheels up to cp312. Pin uv to the
  # devenv-managed Python 3.12 so `uv sync` installs the prebuilt wheel
  # instead of compiling from sdist.
  env.UV_PYTHON = "${pkgs.python312}/bin/python3.12";

  # If someone *does* build confluent-kafka from source (e.g. on Python 3.13
  # or a newer confluent-kafka release), the native librdkafka headers and
  # pkg-config must be on the path for the C extension to compile.
  env.PKG_CONFIG_PATH = "${pkgs.rdkafka.dev}/lib/pkgconfig";

  # uv's default "clone" link mode (APFS reflink) copies macOS BSD flags
  # and xattrs from the cache. Files in uv's cache pick up
  # `com.apple.provenance` + `UF_HIDDEN` from Gatekeeper, and
  # CPython's site.py (>=3.12.5) silently skips `.pth` files with
  # `UF_HIDDEN` — which would disable the editable install of this
  # project. "copy" mode is a plain copy that doesn't carry those.
  env.UV_LINK_MODE = "copy";

  # https://devenv.sh/packages/
  packages = [
    pkgs.git
    pkgs.python312
    pkgs.uv
    pkgs.ruff
    pkgs.just
    pkgs.awscli2
    pkgs.pipx
    # Native deps needed to build confluent-kafka from sdist.
    pkgs.rdkafka
    pkgs.pkg-config
  ];

  enterShell = ''
    # Create/update the project venv against the pinned Python 3.12.
    # --frozen respects uv.lock; drop it when you want to resolve new deps.
    uv sync --frozen
    # Belt-and-braces: even with UV_LINK_MODE=copy, some `.pth` files
    # (notably `_virtualenv.pth`, seeded during venv creation) can still
    # carry `UF_HIDDEN` from uv's cache. Strip it or site.py skips them.
    if [ -d .venv ]; then
      find .venv -name '*.pth' -exec chflags nohidden {} + 2>/dev/null || true
      xattr -rc .venv 2>/dev/null || true
    fi
    echo ""
    echo "To run the TUI:  source .venv/bin/activate && lazy-kafka"
    echo "Avoid 'uv run'  — its implicit re-sync can re-set UF_HIDDEN on .pth files."
    echo "If the app is misbehaving, run 'uv run --reinstall lazy-kafka'"
  '';

}
