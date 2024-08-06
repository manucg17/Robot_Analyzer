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
            log_file.write(f'Script Analysis of {self.script_path.stem}.robot started.\n\n')
            for error in self.errors:
                log_file.write(f"- {error}\n")
            log_file.write(f"\nScript Analysis of {self.script_path.stem}.robot completed.")    
        summary = "\n\n----------------------------------------\n"
        issues_found = any(count > 0 for count in self.counts.values())
        if issues_found:
            summary += "\n    Summary of Issues observed:\n"
            summary += "-------------------------------------\n"
            summary += "\tCheck\t\t\t\t\t Count\n"
            summary += "-------------------------------------\n"
            
            for check, count in self.counts.items():
                if count > 0:
                    summary += f" {check.ljust(30)}{count}\n"
        else:
            summary += " No Issues observed after Analyzing the Script\n"

        summary += "----------------------------------------\n"
        with open(self.log_file, 'a') as log_file:
            log_file.write(summary)

    def analyze_robot_file(self):
        suite = TestSuiteBuilder().build(self.script_path)
        self.errors = []

        def log_and_record_error(message):
            self.errors.append(message)
            logging.error(message)

        def check_naming_convention(name, type_):
            if not re.match(r'^[A-Z][a-zA-Z0-9 ]*$', name):
                log_and_record_error(f"{type_} '{name}' should follow naming conventions (Title Case)")

        def check_documentation(doc, name, type_):
            if not doc:
                log_and_record_error(f"{type_} '{name}' lacks documentation")

        if not suite.resource:
            self.counts['missing_settings'] += 1
            log_and_record_error("Missing *** Settings *** section")
        else:
            if not suite.resource.imports:
                self.counts['missing_imports'] += 1
                log_and_record_error("Missing import statements in *** Settings *** section")

            libraries = [imp for imp in suite.resource.imports if imp.type.lower() == 'library']
            resources = [imp for imp in suite.resource.imports if imp.type.lower() == 'resource']
            if not libraries:
                self.counts['missing_imports'] += 1
                log_and_record_error("Missing Library import in *** Settings *** section")
            if not resources:
                self.counts['missing_imports'] += 1
                log_and_record_error("Missing Resource import in *** Settings *** section")

            if not suite.setup:
                self.counts['missing_suite_setup'] += 1
                log_and_record_error("Missing Suite Setup in *** Settings *** section")
            if not suite.teardown:
                self.counts['missing_suite_teardown'] += 1
                log_and_record_error("Missing Suite Teardown in *** Settings *** section")

        if not suite.tests:
            self.counts['missing_tests'] += 1
            log_and_record_error("Missing *** Test Cases *** section")

        if not suite.doc:
            self.counts['missing_documentation'] += 1
            log_and_record_error("Test suite lacks documentation")

        for test in suite.tests:
            check_documentation(test.doc, test.name, "Test case")
            check_naming_convention(test.name, "Test case")
            if not test.setup:
                self.counts['missing_setup'] += 1
                log_and_record_error(f"Test case '{test.name}' lacks a setup step")
            if not test.teardown:
                self.counts['missing_teardown'] += 1
                log_and_record_error(f"Test case '{test.name}' lacks a teardown step")
            if not test.tags:
                self.counts['missing_tags'] += 1
                log_and_record_error(f"Test case '{test.name}' lacks tags")

        for keyword in suite.resource.keywords:
            check_documentation(keyword.doc, keyword.name, "Keyword")
            if not keyword.doc:
                self.counts['keyword_documentation'] += 1

        for var in suite.resource.variables:
            if not re.match(r'^[A-Z_][A-Z0-9_]*$', var.name):
                self.counts['variable_naming'] += 1
                log_and_record_error(f"Variable '{var.name}' should be uppercase with underscores (e.g., '${{VAR_NAME}}')")

        if self.errors:
            logging.info("Errors found:")
            for error in self.errors:
                logging.info(f"- {error}")
        else:
            logging.info("No errors found. The script follows the coding standards.")

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
        body += "Please find attached the log file for the script analysis.<br>"
        body += "<b><font size='4.5' color='#000000'>File Type: </font></b> .robot File<br><br>"
        body += "<u><b><font size='4.5' color='#000000'>Summary:</font></b></u><br><br>"

        # Create a table for counts with added CSS for better styling
        table = "<table style='border-collapse: collapse; border: 4px solid black; width: 50%; background-color: #f2f2f2;'>"
        table += "<tr style='background-color: #4CAF50; color: white;'>"
        table += "<th style='border: 1px solid black; padding: 8px;'>Check</th>"
        table += "<th style='border: 1px solid black; padding: 8px;'>Count</th>"
        table += "</tr>"

        # Define a dictionary to map the check names to more understandable terms
        check_names = {
            'missing_settings': 'Settings Check',
            'missing_imports': 'Imports Check',
            'missing_suite_setup': 'Suite Setup Check',
            'missing_suite_teardown': 'Teardown Check',
            'missing_tests': 'Testcase Check',
            'missing_documentation': 'Documentation Check',
            'missing_tags': 'Tags Check',
            'keyword_documentation': 'Keyword Check',
            'variable_naming': 'Variable Naming Check',
            'missing_setup': 'Testcase Setup Check',
            'missing_teardown': 'Testcase Teardown Check',

        }
        for check, count in self.counts.items():
            if count > 0:
                table += "<tr>"
                table += f"<td style='border: 1px solid black; padding: 8px;'>{check}</td>"
                table += f"<td style='border: 1px solid black; padding: 8px;'>{count}</td>"
                table += "</tr>"

        table += "</table><br>"

        # Append the table to the body
        body += table
        body += "<br>Best regards,<br>Script Analyzer Team"

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
