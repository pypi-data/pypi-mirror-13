elf_commander_python
====================

This Python package (elfcommander) creates a class named ElfCommander
to communcate with and control the Janelia Elf. The Elf uses two
hardware control devices, the mixed_signal_controller modular_device,
and the bioshake_device. The mixed_signal_controller both switches the
valves and reads the analog signals from the cylinder hall effect
sensors. The bioshake_device controls the heater/shaker.

Authors::

    Peter Polidoro <polidorop@janelia.hhmi.org>

License::

    BSD

Example Usage::

    from elfcommander import ElfCommander
    elf = ElfCommander('example_calibration.yaml','example_config.yaml')
    elf.run_protocol()

