from typing import Dict, Text, List, Any
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet
import requests
import os
import re
from datetime import datetime
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

class ActionTimeBasedGreet(Action):
    def name(self) -> Text:
        return "action_time_based_greet"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_time = datetime.now().hour
        if 5 <= current_time < 12:
            greeting = "Good morning! Welcome to Alberta Educational Centre. How can I assist you today?"
        elif 12 <= current_time < 17:
            greeting = "Good afternoon! Welcome to Alberta Educational Centre. How can I assist you today?"
        else:
            greeting = "Good evening! Welcome to Alberta Educational Centre. How can I assist you today?"
        
        dispatcher.utter_message(text=greeting)
        return []

class ActionProvideLink(Action):
    def name(self) -> Text:
        return "action_provide_link"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message['intent'].get('name')
        
        if intent == "ask_about_digital_id":
            message = "To register for MyAlberta Digital ID, go to the Create account page. Fill-in the rquested information and follow the navigation page here: [Alberta.ca Account](https://learnerregistry.ae.alberta.ca/Home/StartLookup)"
        elif intent == "ask_about_admissions":
            message = "You can find detailed information about our admissions process here: [Admissions Page](https://myaec.ca/admissions/)"
        else:
            message = "I'm sorry, I don't have a specific link for that information. How else can I assist you?"
            
        dispatcher.utter_message(text=message)
        return []

class ActionProvideProgramDetails(Action):
    def name(self) -> Text:
        return "action_provide_program_details"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        programs = {
            "cybersecurity": ("[Cybersecurity Specialist Diploma](https://www.afewoldiesandagoodie.ca/cybersecurity-specialist)", "prepares you for a career in information security."),
            "cloud": ("[Cloud Engineering Diploma](https://www.afewoldiesandagoodie.ca/cloud-engineering)", "focuses on cloud computing technologies and architectures."),
            "medical office": ("[Medical Office Assistant Diploma](https://www.afewoldiesandagoodie.ca/medical-office-assistant)", "trains you for administrative roles in healthcare settings."),
            "digital office": ("[Digital Office Certificate](https://www.afewoldiesandagoodie.ca/digital-office)", "equips you with essential digital skills for modern office environments."),
            "pc technician": ("[PC Technician Certificate](https://www.afewoldiesandagoodie.ca/pc-tech)", "covers hardware and software troubleshooting and maintenance."),
            "it professional": ("[IT Professional Certificate](https://www.afewoldiesandagoodie.ca/it-professional)", "provides a broad foundation in information technology."),
            "security analyst": ("[Security Analyst Certificate](https://www.afewoldiesandagoodie.ca/security-analyst)", "focuses on network security and threat analysis.")
        }
        
        program_message = "These are all the programs we currently offer at Alberta Educational Centre:\n\n"
        for link, details in programs.values():
            program_message += f"• {link} - {details}\n"
        dispatcher.utter_message(text=program_message)
        return []

class ActionProvideLocation(Action):
    def name(self) -> Text:
        return "action_provide_location"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message = "Alberta Educational Centre is located in Calgary, Alberta."
        dispatcher.utter_message(text=message)
        return []

class ActionProvideExactAddress(Action):
    def name(self) -> Text:
        return "action_provide_exact_address"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        address = "5980 Centre Street S, Calgary, AB T2H 0C1"
        message = f"Our campus is located at {address}. You can use this address for GPS navigation or mailing purposes."
        dispatcher.utter_message(text=message)
        return []

class ValidateContactForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_contact_form"

    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> List[Text]:
        """A list of required slots that the form has to fill"""
        logger.debug("Extracting required slots")  # Add logging
        return ["first_name", "last_name", "email", "phone_number"]

    async def validate_first_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate first_name value."""
        if not slot_value or len(slot_value.strip()) < 2:
            dispatcher.utter_message(text="Please provide a valid first name.")
            return {"first_name": None}
        return {"first_name": slot_value.strip().title()}

    async def validate_last_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate last_name value."""
        if not slot_value or len(slot_value.strip()) < 2:
            dispatcher.utter_message(text="Please provide a valid last name.")
            return {"last_name": None}
        return {"last_name": slot_value.strip().title()}

    async def validate_email(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate email input."""
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not slot_value or not re.match(email_pattern, slot_value):
            dispatcher.utter_message(text="Please provide a valid email address (example@domain.com)")
            return {"email": None}
        return {"email": slot_value.lower()}

    async def validate_phone_number(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate phone number input."""
        phone_number = re.sub(r'\D', '', str(slot_value))
        if len(phone_number) not in [10, 11]:
            dispatcher.utter_message(text="Please provide a valid phone number (10 digits).")
            return {"phone_number": None}
        if len(phone_number) == 10:
            formatted_phone = f"{phone_number[:3]}-{phone_number[3:6]}-{phone_number[6:]}"
        else:
            formatted_phone = f"{phone_number[0]}-{phone_number[1:4]}-{phone_number[4:7]}-{phone_number[7:]}"
        return {"phone_number": formatted_phone}

class ActionSubmitToHubSpot(Action):
    def name(self) -> Text:
        return "action_submit_to_hubspot"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        logger.info("Starting new HubSpot submission")
        first_name = tracker.get_slot("first_name")
        last_name = tracker.get_slot("last_name")
        email = tracker.get_slot("email")
        phone_number = tracker.get_slot("phone_number")
        
        hubspot_api_key = os.getenv("HUBSPOT_API_KEY")
        logger.info(f"API key status: {'Present' if hubspot_api_key else 'Missing'}")
        if not hubspot_api_key:
            logger.error("Missing HubSpot API key in environment variables")
            dispatcher.utter_message(
                text="I apologize, but I'm having trouble connecting to our system. Please contact us directly at +1 403 441 2059."
            )
            return []
        contact_data = {
            "properties": {
                "firstname": first_name,
                "lastname": last_name,
                "email": email,
                "phone": phone_number
            }
        }
        headers = {
            "Authorization": f"Bearer {hubspot_api_key}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(
                "https://api.hubapi.com/crm/v3/objects/contacts",
                headers=headers,
                json=contact_data,
                timeout=10
            )
            if response.status_code == 201:
                logger.info(f"Successfully created HubSpot contact for {first_name} {last_name}")
                dispatcher.utter_message(
                    text=f"Thank you {first_name}! An advisor will reach out to you shortly."
                )
            elif response.status_code == 409:
                logger.info(f"Contact already exists for email {email}")
                dispatcher.utter_message(
                    text=f"Thank you {first_name}! An advisor will reach out to you shortly."
                )
            else:
                logger.error(f"HubSpot Error: {response.status_code} - {response.text}")
                dispatcher.utter_message(
                    text="I'm having trouble saving your information. Please contact us at +1 403 441 2059."
                )
        except Exception as e:
            logger.error(f"Error submitting to HubSpot: {str(e)}")
            dispatcher.utter_message(
                text="I'm having trouble with your request. Please contact us at +1 403 441 2059."
            )
        return [SlotSet("first_name", None), SlotSet("last_name", None), SlotSet("email", None), SlotSet("phone_number", None)]

class ActionProvidePDF(Action):
    def name(self):
        return "action_provide_pdf"
    
    async def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message("You can find the inclusion of our tuition fees per program in our [Course Outline](https://mysait-my.sharepoint.com/:b:/r/personal/hyacinth_galicha_edu_sait_ca/Documents/AEC%20Files/COURSE%20OUTLINE%202023.pdf?csf=1&web=1&e=MWfdBg). For further questions regarding any of these, contact our admissions office.")
        return []
