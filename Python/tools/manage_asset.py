"""
Defines the manage_asset tool for interacting with Unity assets.
"""

import asyncio  # Added: Import asyncio for running sync code in async
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP, Context

# from ..unity_connection import get_unity_connection  # Original line that caused error
from unity_connection import (
    get_unity_connection,
)  # Use absolute import relative to Python dir


def register_manage_asset_tools(mcp: FastMCP):
    """Registers the manage_asset tool with the MCP server."""

    @mcp.tool()
    async def manage_asset(
        ctx: Context,
        action: str,
        path: str,
        asset_type: str | None = None,
        properties: Dict[str, Any] | None = None,
        destination: str | None = None,
        generate_preview: bool | None = False,
        search_pattern: str | None = None,
        filter_type: str | None = None,
        filter_date_after: str | None = None,
        page_size: int | None = None,
        page_number: int | None = None,
    ) -> Dict[str, Any]:
        """Performs asset operations (import, create, modify, delete, etc.) in Unity.

        Args:
            ctx: The MCP context (not directly used in the Unity command).
            action (str): The operation to perform ('import', 'create', 'modify', 'delete', 'duplicate', 'move', 'rename', 'search', 'get_info', 'create_folder', 'get_components').  This determines the action taken on the asset or assets.
            path (str): The path to the asset (e.g., "Assets/Materials/MyMaterial.mat"). For 'create' and 'create_folder', this is the path where the new asset/folder will be created. For 'search', this specifies the folder to search within (if any).  For other actions, it specifies the target asset.
            asset_type (str | None): The type of asset to create (e.g., "Material", "ScriptableObject", "Folder").  Required only for the 'create' action.
            properties (Dict[str, Any] | None): A dictionary of properties to apply to the asset during 'create' or 'modify'. The specific keys and values depend on the asset type. For materials, properties like "shader," "color," "texture," etc. can be set. For ScriptableObjects, properties map to public fields/properties.
            destination (str | None): The destination path for 'duplicate' or 'move/rename' actions. If omitted for 'duplicate', a unique path will be generated.
            generate_preview (bool | None):  If True, generates a preview image (base64 encoded PNG) for the asset when getting asset info ('get_info' and 'search').
            search_pattern (str | None): The search pattern for the 'search' action (e.g., "*.prefab" to find all prefabs).
            filter_type (str | None): Filters search results by asset type (e.g., "t:Material" to find only materials). Used with the 'search' action.
            filter_date_after (str | None): Filters search results to include only assets modified after the specified date and time (ISO 8601 format, e.g., "2024-10-26T12:00:00Z"). Used with the 'search' action.
            page_size (int | None): The number of results per page for the 'search' action. If omitted, a default page size is used (usually 50).
            page_number (int | None):  The page number to retrieve for the 'search' action (1-based indexing). If omitted, the first page is returned.

        Returns:
            Dict[str, Any]: A dictionary containing the results from Unity.  The dictionary will typically have a "success" key (boolean) indicating whether the operation was successful.  If successful, there might be a "data" key with the results (e.g., the created asset's data, the list of found assets).  If unsuccessful, there will be an "error" key with the error message.
        """
        # Ensure properties is a dict if None
        if properties is None:
            properties = {}

        # Prepare parameters for the C# handler
        params_dict = {
            "action": action.lower(),
            "path": path,
            "assetType": asset_type,
            "properties": properties,
            "destination": destination,
            "generatePreview": generate_preview,
            "searchPattern": search_pattern,
            "filterType": filter_type,
            "filterDateAfter": filter_date_after,
            "pageSize": page_size,
            "pageNumber": page_number,
        }

        # Remove None values to avoid sending unnecessary nulls
        params_dict = {k: v for k, v in params_dict.items() if v is not None}

        # Get the current asyncio event loop
        loop = asyncio.get_running_loop()
        # Get the Unity connection instance
        connection = get_unity_connection()

        # Run the synchronous send_command in the default executor (thread pool)
        # This prevents blocking the main async event loop.
        result = await loop.run_in_executor(
            None,  # Use default executor
            connection.send_command,  # The function to call
            "manage_asset",  # First argument for send_command
            params_dict,  # Second argument for send_command
        )
        # Return the result obtained from Unity
        return result
