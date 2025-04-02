from mcp.server.fastmcp import FastMCP, Context
from typing import Dict, Any
from unity_connection import get_unity_connection


def register_manage_editor_tools(mcp: FastMCP):
    """Register all editor management tools with the MCP server."""

    @mcp.tool()
    def manage_editor(
        ctx: Context,
        action: str,
        wait_for_completion: bool | None = None,
        # --- Parameters for specific actions ---
        tool_name: str | None = None,
        tag_name: str | None = None,
        layer_name: str | None = None,
    ) -> Dict[str, Any]:
        """Controls and queries the Unity editor's state and settings, including play mode, active tool, selection, tags, and layers.

        Args:
            ctx (Context): The MCP context (not directly used in the Unity command).
            action (str): The operation to perform.  Supported actions:
                - Play Mode Control: 'play', 'pause', 'stop'
                - Editor State/Info: 'get_state', 'get_windows', 'get_active_tool', 'get_selection'
                - Active Tool: 'set_active_tool'
                - Tag Management: 'add_tag', 'remove_tag', 'get_tags'
                - Layer Management: 'add_layer', 'remove_layer', 'get_layers'
            wait_for_completion (bool | None):  Currently only used for specific actions.  If True, the Python function will wait for the action to complete in Unity before returning. (Optional, defaults to False).
            tool_name (str | None): The name of the tool to set as active (e.g., "Move," "Rotate," "Scale").  Used with the 'set_active_tool' action.  Case-insensitive.  You cannot directly activate custom tools with this.
            tag_name (str | None): The name of the tag to add or remove. Used with 'add_tag' and 'remove_tag' actions.
            layer_name (str | None): The name of the layer to add or remove. Used with 'add_layer' and 'remove_layer' actions.


        Returns:
            Dict[str, Any]: A dictionary containing the results of the operation:
                            - success (bool): True if the operation was successful, False otherwise.
                            - message (str): A message describing the result or error.
                            - data (Any): Data returned by the Unity editor (if applicable). The content of this field varies based on the 'action' performed.

        Raises:
            Exception:  If there's an error communicating with the Unity editor or an unexpected error occurs.
        """
        try:
            # Prepare parameters, removing None values
            params = {
                "action": action,
                "waitForCompletion": wait_for_completion,
                "toolName": tool_name,  # Corrected parameter name to match C#
                "tagName": tag_name,  # Pass tag name
                "layerName": layer_name,  # Pass layer name
                # Add other parameters based on the action being performed
                # "width": width,
                # "height": height,
                # etc.
            }
            params = {k: v for k, v in params.items() if v is not None}

            # Send command to Unity
            response = get_unity_connection().send_command("manage_editor", params)

            # Process response
            if response.get("success"):
                return {
                    "success": True,
                    "message": response.get("message", "Editor operation successful."),
                    "data": response.get("data"),
                }
            else:
                return {
                    "success": False,
                    "message": response.get(
                        "error", "An unknown error occurred during editor management."
                    ),
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Python error managing editor: {str(e)}",
            }
