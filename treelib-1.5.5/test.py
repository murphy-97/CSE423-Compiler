import treelib
from treelib.plugins import export_to_dot

t = treelib.Tree()
t.create_node([1,2,3])
export_to_dot(t)