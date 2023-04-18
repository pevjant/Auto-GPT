"""Welcome to Pynecone! This file outlines the steps to create a basic app."""
import pynecone as pc
import keyring
import google
"""Main script for the autogpt package."""
import logging
import json
from colorama import Fore, Style
from autogpt.agent.agent import Agent
from autogpt.app import execute_command, get_command
from autogpt.chat import chat_with_ai, create_chat_message
from autogpt.json_fixes.master_json_fix_method import fix_json_using_multiple_techniques
from autogpt.json_validation.validate_json import validate_json
from autogpt.logs import logger, print_assistant_thoughts
from autogpt.speech import say_text
from autogpt.args import parse_arguments
from autogpt.config.ai_config import AIConfig
from autogpt.config import Config
from autogpt.logs import logger
from autogpt.memory import get_memory
from autogpt.prompt import construct_prompt
# Load environment variables from .env file
from autogpt.spinner import Spinner
from autogpt.setup import prompt_user
from googletrans import Translator

translator = Translator()

def trans(msg, dest: str = None) -> str:
    if not dest:
        lang = translator.detect(msg).lang
        if lang == "en":
            dest = "ko"
        elif lang == "ko":
            dest = "en"
        else:
            dest = "en"
    return translator.translate(msg, dest=dest).text

question_style = {
    'bg': 'white',
    'padding': '2em',
    'border_radius': '25px',
    'w': '100%',
    'align_items': 'left',
}

cfg = Config()
cfg.set_openai_api_key(keyring.get_password('openai_api_key','pevjant'))

config = AIConfig.load()
if not config.ai_name:
    config = AIConfig("Auto-GPT", "", [""] * 5)
    config.save()
memory = get_memory(cfg)

class History(pc.Base):
    thoughts: str
    reasoning: str
    plans: list[str]
    criticism: str
    system: str

