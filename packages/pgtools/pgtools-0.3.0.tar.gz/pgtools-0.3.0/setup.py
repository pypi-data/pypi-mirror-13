import setuptools

VER = '0.3.0'

print('*'*80)
print('* {:<76} *'.format('pgtools version {} by phageghost'.format(VER)))
print('*'*80)
print()

setuptools.setup(name='pgtools',
				version=VER,
				description='A collection of useful Python code',
				url='http://github.com/phageghost/pg_tools',
				author='phageghost',
				author_email='pgtools@phageghost.net',
				license='MIT',
				packages=['pgtools'],
				zip_safe=False)
