from setuptools import setup

setup(
    name='jenkins-jobs-hidden-param',
    version='0.1.0',
    description='Jenkins Job Builder Hidden Param',
    url='https://github.com/ochirkov/jenkins-job-builder-hidden-param',
    author='Chyrkov Oleksandr',
    author_email='ironloriin20@gmail.com',
    license='MIT license',
    install_requires=[],
    entry_points={
        'jenkins_jobs.parameters': [
            'hidden = jjb_hidden_param.hidden_param:hidden_param']},
    packages=['jjb_hidden_param'],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3'])
