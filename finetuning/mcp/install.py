#!/usr/bin/env python3
"""
Installation script for EU Funds Fine-tuning MCP Server

This script:
1. Checks prerequisites
2. Installs Python dependencies
3. Configures Claude Desktop automatically
4. Validates the installation
"""

import json
import os
import platform
import subprocess
import sys
from pathlib import Path


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def print_success(text):
    """Print success message"""
    print(f"✅ {text}")


def print_error(text):
    """Print error message"""
    print(f"❌ {text}")


def print_warning(text):
    """Print warning message"""
    print(f"⚠️  {text}")


def print_info(text):
    """Print info message"""
    print(f"ℹ️  {text}")


def check_python_version():
    """Check Python version is >= 3.10"""
    print_info("Checking Python version...")

    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print_error(f"Python 3.10 or higher required. You have {version.major}.{version.minor}")
        return False

    print_success(f"Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_api_key():
    """Check if ANTHROPIC_API_KEY is set"""
    print_info("Checking for Anthropic API key...")

    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print_warning("ANTHROPIC_API_KEY environment variable not set")
        print_info("You can:")
        print("  1. Set it now: export ANTHROPIC_API_KEY='your-key'")
        print("  2. Add it to the Claude Desktop config later")
        return None

    # Mask the key for display
    masked = api_key[:7] + "..." + api_key[-4:] if len(api_key) > 11 else "***"
    print_success(f"API key found: {masked}")
    return api_key


def install_dependencies():
    """Install Python dependencies"""
    print_info("Installing Python dependencies...")

    try:
        # Install in editable mode with all dependencies
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", "."],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            check=True
        )
        print_success("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        print(e.stderr)
        return False


def get_claude_config_path():
    """Get the Claude Desktop config file path for this platform"""
    system = platform.system()

    if system == "Darwin":  # macOS
        config_dir = Path.home() / "Library" / "Application Support" / "Claude"
    elif system == "Windows":
        config_dir = Path(os.environ.get("APPDATA", "")) / "Claude"
    elif system == "Linux":
        # Claude Desktop might not be officially supported on Linux
        # but some users run it
        config_dir = Path.home() / ".config" / "Claude"
    else:
        return None

    return config_dir / "claude_desktop_config.json"


def get_server_path():
    """Get absolute path to server.py"""
    return str(Path(__file__).parent.absolute() / "server.py")


def configure_claude_desktop(api_key=None):
    """Configure Claude Desktop to use the MCP server"""
    print_info("Configuring Claude Desktop...")

    config_path = get_claude_config_path()

    if not config_path:
        print_error("Unsupported platform for automatic configuration")
        print_info("Please configure manually. See README.md")
        return False

    # Create config directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Read existing config or create new one
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError:
            print_warning("Existing config file is invalid. Creating new one.")
            config = {}
    else:
        config = {}

    # Ensure mcpServers section exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}

    # Get server path
    server_path = get_server_path()

    # Configure the MCP server
    server_config = {
        "command": sys.executable,  # Use current Python interpreter
        "args": [server_path]
    }

    # Add API key if provided
    if api_key:
        server_config["env"] = {
            "ANTHROPIC_API_KEY": api_key
        }

    # Add or update our server
    config["mcpServers"]["eu-funds-finetuning"] = server_config

    # Write config back
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        print_success(f"Configuration written to: {config_path}")
        return True
    except Exception as e:
        print_error(f"Failed to write config: {e}")
        return False


def validate_installation():
    """Validate the installation"""
    print_info("Validating installation...")

    # Check server.py exists and is executable
    server_path = Path(__file__).parent / "server.py"
    if not server_path.exists():
        print_error(f"Server file not found: {server_path}")
        return False

    print_success("Server file found")

    # Check that we can import required modules
    try:
        import mcp
        print_success("MCP SDK installed")
    except ImportError:
        print_error("MCP SDK not installed")
        return False

    try:
        import anthropic
        print_success("Anthropic SDK installed")
    except ImportError:
        print_error("Anthropic SDK not installed")
        return False

    # Check config file
    config_path = get_claude_config_path()
    if config_path and config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)

            if "mcpServers" in config and "eu-funds-finetuning" in config["mcpServers"]:
                print_success("Claude Desktop configured")
            else:
                print_warning("MCP server not found in Claude Desktop config")
        except Exception as e:
            print_warning(f"Could not validate config: {e}")

    return True


def print_next_steps(api_key_set):
    """Print next steps for the user"""
    print_header("Installation Complete! 🎉")

    print("Next steps:\n")

    if not api_key_set:
        print("1. Set your Anthropic API key:")
        print("   export ANTHROPIC_API_KEY='your-key-here'")
        print("   OR add it to Claude Desktop config (see README.md)\n")
        step_num = 2
    else:
        step_num = 1

    print(f"{step_num}. Restart Claude Desktop")
    print("   - Quit Claude Desktop completely")
    print("   - Start it again\n")

    print(f"{step_num + 1}. Verify the MCP server is loaded:")
    print("   - Open Claude Desktop")
    print("   - Look for MCP tools in the interface")
    print("   - Try: 'What MCP tools do you have available?'\n")

    print(f"{step_num + 2}. Test it out:")
    print("   - 'Get sample questions for UCITS'")
    print("   - 'Analyze my document at /path/to/doc.pdf'")
    print("   - 'Generate training data from my UCITS directive'\n")

    print("📚 Documentation:")
    print("   - README.md - Full MCP documentation")
    print("   - ../EU_FUNDS_TRAINING_README.md - Training guide")
    print("   - ../QUICK_START.md - Quick reference\n")

    print("🆘 Troubleshooting:")
    print("   - Check logs: ~/Library/Logs/Claude/mcp*.log (macOS)")
    print("   - Verify config: cat ~/Library/Application\\ Support/Claude/claude_desktop_config.json")
    print("   - See README.md for more help\n")


def main():
    """Main installation flow"""
    print_header("EU Funds Fine-tuning MCP Server - Installation")

    print("This script will:")
    print("  1. Check prerequisites")
    print("  2. Install Python dependencies")
    print("  3. Configure Claude Desktop")
    print("  4. Validate the installation\n")

    input("Press Enter to continue or Ctrl+C to cancel...")

    # Check Python version
    print_header("Step 1: Prerequisites")
    if not check_python_version():
        sys.exit(1)

    # Check API key
    api_key = check_api_key()

    # Install dependencies
    print_header("Step 2: Install Dependencies")
    if not install_dependencies():
        print_error("Installation failed at dependency installation")
        sys.exit(1)

    # Configure Claude Desktop
    print_header("Step 3: Configure Claude Desktop")

    if not configure_claude_desktop(api_key):
        print_warning("Automatic configuration failed")
        print_info("You'll need to configure manually. See README.md")

    # Validate
    print_header("Step 4: Validate Installation")
    if not validate_installation():
        print_warning("Some validation checks failed")
        print_info("The MCP server may still work. Try restarting Claude Desktop.")

    # Next steps
    print_next_steps(api_key is not None)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
