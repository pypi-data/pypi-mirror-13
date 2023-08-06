# -*- coding: utf-8 -*-

from __future__ import print_function
from codecs import open

import sys
import os.path
import xml.etree.ElementTree
import re
import shutil



FAIL="FAIL"
TEST_FAILED="Test failed"
PASS="OK"

_TEMP_LOCATION_FOR_PROVIDED_FILES="temp_location_for_provided_files"
_known_test_libraries = ["vpltest.py", "edutest.py"]

def main(argv):
    submitted_files = get_submitted_files()
    
    def may_be_test_file(x):
        return (os.path.exists(x) 
                and x.endswith(".py")
                and x not in submitted_files
                and x != "vpltest.py")
    
    test_files = [arg for arg in argv if may_be_test_file(arg)]
    params     = [arg for arg in argv if not may_be_test_file(arg)]
    if len(test_files) == 0:
        test_files = _discover_test_files()
    
    framework = None
    show_grade = False
    show_traceback = False
    allow_deletion = False
    
    # some params are meant for this script, others for framework
    for vpl_flag in ["--nose", "--pytest", "--show-grade", "--show-traceback", "--allow-deletion"]:
        if vpl_flag in params:
            params.remove(vpl_flag)
            if vpl_flag == "--nose":
                framework = "nose"
            elif vpl_flag == "--pytest":
                framework = "pytest"
            elif vpl_flag == "--show-grade":
                show_grade = True
            elif vpl_flag == "--show-traceback":
                show_traceback = True
            elif vpl_flag == "--allow-deletion":
                allow_deletion = True

    if not allow_deletion:
        _restore_provided_files()
    
    # set TESTABLE_SCRIPT (used by edutest)
    if (len(get_submitted_files()) == 1
        and len(_discover_test_files()) == 1): 
        # I check also provided files, because if there is single submitted file
        # and several test files, then this may be because of incomplete submission
        os.environ["TESTABLE_SCRIPT"] = get_submitted_files()[0]
    else:
        os.environ["TESTABLE_SCRIPT"] = ""
    
    xml_filename = _run_tests(framework, test_files, params)
        
    _print_response(xml_filename, test_files, submitted_files, show_grade, show_traceback)
        

def get_submitted_file():
    files = get_submitted_files()
    if len(files) != 1:
        raise AssertionError("Can't give one file, when %d files were submitted",
                             len(files))
    return files[0]


def get_submitted_files():
    result = []
    for i in range(100):
        key = "VPL_SUBFILE" + str(i)
        if key in os.environ:
            result.append(os.environ[key])
        else:
            break
        
    return result

def get_max_grade():
    try:
        return float(os.environ["VPL_GRADEMAX"])
    except:
        return None

def get_vpl_language():
    return os.environ.get("VPL_LANG", None)

def create_text_block(s):
    s = ">" + s.replace("\n", "\n>")
    if not s.endswith("\n"):
        s = s + "\n"
    return s

def _compile_execution_files(args=[]):
    def _get_provided_files():
        return [file for file in os.listdir() 
                if not file.startswith("vpl_")
                and os.path.isfile(file)]
    
    def _store_provided_files():
        os.mkdir(_TEMP_LOCATION_FOR_PROVIDED_FILES)
        for file in _get_provided_files():
            shutil.copy(file, os.path.join(_TEMP_LOCATION_FOR_PROVIDED_FILES, file))
    
    filename = "vpl_execution"
    f = open(filename, mode="w", encoding="UTF-8")
    f.write('#!/bin/bash\n')
    f.write('export PYTHONIOENCODING=utf-8\n')
    f.write('source vpl_environment.sh\n')
    
    # run with the same executable
    cmd_parts = [sys.executable]
    
    # run with the same mode (-m <module name> vs. <module name>.py)
    if __package__ == None:
        cmd_parts.append(sys.argv[0])
    else:
        cmd_parts.extend(["-m", "vpltest"])
    
    cmd_parts.extend(args)
        
    f.write(" ".join(cmd_parts) + '\n')
    f.close()
    os.chmod(filename, 0o755)
    
    if "--allow-deletion" not in args:
        _store_provided_files()


def _restore_provided_files():
    if os.path.exists(_TEMP_LOCATION_FOR_PROVIDED_FILES):
        for file in os.listdir(_TEMP_LOCATION_FOR_PROVIDED_FILES):
            if not os.path.exists(file):
                shutil.move(os.path.join(_TEMP_LOCATION_FOR_PROVIDED_FILES, file), file)
    shutil.rmtree(_TEMP_LOCATION_FOR_PROVIDED_FILES, True)

