import re
import os
import socket
import logging
import smtplib
from pathlib import Path
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from robot.api import TestSuiteBuilder
from encryption_utils import decrypt_data

# Set global configuration values
SMTP_SERVER = 'smtp-mail.outlook.com'
SMTP_PORT = 587

class ScriptAnalyzer:
    def __init__(self, script_path, recipient_email, encrypted_sender_email, encrypted_sender_password, encryption_key):
        self.script_path = Path(script_path)
        self.recipient_email = recipient_email
        self.sender_email = decrypt_data(encrypted_sender_email, encryption_key).decode()
        self.sender_password = decrypt_data(encrypted_sender_password, encryption_key).decode()
        self.log_file = self.get_log_file_name()
        self.encryption_key = encryption_key
        self.counts = {
            'human_error': 0,
            'missing_settings': 0,
            'missing_imports': 0,
            'missing_suite_setup': 0,
            'missing_suite_teardown': 0,
            'missing_tests': 0,
            'missing_documentation': 0,
            'missing_tags': 0,
            'keyword_documentation': 0,
            'variable_naming': 0,
            'missing_setup': 0,
            'missing_teardown': 0,
        }
        self.test_case_errors = {}
        logging.basicConfig(filename=self.log_file, level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')

        def filter_out_http_requests(record):
            server_ip = socket.gethostbyname(socket.gethostname())
            message = record.getMessage()
            if "GET /upload" in message and "HTTP/1.1" in message:
                return False
            if f"{server_ip} - -" in message:
                return False
            return True

        logger = logging.getLogger(__name__)
        logger.addFilter(filter_out_http_requests)

    def get_log_file_name(self):
        current_datetime = datetime.now().strftime("%H-%M-%S-on-%d-%m-%Y")
        log_folder = self.script_path.parent / "Logs"
        log_folder.mkdir(parents=True, exist_ok=True)
        os.chmod(log_folder, 0o777)
        log_file_name = f"Logs-{self.script_path.stem}-at-{current_datetime}.log"
        return log_folder / log_file_name

    def run_analysis(self):
        try:
            print(f"Starting Script Analysis of {self.script_path.stem}.")
            logging.info(f"Starting Script Analysis of {self.script_path.stem}.")

            self.analyze_robot_file()

            print(f"Script Analysis of {self.script_path.stem} Completed.")
            logging.info(f"Script Analysis of {self.script_path.stem} Completed.")

            self.add_summary_to_log()
            self.send_email()

        except Exception as e:
            logging.error(f"Error during analysis: {str(e)}")

    def add_summary_to_log(self):
        # Add errors to the log file
        with open(self.log_file, 'a') as log_file:
            log_file.write(f'------------------------------------------------------------------------------------------------------------\n')
            log_file.write(f'------------------------------------------------------------------------------------------------------------\n')
            log_file.write(f'\nScript Analysis of <{self.script_path.stem}.robot> Started\n\n')
            for error in self.errors:
                log_file.write(f"INFO --{error}\n")
            log_file.write(f"\nScript Analysis of <{self.script_path.stem}.robot> has been Completed\n\n")
            log_file.write(f'------------------------------------------------------------------------------------------------------------\n')
            log_file.write(f'------------------------------------------------------------------------------------------------------------\n')
            log_file.write(f"\n-----------------------------------------\n        Total Errors Identified         \n-----------------------------------------\n")
            for test_case, error_count in self.test_case_errors.items():
                log_file.write(f"   <{test_case}> :: Error Count - {error_count}\n")
            
        summary = "-----------------------------------------\n"
        summary += "\n------------------------------------------------------------------------------------------------------------\n"
        summary += "------------------------------------------------------------------------------------------------------------\n"
        summary += "\n-----------------------------------------\n"
        issues_found = any(count > 0 for count in self.counts.values())
        if issues_found:
            summary += "       Summary of Issues observed       \n"
            summary += "-----------------------------------------\n"
            summary += "	Check					    Count\n"
            
            for check, count in self.counts.items():
                if count > 0:
                    summary += f" {check.ljust(33)}{count}\n"
        else:
            summary += " No Issues observed after Analyzing the Script\n"

        summary += "-----------------------------------------\n"
        summary += "\n------------------------------------------------------------------------------------------------------------"
        summary += "\n------------------------------------------------------------------------------------------------------------\n"
        with open(self.log_file, 'a') as log_file:
            log_file.write(summary)

    def analyze_robot_file(self):
        suite = TestSuiteBuilder().build(self.script_path)
        self.errors = []
        test_case_names = {}
        self.test_case_errors = {}

        def log_and_record_error(message, count_key, test_case_name=None):
            self.errors.append(message)
            self.counts[count_key] += 1
            if test_case_name:
                if test_case_name not in self.test_case_errors:
                    self.test_case_errors[test_case_name] = 0
                self.test_case_errors[test_case_name] += 1

        def check_naming_convention(name, type_):
            short_name = name.split(':')[0].strip()
            if not re.match(r'^[A-Z][a-zA-Z0-9 ]*$', name):
                log_and_record_error(f' <{short_name}> :: {type_} should follow Naming Conventions (Title Case)', 'variable_naming', short_name)

        def check_documentation(doc, name, type_):
            short_name = name.split(':')[0].strip()
            if not doc:
                log_and_record_error(f' <{short_name}> :: {type_} lacks Documentation', 'missing_documentation', short_name)

        if not suite.resource:
            log_and_record_error(" <Settings> :: Missing *** Settings *** section in the Test Suite", 'missing_settings')
        else:
            if not suite.resource.imports:
                log_and_record_error(" <Settings> :: Missing Import statements in *** Settings *** section", 'missing_imports')

            libraries = [imp for imp in suite.resource.imports if imp.type.lower() == 'library']
            resources = [imp for imp in suite.resource.imports if imp.type.lower() == 'resource']
            if not libraries:
                log_and_record_error(" <Settings> :: Missing Library import in *** Settings *** section", 'missing_imports')
            if not resources:
                log_and_record_error(" <Settings> :: Missing Resource import in *** Settings *** section", 'missing_imports')

            if not suite.setup:
                log_and_record_error(" <Settings> :: Missing Suite Setup in *** Settings *** section", 'missing_suite_setup')
            if not suite.teardown:
                log_and_record_error(" <Settings> :: Missing Suite Teardown in *** Settings *** section", 'missing_suite_teardown')

        if not suite.tests:
            log_and_record_error(" <TestCase> :: Missing *** Test Cases *** section in the test suite", 'missing_tests')

        if not suite.doc:
            log_and_record_error(" <Settings> :: Missing Documentation in *** Settings *** section", 'missing_documentation')

        for test in suite.tests:
            short_name = test.name.split(':')[0].strip()
            if short_name not in test_case_names:
                test_case_names[short_name] = 0
            test_case_names[short_name] += 1

            if test_case_names[short_name] > 1:
                log_and_record_error(f' <HUMAN ERROR> :: <{short_name}> is Repeated more than once in the Script, Please Verify!', 'human_error', short_name)

            check_documentation(test.doc, test.name, "Test case")
            check_naming_convention(test.name, "Test case")
            if not test.setup:
                log_and_record_error(f' <{short_name}> :: Test case lacks a setup step', 'missing_setup', short_name)
            if not test.teardown:
                log_and_record_error(f' <{short_name}> :: Test case lacks a teardown step', 'missing_teardown', short_name)
            if not test.tags:
                log_and_record_error(f' <{short_name}> :: Test case lacks tags', 'missing_tags', short_name)

        for keyword in suite.resource.keywords:
            check_documentation(keyword.doc, keyword.name, "Keyword")
            if not keyword.doc:
                log_and_record_error(f' <{keyword.name}> :: Keyword lacks documentation', 'keyword_documentation')

        for var in suite.resource.variables:
            if not re.match(r'^[A-Z_][A-Z0-9_]*$', var.name):
                log_and_record_error(f' <{var.name}> :: Variable should be uppercase with underscores (e.g., "${{VAR_NAME}}")', 'variable_naming')

        if self.errors:
            logging.info("Errors found:")
            for error in self.errors:
                logging.info(f'INFO - {error}')
            for test_case, error_count in self.test_case_errors.items():
                logging.info(f'INFO -- <{test_case}> :: Total Errors - {error_count}')
        else:
            logging.info("No Errors Detected. The script follows the Coding Standards.")

    def send_email(self):
        # Create a multipart message
        message = MIMEMultipart()
        message['From'] = self.sender_email
        message['To'] = self.recipient_email
        recipient_user = self.recipient_email.split('@')[0].capitalize()

        # Get the current date and format it as desired
        current_date = datetime.now().strftime('%d-%m-%Y')
        subject = f"Script Analysis Log - {self.script_path.stem} - {current_date}"
        message['Subject'] = subject

        # Add body to email
        body = f"Hello {recipient_user},<br><br>"
        body += "<b><font size='4.5' color='#000000'>File Type: </font></b> .robot<br><br>"
        body += "<u><b><font size='4.5' color='#000000'>Summary:</font></b></u><br>"

        # Create a table for counts with added CSS for better styling
        table = "<table style='border-collapse: collapse; border: 4px solid black; width: 50%; background-color: #f2f2f2;'>"
        table += "<tr style='background-color: #4CAF50; color: white;'>"
        table += "<th style='border: 3px solid black; padding: 15px;'>Check</th>"
        table += "<th style='border: 3px solid black; padding: 15px;'>Count</th>"
        table += "</tr>"

        # Define a dictionary to map the check names to more understandable terms
        check_names = {
            'human_error': 'Human Error Check',
            'missing_settings': 'Settings Check',
            'missing_imports': 'Settings: Imports Check',
            'missing_suite_setup': 'Settings: Suite Setup Check',
            'missing_suite_teardown': 'Settings: Teardown Check',
            'missing_tests': 'Testcase Check',
            'missing_documentation': 'TestCase: Documentation Check',
            'missing_tags': 'TestCase: Tags Check',
            'missing_setup': 'TestCase: Setup Check',
            'missing_teardown': 'TestCase: Teardown Check',
            'variable_naming': 'TestCase: Variable Naming Check',
            'keyword_documentation': 'Keyword Documentation Check'
        }
        
        for check, count in self.counts.items():
            if count > 0:
                check_name = check_names.get(check, check)
                table += f"<tr><td style='border: 3px solid black; padding: 15px; text-align: left;'>{check_name}</td><td style='border: 3px solid black; padding: 15px; text-align: center;'>{count}</td></tr>"
        table += "</table><br>"

        # Append the table to the body
        body += table
        body += "<br>Please Refer to the Attached Log for the detailed Analysis<br><br>Regards<br>ScriptAnalyzer-QA<br>"

        # Attach the body with the msg instance
        message.attach(MIMEText(body, 'html'))

        # Attach the log file
        with open(self.log_file, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(self.log_file)}")
            message.attach(part)

        # Send the email
        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, self.recipient_email, message.as_string())
                logging.info("Email sent successfully.")
        except Exception as e:
            logging.error(f"Failed to send email: {str(e)}")

if __name__ == "__main__":
    # Analyze the script
    script_analyzer = ScriptAnalyzer(script_path, recipient_email, encrypted_sender_email, encrypted_sender_password, encryption_key)
    script_analyzer.run_analysis()
