import os

class Tree:
    """
    Node represents a node in a directory tree structure.

    Attributes:
        - is_dir (bool): Indicates whether the node represents a directory (True) or a file (False).
        - name (str): The name of the node.
        - files (list): A list of file names contained within the directory (if the node represents a directory).
        - parent (Node): The parent node in the directory tree. Defaults to None for the root node.

    Methods:
        __init__(self, is_dir: bool, name: str, files_name: list = [], parent=None) -> None:
            Constructor for the Node class. Initializes the node with the specified attributes.

        add_adyecency(self, node):
            Placeholder method for adding an adjacent node. This can be extended based on specific requirements.

    Usage:
        ExampleNode = Node(is_dir=True, name="example_directory", files_name=["file1.txt", "file2.txt"])
    """

    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)
        self.__children = []

    def add_children(self, node):
        self.__children.append(node)

    def get_children(self):
        return self.__children

    def print_directory(self, node=None, indent=''):
        if node == None:
            node = self
        tree_string = f"{indent}+ {node.name}/\n"

        for child in node.get_children():
            if child.get_children():
                tree_string += self.print_directory(child, indent + '  ')
            else:
                tree_string += f"{indent}- {child.name}\n"

        return tree_string

class AdjNode:
    """
    AdjNode represents a node of dependecies in the project as connections in a graph.

    Attributes:
        - __connections (list): A list of node names connected to the current node.
        - __raw_connections (list): A list of raw connections associated with the node.
        - id (str): The unique identifier for the node.

    Methods:
        __init__(self, id: str, raw_connections: list) -> None:
            Constructor for the AdjNode class. Initializes the node with the specified ID and raw connections.

        add(self, name):
            Adds a connection to the list of node connections.

        get_raw_connections(self):
            Retrieves the raw connections associated with the node.

        __str__(self) -> str:
            Returns a string representation of the node (its ID).

    Usage:
        example_node = AdjNode(id="node1", raw_connections=["node2", "node3"])
        example_node.add("node4")
        raw_connections = example_node.get_raw_connections()
        node_string = str(example_node)
    """

    def __init__(self, id: str, raw_connections: list) -> None:
        self.__connections = []
        self.__raw_connections = raw_connections
        self.id = id

    def add(self, name):
        self.__connections.append(name)

    def get_raw_connections(self):
        return self.__raw_connections

    def __str__(self) -> str:
        return self.id

    def __repr__(self) -> str:
        return str(self.__raw_connections)


class Graph:
    """
    Graph represents the graph structure using an adjacency list and the node list.

    Attributes:
        - __adj_list (list): A Dict representing theadjacency list.
        - __nodes (list): A list all the nodes.

    Methods:
        __init__(self) -> None:
            Constructor for the Graph class.

        __create_connection(self, name):
            Populate the adjacency list

        __add_edge(self):
            Create a new edge for the graph.

        add_node(self) -> str:
            Append a new node to the node list

        __search(self) -> AdjNode:
            Private method to search for a node by its ID.

        construct(self):
            Build the files dependencies graph.

    """

    def __init__(self):
        self.__adj_list = {}
        self.__nodes = {}

    def __create_connection(self, s_id: str, d_id: str):
        if self.__adj_list.get(s_id, -1) == -1:
            self.__adj_list[s_id] = [d_id]
        else:
            self.__adj_list[s_id].append(d_id)

    def __add_edge(self, s_id: str, d_id: str, bilateral: bool):
        self.__create_connection(s_id, d_id)
        if bilateral:
            self.__create_connection(d_id, s_id)

    def add_node(self, id: str, node: AdjNode):
        self.__nodes[id] = node

    def __search(self, id):
        """
        Private method to search for a node by its ID.

        Args:
            id: The ID of the node to search for.

        Returns:
            Node: The node if found, or -1 if the node with the given ID is not found.
        """
        return self.__nodes.get(id, -1)

    def construct(self):
        """
        Build the files dependencies graph.

        Returns:
            None
        """
        for node_id in self.__nodes.keys():
            node = self.__nodes[node_id]
            raw_connections = node.get_raw_connections()
            if len(raw_connections) > 0:
                for conn in raw_connections:
                    conn_node = self.__search(conn)
                    if conn_node != -1:
                        self.__add_edge(node.id, conn_node.id, False)

    def get_graph(self):
        return self.__adj_list

    def get_node_dependencies(self, node_id: str):
        return self.__adj_list[node_id]

    def get_nodes(self):
        return [i for i in list(self.__nodes.keys()) if self.__adj_list.get(i, -1) != -1]
