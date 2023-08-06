from setuptools import setup

setup(name='pycaesar',
      version='0.2.2',
      description='Simple caesar cipher',
      long_description='Simple caesar cipher in python. IMPORTANT: IMPORTANT: This is not secure and should not be'
                       ' used for a purpose other than have fun. '
                       'Only alphabetic symbols are encrypted/decrypted. Non-alphabetic symbols like digits, '
                       'whitespaces, etc, are not transformed.',
      url='https://github.com/nicolastrres/pycaesar',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.4',
      ],
      author='Nicolas Agustin Torres',
      author_email='nicolastrres@gmail.com',
      license='MIT',
      packages=['pycaesar'],
      entry_points={
          'console_scripts': [
              'pycaesar=pycaesar.__main__:main',
          ],
      },
      zip_safe=False)
