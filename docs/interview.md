# Five-minute walkthrough

1. Open `docs/demo/index.html`. Start by pointing to the simulation notice.
2. Contrast a confident intent mismatch and an uncertain judgment. Explain the difference between a candidate worth investigating and an SEO ranking claim.
3. Open `request_body` and `decide`. The former asks the model two narrow questions; the latter owns the policy.
4. Run the tests. Show that the fake HTTP transport checks the official API contract but does not measure Jev's real accuracy.
5. Explain the next experiment: independently label real public snippets, pin the model, call the live API with a bounded request count, and report accuracy plus human-review coverage.

Do not claim the fixture probabilities are calibrated, that the demo uses live Google data, or that third-party cost/speed results were reproduced.
