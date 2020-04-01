from setuptools import setup


setup(
    name="example_plugin",
    description="Example Open edX plugin",
    packages=["example_plugin"],
    entry_points={
        "lms.djangoapp": ["example_plugin = example_plugin.apps:ExampleConfig"]
    },
    version="0.0.1",
)
