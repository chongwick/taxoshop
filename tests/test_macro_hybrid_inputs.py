import argparse
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('macro',Path(__file__).resolve().parents[1]/'generate_macro_taxonomy.py')
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class HybridInputs(unittest.TestCase):
    def test_hybrid_schema_and_changed_membership(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            clusters={'workflow-0001':{'issues':[1,2]},'workflow-0002':{'issues':[3]}}
            p=root/'clusters.json'
            p.write_text(json.dumps({'schema_version':2,'clusters':clusters}))
            (root/'workflow-0001.json').write_text(json.dumps({'issues':[99]}))
            (root/'workflow-0002.json').write_text(json.dumps({'issues':[3]}))
            args=argparse.Namespace(only=None,force=False,limit=None)
            with patch.object(m,'WORKFLOWS',p),patch.object(m,'OUTPUT',root):
                self.assertEqual(m.read_clusters(),clusters)
                self.assertEqual([k for k,_ in m.pending_clusters(args,clusters)],['workflow-0001'])

if __name__=='__main__':unittest.main()
