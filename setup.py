from setuptools import setup, find_packages

# Normal setup stuff
setup(
    name='vcd',
    packages=find_packages(),
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'vcd = vcd.vcd:vcd_run',
            'vcd-config = vcd.vcd:vcd_config']},
    )
