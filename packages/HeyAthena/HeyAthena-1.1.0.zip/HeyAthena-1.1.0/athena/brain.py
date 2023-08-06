'''
Created on Jun 4, 2015

@author: Connor
'''
import inspect, pkgutil, traceback, os, yaml, re
import athena.modules.active as active_mods

from athena import settings, stt, tts, apis

inst = None
def init():
    global inst
    inst = Brain()

class Brain():
    def __init__(self):
        apis.find_apis()
        self.login()
        
        apis.verify_apis(self.user)
        apis.list_apis()
        
        self.find_mods()
        self.list_mods()
        
        self.greet()
        stt.init()
        
    def find_mods(self):
        """ Find and import modules from the module directory """
        self.modules = []
        print('~ Looking for modules in: '+str(active_mods.__path__).replace('\\\\', '\\')[1:-1])
        for finder, name, _ in pkgutil.iter_modules(active_mods.__path__):
            try:
                mod = finder.find_module(name).load_module(name)
                for member in dir(mod):
                    obj = getattr(mod, member)
                    if inspect.isclass(obj):
                        for parent in obj.__bases__:
                            if 'Module' is parent.__name__:
                                self.modules.append(obj())
            except Exception as e:
                print(traceback.format_exc())
                print('\n~ Error loading \''+name+'\' '+str(e))        
        self.modules.sort(key=lambda mod: mod.priority, reverse=True)

    def list_mods(self):
        """ List module order """
        print('\n~ Module Order: ', end='')
        print(str([mod.name for mod in self.modules])[1:-1]+'\n')
        
    def find_users(self):
        """ Returns a list of available user strings """
        self.users = []
        for file in os.listdir(settings.USERS_DIR):
            if file.endswith('.yml'):
                with open(os.path.join(settings.USERS_DIR, file)) as f:
                    user = yaml.load(f)
                    self.users.append(user['user_api']['username'])
        return self.users
        
    def verify_user_exists(self):
        """ Verify that at least 1 user exists """
        self.find_users()
        if not self.users:
            print('~ No users found. Please create a new user.\n')
            import athena.config as cfg
            cfg.generate()
            self.find_users()

    def load_user(self, username):
        with open(os.path.join(settings.USERS_DIR, username+'.yml'), 'r') as f:
            self.user = yaml.load(f)
            print('\n~ Logged in as: '+self.user['user_api']['username'])
            
    def login(self):
        self.verify_user_exists()
        if len(self.users) == 1:
            self.load_user(self.users[0])
            return
        
        print('~ Users: ', str(self.users)[1:-1])
        username = ''
        while username not in self.users:
            username = input('\n~ Username: ')
            if username not in self.users:
                print('\n~ Please enter a valid username')
                continue
        self.load_user(username)
        
    def greet(self):
        """ Greet the user """
        print(r"  _    _                      _   _                      ")
        print(r" | |  | |                /\  | | | |                     ")
        print(r" | |__| | ___ _   _     /  \ | |_| |__   ___ _ __   __ _ ")
        print(r" |  __  |/ _ \ | | |   / /\ \| __| '_ \ / _ \ '_ \ / _` |")
        print(r" | |  | |  __/ |_| |  / ____ \ |_| | | |  __/ | | | (_| |")
        print(r" |_|  |_|\___|\__, | /_/    \_\__|_| |_|\___|_| |_|\__,_|")
        print(r"               __/ |                                     ")
        print(r"              |___/                                      ")
        if self.user['user_api']['nickname']:
            print('\n~ Hey there, '+self.user['user_api']['nickname']+'!\n')
        else:
            print('\n~ Hello, what can I do for you today?\n')
            
    def execute_tasks(self, mod, text):
        """ Executes a module's task queue """
        for task in mod.task_queue:
            task.action(text)
            if task.greedy:
                break
    
    def execute_mods(self, text):
        """ Executes a module's task queue """
        if len(self.matched_mods) <= 0:
            tts.speak(settings.NO_MODULES)
            return
        
        self.matched_mods.sort(key=lambda mod: mod.priority, reverse=True)
        
        normal_mods = []
        greedy_mods = []
        greedy_flag = False
        priority = 0
        for mod in self.matched_mods:
            if greedy_flag and mod.priority < priority:
                break
            if mod.greedy:
                greedy_mods.append(mod)
                greedy_flag = True
                priority = mod.priority
            else:
                normal_mods.append(mod)
    
        if len(greedy_mods) is 1:
            normal_mods.append(greedy_mods[0])
        elif len(greedy_mods) > 1:
            if 0 < len(normal_mods):
                print('\n~ Matched mods (non-greedy): '+str([mod.name for mod in normal_mods])[1:-1]+'\n')
            m = self.mod_select(greedy_mods)
            if not m:
                return
            normal_mods.append(m)
        for mod in normal_mods:
            self.execute_tasks(mod, text)
            
    def mod_select(self, mods):
        """ Prompt user to specify which module to use to respond """
        print('\n~ Which module (greedy) would you like me to use to respond?')
        print('~ Choices: '+str([mod.name for mod in mods])[1:-1]+'\n')
        mod_select = input('> ')
        
        for mod in mods:
            if re.search('^.*\\b'+mod.name+'\\b.*$',  mod_select, re.IGNORECASE):
                return mod
        print('\n~ No module name found.\n')
    
    def match_mods(self, text):
        self.matched_mods = []
        for mod in self.modules:
            if not mod.enabled:
                continue
            """ Find matched tasks and add to module's task queue """
            mod.task_queue = []
            for task in mod.tasks:
                if task.match(text):
                    mod.task_queue.append(task)
                    if task.greedy:
                        break
                    
            """ Add modules with matched tasks to list """
            if len(mod.task_queue):
                self.matched_mods.append(mod)
    
    def error(self):
        """ Prompt user to specify which module to use to respond """
        tts.speak(settings.ERROR)
        text = input('> ')
        #response = stt.active_listen()
        
        return 'y' in text.lower()
    
    def run(self):
        while True:
            try:
                if settings.USE_STT:
                    stt.listen_keyword()
                    text = stt.active_listen()
                else:
                    text = input('> ')
                if not text:
                    print('\n~ No text input received.\n')
                    continue
        
                self.match_mods(text)
                self.execute_mods(text)
            except OSError as e:
                if 'Invalid input device' in str(e):
                    tts.speak(settings.NO_MIC)
                    settings.USE_STT = False
                    continue
                else:
                    raise Exception
            except EOFError:
                print('\n\n~ Shutting down...\n')
                break
            except:
                if self.error():
                    print(traceback.format_exc())
                else:
                    break
        print('~ Arrivederci.')