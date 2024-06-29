
def traverse_graph_recursive(start_node, visited_nodes, path, visitor):
    # Prevent duplicate visits
    if not start_node in visited_nodes:
        visited_nodes.add(start_node)
        # The return decides whether we continue to traverse
        cont = visitor(start_node, path)
        if cont:
            for neighbor in start_node.get_neighbors():
                # Recurse.  The path is copied and extended before continuing
                # the traversal.
                new_path = path.copy()
                new_path.append(neighbor)
                traverse_graph_recursive(neighbor, visited_nodes, new_path, visitor)

def traverse_graph(start_node_list, visitor):
    # This set keeps track of what we have seen already
    visited_nodes = set()
    # Visit every node in the graph, but keep in mind that some
    # will be visited indirectly.
    for start_node in start_node_list:
        traverse_graph_recursive(start_node, visited_nodes, [ start_node ], visitor)