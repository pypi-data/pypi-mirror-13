from reviewboard.extensions.packaging import setup


PACKAGE = "rbautofillbug"
VERSION = "0.1.3"

setup(
    name=PACKAGE,
    version=VERSION,
    description="A ReviewBoard extension that extracts bug IDs from review "
                "request summaries",
    author="Jeremie Jost",
    author_email="jeremiejost@gmail.com",
    url="https://github.com/jjst/rbautofillbug",
    download_url='https://github.com/jjst/rbautofillbug/archive/v0.1.3.tar.gz',
    packages=["rbautofillbug"],
    keywords=['reviewboard', 'extension'],
    entry_points={
        'reviewboard.extensions':
            '%s = rbautofillbug.extension:AutoFillBugExtension' % PACKAGE,
    },
    package_data={
        'rbautofillbug': [
            'templates/rbautofillbug/*.txt',
            'templates/rbautofillbug/*.html',
        ],
    }
)
