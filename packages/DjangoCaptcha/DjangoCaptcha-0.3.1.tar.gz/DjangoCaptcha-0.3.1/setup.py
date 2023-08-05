#encoding:utf-8
from distutils.core import setup  
setup(name='DjangoCaptcha',  
      author='TY(pythoner.org)',  
      author_email='tianyu0915@gmail.com',  
      version='0.3.1',  
      description='在django中生成英文单词、数字验证码',
      keywords ='django captcha 验证码',
      url='http://github.com/tianyu0915/DjangoCaptcha',  
      packages=['DjangoCaptcha'],  
      install_requires=['pillow'],
      package_data={'DjangoCaptcha':['*.*','DjangoCaptcha/*.*']},

)  
