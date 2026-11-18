import sys
sys.path.insert(0, __import__("os").path.dirname(__file__))
import pilot, group1, group1b
pilot.build(sys.argv[1])
