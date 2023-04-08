import asyncio
import os
import io
import aiohttp
import configparser
import json
import random
from typing import Optional
from rhasspyclient import RhasspyClient
from enum import Enum
from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from rhasspyhermes.nlu import NluIntent
from rhasspyhermes_app import ContinueSession, EndSession, HermesApp

class SessionCustomData(BaseModel):
    intent_name: str
    input_text: str
    intent_slots: Optional[str]

class IntentNames(str, Enum):
    INTENT1 = "IntentName1"

class RhasspySkill:
    name:str = None
    app: HermesApp = None
    config = None
    _LOGGER = None
    apiUrl = None
    satellite_id = None
    intents = None
    
    def __init__(self, name: str, app: HermesApp, config = None, logger = None) -> None:
        self.name = name
        self.app = app
        if config == None:
            config = self.read_configuration_file()
        self.config = config
        self.apiUrl = f"{self.config['Rhasspy']['protocol']}://{self.config['Rhasspy']['host']}:{self.config['Rhasspy']['port']}/api"
        if logger != None:
            self._LOGGER = logger            
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.setup_skill())    
    
    async def setup_skill(self):
        
        data = {}
        sentencesString = ""
        
        # Sentence setup
        async with aiohttp.ClientSession(headers=[("accept", "application/json")]) as session:
            async with session.get(
                f"{self.apiUrl}/sentences"
            ) as response:
                response.raise_for_status()
                result = await response.json()
                self._LOGGER.debug(f"Setup: Sentences GET result: {result}")
                if result.get(f"intents/{self.app.client_name}.ini") == None:
                    self._LOGGER.info(f"Setup: Sentences file note found")
                    # open the sentence file in read mode and split into a list
                    sentences = configparser.ConfigParser(allow_no_value=True)
                    sentences.read("./sentences.ini")

                    if self._LOGGER != None:
                        self._LOGGER.info(f"Setup: Sentences config file read")

                        # parse sentences config file
                        for section in sentences.sections():
                            sentencesString = f"{sentencesString}[{section}-{self.satellite_id}]\n"
                            for key in sentences[section]: 
                                sentencesString = f"{sentencesString}{key}\n"
                            sentencesString = f"{sentencesString}\n"   
                        
                        data[f"intents/{self.app.client_name}.ini"] = sentencesString

                        if self._LOGGER != None:
                            self._LOGGER.info(f"Setup: Sentences POST data built")
                        
                        async with aiohttp.ClientSession(headers=[("Content-Type", "application/json")]) as session:
                            async with session.post(
                                    f"{self.apiUrl}/sentences", data=json.dumps(data)
                                ) as response:
                                    response.raise_for_status()
                                    result = await response.text()
                                    self._LOGGER.debug(f"Setup: Sentences POST result: {result}")
                            client = RhasspyClient(f"{self.apiUrl}", session)
                            result = await client.train(no_cache=True)
                            self._LOGGER.info(f"Setup: Train POST result: {result}")
                    else:
                        self._LOGGER.info(f"Setup: Sentences config file not read")
                else:
                    self._LOGGER.info(f"Setup: Sentences file exists")

        # Register intent handlers
        self.app.on_intent(IntentNames.INTENT1)(self.intentHandler1)

    def read_configuration_file(self):
        try:
            cp = configparser.ConfigParser()
            with io.open(os.path.dirname(__file__) + "/config/config.ini", encoding="utf-8") as f:
                cp.read_file(f)
            return {section: {option_name: option for option_name, option in cp.items(section)}
                    for section in cp.sections()}
        except (IOError, configparser.Error):
            return dict()

    def response_sentence(self, intent: NluIntent, contextName:str = None, data_string: str = None) -> str:
        self._LOGGER.debug(f"Intent: {intent.id} | Started response_sentence")

        # open the responses file in read mode
        responses = configparser.ConfigParser(allow_no_value=True)
        responses.read("config/responses.ini")
        
        if contextName == None:
            intentName = intent.intent.intent_name
        else:
            intentName = f"{intent.intent.intent_name}-{contextName}"
        
        intentResponses = responses.items(intentName)
        if intentResponses[-1] == None:
            intentResponses = intentResponses[0:-1]
        
        if data_string == None:
            sentence = str(random.choice(intentResponses)[0])
        else:            
            sentence = str(random.choice(intentResponses)[0]).format(data_string)

        self._LOGGER.debug(f"Intent: {intent.id} | response_sentence sentence: {sentence}")
        self._LOGGER.debug(f"Intent: {intent.id} | Completed response_sentence")
        return sentence

    def fail_sentence(self, intent: NluIntent, errName: str):
        self._LOGGER.debug(f"Intent: {intent.id} | Started response_sentence")

        # open the responses file in read mode
        responses = configparser.ConfigParser(allow_no_value=True)
        responses.read("config/responses.ini")
        
        intentErrName = f"{intent.intent.intent_name}-Fail-{errName}"

        intentErrResponses = responses.items(intentErrName)
        if intentErrResponses[-1] == None:
            intentErrResponses = intentErrResponses[0:-1]
                    
        sentence = str(random.choice(intentErrResponses)[0])

        self._LOGGER.debug(f"Intent: {intent.id} | response_sentence sentence: {sentence}")
        self._LOGGER.debug(f"Intent: {intent.id} | Completed response_sentence")
        return sentence

    async def intentHandler1(self, intent: NluIntent):
        """Intent Handler function"""
        self._LOGGER.info(f"Intent: {intent.id} | Started: {IntentNames.INTENT1}")

        sentence = None

        sentence = self.response_sentence(intent)
        self._LOGGER.info(f"Intent: {intent.id} | Sentence: {sentence}")

        self.app.notify(sentence, intent.site_id)
        self._LOGGER.info(f"Intent: {intent.id} | Responded to {IntentNames.INTENT1}")
        self._LOGGER.info(f"Intent: {intent.id} | Completed: {IntentNames.INTENT1}")
        return EndSession()