from setuptools import setup, find_packages

setup(
    name='pyhsics',  # Nombre de la librería
    version='0.1.0',  # Versión inicial
    packages=find_packages(),  # Buscar todos los paquetes
    install_requires=[  # Dependencias externas, si las hay
        # 'numpy',  # Ejemplo de dependencia
    ],
    test_suite='tests',  # Especificar dónde están los tests
)
