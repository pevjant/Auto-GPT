import {Fragment, useEffect, useRef, useState} from "react"
import {useRouter} from "next/router"
import {E, connect, updateState, uploadFiles} from "/utils/state"
import "focus-visible/dist/focus-visible"
import {Accordion, AccordionButton, AccordionIcon, AccordionItem, AccordionPanel, Button, Center, CircularProgress, CircularProgressLabel, HStack, Heading, Input, List, ListItem, OrderedList, Stack, Text, VStack, useColorMode} from "@chakra-ui/react"
import {InfoOutlineIcon, WarningTwoIcon} from "@chakra-ui/icons"
import {Prism} from "react-syntax-highlighter"
import NextHead from "next/head"

const PING = "http://localhost:8000/ping"
const EVENT = "ws://localhost:8000/event"
const UPLOAD = "http://localhost:8000/upload"
export default function Component() {
const [state, setState] = useState({"ai_goals": ["\ud56d\uc0c1 \ub2e4\uc218(\ucd5c\uc18c 5\uba85)\uc758 agent\ub4e4\uc744 \ud1b5\ud574 \ud1a0\ub860\ud558\uc5ec \ud1b5\uacc4\uc801\uc73c\ub85c \uc2b9\ub960\uc774 \ub192\uc740 \uae30\uc220\uc801 \ubd84\uc11d\uc744 \uc120\ud0dd\ud558\ub3c4\ub85d \ud558\uae30", "\ub2e4\uc591\uc131\uc744 \uc704\ud574 agnet \ub4e4\uc758 \uc758\uacac\uc740 \ubaa8\ub450 \uac19\uc744 \uc218 \uc5c6\uace0 \ud1a0\ub860\uc744 \ud1b5\ud574 \uc77c\uce58 \ub418\uc5b4\uc57c\ud568", "\uc790\uae08 \uad00\ub9ac, \ub9ac\uc2a4\ud06c \uad00\ub9ac \uc6d0\uce59 \uc815\ud558\uae30", "\uac70\ub798\uc2dc \uc5b4\ub5a4 \uc6d0\uce59\uacfc \uadfc\uac70\ub85c \ud588\ub294\uc9c0 \uae30\ub85d\ud558\uae30", "\ub9e4\ub9e4 \uc2e4\ud328\uc2dc \uc2e4\ud328 \uc774\uc720 \ud1a0\ub860 \ubc0f \ubd84\uc11d\ud574 \uae30\ub85d\ud558\uae30, \ub2f5\ubcc0\uc740 \ubb34\uc870\uac74 \ud55c\uad6d\uc5b4\ub85c \ubc88\uc5ed\ud558\uae30"], "ai_name": "\ud2b8\ub808\uc774\ub354-GPT", "ai_role": "\uae30\uc220\uc801 \ubd84\uc11d\uc744 \ud1b5\ud574 price action \uacfc buyer\uc640 seller \uc758 \uc2ec\ub9ac \uc2f8\uc6c0\uc744 \ud310\ub2e8\ud574 \uac70\ub798\ud558\ub294 \uc804\ubb38\uc801\uc778 \uac70\ub798 \uc778\uacf5\uc9c0\ub2a5 \uc785\ub2c8\ub2e4.", "full_message_history": [], "history": [], "is_started": false, "is_thinking": false, "openai_api_key": "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", "prompt": null, "result": null, "update_count": 0, "user_input": "Determine which next command to use, and respond using the format specified above:", "events": [{"name": "state.hydrate"}], "files": []})
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
<Input defaultValue="트레이더-GPT"
onChange={(_e) => Event([E("state.set_ai_name", {value:_e.target.value})])}
placeholder="트레이더-GPT"
type="text"/></HStack>
<HStack><Text as="b"
sx={{"width": "150px"}}>{`최종 목표`}</Text>
<Input defaultValue={state.ai_role}
onChange={(_e) => Event([E("state.set_ai_role", {value:_e.target.value})])}
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
<Input defaultValue={state.openai_api_key}
onChange={(_e) => Event([E("state.set_openai_api_key", {key:_e.target.value})])}
placeholder="sk-..."
type="text"/></HStack></Stack></AccordionPanel></AccordionItem></Accordion>
<Accordion allowToggle={true}><AccordionItem><AccordionButton>{`사용자 입력`}
<AccordionIcon/></AccordionButton>
<AccordionPanel><Stack><HStack><Text sx={{"width": "150px"}}>{`입력`}</Text>
<Input defaultValue=""
onChange={(_e) => Event([E("state.set_user_input", {value:_e.target.value})])}
placeholder={state.user_input}
type="text"/></HStack></Stack></AccordionPanel></AccordionItem></Accordion>
<Center><Fragment>{state.is_started ? <Fragment><Text/></Fragment> : <Fragment><Button onClick={() => Event([E("state.processing", {}),E("state.starting", {}),E("state.think", {})])}
sx={{"bg": "black", "color": "white", "width": "6em", "padding": "1em"}}>{`생각하기`}</Button></Fragment>}</Fragment>
<Fragment>{state.is_started ? <Fragment>{state.is_thinking ? <Fragment><Text/></Fragment> : <Fragment><HStack><Button onClick={() => Event([E("state.processing", {}),E("state.cont", {})])}
sx={{"bg": "black", "color": "white", "width": "6em", "padding": "1em"}}>{`계속 생각하기`}</Button>
<Button onClick={() => Event([E("state.processing", {}),E("state.think", {})])}
sx={{"bg": "red", "color": "white", "width": "6em", "padding": "1em"}}>{`처음부터`}</Button></HStack></Fragment>}</Fragment> : <Fragment/>}</Fragment></Center></VStack>
<Fragment>{state.is_thinking ? <Fragment><VStack sx={{"bg": "white", "padding": "2em", "borderRadius": "25px", "w": "100vh", "alignItems": "center"}}><CircularProgress color="rgb(0, 0, 0)"
isIndeterminate={true}><CircularProgressLabel sx={{"color": "rgb(0, 0, 0)"}}>{`Thinking`}</CircularProgressLabel></CircularProgress></VStack></Fragment> : <Fragment/>}</Fragment>
<Fragment>{state.update_count ? <Fragment>{state.history.map((qmmxsdms, i) => <VStack key={i}
sx={{"bg": "white", "padding": "2em", "borderRadius": "25px", "w": "100%", "alignItems": "left"}}><Heading size="md">{qmmxsdms.thoughts}</Heading>
<List spacing=".25em"><Fragment>{qmmxsdms.reasoning ? <Fragment><ListItem><InfoOutlineIcon sx={{"color": "green"}}/>
{(" " + qmmxsdms.reasoning)}</ListItem></Fragment> : <Fragment/>}</Fragment>
<OrderedList>{qmmxsdms.plans.map((ovopylxi, i) => <ListItem key={i}>{ovopylxi}</ListItem>)}</OrderedList>
<Fragment>{qmmxsdms.agents ? <Fragment><List><ListItem><InfoOutlineIcon sx={{"color": "blue"}}/>
{` Agents 생각들`}</ListItem>
<OrderedList>{qmmxsdms.agents.map((rwypbtxm, i) => <ListItem key={i}>{rwypbtxm}</ListItem>)}</OrderedList></List></Fragment> : <Fragment/>}</Fragment>
<Fragment>{qmmxsdms.criticism ? <Fragment><ListItem><WarningTwoIcon sx={{"color": "red"}}/>
{(" " + qmmxsdms.criticism)}</ListItem></Fragment> : <Fragment/>}</Fragment>
<Accordion allowToggle={true}><AccordionItem><AccordionButton>{`시스템`}
<AccordionIcon/></AccordionButton>
<AccordionPanel><Prism customStyle={{}}
wrapLongLines={true}>{qmmxsdms.system}</Prism></AccordionPanel></AccordionItem></Accordion></List></VStack>)}</Fragment> : <Fragment/>}</Fragment></VStack>
<NextHead><title>{`Auto-GPT UI`}</title>
<meta content="A Pynecone app."
name="description"/>
<meta content="favicon.ico"
property="og:image"/></NextHead></Center>
)
}