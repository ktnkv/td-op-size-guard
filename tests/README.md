# tests

Python that runs inside a live TouchDesigner, against the Size Guard tool at `/tools/sizeguard`. No pytest.

Run it from any Python call in TouchDesigner (the project folder must be this repository):

```python
exec(open(project.folder + '/tests/run_tests.py').read())
```

To run a subset, set `ONLY` to part of a test name first: `ONLY = 'override'`.

Each test gets a fresh scratch COMP, `/sizeguard_test_scratch`, and it is destroyed afterwards, pass or fail. The tool's parameters, its watcher list and the state of its extension are put back after every test. Nothing else is created, removed or resized: the tests call `FixTree` and `FixChildren` on the scratch only, never `FixProject`, which walks the whole project.

The tests do not move panes and do not switch perform mode. The OP Execute callbacks arrive at the end of a frame, after a test has returned, so the tests call the extension methods those callbacks lead to.

| File | Covers |
| --- | --- |
| `test_rule.py` | main size, family override, rounding, exempt operators, bottom-left corner, one network versus a tree |
| `test_watch.py` | watcher patterns, stop, reactions to a new operator and a resized tile |
| `test_page.py` | pages, parameter order, sections, gated sizes, About, wiring of the DATs, DAT text equals `src/` |
