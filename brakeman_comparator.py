import re
import sys
from copy import copy
from bs4 import BeautifulSoup
from difflib import SequenceMatcher


class Comparator:
    def __init__(self, file1, file2):
        with open(file1, "r") as old_scan:
            body = old_scan.read()
            self.old_scan_soup = BeautifulSoup(body, 'html.parser')
        with open(file2, "r") as new_scan:
            body = new_scan.read()
            self.new_scan_soup = BeautifulSoup(body, 'html.parser')
        self.head = """  <!DOCTYPE HTML SYSTEM>
            <html>

            <head>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
            <title>Brakeman Report</title>
            <script type="text/javascript" src="https://code.jquery.com/jquery-2.1.4.min.js"></script>
            <script type="text/javascript" src="https://cdn.datatables.net/1.10.9/js/jquery.dataTables.min.js"></script>
            <script type="text/javascript">
                function toggle(context) {
                var elem = document.getElementById(context);

                if (elem.style.display != "block")
                    elem.style.display = "block";
                else
                    elem.style.display = "none";

                elem.parentNode.scrollIntoView();
                }

                $(document).ready(function () {
                $('table').DataTable({
                    searching: false,
                    paging: false,
                    info: false
                });
                });
            </script>
            <style>
                /* CSS style used for HTML reports */
                body {
                font-family: sans-serif;
                color: #161616;
                }

                a {
                color: #161616;
                }

                p {
                font-weight: bold;
                font-size: 11pt;
                color: #2D0200;
                }

                th {
                background-color: #980905;
                border-bottom: 5px solid #530200;
                color: white;
                font-size: 11pt;
                padding: 1px 8px 1px 8px;
                }

                td {
                border-bottom: 2px solid white;
                font-family: monospace;
                padding: 5px 8px 1px 8px;
                }

                table {
                background-color: #FCF4D4;
                border-collapse: collapse;
                }

                h1 {
                color: #2D0200;
                font-size: 14pt;
                }

                h2 {
                color: #2D0200;
                font-size: 12pt;
                }

                span.high-confidence {
                font-weight: bold;
                color: red;
                }

                span.med-confidence {}

                span.weak-confidence {
                color: gray;
                }

                div.warning_message {
                cursor: pointer;
                }

                div.warning_message:hover {
                background-color: white;
                }

                table caption {
                background-color: #FFE;
                padding: 2px;
                }

                table.context {
                margin-top: 5px;
                margin-bottom: 5px;
                border-left: 1px solid #90e960;
                color: #212121;
                }

                tr.context {
                background-color: white;
                }

                tr.first {
                border-top: 1px solid #7ecc54;
                padding-top: 2px;
                }

                tr.error {
                background-color: #f4c1c1 !important
                }

                tr.near_error {
                background-color: #f4d4d4 !important
                }

                tr.alt {
                background-color: #e8f4d4;
                }

                td.context {
                padding: 2px 10px 0px 6px;
                border-bottom: none;
                }

                td.context_line {
                padding: 2px 8px 0px 7px;
                border-right: 1px solid #b3bda4;
                border-bottom: none;
                color: #6e7465;
                }

                pre.context {
                margin-bottom: 1px;
                }

                .user_input {
                background-color: #fcecab;
                }

                div.render_path {
                display: none;
                background-color: #ffe;
                padding: 5px;
                margin: 2px 0px 2px 0px;
                }

                div.template_name {
                cursor: pointer;
                }

                div.template_name:hover {
                background-color: white;
                }

                span.code {
                font-family: monospace;
                }

                span.filename {
                font-family: monospace;
                }
                
            </style>
            </head>
            """
        body = """  <body>
                    <h1>Brakeman Report</h1>
                    <h2>Summary</h2>
                    <div class="dataTables_wrapper no-footer">
                        <table>
                        <thead>
                            <tr role="row">
                            <th style="text-align: center">Scanned/Reported</th>
                            <th style="text-align: center">Fixed Errors</th>
                            <th style="text-align: center">New Errors</th>
                            </tr>
                        </thead>
                        <tbody id="summary">
                            <tr style="text-align: center">
                            <td>Controllers</td>
                                <td>0</td>
                                <td>0</td>
                            </tr>
                            <tr style="text-align: center">
                            <td>Errors</td>
                                <td>0</td>
                                <td>0</td>
                            </tr>
                            <tr style="text-align: center">
                            <td>Ignored Warnings</td>
                                <td>0</td>
                                <td>0</td>
                            </tr>
                            <tr style="text-align: center">
                            <td>Models</td>
                                <td>0</td>
                                <td>0</td>
                            </tr>
                            <tr style="text-align: center">
                            <td>Security Warnings</td>
                                <td>0</td>
                                <td>0</td>
                            </tr>
                            <tr style="text-align: center">
                            <td>Templates</td>
                                <td>0</td>
                                <td>0</td>
                            </tr>
                        </tbody>
                        </table>
                    </div>


                    <h2>Controllers</h2>
                    <div class="dataTables_wrapper no-footer">
                        <table>
                        <thead>
                            <tr>
                            <th>Name</th>
                            <th>Parent</th>
                            <th>Includes</th>
                            <th>Routes</th>
                            </tr>
                        </thead>
                        <tbody id="controllers">
                        </tbody>
                        </table>
                    </div>


                    <h2>Security Warnings</h2>
                    <div class="dataTables_wrapper no-footer">
                        <table>
                        <thead>
                            <tr>
                            <th>Confidence</th>
                            <th>Class</th>
                            <th>Method</th>
                            <th>Warning Type</th>
                            <th>CWE ID</th>
                            <th>Message</th>
                            </tr>
                        </thead>
                        <tbody id="security_warnings">
                        </tbody>
                        </table>
                    </div>


                    <h2>Controller Warnings</h2>
                    <div class="dataTables_wrapper no-footer">
                        <table>
                        <thead>
                            <tr>
                            <th>Confidence</th>
                            <th>Controller</th>
                            <th>Warning Type</th>
                            <th>CWE ID</th>
                            <th>Message</th>
                            </tr>
                        </thead>
                        <tbody id="controller_warnings">
                        </tbody>
                        </table>
                    </div>

                        <h2>View Warnings</h2>
                    <div class="dataTables_wrapper no-footer">
                        <table>
                        <thead>
                            <tr>
                            <th>Confidence</th>
                            <th>Template</th>
                            <th>Warning Type</th>
                            <th>CWE ID</th>
                            <th>Message</th>
                            </tr>
                        </thead>
                        <tbody id="view_warnings">
                        </tbody>
                        </table>
                    </div>


                    <h2>Templates</h2>
                    <div id="templates">
                    </div>
                    </body>"""

        # HTML SKELETON
        self.html_template_soup = BeautifulSoup(body, 'html.parser')
        self.summary_table_soup = self.html_template_soup.find("tbody", id="summary")
        self.security_warning_table_soup = self.html_template_soup.find("tbody", id="security_warnings")
        self.controller_warning_table_soup = self.html_template_soup.find("tbody", id="controller_warnings")
        self.view_warning_table_soup = self.html_template_soup.find("tbody", id="view_warnings")
        self.controller_error_table_soup = self.html_template_soup.find("tbody", id="controllers")
        self.template_error_table_soup = self.html_template_soup.find("div", id="templates")
        self.no_of_controllers = 0
        self.no_of_errors = 0
        self.no_of_ignored_warnings = 0
        self.no_of_models = 0
        self.no_of_security_warnings = 0
        self.no_of_templates = 0

    def getText(self, parent):
        return ''.join(parent.find_all(string=True, recursive=False)).strip()

    # TEMPLATES
    def templates(self):
        old_scan_template_soup = self.old_scan_soup.find("body").find_all("p", recursive=False)
        new_scan_template_soup_p_tag = self.new_scan_soup.find("body").find_all("p", recursive=False)
        new_scan_template_soup_div_tag = []
        for div in new_scan_template_soup_p_tag:
            x = div.findNextSibling("div") if div.findNextSibling("div") else div.findNextSibling("table")
            new_scan_template_soup_div_tag.append(x)
        old_scan_template_soup_text = []
        for element in old_scan_template_soup:
            if element.text:
                old_scan_template_soup_text.append(element.text)

        for p_tag, div_tag in zip(new_scan_template_soup_p_tag, new_scan_template_soup_div_tag):
            if p_tag.text and p_tag.text not in old_scan_template_soup_text:
                self.template_error_table_soup.append(p_tag)
                if div_tag:
                    self.no_of_templates += 1
                    self.template_error_table_soup.append(div_tag)

    # SUMMARY
    def summary(self):
        try:
            old_scan_soup_summary = self.old_scan_soup.find("h2", string="Summary").findNextSibling("div")
        except AttributeError:
            return
        if old_scan_soup_summary is None:
            old_scan_soup_summary = self.old_scan_soup.find("h2", string="Summary").findNextSibling("table").find("tbody")
        else:
            old_scan_soup_summary = self.old_scan_soup.find("h2", string="Summary").findNextSibling("div").find("tbody")

        new_scan_soup_summary = self.new_scan_soup.find("h2", string="Summary").findNextSibling("div")
        if new_scan_soup_summary is None:
            new_scan_soup_summary = self.new_scan_soup.find("h2", string="Summary").findNextSibling("table").find("tbody")
        else:
            new_scan_soup_summary = self.new_scan_soup.find("h2", string="Summary").findNextSibling("div").find("tbody")

        Controllers = int(self.getText(new_scan_soup_summary.find("td", string="Controllers").find_next_sibling(
            "td"))) - int(self.getText(old_scan_soup_summary.find("td", string="Controllers").find_next_sibling("td"))) - self.no_of_controllers
        Errors = int(self.getText(new_scan_soup_summary.find("td", string="Errors").find_next_sibling(
            "td"))) - int(self.getText(old_scan_soup_summary.find("td", string="Errors").find_next_sibling("td"))) - self.no_of_errors
        Ignored_Warnings = int(self.getText(new_scan_soup_summary.find("td", string="Ignored Warnings").find_next_sibling(
            "td"))) - int(self.getText(old_scan_soup_summary.find("td", string="Ignored Warnings").find_next_sibling("td"))) - self.no_of_ignored_warnings
        Models = int(self.getText(new_scan_soup_summary.find("td", string="Models").find_next_sibling(
            "td"))) - int(self.getText(old_scan_soup_summary.find("td", string="Models").find_next_sibling("td"))) - self.no_of_models
        Security_Warnings = int(self.getText(new_scan_soup_summary.find("td", string="Security Warnings").find_next_sibling(
            "td"))) - int(self.getText(old_scan_soup_summary.find("td", string="Security Warnings").find_next_sibling("td"))) - self.no_of_security_warnings
        Templates = int(self.getText(new_scan_soup_summary.find("td", string="Templates").find_next_sibling(
            "td"))) - int(self.getText(old_scan_soup_summary.find("td", string="Templates").find_next_sibling("td"))) - self.no_of_templates

        self.summary_table_soup.find("td", string="Controllers").find_next_sibling("td").contents[0].replace_with(str(Controllers))
        self.summary_table_soup.find("td", string="Controllers").find_next_sibling("td").find_next_sibling("td").contents[0].replace_with(str(self.no_of_controllers))

        self.summary_table_soup.find("td", string="Errors").find_next_sibling("td").contents[0].replace_with(str(Errors))
        self.summary_table_soup.find("td", string="Errors").find_next_sibling("td").find_next_sibling("td").contents[0].replace_with(str(self.no_of_errors))

        self.summary_table_soup.find("td", string="Ignored Warnings").find_next_sibling("td").contents[0].replace_with(str(Ignored_Warnings))
        self.summary_table_soup.find("td", string="Ignored Warnings").find_next_sibling("td").find_next_sibling("td").contents[0].replace_with(str(self.no_of_ignored_warnings))

        self.summary_table_soup.find("td", string="Models").find_next_sibling("td").contents[0].replace_with(str(Models))
        self.summary_table_soup.find("td", string="Models").find_next_sibling("td").find_next_sibling("td").contents[0].replace_with(str(self.no_of_models))

        self.summary_table_soup.find("td", string="Security Warnings").find_next_sibling("td").contents[0].replace_with(str(Security_Warnings))
        self.summary_table_soup.find("td", string="Security Warnings").find_next_sibling("td").find_next_sibling("td").contents[0].replace_with(str(self.no_of_security_warnings))

        self.summary_table_soup.find("td", string="Templates").find_next_sibling("td").contents[0].replace_with(str(Templates))
        self.summary_table_soup.find("td", string="Templates").find_next_sibling("td").find_next_sibling("td").contents[0].replace_with(str(self.no_of_templates))

    # CONTROLLER
    def controller(self):
        old = True
        try:
            old_scan_soup_controller = self.old_scan_soup.find("h2", string="Controllers").findNextSibling("div")
        except AttributeError:
            old = False
        if old and old_scan_soup_controller is None:
            old_scan_soup_controller = self.old_scan_soup.find("h2", string="Controllers").findNextSibling("table").find("tbody")
            old_scan = old_scan_soup_controller.find_all("tr", recursive=False)
        elif old:
            old_scan_soup_controller = self.old_scan_soup.find("h2", string="Controllers").findNextSibling("div").find("tbody")
            old_scan = old_scan_soup_controller.find_all("tr", role="row", class_={"odd", "even"}, recursive=False)

        try:
            new_scan_soup_controller = self.new_scan_soup.find("h2", string="Controllers").findNextSibling("div")
        except AttributeError:
            return
        if new_scan_soup_controller is None:
            new_scan_soup_controller = self.new_scan_soup.find("h2", string="Controllers").findNextSibling("table").find("tbody")
            new_scan = new_scan_soup_controller.find_all("tr", recursive=False)
        else:
            new_scan_soup_controller = self.new_scan_soup.find("h2", string="Controllers").findNextSibling("div").find("tbody")
            new_scan = new_scan_soup_controller.find_all("tr", role="row", class_={"odd", "even"}, recursive=False)

        old_scan_errors = []
        if old:
            for x in old_scan:
                error_msg = "".join(i.strip() for i in x.text.strip() if i.strip())
                if error_msg:
                    if len(error_msg) > 1500:
                        old_scan_errors.append(error_msg[:1500])
                    else:
                        old_scan_errors.append(error_msg)
        for x in new_scan:
            error_msg = "".join(i.strip() for i in x.text.strip() if i.strip())
            if len(error_msg) > 1500:
                error_msg = error_msg[:1500]
            match = [0]
            if error_msg in old_scan_errors or not error_msg:
                continue
            for string1 in old_scan_errors:
                length = min(len(string1), len(error_msg))
                temp = SequenceMatcher(None, string1[:length], error_msg[:length]).ratio()
                temp = round(temp * 100, 2)
                match.append(temp)
                print("Match Percentage", temp)
                if temp >= 80:
                    print(string1, error_msg, sep='\n')
                    break
            match_percentage = max(match)
            print("MAX", match_percentage)
            if match_percentage <= 80:
                self.no_of_controllers += 1
                print("New Error")
                print(error_msg)
                self.controller_error_table_soup.insert_before(x)
        print("CONTROLLER")

    # SECURITY WARNING
    def securtiy_warning(self):
        old = True
        try:
            old_scan_soup_Security_Warnings = self.old_scan_soup.find("h2", string="Security Warnings").findNextSibling("div")
        except AttributeError:
            old = False
        if old and old_scan_soup_Security_Warnings is None:
            old_scan_soup_Security_Warnings = self.old_scan_soup.find("h2", string="Security Warnings").findNextSibling("table").find("tbody")
            old_scan = old_scan_soup_Security_Warnings.find_all("tr", recursive=False)
        elif old:
            old_scan_soup_Security_Warnings = self.old_scan_soup.find("h2", string="Security Warnings").findNextSibling("div").find("tbody")
            old_scan = old_scan_soup_Security_Warnings.find_all("tr", role="row", class_={"odd", "even"}, recursive=False)
        try:
            new_scan_soup_Security_Warnings = self.new_scan_soup.find("h2", string="Security Warnings").findNextSibling("div")
        except AttributeError:
            return
        if new_scan_soup_Security_Warnings is None:
            new_scan_soup_Security_Warnings = self.new_scan_soup.find("h2", string="Security Warnings").findNextSibling("table").find("tbody")
            new_scan = new_scan_soup_Security_Warnings.find_all("tr", recursive=False)
        else:
            new_scan_soup_Security_Warnings = self.new_scan_soup.find("h2", string="Security Warnings").findNextSibling("div").find("tbody")
            new_scan = new_scan_soup_Security_Warnings.find_all("tr", role="row", class_={"odd", "even"}, recursive=False)

        old_scan_errors = []
        if old:
            for element in old_scan:
                x = copy(element)
                for child in x.find_all("table"):
                    child.clear()
                error_msg = "".join(i.strip() for i in x.text.strip() if i.strip())
                line = re.findall("nearline\d*", error_msg)
                if line:
                    error_msg = error_msg.replace(line[0], "")
                if error_msg:
                    if len(error_msg) > 1500:
                        old_scan_errors.append(error_msg[:1500])
                    else:
                        old_scan_errors.append(error_msg)
        for element in new_scan:
            x = copy(element)
            for child in x.find_all("table"):
                child.clear()
            error_msg = "".join(i.strip() for i in x.text.strip() if i.strip())
            line = re.findall("nearline\d*", error_msg)
            if line:
                error_msg = error_msg.replace(line[0], "")
            if len(error_msg) > 1500:
                error_msg = error_msg[:1500]
            match = [0]
            if error_msg in old_scan_errors or not error_msg:
                continue
            for string1 in old_scan_errors:
                length = min(len(string1), len(error_msg))
                temp = SequenceMatcher(None, string1[:length], error_msg[:length]).ratio()
                temp = round(temp * 100, 2)
                match.append(temp)
                print("Match Percentage", temp)
                if temp >= 80:
                    print(string1, error_msg, sep='\n')
                    break
            match_percentage = max(match)
            print("MAX", match_percentage)
            if match_percentage <= 80:
                print("New Error")
                print(error_msg)
                self.no_of_security_warnings += 1
                self.security_warning_table_soup.insert_before(element)
        print("SECURITY WARNING")

    # CONTROLLER WARNING
    def controller_warning(self):
        old = True
        try:
            old_scan_soup_Controller_Warnings = self.old_scan_soup.find("p", string="Controller Warnings").findNextSibling("div")
        except AttributeError:
            old = False
        if old and old_scan_soup_Controller_Warnings is None:
            old_scan_soup_Controller_Warnings = self.old_scan_soup.find("p", string="Controller Warnings").findNextSibling("table").find("tbody")
            old_scan = old_scan_soup_Controller_Warnings.find_all("tr", recursive=False)
        elif old:
            old_scan_soup_Controller_Warnings = self.old_scan_soup.find("p", string="Controller Warnings").findNextSibling("div").find("tbody")
            old_scan = old_scan_soup_Controller_Warnings.find_all("tr", role="row", class_={"odd", "even"}, recursive=False)

        try:
            new_scan_soup_Controller_Warnings = self.new_scan_soup.find("p", string="Controller Warnings").findNextSibling("div")
        except AttributeError:
            return
        if new_scan_soup_Controller_Warnings is None:
            new_scan_soup_Controller_Warnings = self.new_scan_soup.find("p", string="Controller Warnings").findNextSibling("table").find("tbody")
            new_scan = new_scan_soup_Controller_Warnings.find_all("tr", recursive=False)
        else:
            new_scan_soup_Controller_Warnings = self.new_scan_soup.find("p", string="Controller Warnings").findNextSibling("div").find("tbody")
            new_scan = new_scan_soup_Controller_Warnings.find_all("tr", role="row", class_={"odd", "even"}, recursive=False)

        old_scan_warnings = []
        if old:
            for element in old_scan:
                x = copy(element)
                for child in x.find_all("table"):
                    child.clear()
                error_msg = "".join(i.strip() for i in x.text.strip() if i.strip())
                line = re.findall("nearline\d*", error_msg)
                if line:
                    error_msg = error_msg.replace(line[0], "")
                if error_msg:
                    if len(error_msg) > 1500:
                        old_scan_warnings.append(error_msg[:1500])
                    else:
                        old_scan_warnings.append(error_msg)
        for element in new_scan:
            x = copy(element)
            for child in x.find_all("table"):
                child.clear()
            error_msg = "".join(i.strip() for i in x.text.strip() if i.strip())
            line = re.findall("nearline\d*", error_msg)
            if line:
                error_msg = error_msg.replace(line[0], "")
            if len(error_msg) > 1500:
                error_msg = error_msg[:1500]
            match = [0]
            if error_msg in old_scan_warnings or not error_msg:
                continue
            for string1 in old_scan_warnings:
                length = min(len(string1), len(error_msg))
                temp = SequenceMatcher(None, string1[:length], error_msg[:length]).ratio()
                temp = round(temp * 100, 2)
                match.append(temp)
                print("Match Percentage", temp)
                if temp >= 80:
                    print(string1, error_msg, sep='\n')
                    break
            match_percentage = max(match)
            print("MAX", match_percentage)
            if match_percentage <= 80:
                print("New Error")
                print(error_msg)
                self.controller_warning_table_soup.insert_before(element)
        print("CONTROLLER WARNING")

    # VIEWS WARNING
    def view_warning(self):
        old = True
        try:
            old_scan_soup_View_Warnings = self.old_scan_soup.find("p", string="View Warnings").findNextSibling("div")
        except AttributeError:
            old = False
        if old and old_scan_soup_View_Warnings is None:
            old_scan_soup_View_Warnings = self.old_scan_soup.find("p", string="View Warnings").findNextSibling("table").find("tbody")
            old_scan = old_scan_soup_View_Warnings.find_all("tr", recursive=False)
        elif old:
            old_scan_soup_View_Warnings = self.old_scan_soup.find("p", string="View Warnings").findNextSibling("div").find("tbody")
            old_scan = old_scan_soup_View_Warnings.find_all("tr", role="row", class_={"odd", "even"}, recursive=False)

        try:
            new_scan_soup_view_warnings = self.new_scan_soup.find("p", string="View Warnings").findNextSibling("div")
        except:
            return
        if new_scan_soup_view_warnings is None:
            new_scan_soup_view_warnings = self.new_scan_soup.find("p", string="View Warnings").findNextSibling("table").find("tbody")
            new_scan = new_scan_soup_view_warnings.find_all("tr", recursive=False)
        else:
            new_scan_soup_view_warnings = self.new_scan_soup.find("p", string="View Warnings").findNextSibling("div").find("tbody")
            new_scan = new_scan_soup_view_warnings.find_all("tr", role="row", class_={"odd", "even"}, recursive=False)

        old_scan_warnings = []
        if old:
            for element in old_scan:
                x = copy(element)
                for child in x.find_all("table"):
                    child.clear()
                error_msg = "".join(i.strip() for i in x.text.strip() if i.strip())
                line = re.findall("nearline\d*", error_msg)
                if line:
                    error_msg = error_msg.replace(line[0], "")
                if error_msg:
                    if len(error_msg) > 1500:
                        old_scan_warnings.append(error_msg[:1500])
                    else:
                        old_scan_warnings.append(error_msg)
        for element in new_scan:
            x = copy(element)
            for child in x.find_all("table"):
                child.clear()
            error_msg = "".join(i.strip() for i in x.text.strip() if i.strip())
            line = re.findall("nearline\d*", error_msg)
            if line:
                error_msg = error_msg.replace(line[0], "")
            if len(error_msg) > 1500:
                error_msg = error_msg[:1500]
            match = [0]
            if error_msg in old_scan_warnings or not error_msg:
                continue
            for string1 in old_scan_warnings:
                length = min(len(string1), len(error_msg))
                temp = SequenceMatcher(None, string1[:length], error_msg[:length]).ratio()
                temp = round(temp * 100, 2)
                match.append(temp)
                print("Match Percentage", temp)
                if temp >= 80:
                    print(string1, error_msg, sep='\n')
                    break
            match_percentage = max(match)
            print("MAX", match_percentage)
            if match_percentage <= 80:
                print("New Error")
                print(error_msg)
                self.view_warning_table_soup.insert_before(element)
        print("VIEW WARNING")

    def call_stack(self):
        self.controller()
        self.securtiy_warning()
        self.controller_warning()
        self.view_warning()
        self.templates()
        self.summary()
        return self.head, self.html_template_soup


# file1_before_deployment = sys.argv[1]
# file2_after_deployment = sys.argv[2]
# print("File 1 Name: {}\nFile 2 Name: {}".format(file1_before_deployment, file2_after_deployment))
# Obj = Comparator(file1_before_deployment, file2_after_deployment)
# head, html_template_soup = Obj.call_stack()
#
# file1_before_deployment = file1_before_deployment.split("/")[-1]
# file2_after_deployment = file2_after_deployment.split("/")[-1]
# file_name = "/tmp/artifacts/" + "compared_" + file2_after_deployment.split(".html")[0] + "_with_" + file1_before_deployment.split(".html")[0] + ".html"
#
# content = str(html_template_soup).replace('{', '[').replace('}', ']')
# with open(file_name, "w") as html_template:
#     html_template.write(head + content)
# print("REPORT NAME", file_name)
