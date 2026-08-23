## Summary

What does this PR change, and why.

## Type

- [ ] Bug fix
- [ ] Feature
- [ ] Docs / examples / Skill
- [ ] Tests only
- [ ] Refactor (no behavior change)

## How to test

Commands a reviewer can run:

```bash
python3 -m pytest tests
python3 scripts/generate_script.py examples/douyin_skincare.json --format md
```

## Checklist

- [ ] `python3 -m pytest tests` passes
- [ ] Runtime stays on the Python standard library, or the new dependency is justified in this PR
- [ ] Docs and `examples/` match the new behavior (flags, JSON fields, sample output)
- [ ] No API keys, tokens, or pirated music titles
- [ ] Related issue: #