class State(pc.State):
    history: list[History] = []
    is_thinking = False
    is_started = False
    ai_name: str
    ai_role: str
    ai_goals: list[str]
    prompt: str
    openai_api_key = cfg.openai_api_key
    
    triggering_prompt = (
        "Determine which next command to use, and respond using the"
        " format specified above:"
    )
    
    # Initialize variables
    full_message_history:list = []
    result: str = None
    # Make a constant:
    user_input: str = None
    command_name: str = None

    def __init__(self):
        super().__init__()
        self.ai_name = config.ai_name
        self.ai_role = config.ai_role
        self.ai_goals = config.ai_goals
        self.prompt = config.construct_full_prompt()
        print(f'memory.data.texts: {len(memory.data.texts)}')
        if len(memory.data.texts) > 0:
            self.restore_history()

    def restore_history(self):
        for mem in memory.data.texts:
            data = json.loads(mem)
            assistant_reply = data["Assistant Reply"]
            result = data["Result"]
            user_input = data["Human Feedback"]
            if assistant_reply is not None:
                assistant_reply_json = fix_json_using_multiple_techniques(assistant_reply)
                if assistant_reply_json != {}:
                    validate_json(assistant_reply_json, "llm_response_format_1")
                    # Get command name and arguments
                    try:
                        reply = print_assistant_thoughts(self.ai_name, assistant_reply_json)
                        plans = []
                        if 'plans' in reply and reply['plans']:
                            plans = [plan.replace('- ', '') for plan in reply['plans']]
                        msg = (
                            f"{reply['thoughts']}"
                            f"\n{reply['reasoning']}"
                            f"\n{reply['criticism']}"
                            f"\n{result}"
                            f"\n{plans}"
                            )
                        trans_msg = trans(msg).split("\n")
                        self.history = [History(
                            thoughts=trans_msg[0],
                            reasoning=trans_msg[1],
                            plans=trans_msg[-len(plans):-1],
                            criticism=trans_msg[2],
                            system=trans_msg[3],
                        )] + self.history
                    except Exception as e:
                        logger.error(str(e))
            if result is not None:
                self.full_message_history.append(create_chat_message("system", result))


    def set_ai_goals_0(self, goal):
        self.ai_goals[0] = goal
    def set_ai_goals_1(self, goal):
        self.ai_goals[1] = goal
    def set_ai_goals_2(self, goal):
        self.ai_goals[2] = goal
    def set_ai_goals_3(self, goal):
        self.ai_goals[3] = goal
    def set_ai_goals_4(self, goal):
        self.ai_goals[4] = goal
    def set_ai_name(self, name):
        self.ai_name = name
    def set_ai_role(self, role):
        self.ai_role = role 
    def set_prompt(self, prompt):
        self.prompt = prompt
    def set_user_input(self, user_input: str):
        self.command_name = None
        if not user_input:
            user_input = "GENERATE NEXT COMMAND JSON"
        elif user_input.lower() == "n":
            user_input = "EXIT"
        elif len(user_input) > 1:
            self.command_name = "human_feedback"
        self.user_input = user_input

    def set_openai_api_key(self, key):
        if key:
            self.openai_api_key = key
            cfg.set_openai_api_key(key)

    def think(self):
        self.history = []
        self.full_message_history = []
        self.result = None

        config = AIConfig(self.ai_name, self.ai_role, self.ai_goals)
        config.save()

        self.prompt = config.construct_full_prompt()
        self.continue_think()

    def starting(self):
        self.is_started = True

    def processing(self):
        self.is_thinking = True

    def continue_think(self):
        try:
            with Spinner("Thinking... "):
                assistant_reply = chat_with_ai(
                    self.prompt,
                    self.triggering_prompt,
                    self.full_message_history,
                    memory,
                    cfg.fast_token_limit)


            assistant_reply_json = fix_json_using_multiple_techniques(assistant_reply)
            # Print Assistant thoughts
            if assistant_reply_json != {}:
                validate_json(assistant_reply_json, "llm_response_format_1")
                # Get command name and arguments
                try:
                    reply = print_assistant_thoughts(self.ai_name, assistant_reply_json)
                    if not reply:
                        logger.error("ERROR: ", Fore.RED, "reply is empty")
                    else:
                        logger.typewriter_log("REPLY: ", Fore.CYAN, str(reply))
                    command_name, arguments = get_command(assistant_reply_json)
                    # command_name, arguments = assistant_reply_json_valid["command"]["name"], assistant_reply_json_valid["command"]["args"]
                    if cfg.speak_mode:
                        say_text(f"I want to execute {command_name}")
                except Exception as e:
                    logger.error("Error: \n", str(e))

                ### GET USER AUTHORIZATION TO EXECUTE COMMAND ###
                # Get key press: Prompt the user to press enter to continue or escape
                # to exit
            logger.typewriter_log(
                "NEXT ACTION: ",
                Fore.CYAN,
                f"COMMAND = {Fore.CYAN}{command_name}{Style.RESET_ALL}  "
                f"ARGUMENTS = {Fore.CYAN}{arguments}{Style.RESET_ALL}",
            )
            user_input = "GENERATE NEXT COMMAND JSON"
            if not State.user_input:
                user_input = State.user_input
                command_name = "human_feedback"
            # Execute command
            if command_name is not None and command_name.lower().startswith("error"):
                result = (
                    f"Command {command_name} threw the following error: {arguments}"
                )
            elif command_name == "human_feedback":
                result = f"Human feedback: {user_input}"
            else:
                result = (
                    f"Command {command_name} returned: "
                    f"{execute_command(command_name, arguments)}"
                )
            memory_to_add = {
                "Assistant Reply" : assistant_reply,
                "Result": result,
                "Human Feedback": user_input,
            }
          
            # memory_to_add = {
            #     f"Assistant Reply: {assistant_reply} "
            #     f"\nResult: {result} "
            #     f"\nHuman Feedback: {user_input} "
            # }
            json_str = json.dumps(memory_to_add)
            memory.add(json_str)
            # Check if there's a result from the command append it to the message
            # history
            if result is not None:
                self.full_message_history.append(create_chat_message("system", result))
                logger.typewriter_log("SYSTEM: ", Fore.YELLOW, result)
            else:
                self.full_message_history.append(
                    create_chat_message("system", "Unable to execute command")
                )
                logger.typewriter_log(
                    "SYSTEM: ", Fore.YELLOW, "Unable to execute command"
                )

            plans = []
            if 'plans' in reply and reply['plans']:
                plans = [plan.replace('- ', '') for plan in reply['plans']]

            logger.typewriter_log("PROMPRT", 
                        Fore.YELLOW, 
                    f"ORIGIN = {Fore.CYAN}{memory}{Style.RESET_ALL}")

            msg = (
                f"{reply['thoughts']}"
                f"\n{reply['reasoning']}"
                f"\n{reply['criticism']}"
                f"\n{result}"
                f"\n{plans}"
                )
            trans_msg = trans(msg).split("\n")
            self.history = [History(
                thoughts=trans_msg[0],
                reasoning=trans_msg[1],
                plans=trans_msg[-len(plans):-1],
                criticism=trans_msg[2],
                system=trans_msg[3],
            )] + self.history
        except Exception as e:
            pc.window_alert(str(e))
            logger.error(str(e))
        finally:
            self.is_thinking = False
            # config = AIConfig(self.ai_name, self.ai_role, self.ai_goals)
            # config.save()


