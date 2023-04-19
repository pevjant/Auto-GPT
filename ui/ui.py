import pynecone as pc
import keyring
import traceback
import orjson
from colorama import Fore, Style
from autogpt.agent.agent import Agent
from autogpt.app import execute_command, get_command
from autogpt.chat import chat_with_ai, create_chat_message
from autogpt.json_fixes.master_json_fix_method import fix_json_using_multiple_techniques
from autogpt.json_validation.validate_json import validate_json
from autogpt.logs import logger, print_assistant_thoughts
from autogpt.speech import say_text

from autogpt.config.ai_config import AIConfig
from autogpt.config import Config
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
    next_action_count = 0
    history: list[History] = []
    is_thinking = False
    is_started = False
    is_restoring_history = False
    is_exist_prev_histoy = False
    is_loading = False
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


    # def prepare(self):
    ai_name = config.ai_name
    ai_role = config.ai_role
    ai_goals = config.ai_goals
    prompt = config.construct_full_prompt()
    print(f'memory.data.texts: {len(memory.data.texts)}')
    if len(memory.data.texts) > 0:
        is_exist_prev_histoy = True
        
    def trans_replay_and_history(self, reply) -> dict:
        try:
            plans = []
            plans_split = "\n"
            msg_split = "\n* "
            if 'plans' in reply and reply['plans']:
                plans = ''.join([plan.replace('- ', '') if i == 0 else plan.replace('- ', plans_split) for i, plan in enumerate(reply['plans'])])

            
            msg = (
                f"{reply['thoughts']}"
                f"{msg_split}{reply['reasoning']}"
                f"{msg_split}{reply['criticism']}"
                f"{msg_split}{plans}"
                )
            
            trans_msg = trans(msg, "ko")
            trans_msg = trans_msg.split(msg_split)

            reply['thoughts'] = trans_msg[0]
            reply['reasoning'] = trans_msg[1]
            reply['criticism'] = trans_msg[2]
            reply['plans'] = trans_msg[3].split(plans_split)

        except Exception as e:
            logger.error(traceback.format_exc())
        finally:
            return reply
        
    def restore_history(self):
        for mem in memory.data.texts:
            try:
                data = orjson.loads(mem)
                assistant_reply = data["Assistant Reply"]
                result = data["Result"]
                user_input = data["Human Feedback"]
                if assistant_reply is not None:
                    assistant_reply_json = fix_json_using_multiple_techniques(assistant_reply)
                    if assistant_reply_json != {}:
                        validate_json(assistant_reply_json, "llm_response_format_1")
                        reply = print_assistant_thoughts(self.ai_name, assistant_reply_json)
                        reply2 = self.trans_replay_and_history(reply)
                        self.add_history(reply2, result)
                    
                        # Get command name and arguments
                        
                if result is not None:
                    self.full_message_history.append(create_chat_message("system", result))
            except Exception as e:
                logger.error("memData: ", mem)
                logger.error(traceback.format_exc())
            finally:
                self.is_restoring_history = False
                self.is_loading = False

    def add_history(self, replay, result):
        self.history = [History(
            thoughts=replay['thoughts'],
            reasoning=replay['reasoning'],
            plans=replay['plans'],
            criticism=replay['criticism'],
            system=result,
        )] + self.history
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
        self.user_input = user_input

    def set_openai_api_key(self, key):
        if key:
            self.openai_api_key = key
            cfg.set_openai_api_key(key)

    def think(self):
        memory.clear()
        memory.flush()
        self.history = []
        self.full_message_history = []
        self.result = None

        config = AIConfig(self.ai_name, self.ai_role, [x for x in self.ai_goals if x])
        config.save()

        self.prompt = config.construct_full_prompt()
        self.continue_think()

    def starting(self):
        self.is_started = True

    def processing(self):
        self.is_loading = True
        self.is_thinking = True

    def restoring(self):
        self.is_exist_prev_histoy = False
        self.is_loading = True
        self.is_restoring_history = True

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
                    reply2 = self.trans_replay_and_history(reply)
                    if not reply:
                        logger.error("ERROR: ", Fore.RED, "reply is empty")
                    else:
                        logger.typewriter_log("REPLY: ", Fore.CYAN, str(reply))
                    command_name, arguments = get_command(assistant_reply_json)
                    # command_name, arguments = assistant_reply_json_valid["command"]["name"], assistant_reply_json_valid["command"]["args"]
                    if cfg.speak_mode:
                        say_text(f"I want to execute {command_name}")
                except Exception as e:
                    logger.error(traceback.format_exc())

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
            
            if self.user_input:
                if self.user_input.lower().startswith("y -"):
                    self.next_action_count = abs(
                        int(self.user_input.split(" ")[1])
                    )
                    user_input = "GENERATE NEXT COMMAND JSON"
                elif len(user_input) > 1:
                    command_name = "human_feedback"
                    user_input = State.user_input
   
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
            #     f"\nHuman Feedback: {user_input} 
            # }
            json_str = orjson.dumps(memory_to_add)
            memory.add(json_str.decode())
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

            logger.typewriter_log("PROMPRT", 
                        Fore.YELLOW, 
                    f"ORIGIN = {Fore.CYAN}{memory}{Style.RESET_ALL}")
            if reply2:
                self.add_history(reply2, result)
                logger.typewriter_log("SYSTEM: ", Fore.YELLOW, "add history.")
            else:
                logger.typewriter_log("WARNING", Fore.YELLOW, "reply2 is empty.")
        except Exception as e:
            pc.window_alert(str(e))
            logger.error(traceback.format_exc())
            logger.error("JSON", orjson.dumps(json_str))
        finally:
            self.is_thinking = False
            self.is_loading = False
            self.command_name = None
            logger.typewriter_log("SYSTEM:", Fore.YELLOW, f"user_input: {self.user_input}, action count: {self.next_action_count}")
            self.user_input = ""
            if self.next_action_count > 0:
                self.next_action_count -= 1
                self.continue_think()



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
                        placeholder=State.user_input,
                        default_value='',
                        on_change=State.set_user_input
                    ),
                ),
        pc.center(
            pc.hstack(
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
                pc.cond(State.is_exist_prev_histoy,
                    pc.button(
                        '복원하기',
                        bg='black',
                        color='white',
                        width='6em',
                        padding='1em',
                        on_click=[State.restoring, State.starting, State.restore_history],
                    )
                ),
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
                State.is_loading,
                pc.vstack(
                    pc.cond(State.is_restoring_history,
                            pc.text("기록 복원중"),
                            pc.text()),
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
