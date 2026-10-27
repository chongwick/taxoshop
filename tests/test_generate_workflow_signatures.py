import argparse
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

import numpy as np

spec = importlib.util.spec_from_file_location("workflows", Path(__file__).resolve().parents[1] / "generate_workflow_signatures.py")
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.signatures = {i: {"issue": i, "summary": f"Failure workflow {i}", "workflow": ["Acquire shared resource", f"Invalidate resource {i}"]} for i in range(1, 5)}
        self.state = {"schema_version": 2, "clusters": {
            f"workflow-{i:04d}": {**self.signatures[i], "representative_issue": i, "issues": members}
            for i, members in [(1, [1, 2]), (3, [3]), (4, [4])]
        }, "review": {"model": "gpt-5.6-luna", "order": [3, 4, 1, 2], "decisions": [], "complete": False}}
        self.args = argparse.Namespace(model="gpt-5.6-luna", embedding_model="test", similarity_threshold=.72, restart_review=False)

    def decision(self, action, target, sources=None):
        return json.dumps({"action": action, "target_cluster_id": f"workflow-{target:04d}",
                           "merge_cluster_ids": [f"workflow-{i:04d}" for i in sources or []],
                           "decision_reason": "Equivalent causal failure sequence"})

    def test_move_repairs_representative_and_merge_preserves_partition(self):
        moved = w.apply_review(self.state, self.signatures, 1, self.decision("move", 3))
        self.assertEqual(moved["clusters"]["workflow-0001"]["representative_issue"], 2)
        self.assertEqual(moved["clusters"]["workflow-0001"]["workflow"], self.signatures[2]["workflow"])
        merged = w.apply_review(moved, self.signatures, 4, self.decision("merge", 3, [1, 4]))
        self.assertEqual(list(merged["clusters"]), ["workflow-0003"])
        self.assertEqual(merged["clusters"]["workflow-0003"]["issues"], [1, 2, 3, 4])
        self.assertEqual(self.state["clusters"]["workflow-0001"]["issues"], [1, 2])

    def test_invalid_review_never_mutates_state(self):
        before = copy.deepcopy(self.state)
        for text in [self.decision("move", 99), self.decision("keep", 3), self.decision("merge", 3, [4]), self.decision("merge", 3, [1, 1])]:
            with self.assertRaises(ValueError):
                w.apply_review(self.state, self.signatures, 1, text)
        self.assertEqual(before, self.state)

    def test_complete_linkage_does_not_chain_unrelated_endpoints(self):
        # Adjacent vectors have cosine .866; the endpoints only .5.
        angles = np.radians([0, 30, 60, 180])
        vectors = np.column_stack([np.cos(angles), np.sin(angles)])
        encoder = unittest.mock.Mock()
        encoder.encode.return_value = vectors
        factory = unittest.mock.Mock(return_value=encoder)
        with patch.dict(sys.modules, {"sentence_transformers": types.SimpleNamespace(SentenceTransformer=factory)}):
            state = w.cluster_signatures(self.signatures, "test", .8)
        factory.assert_called_once_with("test", device="cpu")
        for cluster in state["clusters"].values():
            self.assertFalse({1, 3} <= set(cluster["issues"]))
        self.assertEqual(sorted(i for c in state["clusters"].values() for i in c["issues"]), [1, 2, 3, 4])

    def test_resume_after_merge_reviews_every_member_and_repairs_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(w, "SIGNATURES", root), patch.object(w, "CLUSTERS_PATH", root / "clusters.json"):
                for number, signature in self.signatures.items():
                    w.write_json(root / f"gh_{number}.json", {**signature, "cluster_id": "old", "decision_reason": "old reason"})
                codex = unittest.mock.Mock()
                codex.thread_start.return_value.run.side_effect = [types.SimpleNamespace(final_response=self.decision("merge", 1, [3, 4])), RuntimeError("interrupted")]
                with self.assertRaisesRegex(RuntimeError, "interrupted"):
                    w.run_review(codex, "read-only", self.state, self.signatures, self.args.model)
                checkpoint = json.loads(w.CLUSTERS_PATH.read_text())
                self.assertEqual([e["issue"] for e in checkpoint["review"]["decisions"]], [3])
                codex.thread_start.return_value.run.side_effect = [types.SimpleNamespace(final_response=self.decision("keep", 1))] * 3
                final = w.run_review(codex, "read-only", checkpoint, self.signatures, self.args.model)
                self.assertTrue(final["review"]["complete"])
                self.assertEqual([e["issue"] for e in final["review"]["decisions"]], [3, 4, 1, 2])
                for number in self.signatures:
                    record = json.loads((root / f"gh_{number}.json").read_text())
                    self.assertEqual(record["cluster_id"], "workflow-0001")
                    self.assertNotIn("decision_reason", record)
                prompt = codex.thread_start.return_value.run.call_args.args[0]
                for signature in self.signatures.values():
                    self.assertIn(signature["summary"], prompt)

    def test_checkpoint_reused_only_for_matching_inputs(self):
        state = copy.deepcopy(self.state)
        state["input_fingerprint"] = w.input_fingerprint(self.signatures, self.args)
        with tempfile.TemporaryDirectory() as directory, patch.object(w, "CLUSTERS_PATH", Path(directory) / "clusters.json"):
            w.write_json(w.CLUSTERS_PATH, state)
            with patch.object(w, "cluster_signatures", return_value=copy.deepcopy(self.state)) as cluster:
                self.assertEqual(w.prepare_state(self.signatures, self.args), state)
                cluster.assert_not_called()
                self.signatures[1]["summary"] = "A changed causal mechanism"
                new = w.prepare_state(self.signatures, self.args)
                cluster.assert_called_once()
                self.assertNotEqual(new["input_fingerprint"], state["input_fingerprint"])
                self.assertEqual(new["review"]["decisions"], [])

    def test_invalid_merge_retried_without_marking_member_reviewed(self):
        codex = unittest.mock.Mock()
        codex.thread_start.return_value.run.side_effect = [
            types.SimpleNamespace(final_response=self.decision("merge", 1, [1, 3])),
            types.SimpleNamespace(final_response=self.decision("merge", 1, [3, 4])),
            *[types.SimpleNamespace(final_response=self.decision("keep", 1))] * 3,
        ]
        with patch.object(w, "write_json"), patch.object(w, "sync_memberships"):
            final = w.run_review(codex, "read-only", self.state, self.signatures, self.args.model)
        self.assertEqual(len(final["review"]["decisions"]), 4)
        self.assertTrue(final["review"]["complete"])
        self.assertIn("rejected", codex.thread_start.return_value.run.call_args_list[1].args[0])


if __name__ == "__main__":
    unittest.main()
