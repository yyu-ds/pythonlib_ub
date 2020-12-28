os.environ['PATH'] += os.pathsep + r'C:\Users\ub71894\AppData\Graphviz2.38'
os.environ['PATH'] += os.pathsep + r'C:\Users\ub71894\AppData\Graphviz2.38\bin'
from graphviz import Digraph
dot = Digraph(comment='The Round Table')
dot.node('A', 'King Arthur')
dot.node('B', 'Sir Bedevere the Wise')
dot.node('L', 'Sir Lancelot the Brave')
dot.edges(['AB', 'AL'])
dot.edge('B', 'L', constraint='false')


dot
