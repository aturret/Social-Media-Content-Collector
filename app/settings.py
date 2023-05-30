import os
import platform

system = platform.system()
env_var = os.environ
env_var['PWD'] = os.getcwd()
# env_var['PWD_PARENT'] = os.path.dirname(os.getcwd())
print(env_var)
