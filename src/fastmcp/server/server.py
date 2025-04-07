from typing import Any, Dict

import mcp.server.fastmcp
import mcp.types

from fastmcp.prompts.prompt_manager import PromptManager
from fastmcp.resources.resource_manager import ResourceManager
from fastmcp.server.context import Context
from fastmcp.tools.tool_manager import ToolManager
from fastmcp.utilities.logging import get_logger

logger = get_logger(__name__)


class FastMCP(mcp.server.fastmcp.FastMCP):
    def __init__(self, name: str | None = None, **settings: Any):
        # First initialize with default settings
        super().__init__(name=name or "FastMCP", **settings)

        # Replace the default managers with our extended ones
        self._tool_manager = ToolManager(
            warn_on_duplicate_tools=self.settings.warn_on_duplicate_tools
        )
        self._resource_manager = ResourceManager(
            warn_on_duplicate_resources=self.settings.warn_on_duplicate_resources
        )
        self._prompt_manager = PromptManager(
            warn_on_duplicate_prompts=self.settings.warn_on_duplicate_prompts
        )

        # Setup for mounted apps
        self._mounted_apps: Dict[str, "FastMCP"] = {}

    def get_context(self) -> Context:
        """
        Returns a Context object. Note that the context will only be valid
        during a request; outside a request, most methods will error.
        """
        try:
            request_context = self._mcp_server.request_context
        except LookupError:
            request_context = None
        return Context(request_context=request_context, fastmcp=self)

    def mount(self, prefix: str, app: "FastMCP") -> None:
        """Mount another FastMCP application with a given prefix.

        When an application is mounted:
        - The tools are imported with prefixed names
          Example: If app has a tool named "get_weather", it will be available as "weather/get_weather"
        - The resources are imported with prefixed URIs
          Example: If app has a resource with URI "weather://forecast", it will be available as "weather+weather://forecast"
        - The templates are imported with prefixed URI templates
          Example: If app has a template with URI "weather://location/{id}", it will be available as "weather+weather://location/{id}"
        - The prompts are imported with prefixed names
          Example: If app has a prompt named "weather_prompt", it will be available as "weather/weather_prompt"

        Args:
            prefix: The prefix to use for the mounted application
            app: The FastMCP application to mount
        """
        # Mount the app in the list of mounted apps
        self._mounted_apps[prefix] = app

        # Import tools from the mounted app
        self._tool_manager.import_tools(app._tool_manager, prefix)

        # Import resources from the mounted app
        self._resource_manager.import_resources(app._resource_manager, prefix)

        # Import resource templates
        self._resource_manager.import_templates(app._resource_manager, prefix)

        # Import prompts
        self._prompt_manager.import_prompts(app._prompt_manager, prefix)

        logger.info(f"Mounted app with prefix '{prefix}'")
        logger.debug(f"Imported tools with prefix '{prefix}/'")
        logger.debug(f"Imported resources with prefix '{prefix}+'")
        logger.debug(f"Imported templates with prefix '{prefix}+'")
        logger.debug(f"Imported prompts with prefix '{prefix}/'")
