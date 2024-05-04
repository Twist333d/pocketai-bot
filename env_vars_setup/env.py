import os
from dotenv import load_dotenv
from ai_on_the_go.basic_setup import load_env_vars

# set an env variable
os.environ['SOME_VARIABLE_NAME'] = "VARIABLE_VALUE"
print(os.getenv('SOME_VARIABLE_NAME'))

# testing setup of the path
env = os.getenv('ENV', 'dev')
load_env_vars(env)




