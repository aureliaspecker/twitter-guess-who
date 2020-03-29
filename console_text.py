"""
This file controls input and output to console
"""


welcome_message = r"""
-----------------------------------------------------------------
__          __  _                            _        
\ \        / / | |                          | |       
 \ \  /\  / /__| | ___ ___  _ __ ___   ___  | |_ ___  
  \ \/  \/ / _ \ |/ __/ _ \| '_ ` _ \ / _ \ | __/ _ \ 
   \  /\  /  __/ | (_| (_) | | | | | |  __/ | || (_) |
    \/  \/ \___|_|\___\___/|_| |_| |_|\___|  \__\___/ 
                                                      
                                                      
 _______       _ _   _               _____                     
|__   __|     (_) | | |             / ____|                    
   | |_      ___| |_| |_ ___ _ __  | |  __ _   _  ___  ___ ___ 
   | \ \ /\ / / | __| __/ _ \ '__| | | |_ | | | |/ _ \/ __/ __|
   | |\ V  V /| | |_| ||  __/ |    | |__| | |_| |  __/\__ \__ \
   |_| \_/\_/ |_|\__|\__\___|_|     \_____|\__,_|\___||___/___/
                                                               
                                                               
__          ___           _ 
\ \        / / |         | |
 \ \  /\  / /| |__   ___ | |
  \ \/  \/ / | '_ \ / _ \| |
   \  /\  /  | | | | (_) |_|
    \/  \/   |_| |_|\___/(_)
    
----------------------------------------------------------------
"""

yes = ['y','Y','yes','Yes']
no = ['n','N','no','No']


def write_welcome():
    """
    Write welcome message to console.
    """
    print(welcome_message)


def write_message(message):
    """
    Write message to console.
    :param message: str, message
    """
    print(message)


def write_list(message,values):
    """
    Write list of values to console.
    :param message: introductary message
    :param values: list
    """
    print(message)
    for v in values:
        print(f'    * {v}')

def yes_no_question(question):
    """
    Get yes/no response to quesiton from console.
    :param question: str, question
    :return: bool, True for yes False for no
    """
    response = input(question+" ")
    return response in yes


def option_question(question,options):
    """
    Get option response to question from console.
    :param question: str, question
    :param options: list, list of answers to question
    :return: int, corresponding to option
    """

    print(question+'\n')
    for i,op in enumerate(options):
        print('{}) {}\n'.format(i+1,op))
    while True:
        try:
            response = int(input())
        except:
            pass
        if response>=1 and response<=len(options):
            break
    return response-1


