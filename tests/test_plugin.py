"""Tests for the plugin system."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock, patch

import pytest

from lazy_kafka.config import Configuration
from lazy_kafka.plugin import Plugin, iter_plugins, load_builtin_plugins, register

if TYPE_CHECKING:
    from textual.widgets import Widget


class TestPlugin:
    """Tests for Plugin protocol."""

    def test_plugin_has_required_attributes(self) -> None:
        """Test that Plugin protocol has required attributes."""
        # Create a mock plugin
        mock_plugin = MagicMock(spec=Plugin)
        
        # Check that the protocol requires these attributes
        assert hasattr(mock_plugin, "tab_id")
        assert hasattr(mock_plugin, "tab_label")
        assert hasattr(mock_plugin, "build_panel")
        assert hasattr(mock_plugin, "build_cli")


class TestRegister:
    """Tests for register function."""

    def test_register_returns_plugin(self) -> None:
        """Test that register returns the plugin."""
        @register
        class TestPlugin:
            tab_id = "test"
            tab_label = "Test"
            
            def build_panel(self, config: Configuration) -> Widget | str:
                return "test"
            
            def build_cli(self) -> Any | None:
                return None
        
        plugin = TestPlugin()
        result = register(plugin)
        assert isinstance(result, TestPlugin)

    def test_register_adds_to_registry(self) -> None:
        """Test that register adds the plugin to the registry."""
        @register
        class TestPlugin:
            tab_id = "test-registry"
            tab_label = "Test Registry"
            
            def build_panel(self, config: Configuration) -> Widget | str:
                return "test"
            
            def build_cli(self) -> Any | None:
                return None
        
        # Create an instance to trigger registration
        plugin = TestPlugin()
        
        # Check that the plugin is in the registry
        plugins = list(iter_plugins())
        assert any(p.tab_id == "test-registry" for p in plugins)


class TestIterPlugins:
    """Tests for iter_plugins function."""

    def test_iter_plugins_returns_generator(self) -> None:
        """Test that iter_plugins returns a generator."""
        result = iter_plugins()
        assert hasattr(result, "__iter__")

    def test_iter_plugins_yields_plugins(self) -> None:
        """Test that iter_plugins yields Plugin instances."""
        load_builtin_plugins()
        plugins = list(iter_plugins())
        
        # Should have at least the builtin plugins
        assert len(plugins) > 0
        for plugin in plugins:
            assert hasattr(plugin, "tab_id")
            assert hasattr(plugin, "tab_label")
            assert hasattr(plugin, "build_panel")


class TestLoadBuiltinPlugins:
    """Tests for load_builtin_plugins function."""

    @patch("lazy_kafka.plugin.importlib.import_module")
    def test_load_builtin_plugins(self, mock_import: MagicMock) -> None:
        """Test that load_builtin_plugins imports all plugin modules."""
        # Setup mock modules
        mock_module1 = MagicMock()
        mock_module2 = MagicMock()
        
        def import_side_effect(name: str) -> MagicMock:
            if name == "lazy_kafka.plugins.core_kafka":
                return mock_module1
            elif name == "lazy_kafka.plugins.schema_registry":
                return mock_module2
            raise ImportError(f"No module named {name}")
        
        mock_import.side_effect = import_side_effect
        
        # Call the function
        load_builtin_plugins()
        
        # Check that import was called for plugin modules
        assert any("core_kafka" in str(call) for call in mock_import.call_args_list)
        assert any("schema_registry" in str(call) for call in mock_import.call_args_list)


class TestPluginImplementation:
    """Tests for plugin implementation details."""

    def test_plugin_tab_id_unique(self) -> None:
        """Test that all plugins have unique tab_ids."""
        load_builtin_plugins()
        plugins = list(iter_plugins())
        
        tab_ids = [p.tab_id for p in plugins]
        # Check for duplicates
        assert len(tab_ids) == len(set(tab_ids))

    def test_plugin_tab_label_not_empty(self) -> None:
        """Test that all plugins have non-empty tab_labels."""
        load_builtin_plugins()
        plugins = list(iter_plugins())
        
        for plugin in plugins:
            assert plugin.tab_label, f"Plugin {plugin.tab_id} has empty tab_label"

    def test_plugin_build_panel_returns_widget_or_str(self) -> None:
        """Test that build_panel returns Widget or str."""
        load_builtin_plugins()
        plugins = list(iter_plugins())
        config = Configuration()
        
        for plugin in plugins:
            result = plugin.build_panel(config)
            # Should be either a Widget or a string
            assert isinstance(result, (str, MagicMock)) or hasattr(result, "compose")

    def test_plugin_build_cli_may_return_none(self) -> None:
        """Test that build_cli may return None."""
        load_builtin_plugins()
        plugins = list(iter_plugins())
        
        for plugin in plugins:
            result = plugin.build_cli()
            # Should be either None or a CLI command
            assert result is None or hasattr(result, "callback")
