from mcp.server.fastmcp import FastMCP, Context
from typing import Dict, Any, List
from unity_connection import get_unity_connection


def register_manage_gameobject_tools(mcp: FastMCP):
    """Register all GameObject management tools with the MCP server."""

    @mcp.tool()
    def manage_gameobject(
        ctx: Context,
        action: str,
        target: str | None = None,  # GameObject identifier by name or path
        search_method: str | None = None,
        # --- Combined Parameters for Create/Modify ---
        name: str
        | None = None,  # Used for both 'create' (new object name) and 'modify' (rename)
        tag: str
        | None = None,  # Used for both 'create' (initial tag) and 'modify' (change tag)
        parent: str
        | None = None,  # Used for both 'create' (initial parent) and 'modify' (change parent)
        position: List[float] | None = None,
        rotation: List[float] | None = None,
        scale: List[float] | None = None,
        components_to_add: List[str] | None = None,  # List of component names to add
        primitive_type: str | None = None,
        save_as_prefab: bool | None = False,
        prefab_path: str | None = None,
        prefab_folder: str = "Assets/Prefabs",
        # --- Parameters for 'modify' ---
        set_active: bool | None = None,
        layer: str | None = None,  # Layer name
        components_to_remove: List[str] | None = None,
        component_properties: Dict[str, Dict[str, Any]] | None = None,
        # --- Parameters for 'find' ---
        search_term: str | None = None,
        find_all: bool = False,
        search_in_children: bool = False,
        search_inactive: bool = False,
        # -- Component Management Arguments --
        component_name: str | None = None,
    ) -> Dict[str, Any]:
        """Manages GameObjects in the Unity scene: create, modify, delete, find, and component operations.

        Args:
            action (str): The operation to perform ('create', 'modify', 'delete', 'find', 'get_components', 'add_component', 'remove_component', 'set_component_property').
            target (str | int | None):  The GameObject to operate on.  Can be:
                                        - A name (string).
                                        - A path (string).
                                        - An instance ID (integer).
                                        Used for 'modify', 'delete', 'get_components', 'add_component', 'remove_component', 'set_component_property'.
            search_method (str | None): How to search for the 'target' GameObject ('by_name', 'by_path', 'by_id', 'by_tag', 'by_layer', 'by_component').
                                         If the 'target' is provided as an instance ID (int), the search method is typically 'by_id'. If not specified, the search method is determined automatically based on the 'target' type.
            name (str | None): The name of the GameObject (for 'create' and 'modify' - rename). Required for 'create' unless instantiating a prefab.
            tag (str | None): The tag to apply to the GameObject (for 'create' and 'modify').
            parent (str | None): The parent GameObject (name, path or ID) to set (for 'create' and 'modify').
            position (List[float] | None):  The local position of the GameObject as a list [x, y, z].
            rotation (List[float] | None): The local rotation (Euler angles) of the GameObject as a list [x, y, z].
            scale (List[float] | None): The local scale of the GameObject as a list [x, y, z].
            components_to_add (List[str | Dict] | None):  A list of components to add. Can be a simple list of component type names (strings) OR
                                                          a list of dictionaries, where each dictionary has a "typeName" key and an optional "properties" dictionary for initial property values:
                                                          [{"typeName": "Rigidbody", "properties": {"mass": 5.0}}].
            primitive_type (str | None): The type of primitive to create (e.g., "Cube", "Sphere", "Plane") when 'action' is 'create'.
            save_as_prefab (bool | None): If True and 'action' is 'create', the new GameObject will be saved as a prefab.  Requires 'prefab_path' or 'name' (to construct a path) to be set.
            prefab_path (str | None): The path to save the prefab (must end in '.prefab'). Used with 'create' and 'save_as_prefab'. If omitted, a default path is constructed using 'prefab_folder' and the GameObject's 'name'.
            prefab_folder (str): The default folder for saving prefabs if 'prefab_path' is not provided (defaults to "Assets/Prefabs").
            set_active (bool | None): Sets the GameObject's active state in the hierarchy (for 'modify').
            layer (str | None): The name of the layer to assign the GameObject to (for 'create' and 'modify').
            components_to_remove (List[str] | None): A list of component names (strings) to remove from the GameObject.
            component_properties (Dict[str, Dict[str, Any]] | None): A dictionary to set component properties.  The keys are component type names, and the values are dictionaries of property names and their values.
                                                                      Example: `{"Rigidbody": {"mass": 10.0, "useGravity": True}, "MeshRenderer": {"sharedMaterial.color": [1, 0, 0, 1]}}`.
                                                                      You can use dot notation for nested properties (e.g., "sharedMaterial.color") and array indexers (e.g., "materials[0].color") to access materials.
                                                                      To assign a Material asset, provide the asset path (string).  To assign a GameObject or component, use the "find" syntax:
                                                                      {"MyScript": {"targetObject": {"find": "OtherObject", "method": "by_name"}}} (finds a GameObject) or
                                                                      {"MyScript": {"healthComponent": {"find": "Player", "method": "by_id", "component": "Health"}}} (finds a component of type "Health").

            search_term (str | None): The term to search for when 'action' is 'find'.  The meaning of the search term depends on the 'search_method' (name, tag, etc.).
            find_all (bool): If True, return all matching GameObjects when using 'find'.  If False (default), return only the first match.
            search_in_children (bool): If True, the search will be limited to the children of the 'target' GameObject (when 'action' is 'find').
            search_inactive (bool): If True, include inactive GameObjects in searches (for 'find' and when resolving the 'target' object).
            component_name (str | None): The name of the component to add, remove, or set properties on. Used with 'add_component', 'remove_component', and 'set_component_property' actions.

        Returns:
            Dict[str, Any]: A dictionary containing the results of the operation:
                            - `success` (bool): True if the operation was successful, False otherwise.
                            - `message` (str): A message describing the result (success message or error message).
                            - `data` (Any):  Data returned by the operation (e.g., the created GameObject's data, a list of found GameObjects, etc.).  May be None.

        Raises:
            Exception: If there is a communication error with Unity or an unexpected error during processing.
        """
        try:
            # --- Early check for attempting to modify a prefab asset ---
            # ----------------------------------------------------------

            # Prepare parameters, removing None values
            params = {
                "action": action,
                "target": target,
                "searchMethod": search_method,
                "name": name,
                "tag": tag,
                "parent": parent,
                "position": position,
                "rotation": rotation,
                "scale": scale,
                "componentsToAdd": components_to_add,
                "primitiveType": primitive_type,
                "saveAsPrefab": save_as_prefab,
                "prefabPath": prefab_path,
                "prefabFolder": prefab_folder,
                "setActive": set_active,
                "layer": layer,
                "componentsToRemove": components_to_remove,
                "componentProperties": component_properties,
                "searchTerm": search_term,
                "findAll": find_all,
                "searchInChildren": search_in_children,
                "searchInactive": search_inactive,
                "componentName": component_name,
            }
            params = {k: v for k, v in params.items() if v is not None}

            # --- Handle Prefab Path Logic ---
            if action == "create" and params.get(
                "saveAsPrefab"
            ):  # Check if 'saveAsPrefab' is explicitly True in params
                if "prefabPath" not in params:
                    if "name" not in params or not params["name"]:
                        return {
                            "success": False,
                            "message": "Cannot create default prefab path: 'name' parameter is missing.",
                        }
                    # Use the provided prefab_folder (which has a default) and the name to construct the path
                    constructed_path = f"{prefab_folder}/{params['name']}.prefab"
                    # Ensure clean path separators (Unity prefers '/')
                    params["prefabPath"] = constructed_path.replace("\\", "/")
                elif not params["prefabPath"].lower().endswith(".prefab"):
                    return {
                        "success": False,
                        "message": f"Invalid prefab_path: '{params['prefabPath']}' must end with .prefab",
                    }
            # Ensure prefab_folder itself isn't sent if prefabPath was constructed or provided
            # The C# side only needs the final prefabPath
            params.pop("prefab_folder", None)
            # --------------------------------

            # Send the command to Unity via the established connection
            # Use the get_unity_connection function to retrieve the active connection instance
            # Changed "MANAGE_GAMEOBJECT" to "manage_gameobject" to potentially match Unity expectation
            response = get_unity_connection().send_command("manage_gameobject", params)

            # Check if the response indicates success
            # If the response is not successful, raise an exception with the error message
            if response.get("success"):
                return {
                    "success": True,
                    "message": response.get(
                        "message", "GameObject operation successful."
                    ),
                    "data": response.get("data"),
                }
            else:
                return {
                    "success": False,
                    "message": response.get(
                        "error",
                        "An unknown error occurred during GameObject management.",
                    ),
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Python error managing GameObject: {str(e)}",
            }
