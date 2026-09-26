import unittest
from meta_synthesizer.models import HotPatchDescriptor, PatchStatus
from meta_synthesizer.shadow_sandbox import ShadowSandbox
from meta_synthesizer.live_patcher import LivePatcher


class TestMetaSynthesizer(unittest.TestCase):
    def setUp(self):
        self.sandbox = ShadowSandbox()
        self.patcher = LivePatcher()

    def test_shadow_sandbox_security_rejection(self):
        # Forbidden call in AST
        bad_code = """
def malicious():
    import os
    os.system("rm -rf /")
"""
        desc = HotPatchDescriptor(
            target_symbol="malicious",
            synthesized_source_code=bad_code
        )
        audit, symbol = self.sandbox.verify_patch(desc)
        self.assertFalse(audit.ast_invariants_passed)
        self.assertIn("forbidden call", audit.error_message)
        self.assertIsNone(symbol)

    def test_live_patching_and_rollback(self):
        namespace = {"multiply": lambda a, b: a * b}

        # Verify initial
        self.assertEqual(namespace["multiply"](3, 4), 12)

        # Apply patch
        new_code = """
def multiply(a, b):
    return (a * b) + 100
"""
        desc = HotPatchDescriptor(
            target_symbol="multiply",
            synthesized_source_code=new_code
        )

        applied = self.patcher.apply_patch(desc, namespace, test_inputs={"a": 2, "b": 2})
        self.assertTrue(applied)
        self.assertEqual(desc.status, PatchStatus.HOT_SWAPPED)
        self.assertEqual(namespace["multiply"](3, 4), 112)

        # Trigger rollback
        rolled_back = self.patcher.trigger_rollback(desc.patch_id, namespace)
        self.assertTrue(rolled_back)
        self.assertEqual(desc.status, PatchStatus.ROLLED_BACK)
        self.assertEqual(namespace["multiply"](3, 4), 12)


if __name__ == "__main__":
    unittest.main()
