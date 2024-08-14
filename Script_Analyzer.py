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
        self.custom_keywords = []
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
            'spacing_errors': 0,
        }
        self.errors = []
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
        with open(self.log_file, 'a') as log_file:
            log_file.write(f'------------------------------------------------------------------------------------------------------------\n')
            log_file.write(f'------------------------------------------------------------------------------------------------------------\n')
            log_file.write(f'\nScript Analysis of <{self.script_path.stem}.robot> Started\n\n')
            for error in self.errors:
                log_file.write(f"INFO --{error}\n")
            log_file.write(f"\nScript Analysis of <{self.script_path.stem}.robot> has been Completed\n\n")
            log_file.write(f'------------------------------------------------------------------------------------------------------------\n')
            log_file.write(f'------------------------------------------------------------------------------------------------------------\n')
            log_file.write(f"\n---------------------------------------------\n           Total Errors Identified\n---------------------------------------------\n")

            # Initialize aggregated counts
            keywords_issue_count = 0
            variable_naming_issue_count = 0

            # Sum up keyword issues and variable naming issues
            for test_case, error_count in self.test_case_errors.items():
                if test_case in ["Dependent Test Case", "Unconfigure"]:
                    keywords_issue_count += error_count
                elif re.match(r'\$\{[a-zA-Z_]+\}', test_case):
                    variable_naming_issue_count += error_count
                else:
                    log_file.write(f"   <{test_case}> :: Error Count - {error_count}\n")
            
            # Add the aggregated counts to the log
            if keywords_issue_count > 0:
                log_file.write(f"   Keywords_Issue :: Error Count - {keywords_issue_count}\n")
            if variable_naming_issue_count > 0:
                log_file.write(f"   Variable_Naming_Issue :: Error Count - {variable_naming_issue_count}\n")
            
            # Log the total count of spacing errors
            if self.counts['spacing_errors'] > 0:
                log_file.write(f"   Spacing Issues :: Error Count - {self.counts['spacing_errors']}\n")

        summary = "---------------------------------------------\n"
        summary += "\n------------------------------------------------------------------------------------------------------------\n"
        summary += "------------------------------------------------------------------------------------------------------------\n"
        summary += "\n---------------------------------------------\n"
        issues_found = any(count > 0 for count in self.counts.values())
        if issues_found:
            summary += "         Summary of Issues observed       \n"
            summary += "---------------------------------------------\n"
            summary += "          Check                   Count\n"
            
            for check, count in self.counts.items():
                if count > 0:
                    summary += f" {check.ljust(33)}{count}\n"
        else:
            summary += " No Issues observed after Analyzing the Script\n"

        summary += "---------------------------------------------\n"
        summary += "\n------------------------------------------------------------------------------------------------------------"
        summary += "\n------------------------------------------------------------------------------------------------------------\n"
        with open(self.log_file, 'a') as log_file:
            log_file.write(summary)

    def check_spacing(self):
        with open(self.script_path, 'r') as script_file:
            lines = script_file.readlines()

        line_number = 0
        prev_line = ""
        errors_on_current_line = set()
        in_keywords_section = False  # Initialize the state to track if we are in the Keywords section

        for line in lines:
            line_number += 1
            stripped_line = line.rstrip()

            # Identify custom keywords in the Keywords section
            if stripped_line.startswith("***") and "keywords" in stripped_line.lower():
                in_keywords_section = True
                continue

            if stripped_line.startswith("***") and not "keywords" in stripped_line.lower():
                in_keywords_section = False
                continue

            if in_keywords_section and re.match(r'^[a-zA-Z]', stripped_line):
                self.custom_keywords.append(stripped_line.split()[0])
                continue

            # Skip comment lines
            if stripped_line.startswith("#"):
                continue

            # Skip section headers (lines that start and end with '**')
            if re.match(r'^\*\*.*\*\*$', stripped_line):
                continue

            errors_on_current_line.clear()

            # Check if the line contains a keyword and skip it if it's a custom keyword
            keyword = stripped_line.split(None, 1)[0] if stripped_line else ""
            if keyword in self.custom_keywords:
                continue

            # Perform spacing checks
            self.check_keyword_and_argument_spacing(line, line_number, errors_on_current_line)

            # Check for non-standard comment block
            self.check_non_standard_comment_block(line, line_number, errors_on_current_line)

            # Check for indentation and tabs
            self.check_indentation_and_tabs(line, line_number, errors_on_current_line)

            # Check for operator spacing
            self.check_operator_spacing(line, line_number, errors_on_current_line)

            # Check for blank line before sections
            self.check_blank_line_before_sections(stripped_line, prev_line, line_number, errors_on_current_line)

            # Check for trailing spaces and line length
            self.check_trailing_spaces_and_line_length(line, stripped_line, line_number, errors_on_current_line)

            prev_line = line

    def check_non_standard_comment_block(self, line, line_number, errors_on_current_line):
        if "################" in line and "non_standard_comment" not in errors_on_current_line:
            self.errors.append(f"Line {line_number}: Found non-standard comment block. Please remove this line.")
            self.counts['spacing_errors'] += 1
            errors_on_current_line.add("non_standard_comment")

    def check_indentation_and_tabs(self, line, line_number, errors_on_current_line):
        indentation_match = re.match(r'^( +)', line)
        if '\t' in line and "tab_character" not in errors_on_current_line:
            self.errors.append(f"Line {line_number}: Found tab character. Please use spaces instead.")
            self.counts['spacing_errors'] += 1
            errors_on_current_line.add("tab_character")
        elif indentation_match and "indentation_error" not in errors_on_current_line:
            indentation_length = len(indentation_match.group(1))
            if indentation_length % 4 != 0:
                self.errors.append(f"Line {line_number}: Indentation error. Expected a multiple of 4 spaces but found {indentation_length}.")
                self.counts['spacing_errors'] += 1
                errors_on_current_line.add("indentation_error")

    # Update the check_keyword_and_argument_spacing method to skip custom keywords
    def check_keyword_and_argument_spacing(self, line, line_number, errors_on_current_line):
        stripped_line = line.strip()

        # Skip comment lines
        if stripped_line.startswith("#"):
            return

        # Extract the keyword and skip checks if it's a custom keyword
        keyword = stripped_line.split(None, 1)[0] if stripped_line else ""
        if keyword in self.custom_keywords:
            return

        # Define a list of built-in keywords that should be excluded from spacing checks
        built_in_keywords = [
            "Log", "Log To Console", "Run Keyword", "Run Keyword If", 
            "Call Method", "Should Be Equal", "Should Be True", "Set Suite Variable", 
            "Suite Setup", "Suite Teardown", "IF", "Check", "Resource", "ELSE IF"
            # Add more built-in keywords as needed
        ]

        if re.match(r'^\s*\S+', line) and len(line.split()) > 1:
            parts = line.split(None, 1)
            keyword = parts[0]

            # Skip the check if the line starts with a built-in keyword
            if any(keyword.lower() == k.lower().split()[0] for k in built_in_keywords):
                return

            args = line[len(keyword):]

            # Check for exactly 4 spaces between keyword and arguments
            if not args.startswith(' ' * 4):
                if "keyword_spacing" not in errors_on_current_line:
                    self.errors.append(f"Line {line_number}: Expected exactly 4 spaces between keyword '{keyword}' and arguments.")
                    self.counts['spacing_errors'] += 1
                    errors_on_current_line.add("keyword_spacing")
                # Skip the second check if the first one fails
                return

            # Check for consistent spacing between arguments only if the first check passed
            args_parts = re.split(r'(\s+)', args.strip())
            if len(args_parts) > 2:
                for i in range(1, len(args_parts), 2):
                    if len(args_parts[i]) != 4 and "argument_spacing" not in errors_on_current_line:
                        self.errors.append(f"Line {line_number}: Inconsistent spacing between arguments after keyword '{keyword}'.")
                        self.counts['spacing_errors'] += 1
                        errors_on_current_line.add("argument_spacing")

    def check_operator_spacing(self, line, line_number, errors_on_current_line):
        stripped_line = line.strip()

        # Skip comment lines
        if stripped_line.startswith("#"):
            return

        # Define arithmetic operators
        arithmetic_operators = r'[\+\-\*/=]'

        # Check if the line contains an arithmetic operator but is not part of a Resource or Library import
        if re.search(arithmetic_operators, line) and "operator_spacing" not in errors_on_current_line:
            # Exclude lines that are Resource or Library import statements
            if stripped_line.startswith("Resource") or stripped_line.startswith("Library"):
                return

            # Exclude cases where the operator is part of a string (e.g., a file path)
            if re.search(r'[\'"].*[\+\-\*/=].*[\'"]|(\.\.\/)+|([\w\.-]+\/)+[\w\.-]+', line):
                return

    def check_operator_spacing(self, line, line_number, errors_on_current_line):
        stripped_line = line.strip()

        # Skip comment lines
        if stripped_line.startswith("#"):
            return

        # Define arithmetic operators
        arithmetic_operators = r'[\+\-\*/=]'

        # Check if the line contains an arithmetic operator but is not part of a URL, file path, query parameter, or key-value pair in a dictionary
        if re.search(arithmetic_operators, line) and "operator_spacing" not in errors_on_current_line:
            # Exclude lines that contain URLs, file paths, query parameters, or key-value pairs
            if re.search(r'https?://|\/[\w\./-]*[\?&]?|(\.\.\/)+[\w\./-]*', line) or re.search(r'[\'"].*[\+\-\*/=].*[\'"]', line):
                return

            # Check for missing spaces around arithmetic operators
            if not re.search(r' [\+\-\*/=] ', line):
                # Heuristic to check if it looks like a valid arithmetic expression
                if re.search(r'\d+ *[\+\-\*/=] *\d+', line) or re.search(r'\w+ *[\+\-\*/=] *\w+', line):
                    self.errors.append(f"Line {line_number}: Missing spaces around operators in expression.")
                    self.counts['spacing_errors'] += 1
                    errors_on_current_line.add("operator_spacing")

        # Check for line length (if needed)
        if len(stripped_line) > 120:
            self.errors.append(f"Line {line_number}: Line exceeds 120 characters.")
            self.counts['spacing_errors'] += 1
            errors_on_current_line.add("line_length")

    def check_blank_line_before_sections(self, stripped_line, prev_line, line_number, errors_on_current_line):
        if re.match(r'^\*\*\* ', stripped_line) and "missing_blank_line" not in errors_on_current_line:
            if prev_line.strip() and prev_line != "":
                self.errors.append(f"Line {line_number}: Missing blank line before section or test case.")
                self.counts['spacing_errors'] += 1
                errors_on_current_line.add("missing_blank_line")

    def check_trailing_spaces_and_line_length(self, line, stripped_line, line_number, errors_on_current_line):
        if len(line.rstrip('\n')) != len(stripped_line) and "trailing_spaces" not in errors_on_current_line:
            self.errors.append(f"Line {line_number}: Trailing spaces found.")
            self.counts['spacing_errors'] += 1
            errors_on_current_line.add("trailing_spaces")
        elif len(stripped_line) > 200 and "line_length" not in errors_on_current_line:
            self.errors.append(f"Line {line_number}: Line exceeds 200 characters.")
            self.counts['spacing_errors'] += 1
            errors_on_current_line.add("line_length")

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
            if type_ == "Variable" and not re.match(r'^\${[A-Z_][A-Z0-9_]*}$', name):
                log_and_record_error(f' <{short_name}> :: {type_} should be uppercase with underscores (e.g., "${{VAR_NAME}}")', 'variable_naming', short_name)
            elif type_ != "Variable" and not re.match(r'^[A-Z][a-zA-Z0-9 ]*$', name):
                log_and_record_error(f' <{short_name}> :: {type_} should follow Naming Conventions (Title Case)', 'variable_naming', short_name)

        def check_documentation(doc, name, type_):
            short_name = name.split(':')[0].strip()
            if not doc:
                error_type = 'keyword_documentation' if type_ == "Keyword" else 'missing_documentation'
                log_and_record_error(f' <{short_name}> :: {type_} lacks Documentation', error_type, short_name)

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
            if not test.tags:
                log_and_record_error(f' <{short_name}> :: Test case lacks tags', 'missing_tags', short_name)
            if not test.setup:
                log_and_record_error(f' <{short_name}> :: Test case lacks a setup step -- Please Implement if Required', 'missing_setup', short_name)
            if not test.teardown:
                log_and_record_error(f' <{short_name}> :: Test case lacks a teardown step -- Please Implement if Required', 'missing_teardown', short_name)

        # Processing keywords with documentation and naming convention checks
        for keyword in suite.resource.keywords:
            check_documentation(keyword.doc, keyword.name, "Keyword")
            check_naming_convention(keyword.name, "Keyword")

        # Processing variables and checking naming convention
        for var in suite.resource.variables:
            check_naming_convention(var.name, "Variable")

        # Check for non-standard section headers
        with open(self.script_path, 'r') as script_file:
            lines = script_file.readlines()

        for line_number, line in enumerate(lines, start=1):
            stripped_line = line.rstrip()
            # Skip comment lines
            if stripped_line.startswith("#"):
                continue

            if re.match(r'^\*\* [A-Za-z ]+ \*\*$', stripped_line):
                self.errors.append(f"Line {line_number}: Found non-standard section header. Use '*** Section ***' format.")
                self.counts['variable_naming'] += 1

        # Perform the spacing check
        self.check_spacing()

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
            'keyword_documentation': 'Keywords: Documentation Check',
            'spacing_errors': 'Spacing Issues'
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
