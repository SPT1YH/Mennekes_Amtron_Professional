# v0.2.1

Fixes a runtime error in `coordinator.py`:

- Python `struct` has no `to_bytes()` method.
- Register values are now converted with `int.to_bytes()`.

Also fixes bounded register slicing for firmware, protocol and model fields so those fields no longer accidentally consume the remainder of a read block.

This is a bug-fix release on top of v0.2.0. The Modbus transport architecture is unchanged.