def _run_tests(testing_framework, test_files, params):
    if testing_framework is None:
        testing_framework = _choose_testing_framework()
    
    if testing_framework == "pytest":
        return _run_with_pytest(test_files, params)
    elif testing_framework == "nose":
        return _run_with_nose(test_files, params)
    else:
        raise RuntimeError("Unsupported testing framework '%s'" % testing_framework)


def _run_with_pytest(files, params):
    import pytest
    
    filename="pytest_testing_report.xml"
    default_params = ["--junitxml=" + filename]
    
    if not _has_arg(params, "--color"):
        default_params.insert(0, "--color=no")
    if not _has_arg(params, "--tb"):
        default_params.insert(0, "--tb=native")
    if not _has_arg(params, "--assert"):
        default_params.insert(0, "--assert=plain")
        
    pytest.main(default_params + params + files)
    
    return filename

def _run_with_nose(files, params):
    import nose
    
    filename="nose_testing_report.xml"
    default_params = [__file__, "--with-xunit", "--xunit-file=" + filename]
    nose.run(argv=default_params + params + files)
    
    return filename

def _get_provided_py_files():
    return [file for file in os.listdir(".") 
            if file.endswith(".py")
            and file not in get_submitted_files()]

def _discover_test_files():
    return [file for file in _get_provided_py_files() 
            if "test" in file.lower()
            and file not in _known_test_libraries]

def _has_arg(argv, arg):
    return (arg in argv
            or any([x.startswith(arg) for x in argv]))

def _print_response(xml_filename, test_files, submitted_files,
                    show_grade, show_traceback):
    total_cases = 0
    passed_cases = 0
    
    tree = xml.etree.ElementTree.parse(xml_filename)
    for case_node in tree.getroot():
        print("<|--")
        case_id, result, exc_type, message, traceback = _extract_case_info(case_node)
        
        print("-" + _format_title(case_id, result))
        
        if result == FAIL:
            print(_format_message(message, exc_type, traceback, 
                                  test_files, submitted_files, show_traceback))
            
        print("--|>")
        print()
        
        total_cases += 1
        if result == PASS:
            passed_cases += 1
    
    max_grade = get_max_grade()
    if max_grade is not None and show_grade:
        pass_ratio = passed_cases / float(total_cases)
        grade = max_grade * pass_ratio
        print()
        print("Grade :=>> %.1f" % grade)

def _format_title(case_id, result):
    return case_id + " ... " + result

def _format_message(message, exc_type, traceback,
                    test_files, submitted_files, show_traceback):
    
    exc_location = _extract_relevant_location_of_exception(traceback,
                                                           test_files + submitted_files)
    
    if (exc_type == "AssertionError" 
        and any([file in exc_location for file in test_files])):
        # If the assertion was caused by test code, then show only error message
        if message:
            result = message
        else:
            result = TEST_FAILED 
    else:
        result = (exc_type 
                + (": " + message if message else "")
                + ("\n" + exc_location if exc_location else ""))
    
    if show_traceback:
        result += "\nStacktrace:\n" + create_text_block(traceback) 
    
    return result

def _extract_case_info(case_node):
    case_id = case_node.attrib["classname"] + "." + case_node.attrib["name"]
    case_id = case_id.strip(".")
    
    failure = case_node.find("failure")
    if failure == None:
        failure = case_node.find("error") # Nose uses error tags
        
    if failure != None:
        message = failure.attrib["message"]
        
        if "type" in failure.attrib:
            # Nose
            exc_type = failure.attrib["type"] 
            if exc_type.startswith("builtins."):
                exc_type = exc_type[len("builtins."):]
        else:
            # Pytest
            parts = message.split(": ", maxsplit=1) 
            if len(parts) == 2:
                exc_type, message = parts
            else:
                exc_type = parts[0]
                message = ""
            
        
        traceback = failure.text.strip()
        result = FAIL
    else:
        exc_type = None
        traceback = None
        message = ""
        result = PASS
    
    return case_id, result, exc_type, message, traceback

def _choose_testing_framework():
    try:
        import nose  # @UnusedImport
        return "nose"
    except ImportError:
        try:
            import pytest  # @UnusedImport
            return "pytest"
        except ImportError:
            raise ImportError("Neither nose nor pytest was available")


def _extract_relevant_location_of_exception(traceback, interesting_files):
    # get location of last frame
    last_location = None
    if traceback:
        for line in reversed(traceback.splitlines()):
            if re.match(r".*File.*, line.*", line):
                if not last_location:
                    last_location = line.strip()
                
                for file in interesting_files:
                    if file in line:
                        return line.strip()
    
    if last_location:
        return last_location
    else:
        return None
            

if __name__ == "__main__":
    if "VPL_LANG" in os.environ and not os.path.exists("vpl_execution"):
        # We're on Jail and should compile vpl_execution first
        _compile_execution_files(sys.argv[1:])
    else:
        main(sys.argv[1:])
