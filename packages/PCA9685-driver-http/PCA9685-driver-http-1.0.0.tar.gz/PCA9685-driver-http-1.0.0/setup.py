from setuptools import setup, find_packages

setup(
    name = "PCA9685-driver-http",
    description = "Web interface for PCA9685 pwm (LED/Servo) controller",
    version = "1.0.0",
    author = 'Lajos Santa',
    author_email = 'santa.lajos@coldline.hu',
    url = 'https://github.com/voidpp/PCA9685-driver-http.git',
    install_requires = [
        "Flask==0.10.1",
        "PCA9685-driver==1.0.0",
        "voidpp-tools==1.5.0",
        "querystring-parser==1.2.3",
        "six==1.10.0",
    ],
    include_package_data = True,
    packages = find_packages(),
)
