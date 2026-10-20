import unittest

from ues_community_signal.policy import (
    AccessNotApproved,
    AccessPolicy,
    require_approved_runtime,
)


class AccessPolicyTests(unittest.TestCase):
    def test_default_policy_is_shadow_only_and_bounded(self):
        policy = AccessPolicy()
        policy.validate()
        self.assertTrue(policy.shadow_only)
        self.assertEqual(policy.active_score_contribution, 0.0)
        self.assertLessEqual(policy.initial_future_contribution_cap, 0.05)
        self.assertGreaterEqual(policy.poll_interval_seconds, 6 * 60 * 60)

    def test_runtime_fails_closed_without_approval(self):
        with self.assertRaises(AccessNotApproved):
            require_approved_runtime({})

    def test_approved_runtime_requires_client_and_truthful_user_agent(self):
        with self.assertRaises(AccessNotApproved):
            require_approved_runtime({"REDDIT_API_ACCESS_APPROVED": "yes"})
        require_approved_runtime({
            "REDDIT_API_ACCESS_APPROVED": "yes",
            "REDDIT_CLIENT_ID": "synthetic-test-client",
            "REDDIT_USER_AGENT": "macos:ues-community-signal:v0.1 (by /u/test_account)",
        })

    def test_user_agent_must_use_reddit_documented_contact_format(self):
        with self.assertRaises(AccessNotApproved):
            require_approved_runtime({
                "REDDIT_API_ACCESS_APPROVED": "yes",
                "REDDIT_CLIENT_ID": "synthetic-test-client",
                "REDDIT_USER_AGENT": "macos:ues-community-signal:v0.1 (contact=test@example.invalid)",
            })

    def test_invalid_policy_cannot_raise_initial_cap(self):
        with self.assertRaises(ValueError):
            AccessPolicy(initial_future_contribution_cap=0.051).validate()


if __name__ == "__main__":
    unittest.main()