def header():
    return pc.vstack(
        pc.heading('스스로 생각하는 인공지능 Auto-GPT'),
        pc.divider(),
        pc.accordion(
            items=[
                ('기능',
                pc.list(items=[
                    '- 🌐 구글링을 통해 검색하고 정보를 수집하여 요약합니다',
                    '- 💾 장기 및 단기적으로 기억을 관리합니다',
                    '- 🧠 GPT-4의 뇌를 탑재하고 있습니다',
                    '- 🔗 인기있는 웹사이트 및 플랫폼에 접속하여 정보를 수집합니다',
                    '- 🗃️ GPT-3.5를 사용하여 자신의 생각을 요약하고 저장합니다',
                ])),
            ]
        ),
        # pc.divider(),
        pc.accordion(items=[('목표 설정',
            pc.stack(
                pc.hstack(
                    pc.text('AI 이름', width='150px'),
                    pc.input(
                        placeholder=State.ai_name,
                        default_value=State.ai_name,
                        on_change=State.set_ai_name
                    ),
                ),
                pc.hstack(
                    pc.text('최종 목표', width='150px', as_='b'),
                    pc.input(
                        placeholder=State.ai_role,
                        default_value=State.ai_role,
                        on_change=State.set_ai_role
                    ),
                ),
                pc.hstack(
                    pc.text('세부 목표 1', width='150px'),
                    pc.input(
                        placeholder=State.ai_goals[0],
                        default_value=State.ai_goals[0],
                        on_change=State.set_ai_goals_0
                    ),
                ),
                pc.hstack(
                    pc.text('세부 목표 2', width='150px'),
                    pc.input(
                        placeholder=State.ai_goals[1],
                        default_value=State.ai_goals[1],
                        on_change=State.set_ai_goals_1
                    ),
                ),
                pc.hstack(
                    pc.text('세부 목표 3', width='150px'),
                    pc.input(
                        placeholder=State.ai_goals[2],
                        default_value=State.ai_goals[2],
                        on_change=State.set_ai_goals_2
                    ),
                ),
                pc.hstack(
                    pc.text('세부 목표 4', width='150px'),
                    pc.input(
                        placeholder=State.ai_goals[3],
                        default_value=State.ai_goals[3],
                        on_change=State.set_ai_goals_3
                    ),
                ),
                pc.hstack(
                    pc.text('세부 목표 5', width='150px'),
                    pc.input(
                        placeholder=State.ai_goals[4],
                        default_value=State.ai_goals[4],
                        on_change=State.set_ai_goals_4
                    ),
                ),
                pc.hstack(
                    pc.text('OpenAI API Key', width='150px'),
                    pc.input(
                        placeholder='sk-...',
                        default_value=cfg.openai_api_key,
                        on_change=State.set_openai_api_key
                    ),
                ),
            )
        )]),
        pc.hstack(
                    pc.text('사용자 의견', width='150px'),
                    pc.input(
                        placeholder='',
                        default_value='',
                        on_change=State.set_user_input
                    ),
                ),
        pc.center(
            pc.cond(State.is_started,
                pc.text(),
                pc.button(
                    '생각하기',
                    bg='black',
                    color='white',
                    width='6em',
                    padding='1em',
                    on_click=[State.processing, State.starting, State.think],
                ),
            ),
            pc.cond(State.is_started,
                pc.cond(State.is_thinking,
                    pc.text(),
                    pc.hstack(
                        pc.button(
                            '계속 생각하기',
                            bg='black',
                            color='white',
                            width='6em',
                            padding='1em',
                            on_click=[State.processing, State.continue_think],
                        ),
                        pc.button(
                            '처음부터',
                            bg='red',
                            color='white',
                            width='6em',
                            padding='1em',
                            on_click=[State.processing, State.think],
                        ),
                    ),
                )
            ),
        ),
        style=question_style,
    )

def history_block(h: History):
    return pc.vstack(
        pc.heading(h.thoughts, size='md'),
        pc.list(
            pc.cond(h.reasoning,
                pc.list_item(
                    pc.icon(tag='info_outline', color='green'),
                    ' ' + h.reasoning,
                )
            ),
            pc.ordered_list(items=h.plans),
            pc.cond(h.criticism,
                pc.list_item(
                    pc.icon(tag='warning_two', color='red'),
                    ' ' + h.criticism
                )
            ),
            pc.accordion(
                items=[
                    ('시스템',
                    pc.code_block(h.system, wrap_long_lines=True)),
                ]
            ),
            spacing='.25em',
        ),
        style=question_style,
    )

def index():
    return pc.center(
        pc.vstack(
            header(),
            pc.cond(
                State.is_thinking,
                pc.vstack(
                    pc.circular_progress(
                        pc.circular_progress_label(
                            'Thinking', color='rgb(0, 0, 0)'
                        ),
                        is_indeterminate=True,
                        color='rgb(0, 0, 0)',
                    ),
                    style={
                        'bg': 'white',
                        'padding': '2em',
                        'border_radius': '25px',
                        'w': '100vh',
                        'align_items': 'center',
                    },
                ),
            ),
            pc.foreach(State.history, history_block),
            spacing='1em',
            width='100vh',
        ),
        padding_y='2em',
        height='100vh',
        align_items='top',
        bg='#ededed',
        overflow='auto',
    )


# Add state and page to the app.
app = pc.App(state=State)
app.add_page(index)
app.compile()
