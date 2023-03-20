import datetime
import re
from copy import copy
from bs4 import BeautifulSoup


head = """  <!DOCTYPE HTML SYSTEM>
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
                    <th>Scanned/Reported</th>
                    <th>Total</th>
                    </tr>
                </thead>
                <tbody id="summary">
                    <tr>
                    <td>Controllers</td>
                    <td>0</td>
                    </tr>
                    <tr>
                    <td>Errors</td>
                        <td>0</td>
                    </tr>
                    <tr>
                    <td>Ignored Warnings</td>
                        <td>0</td>
                    </tr>
                    <tr>
                    <td>Models</td>
                        <td>0</td>
                    </tr>
                    <tr>
                    <td>Security Warnings</td>
                        <td>0</td>
                    </tr>
                    <tr>
                    <td>Templates</td>
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
html_template_soup = BeautifulSoup(body, 'html.parser')
summary_table_soup = html_template_soup.find("tbody", id="summary")
security_warning_table_soup = html_template_soup.find("tbody", id="security_warnings")
controller_warning_table_soup = html_template_soup.find("tbody", id="controller_warnings")
view_warning_table_soup = html_template_soup.find("tbody", id="view_warnings")
controller_error_table_soup = html_template_soup.find("tbody", id="controllers")
template_error_table_soup = html_template_soup.find("div", id="templates")


class comparator:
    def __init__(self, file1, file2):
        with open(file1, "r") as old_scan:
            body = old_scan.read()
            self.old_scan_soup = BeautifulSoup(body, 'html.parser')

        with open(file2, "r") as new_scan:
            body = new_scan.read()
            self.new_scan_soup = BeautifulSoup(body, 'html.parser')

    def getText(self, parent):
        return ''.join(parent.find_all(text=True, recursive=False)).strip()


    # TEMPLATES
    def templates(self):
        global template_error_table_soup

        old_scan_template_soup = self.old_scan_soup.find(
            "body").find_all("p", recursive=False)
        new_scan_template_soup_p_tag = self.new_scan_soup.find(
            "body").find_all("p", recursive=False)
        new_scan_template_soup_div_tag = []
        for div in new_scan_template_soup_p_tag:
            x = div.find_next_sibling("div") if div.find_next_sibling(
                "div") else div.find_next_sibling("table")
            new_scan_template_soup_div_tag.append(x)
        old_scan_template_soup_text = []
        for element in old_scan_template_soup:
            if element.text:
                old_scan_template_soup_text.append(element.text)

        for p_tag, div_tag in zip(new_scan_template_soup_p_tag, new_scan_template_soup_div_tag):
            if p_tag.text and p_tag.text not in old_scan_template_soup_text:
                template_error_table_soup.append(p_tag)
                if div_tag:
                    template_error_table_soup.append(div_tag)


    # SUMMARY
    def summary(self):
        global summary_table_soup

        try:
            old_scan_soup_summary = self.old_scan_soup.find(
                "h2", text="Summary").find_next_sibling("div")
        except AttributeError:
            return
        if old_scan_soup_summary is None:
            old_scan_soup_summary = self.old_scan_soup.find(
                "h2", text="Summary").find_next_sibling("table").find("tbody")
        else:
            old_scan_soup_summary = self.old_scan_soup.find(
                "h2", text="Summary").find_next_sibling("div").find("tbody")

        new_scan_soup_summary = self.new_scan_soup.find(
            "h2", text="Summary").find_next_sibling("div")
        if new_scan_soup_summary is None:
            new_scan_soup_summary = self.new_scan_soup.find(
                "h2", text="Summary").find_next_sibling("table").find("tbody")
        else:
            new_scan_soup_summary = self.new_scan_soup.find(
                "h2", text="Summary").find_next_sibling("div").find("tbody")

        Controllers = int(self.getText(new_scan_soup_summary.find("td", text="Controllers").find_next_sibling(
            "td"))) - int(self.getText(old_scan_soup_summary.find("td", text="Controllers").find_next_sibling("td")))
        Errors = int(self.getText(new_scan_soup_summary.find("td", text="Errors").find_next_sibling(
            "td"))) - int(self.getText(old_scan_soup_summary.find("td", text="Errors").find_next_sibling("td")))
        Ignored_Warnings = int(self.getText(new_scan_soup_summary.find("td", text="Ignored Warnings").find_next_sibling(
            "td"))) - int(self.getText(old_scan_soup_summary.find("td", text="Ignored Warnings").find_next_sibling("td")))
        Models = int(self.getText(new_scan_soup_summary.find("td", text="Models").find_next_sibling(
            "td"))) - int(self.getText(old_scan_soup_summary.find("td", text="Models").find_next_sibling("td")))
        Security_Warnings = int(self.getText(new_scan_soup_summary.find("td", text="Security Warnings").find_next_sibling(
            "td"))) - int(self.getText(old_scan_soup_summary.find("td", text="Security Warnings").find_next_sibling("td")))
        Templates = int(self.getText(new_scan_soup_summary.find("td", text="Templates").find_next_sibling(
            "td"))) - int(self.getText(old_scan_soup_summary.find("td", text="Templates").find_next_sibling("td")))

        summary_table_soup.find("td", text="Controllers").find_next_sibling(
            "td").contents[0].replace_with(str(Controllers))
        summary_table_soup.find("td", text="Errors").find_next_sibling(
            "td").contents[0].replace_with(str(Errors))
        summary_table_soup.find("td", text="Ignored Warnings").find_next_sibling(
            "td").contents[0].replace_with(str(Ignored_Warnings))
        summary_table_soup.find("td", text="Models").find_next_sibling(
            "td").contents[0].replace_with(str(Models))
        summary_table_soup.find("td", text="Security Warnings").find_next_sibling(
            "td").contents[0].replace_with(str(Security_Warnings))
        summary_table_soup.find("td", text="Templates").find_next_sibling(
            "td").contents[0].replace_with(str(Templates))


    # CONTROLLER
    def controller(self):
        global controller_error_table_soup

        old = True
        try:
            old_scan_soup_controller = self.old_scan_soup.find(
                "h2", text="Controllers").find_next_sibling("div")
        except AttributeError:
            old = False
        if old and old_scan_soup_controller is None:
            old_scan_soup_controller = self.old_scan_soup.find(
                "h2", text="Controllers").find_next_sibling("table").find("tbody")
            old_scan = old_scan_soup_controller.find_all("tr", recursive=False)
        elif old:
            old_scan_soup_controller = self.old_scan_soup.find(
                "h2", text="Controllers").find_next_sibling("div").find("tbody")
            old_scan = old_scan_soup_controller.find_all(
                "tr", role="row", class_={"odd", "even"}, recursive=False)

        try:
            new_scan_soup_controller = self.new_scan_soup.find(
                "h2", text="Controllers").find_next_sibling("div")
        except AttributeError:
            return
        if new_scan_soup_controller is None:
            new_scan_soup_controller = self.new_scan_soup.find(
                "h2", text="Controllers").find_next_sibling("table").find("tbody")
            new_scan = new_scan_soup_controller.find_all("tr", recursive=False)
        else:
            new_scan_soup_controller = self.new_scan_soup.find(
                "h2", text="Controllers").find_next_sibling("div").find("tbody")
            new_scan = new_scan_soup_controller.find_all(
                "tr", role="row", class_={"odd", "even"}, recursive=False)

        old_scan_errors = []
        if old:
            for x in old_scan:
                error_msg = "".join(i.strip() for i in x.text.strip() if i.strip())
                if error_msg:
                    old_scan_errors.append(error_msg)
        for x in new_scan:
            error_msg = "".join(i.strip() for i in x.text.strip() if i.strip())
            if error_msg and error_msg not in old_scan_errors:
                controller_error_table_soup.insert_before(x)
        print("CONTROLLER")


    # SECURITY WARNING
    def securtiy_warning(self):
        global security_warning_table_soup

        old = True
        try:
            old_scan_soup_Security_Warnings = self.old_scan_soup.find(
                "h2", text="Security Warnings").find_next_sibling("div")
        except AttributeError:
            old = False
        if old and old_scan_soup_Security_Warnings is None:
            old_scan_soup_Security_Warnings = self.old_scan_soup.find(
                "h2", text="Security Warnings").find_next_sibling("table").find("tbody")
            old_scan = old_scan_soup_Security_Warnings.find_all(
                "tr", recursive=False)
        elif old:
            old_scan_soup_Security_Warnings = self.old_scan_soup.find(
                "h2", text="Security Warnings").find_next_sibling("div").find("tbody")
            old_scan = old_scan_soup_Security_Warnings.find_all(
                "tr", role="row", class_={"odd", "even"}, recursive=False)
        try:
            new_scan_soup_Security_Warnings = self.new_scan_soup.find(
                "h2", text="Security Warnings").find_next_sibling("div")
        except AttributeError:
            return
        if new_scan_soup_Security_Warnings is None:
            new_scan_soup_Security_Warnings = self.new_scan_soup.find(
                "h2", text="Security Warnings").find_next_sibling("table").find("tbody")
            new_scan = new_scan_soup_Security_Warnings.find_all(
                "tr", recursive=False)
        else:
            new_scan_soup_Security_Warnings = self.new_scan_soup.find(
                "h2", text="Security Warnings").find_next_sibling("div").find("tbody")
            new_scan = new_scan_soup_Security_Warnings.find_all(
                "tr", role="row", class_={"odd", "even"}, recursive=False)

        old_scan_errors = []
        if old:
            for element in old_scan:
                x = copy(element)
                for child in x.find_all("td", class_="context_line"):
                    child.clear()
                error_msg = "".join(i.strip() for i in x.text.strip() if i.strip())
                line = re.findall("nearline\d*", error_msg)
                if line:
                    error_msg = error_msg.replace(line[0], "")
                if error_msg:
                    old_scan_errors.append(error_msg)
        for element in new_scan:
            x = copy(element)
            for child in x.find_all("td", class_="context_line"):
                child.clear()
            error_msg = "".join(i.strip() for i in x.text.strip() if i.strip())
            line = re.findall("nearline\d*", error_msg)
            if line:
                error_msg = error_msg.replace(line[0], "")
            if error_msg and error_msg not in old_scan_errors:
                security_warning_table_soup.insert_before(element)
        print("SECURITY WARNING")


    # CONTROLLER WARNING
    def controller_warning(self):
        global controller_warning_table_soup

        old = True
        try:
            old_scan_soup_Controller_Warnings = self.old_scan_soup.find(
                "p", text="Controller Warnings").find_next_sibling("div")
        except AttributeError:
            old = False
        if old and old_scan_soup_Controller_Warnings is None:
            old_scan_soup_Controller_Warnings = self.old_scan_soup.find(
                "p", text="Controller Warnings").find_next_sibling("table").find("tbody")
            old_scan = old_scan_soup_Controller_Warnings.find_all(
                "tr", recursive=False)
        elif old:
            old_scan_soup_Controller_Warnings = self.old_scan_soup.find(
                "p", text="Controller Warnings").find_next_sibling("div").find("tbody")
            old_scan = old_scan_soup_Controller_Warnings.find_all(
                "tr", role="row", class_={"odd", "even"}, recursive=False)

        try:
            new_scan_soup_Controller_Warnings = self.new_scan_soup.find(
                "p", text="Controller Warnings").find_next_sibling("div")
        except AttributeError:
            return
        if new_scan_soup_Controller_Warnings is None:
            new_scan_soup_Controller_Warning = self.new_scan_soup.find(
                "p", text="Controller Warnings").find_next_sibling("table").find("tbody")
            new_scan = new_scan_soup_Controller_Warnings.find_all(
                "tr", recursive=False)
        else:
            new_scan_soup_Controller_Warnings = self.new_scan_soup.find(
                "p", text="Controller Warnings").find_next_sibling("div").find("tbody")
            new_scan = new_scan_soup_Controller_Warnings.find_all(
                "tr", role="row", class_={"odd", "even"}, recursive=False)

        old_scan_warnings = []
        if old:
            for element in old_scan:
                x = copy(element)
                for child in x.find_all("td", class_="context_line sorting_1"):
                    child.clear()
                error_msg = "".join(i.strip() for i in x.text.strip() if i.strip())
                line = re.findall("nearline\d*", error_msg)
                if line:
                    error_msg = error_msg.replace(line[0], "")
                if error_msg:
                    old_scan_warnings.append(error_msg)
        for element in new_scan:
            x = copy(element)
            for child in x.find_all("td", class_="context_line sorting_1"):
                child.clear()
            error_msg = "".join(i.strip() for i in x.text.strip() if i.strip())
            line = re.findall("nearline\d*", error_msg)
            if line:
                error_msg = error_msg.replace(line[0], "")
            if error_msg and error_msg not in old_scan_warnings:
                controller_warning_table_soup.insert_before(element)
        print("CONTROLLER WARNING")


    # VIEWS WARNING
    def view_warning(self):
        global view_warning_table_soup

        old = True
        try:
            old_scan_soup_View_Warnings = self.old_scan_soup.find(
                "p", text="View Warnings").find_next_sibling("div")
        except AttributeError:
            old = False
        if old and old_scan_soup_View_Warnings is None:
            old_scan_soup_View_Warnings = self.old_scan_soup.find(
                "p", text="View Warnings").find_next_sibling("table").find("tbody")
            old_scan = old_scan_soup_View_Warnings.find_all("tr", recursive=False)
        elif old:
            old_scan_soup_View_Warnings = self.old_scan_soup.find(
                "p", text="View Warnings").find_next_sibling("div").find("tbody")
            old_scan = old_scan_soup_View_Warnings.find_all(
                "tr", role="row", class_={"odd", "even"}, recursive=False)

        try:
            new_scan_soup_view_warnings = self.new_scan_soup.find(
                "p", text="View Warnings").find_next_sibling("div")
        except:
            return
        if new_scan_soup_view_warnings is None:
            new_scan_soup_view_warnings = self.new_scan_soup.find(
                "p", text="View Warnings").find_next_sibling("table").find("tbody")
            new_scan = new_scan_soup_view_warnings.find_all("tr", recursive=False)
        else:
            new_scan_soup_view_warnings = self.new_scan_soup.find(
                "p", text="View Warnings").find_next_sibling("div").find("tbody")
            new_scan = new_scan_soup_view_warnings.find_all(
                "tr", role="row", class_={"odd", "even"}, recursive=False)

        old_scan_warnings = []
        if old:
            for element in old_scan:
                x = copy(element)
                for child in x.find_all("td", class_="context_line sorting_1"):
                    child.clear()
                error_msg = "".join(i.strip() for i in x.text.strip() if i.strip())
                line = re.findall("nearline\d*", error_msg)
                if line:
                    error_msg = error_msg.replace(line[0], "")
                if error_msg:
                    old_scan_warnings.append(error_msg)
        for element in new_scan:
            x = copy(element)
            for child in x.find_all("td", class_="context_line sorting_1"):
                child.clear()
            error_msg = "".join(i.strip() for i in x.text.strip() if i.strip())
            line = re.findall("nearline\d*", error_msg)
            if line:
                error_msg = error_msg.replace(line[0], "")
            if error_msg and error_msg not in old_scan_warnings:
                view_warning_table_soup.insert_before(element)
        print("VIEW WARNING")


    def call_stack(self):
        self.summary()
        self.controller()
        self.securtiy_warning()
        self.controller_warning()
        self.view_warning()
        self.templates()
        return (head, html_template_soup)
