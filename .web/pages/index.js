import {Fragment, useEffect, useRef, useState} from "react"
import {useRouter} from "next/router"
import {E, connect, updateState, uploadFiles} from "/utils/state"
import "focus-visible/dist/focus-visible"
import {Accordion, AccordionButton, AccordionIcon, AccordionItem, AccordionPanel, Button, Center, CircularProgress, CircularProgressLabel, Divider, HStack, Heading, Input, List, ListItem, OrderedList, Stack, Text, VStack, useColorMode} from "@chakra-ui/react"
import {InfoOutlineIcon, WarningTwoIcon} from "@chakra-ui/icons"
import {Prism} from "react-syntax-highlighter"
import NextHead from "next/head"

const PING = "http://localhost:8000/ping"
const EVENT = "ws://localhost:8000/event"
const UPLOAD = "http://localhost:8000/upload"
export default function Component() {
const [state, setState] = useState({"ai_goals": ["summary and save to file"], "ai_name": "Auto-GPT", "ai_role": "Learn more about Mark Minervini's investment method and implement it in Python   code.", "command_name": null, "full_message_history": [], "history": [], "is_exist_prev_histoy": false, "is_loading": false, "is_restoring_history": false, "is_started": false, "is_thinking": false, "next_action_count": 0, "openai_api_key": "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", "prompt": "You are Auto-GPT, Learn more about Mark Minervini's investment method and implement it in Python   code.\nYour decisions must always be made independently without seeking user assistance. Play to your strengths as an LLM and pursue simple strategies with no legal complications.\n\nGOALS:\n\n1. summary and save to file\n\n\nConstraints:\n1. ~4000 word limit for short term memory. Your short term memory is short, so immediately save important information to files.\n2. If you are unsure how you previously did something or want to recall past events, thinking about similar events will help you remember.\n3. No user assistance\n4. Exclusively use the commands listed in double quotes e.g. \"command name\"\n5. Use subprocesses for commands that will not terminate within a few minutes\n\nCommands:\n1. Google Search: \"google\", args: \"input\": \"<search>\"\n2. Browse Website: \"browse_website\", args: \"url\": \"<url>\", \"question\": \"<what_you_want_to_find_on_website>\"\n3. Start GPT Agent: \"start_agent\", args: \"name\": \"<name>\", \"task\": \"<short_task_desc>\", \"prompt\": \"<prompt>\"\n4. Message GPT Agent: \"message_agent\", args: \"key\": \"<key>\", \"message\": \"<message>\"\n5. List GPT Agents: \"list_agents\", args: \n6. Delete GPT Agent: \"delete_agent\", args: \"key\": \"<key>\"\n7. Clone Repository: \"clone_repository\", args: \"repository_url\": \"<url>\", \"clone_path\": \"<directory>\"\n8. Write to file: \"write_to_file\", args: \"file\": \"<file>\", \"text\": \"<text>\"\n9. Read file: \"read_file\", args: \"file\": \"<file>\"\n10. Append to file: \"append_to_file\", args: \"file\": \"<file>\", \"text\": \"<text>\"\n11. Delete file: \"delete_file\", args: \"file\": \"<file>\"\n12. Search Files: \"search_files\", args: \"directory\": \"<directory>\"\n13. Evaluate Code: \"evaluate_code\", args: \"code\": \"<full_code_string>\"\n14. Get Improved Code: \"improve_code\", args: \"suggestions\": \"<list_of_suggestions>\", \"code\": \"<full_code_string>\"\n15. Write Tests: \"write_tests\", args: \"code\": \"<full_code_string>\", \"focus\": \"<list_of_focus_areas>\"\n16. Execute Python File: \"execute_python_file\", args: \"file\": \"<file>\"\n17. Task Complete (Shutdown): \"task_complete\", args: \"reason\": \"<reason>\"\n18. Generate Image: \"generate_image\", args: \"prompt\": \"<prompt>\"\n19. Send Tweet: \"send_tweet\", args: \"text\": \"<text>\"\n20. Do Nothing: \"do_nothing\", args: \n21. Task Complete (Shutdown): \"task_complete\", args: \"reason\": \"<reason>\"\n\nResources:\n1. Internet access for searches and information gathering.\n2. Long Term memory management.\n3. GPT-3.5 powered Agents for delegation of simple tasks.\n4. File output.\n\nPerformance Evaluation:\n1. Continuously review and analyze your actions to ensure you are performing to the best of your abilities.\n2. Constructively self-criticize your big-picture behavior constantly.\n3. Reflect on past decisions and strategies to refine your approach.\n4. Every command has a cost, so be smart and efficient. Aim to complete tasks in the least number of steps.\n\nYou should only respond in JSON format as described below \nResponse Format: \n{\n    \"thoughts\": {\n        \"text\": \"thought\",\n        \"reasoning\": \"reasoning\",\n        \"plan\": \"- short bulleted\\n- list that conveys\\n- long-term plan\",\n        \"criticism\": \"constructive self-criticism\",\n        \"speak\": \"thoughts summary to say to user\"\n    },\n    \"command\": {\n        \"name\": \"command name\",\n        \"args\": {\n            \"arg name\": \"value\"\n        }\n    }\n} \nEnsure the response can be parsed by Python json.loads", "result": null, "triggering_prompt": "Determine which next command to use, and respond using the format specified above:", "user_input": null, "events": [{"name": "state.hydrate"}], "files": []})
const [result, setResult] = useState({"state": null, "events": [], "processing": false})
const router = useRouter()
const socket = useRef(null)
const { isReady } = router;
const { colorMode, toggleColorMode } = useColorMode()
const Event = events => setState({
  ...state,
  events: [...state.events, ...events],
})
const File = files => setState({
  ...state,
  files,
})
useEffect(() => {
  if(!isReady) {
    return;
  }
  if (!socket.current) {
    connect(socket, state, setState, result, setResult, router, EVENT, ['websocket', 'polling'])
  }
  const update = async () => {
    if (result.state != null) {
      setState({
        ...result.state,
        events: [...state.events, ...result.events],
      })
      setResult({
        state: null,
        events: [],
        processing: false,
      })
    }
    await updateState(state, setState, result, setResult, router, socket.current)
  }
  update()
})
return (
<Center sx={{"paddingY": "2em", "height": "100vh", "alignItems": "top", "bg": "#ededed", "overflow": "auto"}}><VStack spacing="1em"
sx={{"width": "100vh"}}><VStack sx={{"bg": "white", "padding": "2em", "borderRadius": "25px", "w": "100%", "alignItems": "left"}}><Heading>{`스스로 생각하는 인공지능 Auto-GPT`}</Heading>
<Divider/>
<Accordion allowToggle={true}><AccordionItem><AccordionButton>{`기능`}
<AccordionIcon/></AccordionButton>
<AccordionPanel><List><ListItem>{`- 🌐 구글링을 통해 검색하고 정보를 수집하여 요약합니다`}</ListItem>
<ListItem>{`- 💾 장기 및 단기적으로 기억을 관리합니다`}</ListItem>
<ListItem>{`- 🧠 GPT-4의 뇌를 탑재하고 있습니다`}</ListItem>
<ListItem>{`- 🔗 인기있는 웹사이트 및 플랫폼에 접속하여 정보를 수집합니다`}</ListItem>
<ListItem>{`- 🗃️ GPT-3.5를 사용하여 자신의 생각을 요약하고 저장합니다`}</ListItem></List></AccordionPanel></AccordionItem></Accordion>
<Accordion allowToggle={true}><AccordionItem><AccordionButton>{`목표 설정`}
<AccordionIcon/></AccordionButton>
<AccordionPanel><Stack><HStack><Text sx={{"width": "150px"}}>{`AI 이름`}</Text>
<Input defaultValue={state.ai_name}
onChange={(_e) => Event([E("state.set_ai_name", {name:_e.target.value})])}
placeholder={state.ai_name}
type="text"/></HStack>
<HStack><Text as="b"
sx={{"width": "150px"}}>{`최종 목표`}</Text>
<Input defaultValue={state.ai_role}
onChange={(_e) => Event([E("state.set_ai_role", {role:_e.target.value})])}
placeholder={state.ai_role}
type="text"/></HStack>
<HStack><Text sx={{"width": "150px"}}>{`세부 목표 1`}</Text>
<Input defaultValue={state.ai_goals.at(0)}
onChange={(_e) => Event([E("state.set_ai_goals_0", {goal:_e.target.value})])}
placeholder={state.ai_goals.at(0)}
type="text"/></HStack>
<HStack><Text sx={{"width": "150px"}}>{`세부 목표 2`}</Text>
<Input defaultValue={state.ai_goals.at(1)}
onChange={(_e) => Event([E("state.set_ai_goals_1", {goal:_e.target.value})])}
placeholder={state.ai_goals.at(1)}
type="text"/></HStack>
<HStack><Text sx={{"width": "150px"}}>{`세부 목표 3`}</Text>
<Input defaultValue={state.ai_goals.at(2)}
onChange={(_e) => Event([E("state.set_ai_goals_2", {goal:_e.target.value})])}
placeholder={state.ai_goals.at(2)}
type="text"/></HStack>
<HStack><Text sx={{"width": "150px"}}>{`세부 목표 4`}</Text>
<Input defaultValue={state.ai_goals.at(3)}
onChange={(_e) => Event([E("state.set_ai_goals_3", {goal:_e.target.value})])}
placeholder={state.ai_goals.at(3)}
type="text"/></HStack>
<HStack><Text sx={{"width": "150px"}}>{`세부 목표 5`}</Text>
<Input defaultValue={state.ai_goals.at(4)}
onChange={(_e) => Event([E("state.set_ai_goals_4", {goal:_e.target.value})])}
placeholder={state.ai_goals.at(4)}
type="text"/></HStack>
<HStack><Text sx={{"width": "150px"}}>{`OpenAI API Key`}</Text>
<Input defaultValue="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"
onChange={(_e) => Event([E("state.set_openai_api_key", {key:_e.target.value})])}
placeholder="sk-..."
type="text"/></HStack></Stack></AccordionPanel></AccordionItem></Accordion>
<HStack><Text sx={{"width": "150px"}}>{`사용자 의견`}</Text>
<Input defaultValue=""
onChange={(_e) => Event([E("state.set_user_input", {user_input:_e.target.value})])}
placeholder={state.user_input}
type="text"/></HStack>
<Center><HStack><Fragment>{state.is_started ? <Fragment><Text/></Fragment> : <Fragment><Button onClick={() => Event([E("state.processing", {}),E("state.starting", {}),E("state.think", {})])}
sx={{"bg": "black", "color": "white", "width": "6em", "padding": "1em"}}>{`생각하기`}</Button></Fragment>}</Fragment>
<Fragment>{state.is_started ? <Fragment>{state.is_thinking ? <Fragment><Text/></Fragment> : <Fragment><HStack><Button onClick={() => Event([E("state.processing", {}),E("state.continue_think", {})])}
sx={{"bg": "black", "color": "white", "width": "6em", "padding": "1em"}}>{`계속 생각하기`}</Button>
<Button onClick={() => Event([E("state.processing", {}),E("state.think", {})])}
sx={{"bg": "red", "color": "white", "width": "6em", "padding": "1em"}}>{`처음부터`}</Button></HStack></Fragment>}</Fragment> : <Fragment/>}</Fragment>
<Fragment>{state.is_exist_prev_histoy ? <Fragment><Button onClick={() => Event([E("state.restoring", {}),E("state.starting", {}),E("state.restore_history", {})])}
sx={{"bg": "black", "color": "white", "width": "6em", "padding": "1em"}}>{`복원하기`}</Button></Fragment> : <Fragment/>}</Fragment></HStack></Center></VStack>
<Fragment>{state.is_loading ? <Fragment><VStack sx={{"bg": "white", "padding": "2em", "borderRadius": "25px", "w": "100vh", "alignItems": "center"}}><Fragment>{state.is_restoring_history ? <Fragment><Text>{`기록 복원중`}</Text></Fragment> : <Fragment><Text/></Fragment>}</Fragment>
<CircularProgress color="rgb(0, 0, 0)"
isIndeterminate={true}><CircularProgressLabel sx={{"color": "rgb(0, 0, 0)"}}>{`Thinking`}</CircularProgressLabel></CircularProgress></VStack></Fragment> : <Fragment/>}</Fragment>
{state.history.map((dyvapkxp, i) => <VStack key={i}
sx={{"bg": "white", "padding": "2em", "borderRadius": "25px", "w": "100%", "alignItems": "left"}}><Heading size="md">{dyvapkxp.thoughts}</Heading>
<List spacing=".25em"><Fragment>{dyvapkxp.reasoning ? <Fragment><ListItem><InfoOutlineIcon sx={{"color": "green"}}/>
{(" " + dyvapkxp.reasoning)}</ListItem></Fragment> : <Fragment/>}</Fragment>
<OrderedList>{dyvapkxp.plans.map((kkkiyutw, i) => <ListItem key={i}>{kkkiyutw}</ListItem>)}</OrderedList>
<Fragment>{dyvapkxp.criticism ? <Fragment><ListItem><WarningTwoIcon sx={{"color": "red"}}/>
{(" " + dyvapkxp.criticism)}</ListItem></Fragment> : <Fragment/>}</Fragment>
<Accordion allowToggle={true}><AccordionItem><AccordionButton>{`시스템`}
<AccordionIcon/></AccordionButton>
<AccordionPanel><Prism customStyle={{}}
wrapLongLines={true}>{dyvapkxp.system}</Prism></AccordionPanel></AccordionItem></Accordion></List></VStack>)}</VStack>
<NextHead><title>{`Pynecone App`}</title>
<meta content="A Pynecone app."
name="description"/>
<meta content="favicon.ico"
property="og:image"/></NextHead></Center>
)
}