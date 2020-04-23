"""
This file controls input and output to console
"""


welcome_message = r"""
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
"""

round_ascii = r"""
 _____                       _ 
|  __ \                     | |
| |__) |___  _   _ _ __   __| |
|  _  // _ \| | | | '_ \ / _` |
| | \ \ (_) | |_| | | | | (_| |
|_|  \_\___/ \__,_|_| |_|\__,_|
"""

number_ascii = [r"""
    ___  
   / _ \ 
  | | | |
  | | | |
  | |_| |
   \___/ 
""",
r"""
   __ 
  /_ |
   | |
   | |
   | |
   |_|
""",
r"""
   ___  
  |__ \ 
     ) |
    / / 
   / /_ 
  |____|
 """]
       

yes = ['y','Y','yes','Yes']
no = ['n','N','no','No']
alphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

def write_welcome():
    """
    Write welcome message to console.
    """
    write_dashes()
    print(welcome_message)
    write_dashes()


def write_round(round):
    """
    Write round number to console.
    :param round: int, current round
    """
    message='\n'.join(' '.join(pair) for pair in zip(*(s.split('\n') for s in (round_ascii,number_ascii[round]))))
    print(message)
    write_dashes()


def write_message(message):
    """
    Write message to console.
    :param message: str, message
    """
    print(message)


def write_list(message,values):
    """
    Write list of values to console.
    :param message: introductory message
    :param values: list
    """
    print(message)
    for v in values:
        print(f'    * {v}')


def write_options_numeric(options):
    """
    Write list of numbers followed by options.
    :param options: list, of options
    """
    message = ''
    for i,op in enumerate(options):
        message += f'{i+1}) {op}\n'
    write_message(message)


def write_options_letter(options):
    """
    Write list of letters followed by options.
    :param options: list, of options
    """
    message = ''
    for i,op in enumerate(options):
        message += f'{alphabet[i]}) {op}\n'
    write_message(message)


def write_dashes(size=70):
    """
    Write dashed line of given size to console.
    :param size: int
    """
    print('-'*size)


def yes_no_question(question):
    """
    Get yes/no response to quesiton from console.
    :param question: str, question
    :return: bool, True for yes False for no
    """
    while True:
        response = input(question+" ")
        if response in yes or response in no:
            break
    return response in yes


def integer_question(question,lower_bound=1,upper_bound=100):
    """
    Get integer response to question.
    :param question: 
    """
    while True:
        try:
            response = int(input(question+" "))
            if response>=lower_bound and response<=upper_bound:
                break
        except:
            pass
    return response


def option_question(question,options):
    """
    Get option response to question from console.
    :param question: str, question
    :param options: list, list of answers to question
    :return: int, corresponding to option
    """

    print(question+'\n')
    write_options_numeric(options)
    return integer_question(question)-1


