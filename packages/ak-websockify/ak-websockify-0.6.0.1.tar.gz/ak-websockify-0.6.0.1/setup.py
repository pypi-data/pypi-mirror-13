from setuptools import setup

long_description = open("README.md").read() + "\n" + \
    open("CHANGES.txt").read() + "\n"

setup(
    name='ak-websockify',
    version='0.6.0.1',
    description="Appknox forn of Websockify.",
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python",
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    data_files=[
        ('share/websockify/include', [
            'include/util.js',
            'include/base64.js',
            'include/websock.js']),
        ('share/websockify/include/web-socket-js', [
            'include/web-socket-js/WebSocketMain.swf',
            'include/web-socket-js/swfobject.js',
            'include/web-socket-js/web_socket.js'])],
    keywords='noVNC websockify',
    license='LGPLv3',
    url="https://github.com/kanaka/websockify",
    author="Joel Martin",
    author_email="github@martintribe.org",

    packages=['websockify'],
    include_package_data=True,
    install_requires=['numpy'],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'websockify = websockify.websocketproxy:websockify_init',
        ]
    },
)
